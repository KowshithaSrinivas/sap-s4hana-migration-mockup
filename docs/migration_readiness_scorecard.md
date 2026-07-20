# Migration Readiness Scorecard

**Overall readiness: 89.7%** (42 blocking errors, 17 warnings, 407 total source records)

## Blocking Errors (must resolve before load)

| Object | Reference | Issue |
|---|---|---|
| Material | MAT-1002 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1020 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1026 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1030 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1035 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1040 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1041 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1044 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1048 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1054 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1055 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1056 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1058 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1060 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1061 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1063 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1066 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1070 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1075 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1084 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1086 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1089 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1094 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1096 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1097 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1099 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1101 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1103 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1105 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1106 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1111 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Material | MAT-1114 | Missing MRP Type (DISMM) — required for MRP-relevant materials |
| Work Center | WC-101 | Missing cost center assignment — required for cost object integration |
| Work Center | WC-103 | Missing cost center assignment — required for cost object integration |
| Work Center | WC-112 | Missing cost center assignment — required for cost object integration |
| BOM | BOM-5004 / component MAT-9901 | Component material does not exist in cleaned Material Master — cannot load until resolved |
| BOM | BOM-5012 / component MAT-9910 | Component material does not exist in cleaned Material Master — cannot load until resolved |
| BOM | BOM-5015 / component MAT-9920 | Component material does not exist in cleaned Material Master — cannot load until resolved |
| BOM | BOM-5033 / component MAT-9931 | Component material does not exist in cleaned Material Master — cannot load until resolved |
| BOM | BOM-5036 / component MAT-9935 | Component material does not exist in cleaned Material Master — cannot load until resolved |
| Routing | RTG-7014 / op 20 | References work center WC-902 which does not exist — likely renamed/retired legacy code |
| Routing | RTG-7036 / op 20 | References work center WC-918 which does not exist — likely renamed/retired legacy code |

## Warnings (migrates, but flagged for business review)

| Object | Reference | Issue |
|---|---|---|
| Material | MAT-1016 | Duplicate MATNR in legacy source — kept first record, discarded remainder |
| Material | MAT-1034 | Duplicate MATNR in legacy source — kept first record, discarded remainder |
| Material | MAT-1048 | Duplicate MATNR in legacy source — kept first record, discarded remainder |
| Material | MAT-1059 | Duplicate MATNR in legacy source — kept first record, discarded remainder |
| Material | MAT-1069 | Duplicate MATNR in legacy source — kept first record, discarded remainder |
| Material | MAT-1087 | Duplicate MATNR in legacy source — kept first record, discarded remainder |
| Material | MAT-1022 | MRP type PD but reorder point (MINBE) missing — defaults to 0 |
| Material | MAT-1024 | MRP type PD but safety stock (EISBE) missing — defaults to 0 |
| Material | MAT-1028 | MRP type PD but reorder point (MINBE) missing — defaults to 0 |
| Material | MAT-1059 | MRP type PD but reorder point (MINBE) missing — defaults to 0 |
| Material | MAT-1091 | MRP type PD but reorder point (MINBE) missing — defaults to 0 |
| Work Center | WC-106 | Missing daily capacity — flagged for business input before load |
| Work Center | WC-107 | Missing daily capacity — flagged for business input before load |
| Work Center | WC-110 | Missing daily capacity — flagged for business input before load |
| Work Center | WC-113 | Missing daily capacity — flagged for business input before load |
| Work Center | WC-114 | Missing daily capacity — flagged for business input before load |
| Work Center | WC-115 | Missing daily capacity — flagged for business input before load |