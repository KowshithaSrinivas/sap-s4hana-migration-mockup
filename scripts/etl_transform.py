"""
ETL pipeline: transforms messy 'legacy' master data into S/4HANA Migration
Cockpit-ready load files, with a documented validation/readiness scorecard.

Stages:
  1. Extract  - read legacy CSVs
  2. Transform - standardize UoM, plant codes, dedupe, apply mapping rules
  3. Validate  - completeness + referential integrity checks
  4. Load prep - write clean, migration-ready files + error/readiness report
"""
import pandas as pd
import os

BASE = os.path.dirname(__file__)
LEGACY = os.path.join(BASE, "..", "data", "legacy")
CLEAN = os.path.join(BASE, "..", "data", "migration_ready")
os.makedirs(CLEAN, exist_ok=True)

# ---------------------------------------------------------------------------
# Transformation rule tables (documented, not hardcoded inline logic)
# ---------------------------------------------------------------------------
UOM_MAP = {
    "EA": "PC", "ea": "PC", "Each": "PC", "PC": "PC",
    "KG": "KG", "kg": "KG", "Kilogram": "KG",
    "L": "L", "l": "L", "Liter": "L",
}
PLANT_MAP = {"1000": "1000", "1000 ": "1000", "1100": "1100", "DE01": "1000"}

errors = []          # hard errors: record cannot migrate as-is
warnings = []         # soft issues: migrates, but flagged for review


def log_error(obj, ref, msg):
    errors.append({"object": obj, "reference": ref, "issue": msg})


def log_warning(obj, ref, msg):
    warnings.append({"object": obj, "reference": ref, "issue": msg})


# ---------------------------------------------------------------------------
# 1. MATERIALS
# ---------------------------------------------------------------------------
mat = pd.read_csv(os.path.join(LEGACY, "legacy_materials.csv"), dtype=str)

# Dedupe: keep first occurrence of each MATNR, flag the rest
dupes = mat[mat.duplicated("MATNR", keep=False)]
for matnr in dupes["MATNR"].unique():
    log_warning("Material", matnr, "Duplicate MATNR in legacy source — kept first record, discarded remainder")
mat = mat.drop_duplicates("MATNR", keep="first").copy()

# Standardize UoM
mat["MEINS"] = mat["MEINS"].map(UOM_MAP).fillna(mat["MEINS"])
# Standardize plant code (strip whitespace, map legacy codes to target plant)
mat["WERKS"] = mat["WERKS"].str.strip().map(PLANT_MAP).fillna(mat["WERKS"].str.strip())

# Mandatory-field validation
for _, row in mat.iterrows():
    if not row["DISMM"] or pd.isna(row["DISMM"]):
        log_error("Material", row["MATNR"], "Missing MRP Type (DISMM) — required for MRP-relevant materials")
    if row["DISMM"] == "PD":
        if not row["MINBE"] or pd.isna(row["MINBE"]):
            log_warning("Material", row["MATNR"], "MRP type PD but reorder point (MINBE) missing — defaults to 0")
        if not row["EISBE"] or pd.isna(row["EISBE"]):
            log_warning("Material", row["MATNR"], "MRP type PD but safety stock (EISBE) missing — defaults to 0")

mat.to_csv(os.path.join(CLEAN, "materials_migration_ready.csv"), index=False)
valid_matnrs = set(mat["MATNR"])

# ---------------------------------------------------------------------------
# 2. WORK CENTERS
# ---------------------------------------------------------------------------
wc = pd.read_csv(os.path.join(LEGACY, "legacy_workcenters.csv"), dtype=str)
wc["COST_CENTER"] = wc["COST_CENTER"].str.upper()

for _, row in wc.iterrows():
    if not row["CAPACITY_HRS_DAY"] or pd.isna(row["CAPACITY_HRS_DAY"]):
        log_warning("Work Center", row["ARBPL"], "Missing daily capacity — flagged for business input before load")
    if not row["COST_CENTER"] or pd.isna(row["COST_CENTER"]):
        log_error("Work Center", row["ARBPL"], "Missing cost center assignment — required for cost object integration")

wc.to_csv(os.path.join(CLEAN, "workcenters_migration_ready.csv"), index=False)
valid_arbpl = set(wc["ARBPL"])

# ---------------------------------------------------------------------------
# 3. BOMs — referential integrity against cleaned Material list
# ---------------------------------------------------------------------------
bom = pd.read_csv(os.path.join(LEGACY, "legacy_boms.csv"), dtype=str)
bom["UOM"] = bom["UOM"].map(UOM_MAP).fillna(bom["UOM"])

bom_clean_rows = []
for _, row in bom.iterrows():
    if row["COMPONENT_MATNR"] not in valid_matnrs:
        log_error("BOM", f"{row['STLNR']} / component {row['COMPONENT_MATNR']}",
                   "Component material does not exist in cleaned Material Master — cannot load until resolved")
        continue  # excluded from migration-ready file until resolved
    if row["PARENT_MATNR"] not in valid_matnrs:
        log_error("BOM", row["STLNR"], "Parent material does not exist in cleaned Material Master")
        continue
    bom_clean_rows.append(row)

pd.DataFrame(bom_clean_rows).to_csv(os.path.join(CLEAN, "boms_migration_ready.csv"), index=False)

# ---------------------------------------------------------------------------
# 4. ROUTINGS — referential integrity against cleaned Work Center list
# ---------------------------------------------------------------------------
rtg = pd.read_csv(os.path.join(LEGACY, "legacy_routings.csv"), dtype=str)

rtg_clean_rows = []
for _, row in rtg.iterrows():
    if row["ARBPL"] not in valid_arbpl:
        log_error("Routing", f"{row['PLNNR']} / op {row['OPERATION_SEQ']}",
                   f"References work center {row['ARBPL']} which does not exist — likely renamed/retired legacy code")
        continue
    if row["MATNR"] not in valid_matnrs:
        log_error("Routing", row["PLNNR"], "References material not found in cleaned Material Master")
        continue
    rtg_clean_rows.append(row)

pd.DataFrame(rtg_clean_rows).to_csv(os.path.join(CLEAN, "routings_migration_ready.csv"), index=False)

# ---------------------------------------------------------------------------
# READINESS SCORECARD
# ---------------------------------------------------------------------------
total_records = len(mat) + len(wc) + len(bom) + len(rtg)
total_errors = len(errors)
total_warnings = len(warnings)
readiness_pct = round(100 * (1 - total_errors / total_records), 1)

report_lines = []
report_lines.append("# Migration Readiness Scorecard\n")
report_lines.append(f"**Overall readiness: {readiness_pct}%** "
                     f"({total_errors} blocking errors, {total_warnings} warnings, {total_records} total source records)\n")
report_lines.append("## Blocking Errors (must resolve before load)\n")
report_lines.append("| Object | Reference | Issue |\n|---|---|---|")
for e in errors:
    report_lines.append(f"| {e['object']} | {e['reference']} | {e['issue']} |")
report_lines.append("\n## Warnings (migrates, but flagged for business review)\n")
report_lines.append("| Object | Reference | Issue |\n|---|---|---|")
for w in warnings:
    report_lines.append(f"| {w['object']} | {w['reference']} | {w['issue']} |")

with open(os.path.join(CLEAN, "..", "..", "docs", "migration_readiness_scorecard.md"), "w") as f:
    f.write("\n".join(report_lines))

print(f"Readiness: {readiness_pct}% | Errors: {total_errors} | Warnings: {total_warnings}")
print(f"Clean files written to: {os.path.abspath(CLEAN)}")
print("Scorecard written to docs/migration_readiness_scorecard.md")
