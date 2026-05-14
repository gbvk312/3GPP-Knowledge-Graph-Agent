import pytest
from lambdas.ingestion.relationship_extractor.handler import extract_regex_edges


def test_extract_spec_references():
    text = "The measurement reporting is defined in TS 38.331 and TS 38.213."
    edges = extract_regex_edges(text, "38.304")
    spec_refs = [e for e in edges if e["edge_type"] == "REFERENCES"]
    targets = {e["target"] for e in spec_refs}
    assert "38.331" in targets
    assert "38.213" in targets
    assert "38.304" not in targets  # Should not self-reference


def test_extract_asn1_imports():
    text = """
IMPORTS
    RSRP-Range,
    RSRQ-Range,
    SINR-Range
FROM NR-RRC-Definitions;
"""
    edges = extract_regex_edges(text, "38.213")
    import_edges = [e for e in edges if e["edge_type"] == "IMPORTS"]
    assert len(import_edges) == 3
    assert all(e["target"] == "NR-RRC-Definitions" for e in import_edges)
    sources = {e["source"] for e in import_edges}
    assert "RSRP-Range" in sources
    assert "RSRQ-Range" in sources


def test_extract_clause_references():
    text = "See clause 5.5.4 for measurement reporting and clause 4.1 for physical measurements."
    edges = extract_regex_edges(text, "38.331")
    clause_edges = [e for e in edges if e["edge_type"] == "DEFINED_IN"]
    clauses = {e["source"] for e in clause_edges}
    assert "5.5.4" in clauses
    assert "4.1" in clauses


def test_no_self_reference():
    text = "This is defined in TS 38.331 clause 5.5.4."
    edges = extract_regex_edges(text, "38.331")
    ref_edges = [e for e in edges if e["edge_type"] == "REFERENCES"]
    assert len(ref_edges) == 0  # Should not reference itself


def test_confidence_always_one_for_regex():
    text = "See TS 38.213 for details."
    edges = extract_regex_edges(text, "38.331")
    assert all(e["confidence"] == 1.0 for e in edges)
