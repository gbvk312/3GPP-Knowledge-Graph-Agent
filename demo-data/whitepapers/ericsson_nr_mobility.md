# Ericsson Technology Review: NR Mobility Enhancements Using A3 Event Reporting

**Vendor:** Ericsson
**Date:** January 2024
**Document ID:** ERI-TR-2024-0087

## Abstract

This technology review examines Ericsson's approach to optimizing NR mobility using enhanced A3 event reporting as defined in 3GPP TS 38.331 clause 5.5.4.3. We present results from 23 commercial network deployments showing improved handover performance through intelligent measurement reporting strategies.

## 1. Introduction

### 1.1 5G NR Mobility Framework

The 5G NR mobility framework relies on UE measurement reporting to trigger handover decisions. The core procedure is defined in TS 38.331 Section 5.5.4, where the UE evaluates configured events and reports measurement results to the network.

The A3 event — "Neighbour becomes offset better than SpCell" — is the primary trigger for intra-frequency handover in most commercial deployments. The event condition from TS 38.331 clause 5.5.4.3:

```
Mn + Ofn + Ocn - Hys > Ms + Ofp + Ocp + Off
```

### 1.2 Measurement Quantities

Physical layer measurements (TS 38.213 clause 4.1) provide the input to the A3 event evaluation:
- SS-RSRP for coverage-based mobility
- SS-SINR for quality-based mobility (Rel-16+)

## 2. Ericsson's Enhanced A3 Reporting

### 2.1 Multi-Beam Aware Reporting

Ericsson's implementation enhances the standard A3 event with beam-level awareness:

1. UE reports per-beam SS-RSRP (up to 4 beams per cell) in MeasResultNR IE
2. Network evaluates beam-level A3 condition
3. Handover command includes target beam information

This leverages the `rsIndexResults` field in MeasResultNR (TS 38.331 clause 5.5.4.4 ASN.1).

### 2.2 Velocity-Adaptive Offset

Ericsson introduces velocity-adaptive A3 offset:
- Low mobility (< 30 km/h): Off = 3 dB, TTT = 320ms
- Medium mobility (30-120 km/h): Off = 2 dB, TTT = 160ms
- High mobility (> 120 km/h): Off = 1 dB, TTT = 40ms

Velocity estimation uses the mobility state framework from TS 38.304 clause 5.2.4.

### 2.3 Measurement Gap Optimization

Working with the MAC layer gap handling (TS 38.321 clause 5.3), Ericsson optimizes gap usage:
- Concurrent gaps for FR1+FR2 measurements
- Adaptive MGRP based on mobility state
- Gap-less measurement for intra-frequency (no gap needed)

## 3. Deployment Results

### 3.1 Commercial Network Performance

Results from 23 Ericsson-deployed networks (2023-2024):

| Metric | Standard A3 | Ericsson Enhanced A3 | Improvement |
|--------|-------------|---------------------|-------------|
| Handover success rate | 98.7% | 99.5% | +0.8% |
| Ping-pong rate | 4.2% | 1.8% | -57% |
| RLF during HO | 1.1% | 0.4% | -64% |
| Avg interruption time | 25ms | 18ms | -28% |

### 3.2 Comparison with Conditional Handover

Ericsson also supports Conditional Handover (CHO) from Rel-17, which pre-configures handover commands:
- CHO reduces interruption time to < 10ms
- CHO uses measurement reporting from TS 38.331 clause 5.5.4 as execution trigger
- Combined with enhanced A3, achieves 99.8% handover success rate

## 4. Rel-18 Enhancements

### 4.1 Conditional Measurement Reporting

Ericsson's Rel-18 implementation includes conditional measurement reporting (TS 38.331 clause 5.5.5):
- L1 filtering before report trigger evaluation
- Reduces unnecessary reports by 35-45%
- Compatible with Nokia's implementation approach

### 4.2 Relaxed Measurements for Stationary UEs

Integration with relaxed measurement criteria (TS 38.304 clause 5.2.4.4):
- Stationary UE detection via mobility state parameters
- Measurement cycle extension reduces UE power by 25%
- Automatic fallback to normal measurements on mobility detection

## 5. Conclusion

Ericsson's enhanced A3 event reporting demonstrates significant mobility improvements across commercial 5G NR deployments. The combination of multi-beam awareness, velocity-adaptive parameters, and Rel-18 conditional reporting provides a comprehensive mobility optimization solution.

## References

- 3GPP TS 38.331 v18.2.0, "NR; RRC protocol specification"
- 3GPP TS 38.213 v18.3.0, "NR; Physical layer procedures for control"
- 3GPP TS 38.321 v18.2.0, "NR; MAC protocol specification"
- 3GPP TS 38.304 v18.1.0, "NR; UE procedures in idle mode"
- Ericsson Mobility Report, November 2023
