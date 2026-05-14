# Nokia White Paper: L3 Measurement Reporting Optimization for 5G NR Rel-18

**Vendor:** Nokia
**Date:** March 2024
**Document ID:** NKA-WP-2024-0142

## Executive Summary

This white paper describes Nokia's implementation of the Rel-18 conditional measurement reporting feature defined in 3GPP TS 38.331 Section 5.5.5. Our field trials demonstrate a 42% reduction in uplink signalling overhead while maintaining handover success rates above 99.2%.

## 1. Background: Measurement Reporting in 5G NR

### 1.1 Current Framework

The measurement reporting framework in TS 38.331 clause 5.5.4 defines event-triggered and periodic reporting mechanisms. In dense urban deployments, a UE may report measurements every 40ms (MGRP from TS 38.321 clause 5.3), generating significant uplink overhead.

Key measurement quantities (defined in TS 38.213 clause 4.1):
- SS-RSRP: Primary metric for cell selection and handover
- SS-RSRQ: Quality indicator accounting for interference
- SS-SINR: Used for beam management decisions

### 1.2 Problem Statement

In Nokia's commercial 5G SA networks (deployed across 47 operators), we observe:
- Average of 12.3 measurement reports per second per cell in dense urban
- 18% of uplink PUSCH resources consumed by measurement reporting
- 73% of reports do not trigger any mobility action

## 2. Nokia's Conditional Measurement Reporting Solution

### 2.1 Architecture

Nokia's implementation extends the A3 event (TS 38.331 clause 5.5.4.3) with L1 pre-filtering:

1. **L1 Condition Check**: Before triggering A3 event evaluation, the UE checks if SS-RSRP delta exceeds a configured threshold (condReportThreshold)
2. **Adaptive Time-to-Trigger**: TTT is dynamically adjusted based on UE velocity estimation
3. **Report Bundling**: Multiple events are bundled into a single MeasurementReport message

### 2.2 Performance Results

Field trial results from Nokia's network in Tokyo (March 2024):

| Metric | Baseline (Rel-17) | Nokia Rel-18 | Improvement |
|--------|-------------------|--------------|-------------|
| Reports/sec/cell | 12.3 | 7.1 | -42% |
| Handover success rate | 99.1% | 99.2% | +0.1% |
| Handover latency (avg) | 48ms | 45ms | -6% |
| UE power saving | - | 15% | +15% |

### 2.3 Interaction with Pre-configured Gaps

Nokia's solution leverages the pre-configured measurement gaps (TS 38.321 clause 5.3.3) to further optimize:
- Gap activation is tied to the conditional reporting trigger
- Unnecessary gaps are skipped when L1 conditions are not met
- This saves additional 8% of measurement gap overhead

## 3. Deployment Recommendations

### 3.1 Network Configuration

Recommended parameter settings for dense urban:
- condReportThreshold: 3 dB (SS-RSRP delta)
- Adaptive TTT range: 40ms - 320ms
- Report bundling window: 10ms

### 3.2 Compatibility

The solution is backward compatible with Rel-15/16/17 UEs. Legacy UEs continue using standard A3 event reporting per TS 38.331 clause 5.5.4.3.

## 4. Conclusion

Nokia's conditional measurement reporting implementation demonstrates significant signalling reduction in commercial 5G NR networks while maintaining mobility robustness. The feature is available in Nokia AirScale SW release 24.3 and later.

## References

- 3GPP TS 38.331 v18.2.0, "NR; RRC protocol specification"
- 3GPP TS 38.213 v18.3.0, "NR; Physical layer procedures for control"
- 3GPP TS 38.321 v18.2.0, "NR; MAC protocol specification"
- 3GPP TS 38.304 v18.1.0, "NR; UE procedures in idle mode"
