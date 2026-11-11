# CivicLens documentation

The repository root keeps only the essentials: [`README.md`](../README.md), [`CHANGELOG.md`](../CHANGELOG.md), [`SECURITY.md`](../SECURITY.md) and [`LICENSE`](../LICENSE).

## Guides (`docs/guides/`)

| Guide | Read it when |
|---|---|
| [Development guide](guides/DEVELOPMENT_GUIDE.md) | Running and changing the code locally |
| [Environment setup](guides/ENVIRONMENT_SETUP.md) | Configuring `backend/.env` and quota limits |
| [Testing](guides/TESTING.md) | Running unit tests, the retrieval evaluation and manual checks |
| [Admin guide](guides/ADMIN_GUIDE.md) | Signing in as a maintainer and recording source checks |
| [Deployment guide](guides/DEPLOYMENT_GUIDE.md) | Preparing a free-tier deployment |
| [Production checklist](guides/PRODUCTION_CHECKLIST.md) | Deciding whether a release is ready |
| [Backup and recovery](guides/BACKUP_AND_RECOVERY.md) | Restoring data or configuration |
| [Incident response](guides/INCIDENT_RESPONSE.md) | Handling a leaked key, outage or bad answer |

## Evaluation (`docs/evaluation/`)

| Report | Contents |
|---|---|
| [Evaluation dataset](evaluation/EVALUATION_DATASET.md) | The 28 retrieval and answer cases and their gaps |
| [RAG evaluation report](evaluation/RAG_EVALUATION_REPORT.md) | Retrieval and end-to-end answer metrics, and review status |
| [Security test report](evaluation/SECURITY_TEST_REPORT.md) | What the security tests and repository checks cover |
| [Test coverage report](evaluation/TEST_COVERAGE_REPORT.md) | Backend and frontend coverage by module |

## Where the brief's documents live

| Brief name | File |
|---|---|
| PRD | [research/PRODUCT_REQUIREMENTS.md](research/PRODUCT_REQUIREMENTS.md) |
| Architecture | [research/ARCHITECTURE_BLUEPRINT.md](research/ARCHITECTURE_BLUEPRINT.md) |
| Source registry | [research/SOURCE_INVENTORY.md](research/SOURCE_INVENTORY.md), [research/PHASE2_SOURCE_AUDIT.md](research/PHASE2_SOURCE_AUDIT.md) |
| Environment variables | [guides/ENVIRONMENT_SETUP.md](guides/ENVIRONMENT_SETUP.md), `backend/.env.example` |
| Technical debt | [audit/TECHNICAL_DEBT.md](audit/TECHNICAL_DEBT.md) |
| User feedback, improvement roadmap | Not written. There has been no user testing (citizen interviews were dropped), so there is no feedback to report. |

## Audit (`docs/audit/`) and research (`docs/research/`)

Phase 0 audit findings and the technical-debt register live in [`audit/`](audit/). Product, market, source and architecture research lives in [`research/`](research/).
