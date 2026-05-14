# 3GPP Knowledge Graph Agent

A serverless AWS application that ingests 3GPP technical specifications and vendor whitepapers, builds a Neptune property graph, embeds content into a vector knowledge base, and exposes everything through a Bedrock Agent with a React + Cytoscape.js frontend.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────────────────────┐
│  S3 Upload  │────▶│  EventBridge │────▶│  Step Functions Pipeline            │
│  (raw-bucket)│     └──────────────┘     │  Textract → Metadata → Chunker →   │
└─────────────┘                           │  Relationships → Neptune → KB Sync │
                                          └─────────────────────────────────────┘
                                                         │
                              ┌───────────────────────────┼───────────────────┐
                              ▼                           ▼                   ▼
                    ┌──────────────┐          ┌──────────────┐     ┌──────────────┐
                    │   Neptune    │          │  OpenSearch   │     │   DynamoDB   │
                    │  (Graph DB)  │          │  (Vector KB)  │     │  (Metadata)  │
                    └──────────────┘          └──────────────┘     └──────────────┘
                              ▲                           ▲                   ▲
                              └───────────────────────────┼───────────────────┘
                                                         │
                                              ┌──────────────────┐
                                              │  Bedrock Agent   │
                                              │  (Claude 3.5)    │
                                              └──────────────────┘
                                                         ▲
                                              ┌──────────────────┐
                                              │  API Gateway     │
                                              │  POST /ask       │
                                              └──────────────────┘
                                                         ▲
                                              ┌──────────────────┐
                                              │  React Frontend  │
                                              │  Cytoscape.js    │
                                              └──────────────────┘
```

## Project Structure

```
├── app.py                          # CDK app entry point
├── cdk.json                        # CDK configuration
├── pyproject.toml                  # Python dependencies (uv)
├── infra/stacks/                   # CDK stacks (7 stacks)
│   ├── storage.py                  # S3 + DynamoDB
│   ├── knowledge.py                # OpenSearch + Bedrock KB
│   ├── graph.py                    # Neptune + VPC
│   ├── pipeline.py                 # Step Functions + ingestion Lambdas
│   ├── agent.py                    # Bedrock Agent + action groups
│   ├── api.py                      # API Gateway
│   └── observability.py            # CloudWatch alarms + dashboard
├── lambdas/
│   ├── ingestion/                  # Pipeline stage handlers
│   │   ├── image_textract/
│   │   ├── metadata_extractor/
│   │   ├── semantic_chunker/
│   │   ├── relationship_extractor/
│   │   ├── neptune_writer/
│   │   ├── metadata_writer/
│   │   └── kb_sync/
│   ├── agent_tools/                # Bedrock Agent action group handlers
│   │   ├── vector_search/
│   │   ├── graph_search/
│   │   ├── metadata_query/
│   │   ├── whitepaper_lookup/
│   │   └── agent_invoker/
│   └── shared/                     # Lambda layer (logging, metrics)
├── schemas/                        # OpenAPI 3.0 schemas for action groups
├── frontend/                       # React + TypeScript + Cytoscape.js
├── tests/unit/                     # pytest unit tests
└── demo-data/                      # Sample 3GPP specs + whitepapers
```

## Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.12+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) for Python dependency management

## Setup

```bash
# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend && npm install && cd ..

# Bootstrap CDK (first time only)
cdk bootstrap
```

## Deploy

```bash
# Deploy all stacks
cdk deploy --all

# Deploy specific stack
cdk deploy Team49StorageStack
```

## Run Tests

```bash
export PYTHONPATH=.:lambdas:lambdas/shared/python
python3 -m pytest tests/ -v
```

## Frontend Development

```bash
cd frontend
cp .env.example .env  # Set VITE_API_URL to your deployed API Gateway URL
npm run dev
```

## Demo Data

Upload the demo dataset to trigger the pipeline:

```bash
# Get the raw bucket name from CDK outputs
RAW_BUCKET=$(aws cloudformation describe-stacks --stack-name Team49StorageStack --query 'Stacks[0].Outputs[?OutputKey==`RawBucketName`].OutputValue' --output text)

# Upload 3GPP specs
aws s3 cp demo-data/3gpp/ s3://$RAW_BUCKET/3gpp/ --recursive

# Upload whitepapers
aws s3 cp demo-data/whitepapers/ s3://$RAW_BUCKET/whitepapers/ --recursive
```

## Graph Node Types

| Type | Color | Description |
|------|-------|-------------|
| Spec | 🔵 Blue | 3GPP specification (e.g. TS 38.331) |
| Feature | 🟢 Green | Technical feature (e.g. measurement_reporting) |
| Whitepaper | 🟠 Orange | Vendor whitepaper |
| Vendor | 🟣 Purple | Vendor (Nokia, Ericsson) |
| Release | ⚪ Grey | 3GPP release (Rel-18) |
| ASN1Type | 🔴 Red | ASN.1 type definition |

## Edge Types

| Edge | Description |
|------|-------------|
| REFERENCES | Spec A references Spec B |
| IMPORTS | ASN.1 type imported from module |
| DEFINED_IN | Feature/type defined in a spec |
| EXPLAINS | Whitepaper explains a feature |
| SUPERSEDES | Feature replaces older feature |
| DEPLOYED_BY | Feature deployed by vendor |
| PUBLISHED_BY | Whitepaper published by vendor |
