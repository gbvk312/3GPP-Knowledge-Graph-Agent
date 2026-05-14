# 3GPP Knowledge Graph Agent

A serverless AWS application that ingests 3GPP technical specifications and vendor whitepapers, builds a Neptune property graph, embeds content into a vector knowledge base, and exposes everything through a Bedrock Agent with a React + Cytoscape.js frontend.

## Live Demo

| Resource | URL |
|----------|-----|
| Frontend | http://team49-frontend-715001841576.s3-website-us-west-2.amazonaws.com |
| API | https://wrwxpqi0u5.execute-api.us-west-2.amazonaws.com/ask |

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
│   │   ├── image_textract/         # PDF/markdown text extraction
│   │   ├── metadata_extractor/     # Claude-powered metadata extraction
│   │   ├── semantic_chunker/       # Structural boundary chunking
│   │   ├── relationship_extractor/ # Regex + Claude edge extraction
│   │   ├── neptune_writer/         # openCypher graph writes
│   │   ├── metadata_writer/        # DynamoDB enrichment
│   │   └── kb_sync/                # Bedrock KB ingestion trigger
│   ├── agent_tools/                # Bedrock Agent action group handlers
│   │   ├── vector_search/          # OpenSearch via Bedrock KB Retrieve
│   │   ├── graph_search/           # Neptune openCypher traversal
│   │   ├── metadata_query/         # DynamoDB GSI queries
│   │   ├── whitepaper_lookup/      # Filtered vector search
│   │   └── agent_invoker/          # API Gateway → Bedrock Agent
│   └── shared/                     # Lambda layer (logging, metrics)
│       └── python/shared/
├── schemas/                        # OpenAPI 3.0 schemas for action groups
├── frontend/                       # React + TypeScript + Cytoscape.js
│   ├── src/
│   │   ├── api/agent.ts            # API client
│   │   ├── components/
│   │   │   ├── FeatureCloud.tsx    # Cytoscape.js graph panel
│   │   │   └── DetailPanel.tsx     # Summary + citations panel
│   │   ├── App.tsx                 # Main layout
│   │   └── index.css               # Global styles
│   ├── .env.example                # Environment template
│   ├── vite.config.ts              # Vite configuration
│   └── package.json                # Frontend dependencies
├── tests/unit/                     # pytest unit tests (13 passing)
└── demo-data/                      # Sample 3GPP specs + whitepapers
    ├── 3gpp/                       # 4 markdown specs
    ├── whitepapers/                # 2 vendor whitepapers
    ├── mock_api.py                 # Local mock API server
    └── EXPECTED_GRAPH.md           # Expected graph output documentation
```

## Data Sources

| Source | Location | Format |
|--------|----------|--------|
| 3GPP Rel-18 Specs | `s3://team49-715001841576/datasets/marked/Rel-18/` | Markdown (pre-converted) |
| Vendor Whitepapers | `s3://team49-715001841576/datasets/Whitepapers/` | PDF |

Currently processing **27 specs** from the 38-series (5G NR), producing:
- 55 graph nodes (46 Specs + 5 Features + 3 Whitepapers + 1 Release)
- 140 edges (REFERENCES, DEFINED_IN, EXPLAINS)
- 270+ chunks in DynamoDB + S3

## Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.11+
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
# Synthesize all stacks
cdk synth

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

All 13 tests passing:
- `test_semantic_chunker.py` — chunk ID generation, boundary splitting, sub-splitting
- `test_relationship_extractor.py` — spec references, ASN.1 imports, clause detection
- `test_metadata_extractor.py` — Claude response parsing, feature ID format

## Frontend Development

```bash
cd frontend
cp .env.example .env  # Set VITE_API_URL to your deployed API Gateway URL
npm run dev
```

For production build:
```bash
cd frontend && npm run build
aws s3 sync dist/ s3://your-frontend-bucket/
```

## Upload Data to Trigger Pipeline

```bash
RAW_BUCKET=$(aws cloudformation describe-stacks --stack-name Team49StorageStack \
  --query 'Stacks[0].Outputs[?OutputKey==`RawBucketName`].OutputValue' --output text)

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

## AWS Services Used

| Category | Service | Purpose |
|----------|---------|---------|
| Compute | Lambda (Python 3.12) | All pipeline + agent handlers |
| Orchestration | Step Functions, EventBridge | Ingestion pipeline |
| Storage | S3 (KMS, versioned) | Raw files + chunks |
| Database | DynamoDB (on-demand) | Metadata + chunk index |
| Graph | Neptune Serverless | Knowledge graph (openCypher) |
| Vector | OpenSearch Serverless | Bedrock KB vector index |
| AI/ML | Bedrock (Claude 3.5, Titan Embeddings v2) | LLM + embeddings |
| Agent | Bedrock Agent | Tool orchestration |
| API | API Gateway HTTP API | POST /ask endpoint |
| Networking | VPC + Interface Endpoints | Neptune isolation |
| Security | KMS, IAM (least-privilege) | Encryption + access control |
| Observability | CloudWatch | Alarms + dashboard |
| IaC | CDK (Python) | Infrastructure deployment |

## CDK Stacks (Deploy Order)

1. **Team49StorageStack** — S3 buckets + DynamoDB tables
2. **Team49KnowledgeStack** — OpenSearch Serverless + Bedrock KB
3. **Team49GraphStack** — Neptune Serverless + VPC
4. **Team49PipelineStack** — Step Functions + ingestion Lambdas + EventBridge
5. **Team49AgentStack** — Bedrock Agent + 4 action groups
6. **Team49ApiStack** — API Gateway HTTP API
7. **Team49ObservabilityStack** — CloudWatch alarms + dashboard
