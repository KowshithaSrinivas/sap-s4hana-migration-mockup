# SAP PP Master Data — Reference Sheet

Purpose: working fluency in the objects this project migrates, so you can explain *why*
a field or transformation rule exists, not just that it does.

## 1. Material Master
The central record for anything a company buys, makes, stores, or sells. Organized in
**views** — each view = one department's slice of the same material.

| View | Owned by | Key fields |
|---|---|---|
| Basic Data | All | Material number (MATNR), description, base unit of measure (MEINS), material type (MTART, e.g. FERT=finished good, ROH=raw material, HALB=semi-finished) |
| MRP | Planning | MRP type (DISMM — e.g. PD=MRP, VB=reorder point), reorder point (MINBE), safety stock (EISBE), lot size, procurement type (make/buy) |
| Work Scheduling | Production | Production scheduling profile, in-house production time |
| Accounting | Finance/Controlling | Standard price, valuation class |
| Plant/Storage | Plant-specific | Data is maintained **per plant** — this is why "orphaned" or plant-inconsistent records are a classic migration defect |

**Why this matters for migration:** a material isn't one flat row — it's a bundle of
view-specific data, often maintained by different legacy systems or teams. Harmonizing
these into one clean S/4HANA record is most of the real work.

## 2. Bill of Materials (BOM)
Defines *what goes into* a finished product — a parent material and its component
materials with quantities. Key object: **STLNR** (BOM number), linked to a header
material, containing BOM items (component + quantity + unit of measure).

**Common migration defect:** BOM items referencing a component material number that
doesn't exist (or was deleted/renamed) in the cleaned Material Master — a referential
integrity break. This is exactly the kind of check a migration readiness scorecard exists to catch.

## 3. Work Center
A physical or logical production resource (a machine, a line, a labor pool). Key
identifier: **ARBPL**. Carries capacity data (available hours/shifts) and cost center
assignment (links production activity to financial reporting).

## 4. Routing
The sequence of **operations** performed at specific work centers to produce a
material — e.g. "Cut → Assemble → Test", each step assigned to a work center with a
standard time. Key object: **PLNNR**.

**Common migration defect:** a routing operation referencing a work center that either
doesn't exist yet in the target system or was renamed during harmonization.

## 5. Production Version
Links a **BOM + Routing + material** together into one valid "how do we actually make
this" combination — a material can have multiple production versions (e.g. different
lines, different regions) but each version must reference a valid, consistent BOM and routing.

## How these connect (the dependency chain that migration sequencing must respect)
```
Material Master  →  BOM (references component materials)
Work Center      →  Routing (references work centers)
Material + BOM + Routing  →  Production Version
```
This load order matters: you cannot load a BOM before its component materials exist, or a
routing before its work centers exist. Migration Cockpit's object sequencing enforces this,
and it's a standard interview question — "how do you sequence a PP master data migration."

## Migration-relevant vocabulary (use these terms deliberately)
- **Migration object** — SAP's predefined package describing source/target structure and field mapping for one business object (e.g. "Material," "Bill of Material")
- **Data mapping specification** — the document defining legacy field → target field, plus transformation/conversion rules
- **Mock load** — a trial migration run (often into a test/QA system) used to surface data errors before the real cutover
- **Migration readiness assessment** — a structured check of source data quality *before* attempting a load: completeness, referential integrity, mandatory-field coverage
- **Cutover** — the final, time-boxed migration into production, usually preceded by a data freeze on the legacy system
