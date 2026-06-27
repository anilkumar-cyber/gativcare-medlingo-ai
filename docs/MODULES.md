# Module Architecture

Each module is independent: owns its own DB tables, exposes a `service.py` as its only inbound
API for other modules, and declares the permission strings it checks. No module imports another
module's `models.py`.

## Platform / Identity

| Module | Owns | Exposes to other modules |
|---|---|---|
| `auth` | users, sessions, MFA, invites | `get_current_user()`, `verify_permission()` |
| `organizations` | orgs, branding, domains, AI config, subscription tier | `get_org_settings(org_id)` |
| `administration` | platform-level settings, feature flags | `get_feature_flag()` |
| `audit` | append-only audit log | `record_event()` (write-only, never read by other modules) |

## Care delivery

| Module | Owns | Exposes |
|---|---|---|
| `hospitals` | hospitals, departments | `get_hospital(id)` |
| `doctors` | doctor profiles, specialties, schedules | `get_doctor(id)`, `is_available()` |
| `patients` | patient profiles, case records, consent flags | `get_patient(id)`, `has_consent(scope)` |
| `appointments` | bookings, calendar | `book()`, `reschedule()` |
| `video_consultation` | session rooms, recordings metadata | `create_session()` |
| `medical_reports` | lab/radiology report metadata + files | `attach_report()` |
| `medical_documents` | discharge summaries, prescriptions | `get_documents(patient_id)` |
| `clinical_documentation` | AI-assisted note generation | consumes `ai.orchestrator` |
| `medical_twin` | nothing of its own — read-aggregate over patients/cases/reports/memory/travel/insurance | `get_twin(patient_id)` |

## Communication / AI surface

| Module | Owns | Exposes |
|---|---|---|
| `conversations` | conversation sessions, turns, transcripts | `start_session()`, `add_turn()` |
| `translation` | translation jobs (doc/text) | `translate(text, ctx)` |
| `voice` | STT/TTS job records | `transcribe()`, `synthesize()` |
| `interpreter` | live interpreter session state, speaker roles | `assign_role()` |
| `ai_memory` | consent-gated conversation/case memory | `recall(patient_id, scope)` |

These call into `app/ai/` (orchestrator + engines), which is shared infrastructure, not a module
with its own DB tables or REST routes.

## Patient journey / coordination

| Module | Owns | Exposes |
|---|---|---|
| `medical_tourism` | inquiry, case qualification, quotation | `qualify_lead()` |
| `travel` | itineraries | `plan_trip()` |
| `hotels` | bookings | `book_hotel()` |
| `airport_pickup` | pickup scheduling | `schedule_pickup()` |
| `visa` | visa application tracking | `track_status()` |
| `insurance` | policies, claims, pre-auth | `check_coverage()` |

## Commercial / ops

| Module | Owns | Exposes |
|---|---|---|
| `payments` | transactions | `charge()` |
| `billing` | invoices, subscriptions | `generate_invoice()` |
| `crm` | leads, follow-ups | `log_interaction()` |
| `analytics` | aggregated metrics/dashboards | read-only views over other modules' events |
| `notifications` | email/SMS/push/in-app | `notify(user_id, template)` |
| `settings` | per-org configurable options | `get_setting()` |
| `api_gateway` | external API keys, rate limits | enforced at edge, not per-module |
| `developer_portal` | API docs, key self-service | consumes `api_gateway` |
| `marketplace` | third-party integration listings | future |
| `integrations` | webhook/connector configs | `dispatch_webhook()` |
| `knowledge_base` | help articles | `search_articles()` |
| `support_center` | tickets | `create_ticket()` |

## Rule of thumb for adding a module

1. Does it own a distinct entity (patient, invoice, visa)? → new module.
2. Does it just *use* other modules' data to present something (a dashboard, a report)? →
   it belongs in `analytics` or a route handler, not a new module.
3. Always five files: `router.py`, `service.py`, `schemas.py`, `models.py`, `permissions.py`.
