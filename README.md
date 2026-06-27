# GativCare MedLingo AI

AI Medical Communication Intelligence Platform. Not a translator — see [PRD.md](PRD.md) for vision.

## Status

Architecture, AI orchestration layer, and design system are built. Backend: **auth,
organizations, hospitals, doctors, patients/medical_cases, appointments, and conversations are
real** — SQLAlchemy models, Alembic-migrated Postgres schema, JWT auth, DB-backed RBAC permission
checks, all verified end-to-end against a running Postgres (org signup → login → RBAC-gated
create → real rows). Remaining ~28 modules (billing, insurance, travel, visa, CRM, analytics,
etc.) are still interface stubs — `raise NotImplementedError` — marking where that lands next.
Frontend: design tokens, primitive component library, and the cross-portal navigation shell
(AppShell/CommandPalette/NotificationCenter/AIAssistantWidget/JourneyCompanion) are real; most
individual portal pages are not yet built, per [UX_ARCHITECTURE.md](docs/UX_ARCHITECTURE.md)'s
"design before pages" sequencing.

## Stack

Next.js (TS) + FastAPI (Python) + PostgreSQL + Redis. Shared DB, row-level `org_id` tenant
isolation + Postgres RLS. Claude as primary LLM behind a provider interface. Docker Compose on a
single VPS for launch, cloud-agnostic so AWS/Azure/GCP is an infra-only move later.

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system, AI, security, deployment architecture, decisions, future expansion
- [docs/MODULES.md](docs/MODULES.md) — module boundaries and service interfaces
- [docs/RBAC.md](docs/RBAC.md) — roles and permission matrix
- [docs/DATA_MODEL.md](docs/DATA_MODEL.md) — ERD, schema, multi-tenant enforcement
- [docs/WORKFLOWS.md](docs/WORKFLOWS.md) — patient journey, AI orchestration pipeline, business workflows
- [docs/AI_ARCHITECTURE.md](docs/AI_ARCHITECTURE.md) — MedLingoOrchestrator, 7 specialized agents, memory architecture, voice pipeline, document intelligence, safety layer, Medical Twin
- [docs/AI_TESTING.md](docs/AI_TESTING.md) — AI quality testing strategy
- [docs/UX_ARCHITECTURE.md](docs/UX_ARCHITECTURE.md) — design tokens, portal IA, navigation system, Journey Companion
- [docs/FOLDER_STRUCTURE.md](docs/FOLDER_STRUCTURE.md) — repo layout and navigation mapping

## Layout

```
apps/web   Next.js — all role portals as route groups
apps/api   FastAPI — 35 modules + AI orchestration layer
packages/  shared types generated from the API's OpenAPI schema
infra/     docker-compose + Caddyfile for VPS deployment
```

## Local dev

```
cp .env.example .env
docker compose -f infra/docker/docker-compose.yml -f infra/docker/docker-compose.dev.yml \
  up --build web api postgres redis
docker exec <api-container> alembic upgrade head   # first run only
```

Frontend at http://localhost:3100, API docs at http://localhost:8000/docs.
