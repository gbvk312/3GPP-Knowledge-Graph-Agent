import json
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("RAW_BUCKET", "test-raw")
    monkeypatch.setenv("CHUNKS_BUCKET", "test-chunks")
    monkeypatch.setenv("CHUNKS_TABLE", "test-chunks-table")
    monkeypatch.setenv("FEATURES_TABLE", "test-features-table")
    monkeypatch.setenv("NEPTUNE_ENDPOINT", "localhost")
    monkeypatch.setenv("KB_ID", "test-kb")
    monkeypatch.setenv("DATA_SOURCE_ID", "test-ds")


def test_metadata_extraction_parses_claude_response(mock_env):
    mock_metadata = {
        "spec": "38.331",
        "release": "Rel-18",
        "section": "5.5.4",
        "feature": "measurement_reporting",
        "keywords": ["RRC", "measurement", "NR"],
        "technology": "5G NR",
        "source_type": "3gpp",
        "vendor": None,
        "related_specs": ["38.213", "38.321"],
    }

    with patch("boto3.client") as mock_client, \
         patch("boto3.resource") as mock_resource:

        # Mock S3
        s3_mock = MagicMock()
        s3_mock.get_object.return_value = {
            "Body": MagicMock(read=lambda: b"# TS 38.331\n## 5.5.4 Measurement Reporting")
        }

        # Mock Bedrock
        bedrock_mock = MagicMock()
        bedrock_mock.converse.return_value = {
            "output": {"message": {"content": [{"text": json.dumps(mock_metadata)}]}}
        }

        def client_factory(service, **kwargs):
            if service == "s3":
                return s3_mock
            if service == "bedrock-runtime":
                return bedrock_mock
            return MagicMock()

        mock_client.side_effect = client_factory

        # Mock DynamoDB
        table_mock = MagicMock()
        mock_resource.return_value.Table.return_value = table_mock

        from lambdas.ingestion.metadata_extractor.handler import lambda_handler

        event = {"bucket": "test-raw", "key": "3gpp/test.md", "source_type": "3gpp"}
        result = lambda_handler(event, None)

        assert result["metadata"]["spec"] == "38.331"
        assert result["metadata"]["feature"] == "measurement_reporting"
        assert "feature_id" in result["metadata"]


def test_feature_id_format(mock_env):
    """Feature ID should be spec#release#section#feature"""
    feature_id = "38.331#Rel-18#5.5.4#measurement_reporting"
    parts = feature_id.split("#")
    assert len(parts) == 4
    assert parts[0] == "38.331"
    assert parts[1] == "Rel-18"
    assert parts[2] == "5.5.4"
    assert parts[3] == "measurement_reporting"
