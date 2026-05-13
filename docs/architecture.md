# Architecture

The enterprise alpha is a local-first cyber range control plane.

## Logical Services

- Backend API: scenarios, exercises, telemetry, detections, evidence, RBAC, and reports.
- Worker: executes scenarios through the backend API.
- Frontend: operator console.
- Postgres: future metadata persistence target.
- Redis: future queue target.
- OpenSearch: future log search target.
- MinIO: future evidence object storage target.

The current alpha keeps execution deterministic and testable while preserving interfaces for durable storage and external integrations.

## Trust Boundaries

- Scenario execution is constrained by configuration.
- Lab targets must match configured hosts or CIDRs.
- External integrations are opt-in and disabled by default.
- Evidence writes append audit-chain records.

