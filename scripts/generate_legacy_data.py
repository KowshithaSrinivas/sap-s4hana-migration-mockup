"""
Generates a synthetic 'legacy ERP export' simulating messy master data that a
company would face ahead of an SAP S/4HANA migration.

Objects: Materials, Bills of Material (BOM), Work Centers, Routings, Production Versions
Deliberately injected defects (documented below) mirror the kinds of issues a
Master Data Migration Expert is expected to catch during a readiness assessment.
"""
import csv
import random
import os

random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "legacy")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. MATERIALS (legacy "Item Master")
# ---------------------------------------------------------------------------
material_types = ["FERT", "HALB", "ROH"]
uom_variants = {"EA": ["EA", "ea", "Each", "PC"], "KG": ["KG", "kg", "Kilogram"], "L": ["L", "l", "Liter"]}
plants = ["1000", "1100", "DE01", "1000 "]  # inconsistent plant coding is a real defect

materials = []
for i in range(1, 121):
    matnr = f"MAT-{1000+i}"
    mtype = random.choice(material_types)
    base_uom_clean = random.choice(list(uom_variants.keys()))
    uom = random.choice(uom_variants[base_uom_clean])  # inconsistent UoM spelling
    plant = random.choice(plants)
    description = f"{mtype} Component {i}"

    # Defect: ~8% missing MRP-critical fields
    reorder_point = "" if random.random() < 0.08 else round(random.uniform(10, 500), 0)
    safety_stock = "" if random.random() < 0.08 else round(random.uniform(5, 100), 0)
    mrp_type = random.choice(["PD", "VB", "ND", ""])  # blank = defect

    materials.append({
        "MATNR": matnr, "MTART": mtype, "MAKTX": description,
        "MEINS": uom, "WERKS": plant,
        "DISMM": mrp_type, "MINBE": reorder_point, "EISBE": safety_stock,
    })

# Defect: inject 6 exact duplicate material numbers with conflicting descriptions
for _ in range(6):
    src = random.choice(materials).copy()
    src["MAKTX"] = src["MAKTX"] + " (DUPLICATE ENTRY)"
    materials.append(src)

with open(os.path.join(OUT, "legacy_materials.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=materials[0].keys())
    w.writeheader()
    w.writerows(materials)

# ---------------------------------------------------------------------------
# 2. WORK CENTERS
# ---------------------------------------------------------------------------
work_centers = []
for i in range(1, 16):
    work_centers.append({
        "ARBPL": f"WC-{100+i}",
        "KTEXT": f"Work Center {i}",
        "CAPACITY_HRS_DAY": random.choice([8, 16, 24, ""]),  # blank = defect
        "COST_CENTER": random.choice(["CC-4000", "CC-4100", "cc-4200", ""]),  # inconsistent case + blank
    })

with open(os.path.join(OUT, "legacy_workcenters.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=work_centers[0].keys())
    w.writeheader()
    w.writerows(work_centers)

# ---------------------------------------------------------------------------
# 3. BOMs (component structures for FERT/HALB materials)
# ---------------------------------------------------------------------------
finished_materials = [m for m in materials if m["MTART"] in ("FERT", "HALB")][:40]
all_matnrs = [m["MATNR"] for m in materials]

bom_items = []
bom_counter = 5000
for parent in finished_materials:
    bom_counter += 1
    n_components = random.randint(2, 5)
    for _ in range(n_components):
        component = random.choice(all_matnrs)
        # Defect: ~5% of BOM items reference a material number that doesn't exist
        if random.random() < 0.05:
            component = f"MAT-{9900 + random.randint(1, 50)}"  # nonexistent
        bom_items.append({
            "STLNR": f"BOM-{bom_counter}",
            "PARENT_MATNR": parent["MATNR"],
            "COMPONENT_MATNR": component,
            "QTY": round(random.uniform(1, 10), 2),
            "UOM": random.choice(["EA", "ea", "KG"]),
        })

with open(os.path.join(OUT, "legacy_boms.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=bom_items[0].keys())
    w.writeheader()
    w.writerows(bom_items)

# ---------------------------------------------------------------------------
# 4. ROUTINGS (operations per parent material, referencing work centers)
# ---------------------------------------------------------------------------
routing_ops = []
all_wc = [w["ARBPL"] for w in work_centers]
plan_counter = 7000
for parent in finished_materials:
    plan_counter += 1
    n_ops = random.randint(2, 4)
    for seq, _ in enumerate(range(n_ops), start=1):
        wc = random.choice(all_wc)
        # Defect: ~4% reference a work center that doesn't exist (renamed/retired)
        if random.random() < 0.04:
            wc = f"WC-{900 + random.randint(1, 20)}"
        routing_ops.append({
            "PLNNR": f"RTG-{plan_counter}",
            "MATNR": parent["MATNR"],
            "OPERATION_SEQ": seq * 10,
            "ARBPL": wc,
            "STD_TIME_MIN": round(random.uniform(2, 45), 1),
        })

with open(os.path.join(OUT, "legacy_routings.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=routing_ops[0].keys())
    w.writeheader()
    w.writerows(routing_ops)

print(f"Generated {len(materials)} materials, {len(work_centers)} work centers, "
      f"{len(bom_items)} BOM items, {len(routing_ops)} routing operations.")
print(f"Files written to: {os.path.abspath(OUT)}")
