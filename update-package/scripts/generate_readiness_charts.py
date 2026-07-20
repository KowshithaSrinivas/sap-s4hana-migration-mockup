"""
Generates visual charts from the migration readiness scorecard — turns the
raw error/warning log into a dashboard-style view (readiness %, errors by
object, error type breakdown), similar in spirit to the Power BI KPI
dashboards referenced elsewhere in the candidate's portfolio.
"""
import re
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(__file__)
SCORECARD = os.path.join(BASE, "..", "docs", "migration_readiness_scorecard.md")
OUT_DIR = os.path.join(BASE, "..", "docs", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

with open(SCORECARD) as f:
    content = f.read()

# Parse overall readiness line
readiness_match = re.search(r"Overall readiness: ([\d.]+)%", content)
readiness_pct = float(readiness_match.group(1))

counts_match = re.search(r"\((\d+) blocking errors, (\d+) warnings, (\d+) total source records\)", content)
n_errors, n_warnings, n_total = map(int, counts_match.groups())

# Parse table rows: | Object | Reference | Issue |
def parse_table_rows(section_text):
    rows = []
    for line in section_text.splitlines():
        if line.startswith("| ") and "Object" not in line and "---" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) == 3:
                rows.append(parts)
    return rows

error_section = content.split("## Blocking Errors")[1].split("## Warnings")[0]
warning_section = content.split("## Warnings")[1]

error_rows = parse_table_rows(error_section)
warning_rows = parse_table_rows(warning_section)

from collections import Counter
error_by_obj = Counter(r[0] for r in error_rows)
warning_by_obj = Counter(r[0] for r in warning_rows)

objects = sorted(set(list(error_by_obj.keys()) + list(warning_by_obj.keys())))

# --- Chart 1: Readiness donut ---
fig, ax = plt.subplots(figsize=(5, 5))
sizes = [readiness_pct, 100 - readiness_pct]
colors = ["#2E7D32", "#C62828"]
ax.pie(sizes, colors=colors, startangle=90, counterclock=False,
       wedgeprops=dict(width=0.35, edgecolor="white"))
ax.text(0, 0, f"{readiness_pct}%\nReady", ha="center", va="center", fontsize=20, fontweight="bold")
ax.set_title("Migration Readiness Score", fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "readiness_donut.png"), dpi=150, transparent=False, facecolor="white")
plt.close()

# --- Chart 2: Errors & warnings by object ---
fig, ax = plt.subplots(figsize=(8, 4.5))
x = range(len(objects))
err_vals = [error_by_obj.get(o, 0) for o in objects]
warn_vals = [warning_by_obj.get(o, 0) for o in objects]
width = 0.35
ax.bar([i - width/2 for i in x], err_vals, width, label="Blocking Errors", color="#C62828")
ax.bar([i + width/2 for i in x], warn_vals, width, label="Warnings", color="#F9A825")
ax.set_xticks(list(x))
ax.set_xticklabels(objects, rotation=0)
ax.set_ylabel("Count")
ax.set_title(f"Data Issues by Object ({n_total} total source records)", fontsize=13, fontweight="bold")
ax.legend()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
for i, v in enumerate(err_vals):
    if v > 0:
        ax.text(i - width/2, v + 0.3, str(v), ha="center", fontsize=9)
for i, v in enumerate(warn_vals):
    if v > 0:
        ax.text(i + width/2, v + 0.3, str(v), ha="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "issues_by_object.png"), dpi=150, facecolor="white")
plt.close()

# --- Chart 3: Summary KPI strip ---
fig, ax = plt.subplots(figsize=(9, 2.2))
ax.axis("off")
kpis = [
    (f"{n_total}", "Source Records"),
    (f"{n_errors}", "Blocking Errors"),
    (f"{n_warnings}", "Warnings Flagged"),
    (f"{readiness_pct}%", "Migration Readiness"),
]
kpi_colors = ["#37474F", "#C62828", "#F9A825", "#2E7D32"]
for i, ((val, label), color) in enumerate(zip(kpis, kpi_colors)):
    ax.text(0.125 + i * 0.25, 0.65, val, ha="center", va="center",
             fontsize=24, fontweight="bold", color=color, transform=ax.transAxes)
    ax.text(0.125 + i * 0.25, 0.2, label, ha="center", va="center",
             fontsize=11, color="#333333", transform=ax.transAxes)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "kpi_summary.png"), dpi=150, facecolor="white")
plt.close()

print(f"Saved 3 charts to {os.path.abspath(OUT_DIR)}")
print(f"Readiness: {readiness_pct}% | Errors: {n_errors} | Warnings: {n_warnings} | Objects: {objects}")
