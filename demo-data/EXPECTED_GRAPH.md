# Demo Dataset — Expected Graph Output

## Overview

This demo dataset covers the **"Measurement Reporting in 5G NR"** domain — a tightly coupled set of 3GPP specs and vendor whitepapers that produce a rich, interconnected knowledge graph.

## Source Files

```
demo-data/
├── 3gpp/
│   ├── TS_38.331_Rel18_5.5.4.md   # Core: RRC Measurement Reporting
│   ├── TS_38.213_Rel18_4.1.md     # Physical layer measurements
│   ├── TS_38.321_Rel18_5.3.md     # MAC measurement gap handling
│   └── TS_38.304_Rel18_5.2.4.md   # Cell reselection criteria
└── whitepapers/
    ├── nokia_measurement_optimization.md   # Nokia: L3 reporting optimization
    └── ericsson_nr_mobility.md             # Ericsson: A3 event enhancements
```

## Expected Nodes (14)

| ID | Label | Type |
|----|-------|------|
| 38.331 | TS 38.331 | Spec |
| 38.213 | TS 38.213 | Spec |
| 38.321 | TS 38.321 | Spec |
| 38.304 | TS 38.304 | Spec |
| rel-18 | Rel-18 | Release |
| measurement-reporting | Measurement Reporting | Feature |
| conditional-measurement-reporting | Conditional Measurement Reporting | Feature |
| cell-reselection | Cell Reselection | Feature |
| nokia-wp-0142 | Nokia L3 Optimization | Whitepaper |
| ericsson-wp-0087 | Ericsson NR Mobility | Whitepaper |
| nokia | Nokia | Vendor |
| ericsson | Ericsson | Vendor |
| MeasurementReport | MeasurementReport | ASN1Type |
| MeasGapConfig | MeasGapConfig | ASN1Type |

## Expected Edges (22)

| Source | Target | Type | Confidence |
|--------|--------|------|-----------|
| 38.331 | 38.213 | REFERENCES | 1.0 |
| 38.331 | 38.321 | REFERENCES | 1.0 |
| 38.331 | 38.304 | REFERENCES | 1.0 |
| 38.304 | 38.213 | REFERENCES | 1.0 |
| 38.304 | 38.331 | REFERENCES | 1.0 |
| 38.321 | 38.331 | REFERENCES | 1.0 |
| 38.213 | 38.331 | REFERENCES | 1.0 |
| measurement-reporting | 38.331 | DEFINED_IN | 1.0 |
| conditional-measurement-reporting | 38.331 | DEFINED_IN | 1.0 |
| cell-reselection | 38.304 | DEFINED_IN | 1.0 |
| conditional-measurement-reporting | measurement-reporting | SUPERSEDES | 1.0 |
| MeasurementReport | 38.331 | DEFINED_IN | 1.0 |
| MeasGapConfig | 38.321 | DEFINED_IN | 1.0 |
| MeasQuantityResults | 38.213 | IMPORTS | 1.0 |
| nokia-wp-0142 | measurement-reporting | EXPLAINS | 0.95 |
| nokia-wp-0142 | conditional-measurement-reporting | EXPLAINS | 0.92 |
| ericsson-wp-0087 | measurement-reporting | EXPLAINS | 0.93 |
| ericsson-wp-0087 | cell-reselection | EXPLAINS | 0.78 |
| nokia-wp-0142 | nokia | PUBLISHED_BY | 1.0 |
| ericsson-wp-0087 | ericsson | PUBLISHED_BY | 1.0 |
| nokia | conditional-measurement-reporting | DEPLOYED_BY | 0.90 |
| ericsson | measurement-reporting | DEPLOYED_BY | 0.88 |

## Demo Queries

These queries demonstrate the graph intelligence capabilities:

### 1. Dependency Depth (from 38.331, depth=2)
Returns: 38.331 → 38.213, 38.321, 38.304 (depth 1) → no further outgoing (depth 2)

### 2. Feature Lineage
conditional-measurement-reporting SUPERSEDES measurement-reporting (Rel-15 → Rel-18)

### 3. Whitepaper Coverage for 38.331
Returns: nokia-wp-0142, ericsson-wp-0087 (both EXPLAIN features DEFINED_IN 38.331)

### 4. Cross-Vendor Analysis for "measurement-reporting"
Returns: Nokia (DEPLOYED_BY conditional-measurement-reporting), Ericsson (DEPLOYED_BY measurement-reporting)

### 5. Orphan Detection
All specs have incoming REFERENCES → no orphans in this demo set

## Expected Chunks (~35)

Approximate chunking output:
- TS_38.331: 8 chunks (headings, event table, ASN.1 block, feature table)
- TS_38.213: 7 chunks (4.1.1-4.1.4, ASN.1, L1-RSRP, filtering)
- TS_38.321: 7 chunks (5.3.1-5.3.5, ASN.1 block)
- TS_38.304: 8 chunks (5.2.4.1-5.2.4.5, table, ASN.1 block)
- Nokia WP: 5 chunks (sections 1-4 + references)
- Ericsson WP: 6 chunks (sections 1-5 + references)
