# GativCare MedLingo AI — Enterprise Architecture

Status: Phase 1 foundation. No feature code yet — this defines the skeleton everything else is built on.

## 1. What this is

An AI Medical Communication Intelligence Platform, not a translator. Core loop for every utterance:

```
Audio/Text In
  -> Speaker Recognition Engine   (who is speaking: doctor/patient/nurse/family/interpreter)
  -> Language Intelligence Engine (detect language, detect code-switching)
  -> Context Engine                (pull conversation memory + patient case context)
  -> Medical Knowledge Engine      (terminology, drug names, abbreviations, ICD/SNOMED mapping)
  -> Clinical Reasoning Engine     (intent: symptom report? instruction? question? — never diagnosis)
  -> Emotion Engine                (fear/pain/urgency -> tone adaptation)
  -> Safety Engine                 (PHI redaction checks, disclaimer injection, escalation flags)
  -> Conversation Intelligence     (compose natural, role-appropriate, culturally adapted response)
  -> Voice Intelligence Engine     (TTS, prosody, pronunciation of drug/medical terms)
  -> Memory Engine                 (persist turn to case-scoped conversation memory, consent-gated)
```

Every engine is a separate service-layer component behind a common `Engine` interface in
`apps/api/app/ai/engines/`. They are composed by an **AI Orchestrator** — no engine calls another
engine directly. This is the only way 14 "engines" stay maintainable instead of turning into a ball
of mud.

## 2. Application architecture

One Next.js app (`apps/web`), not eleven separate apps. Portals are **role-aware route groups**
sharing the same design system, auth, and data layer — separate apps would mean 11x the build/deploy
surface for zero isolation benefit (isolation is a backend/RBAC concern, not a frontend one).

```
apps/web/app/
  (marketing)/              public site, pricing, about
  (auth)/                   login, MFA, invite-accept, org-signup
  (dashboard)/
    super-admin/
    organization/
    hospital/
    doctor/
    patient/
    interpreter/
    finance/
    support/
  (api-proxy)/              server actions / route handlers that call apps/api
```

Mobile app and Public API / Developer Console are listed in the PRD as future workspaces — they
consume the same `apps/api` REST/WebSocket surface, so they're additive later, not a Phase-1 cost.

## 3. Backend architecture

`apps/api` (FastAPI) is organized by **bounded module**, one folder per Enterprise Module
(`auth`, `organizations`, `hospitals`, `doctors`, `patients`, `appointments`, `conversations`,
`translation`, `voice`, `medical_reports`, `travel`, `insurance`, `billing`, `analytics`,
`audit`, ...). Each module owns:

```
modules/<name>/
  router.py       # FastAPI routes — HTTP boundary only
  service.py      # business logic
  schemas.py      # Pydantic request/response models
  models.py       # SQLAlchemy ORM models owned by this module
  permissions.py  # permission strings this module defines/checks
```

Cross-module calls go through each module's `service.py`, never through another module's `models.py`
directly — this is the boundary that keeps "Every module must be independent" true in practice and
makes a future microservice split (e.g. pulling Voice or Translation out under load) a move, not a
rewrite.

`app/core/` holds cross-cutting concerns: tenant context middleware, auth/JWT, RBAC dependency,
audit logging hook, exception handlers, settings.

`app/ai/` holds the orchestrator + engines, consumed by the `conversations` and `translation`
modules — AI is a service the modules call, not a module itself with REST routes of its own.

## 4. AI provider architecture

Single `LLMProvider` interface (`app/ai/providers/base.py`). Claude (Anthropic) is the default
implementation for reasoning/interpretation/composition. Speech-to-text and text-to-speech sit
behind their own `STTProvider`/`TTSProvider` interfaces so a specialized voice model can be swapped
in per-language without touching the orchestrator. This is what "communicate through orchestration
rather than direct coupling" means concretely — no engine imports `anthropic` directly; they all go
through the provider interface.

## 5. Multi-tenancy

Shared Postgres database. Every tenant-scoped table carries `org_id`. Enforced twice:
1. **App layer** — a request-scoped tenant context (set from the authenticated user's org) is
   injected into every query via a SQLAlchemy session-level filter.
2. **DB layer** — Postgres Row-Level Security policies on every tenant table, keyed to a
   `current_setting('app.current_org_id')` session variable set per-request.

Two layers because app-layer bugs (a forgotten `.filter(org_id=...)`) are the single most common
cause of cross-tenant data leaks in SaaS; RLS is the backstop that makes such a bug a non-event
instead of an incident.

Org-level branding/logo/domain/AI-config/subscription live in the `organizations` module as
settings rows, not environment config — every tenant-specific value must be DB-driven, never
hardcoded or deployed-per-customer.

## 6. Security architecture

- AuthN: JWT access/refresh, MFA (TOTP) required for clinical roles.
- AuthZ: RBAC, permission strings checked via a FastAPI dependency (`require_permission("patients.edit")`).
- Encryption: TLS in transit (Caddy auto-HTTPS), AES-256 at rest for PHI columns, S3-compatible
  storage with server-side encryption for documents/reports.
- Audit: every read/write to patient/clinical data emits an audit-log event (who, what, when, org)
  — append-only table, no update/delete permission on it even for admins.
- Consent: conversation-memory carry-forward (e.g. recalling prior surgeries) is gated by an explicit
  per-patient consent flag, checked before the Memory Engine returns anything.
- Compliance posture: architecture supports HIPAA/GDPR-style controls (audit trail, encryption,
  access control, data residency via deployable-anywhere infra) — actual certification is a
  deployment/process exercise on top of this, not a code claim.

## 7. Deployment architecture

Phase 1 target: single Hostinger VPS, Docker Compose, Caddy reverse proxy (auto TLS).

```
infra/docker/
  docker-compose.yml   # web, api, postgres, redis, caddy
infra/nginx/           # alt reverse-proxy config if Caddy is swapped later
```

Every app container is stateless (sessions in Redis/JWT, files in S3-compatible object storage, not
local disk) — this is the one rule that makes the later move from "1 VPS" to "N VPS behind a load
balancer" to "AWS ECS/EKS" a deployment change instead of a code change. Postgres and Redis are the
only stateful services; they're the first things you'd move to managed services (RDS/ElastiCache or
equivalent) when a single VPS stops being enough.

## 8. Scalability roadmap

| Stage | Infra | Trigger |
|---|---|---|
| Launch | 1 VPS, docker-compose | first paying orgs |
| Growth | N VPS behind LB, managed Postgres | sustained CPU/connection pressure |
| Scale | Container orchestration (ECS/K8s), read replicas, queue workers split out | multi-region orgs, conversation volume needing horizontal AI worker scaling |
| Global | Multi-region deployment, per-region data residency | enterprise/government contracts requiring data locality |

Nothing in the app code changes between stages — only `infra/` and connection strings/env config do,
because of the stateless-container + DB-driven-tenant-config rules above.

## 9. Future expansion points (explicitly designed for, not built yet)

- New AI engine = new file in `app/ai/engines/` + orchestrator wiring. No existing engine touched.
- New module (e.g. future "AI Recovery Coach") = new folder in `modules/`, same five-file shape.
- New portal/role = new route group in `apps/web/app/(dashboard)/` + permission strings in RBAC.md.
- New LLM/STT/TTS vendor = new provider implementation, zero orchestrator changes.
- Microservice extraction = move one `modules/<x>` folder to its own FastAPI app; the
  service-layer boundary already exists, so this is mechanical, not a redesign.

See [MODULES.md](MODULES.md), [RBAC.md](RBAC.md), [DATA_MODEL.md](DATA_MODEL.md),
[WORKFLOWS.md](WORKFLOWS.md), [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) for the detailed designs
this overview summarizes.
