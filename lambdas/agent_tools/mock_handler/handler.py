import json

DEMO_RESPONSE = {
    "summary": "**TS 38.331 Section 5.5.4** defines the measurement reporting framework for 5G NR. The UE evaluates configured events (A1-A6) and reports measurement results to the network. Physical layer measurements (SS-RSRP, SS-RSRQ, SS-SINR) are defined in **TS 38.213 clause 4.1**, while measurement gap handling is specified in **TS 38.321 clause 5.3**.\n\n**Rel-18 Enhancement:** Conditional measurement reporting reduces signalling overhead by up to 40% by applying L1 pre-filtering before triggering event evaluation.\n\nNokia reports 42% reduction in measurement reports/sec/cell in Tokyo field trials. Ericsson achieves 99.5% handover success rate with enhanced A3 event reporting across 23 commercial networks.",
    "nodes": [
        {"data": {"id": "38.331", "label": "TS 38.331", "type": "Spec"}},
        {"data": {"id": "38.213", "label": "TS 38.213", "type": "Spec"}},
        {"data": {"id": "38.321", "label": "TS 38.321", "type": "Spec"}},
        {"data": {"id": "38.304", "label": "TS 38.304", "type": "Spec"}},
        {"data": {"id": "measurement-reporting", "label": "Measurement Reporting", "type": "Feature"}},
        {"data": {"id": "conditional-measurement-reporting", "label": "Conditional Measurement Reporting", "type": "Feature"}},
        {"data": {"id": "cell-reselection", "label": "Cell Reselection", "type": "Feature"}},
        {"data": {"id": "physical-measurements", "label": "Physical Measurements", "type": "Feature"}},
        {"data": {"id": "nokia-wp-0142", "label": "Nokia L3 Optimization", "type": "Whitepaper"}},
        {"data": {"id": "ericsson-wp-0087", "label": "Ericsson NR Mobility", "type": "Whitepaper"}},
        {"data": {"id": "nokia", "label": "Nokia", "type": "Vendor"}},
        {"data": {"id": "ericsson", "label": "Ericsson", "type": "Vendor"}},
        {"data": {"id": "rel-18", "label": "Rel-18", "type": "Release"}},
        {"data": {"id": "MeasurementReport", "label": "MeasurementReport", "type": "ASN1Type"}},
    ],
    "edges": [
        {"data": {"source": "38.331", "target": "38.213", "label": "REFERENCES"}},
        {"data": {"source": "38.331", "target": "38.321", "label": "REFERENCES"}},
        {"data": {"source": "38.331", "target": "38.304", "label": "REFERENCES"}},
        {"data": {"source": "38.304", "target": "38.213", "label": "REFERENCES"}},
        {"data": {"source": "38.304", "target": "38.331", "label": "REFERENCES"}},
        {"data": {"source": "38.321", "target": "38.331", "label": "REFERENCES"}},
        {"data": {"source": "38.213", "target": "38.331", "label": "REFERENCES"}},
        {"data": {"source": "measurement-reporting", "target": "38.331", "label": "DEFINED_IN"}},
        {"data": {"source": "conditional-measurement-reporting", "target": "38.331", "label": "DEFINED_IN"}},
        {"data": {"source": "cell-reselection", "target": "38.304", "label": "DEFINED_IN"}},
        {"data": {"source": "physical-measurements", "target": "38.213", "label": "DEFINED_IN"}},
        {"data": {"source": "conditional-measurement-reporting", "target": "measurement-reporting", "label": "SUPERSEDES"}},
        {"data": {"source": "MeasurementReport", "target": "38.331", "label": "DEFINED_IN"}},
        {"data": {"source": "nokia-wp-0142", "target": "measurement-reporting", "label": "EXPLAINS"}},
        {"data": {"source": "nokia-wp-0142", "target": "conditional-measurement-reporting", "label": "EXPLAINS"}},
        {"data": {"source": "ericsson-wp-0087", "target": "measurement-reporting", "label": "EXPLAINS"}},
        {"data": {"source": "ericsson-wp-0087", "target": "cell-reselection", "label": "EXPLAINS"}},
        {"data": {"source": "nokia-wp-0142", "target": "nokia", "label": "PUBLISHED_BY"}},
        {"data": {"source": "ericsson-wp-0087", "target": "ericsson", "label": "PUBLISHED_BY"}},
        {"data": {"source": "nokia", "target": "conditional-measurement-reporting", "label": "DEPLOYED_BY"}},
        {"data": {"source": "ericsson", "target": "measurement-reporting", "label": "DEPLOYED_BY"}},
    ],
    "citations": [
        {"spec": "38.331", "release": "Rel-18", "section": "5.5.4", "text": "The UE shall initiate the measurement reporting procedure when reporting criteria are fulfilled for a measurement configured with report type set to eventTriggered or periodical."},
        {"spec": "38.213", "release": "Rel-18", "section": "4.1", "text": "SS-RSRP is defined as the linear average over the power contributions of the resource elements that carry secondary synchronization signals."},
        {"spec": "38.321", "release": "Rel-18", "section": "5.3", "text": "Measurement gaps are time intervals during which the UE performs inter-frequency and inter-RAT measurements."},
        {"spec": "38.331", "release": "Rel-18", "section": "5.5.5", "text": "In Rel-18, conditional measurement reporting allows the UE to report measurements only when specific L1 conditions are met, reducing signalling overhead by up to 40%."},
    ],
}


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(DEMO_RESPONSE),
    }
