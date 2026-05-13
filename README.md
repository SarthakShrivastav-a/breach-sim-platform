# Breach Simulation Platform

Enterprise alpha for an isolated breach simulation cyber range, scenario execution, telemetry collection, detection validation, evidence tracking, and after-action reporting.

This repository is intentionally separate from any healthcare projects.

## What Works In This Alpha

- FastAPI control plane with scenario, exercise, telemetry, detection, evidence, RBAC, and report endpoints.
- Safe scenario execution engine with telemetry-only and allowlisted local command modes.
- YAML scenario library aligned to MITRE ATT&CK metadata.
- Sigma-like rule loader and deterministic detection correlation.
- Tamper-evident audit hash chaining for evidence events.
- React/Vite operator console for scenarios, exercises, detections, evidence, and reports.
- Worker CLI for executing a scenario through the API.
- Docker Compose stack for backend, frontend, worker, Postgres, Redis, OpenSearch, and MinIO.
- GitHub Actions for backend, frontend, Docker Compose, Docker image build, and gated publish workflow.

## Safety Model

The default runtime blocks unsafe behavior:

- Only telemetry-only and allowlisted command execution modes are supported.
- Commands must be explicitly allowed by configuration.
- Targets are constrained to configured lab CIDRs/hosts.
- External SIEM/SOAR pushes are disabled unless configured.
- No secrets, provider names, endpoints, ports, or thresholds are hardcoded in business logic.

## Quick Start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pytest backend\tests worker\tests

cd frontend
npm install
npm run lint
npm test
npm run build
```

Run the API:

```powershell
uvicorn app.main:app --app-dir backend --reload
```

Run the frontend:

```powershell
cd frontend
npm run dev
```

Run the full Docker stack:

```powershell
docker compose up --build
```

Local URLs:

- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`
- OpenSearch: `http://localhost:9200`
- MinIO Console: `http://localhost:9001`

## Release Workflow

This repo follows the Sarthak GitHub release workflow:

- `main`: release branch.
- `dev`: integration branch.
- `feature/*`, `fix/*`, `test/*`, `docs/*`, `ci/*`: short-lived PR branches.
- Release PRs merge `dev` into `main`.
- Docker Hub publish workflow is present but disabled until `ENABLE_DOCKER_PUBLISH=true` and Docker Hub secrets are configured.

