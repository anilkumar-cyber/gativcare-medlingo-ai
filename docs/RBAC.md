# Roles & Permissions (RBAC)

Permissions are strings: `<module>.<action>`, e.g. `patients.edit`. Checked via a FastAPI
dependency `require_permission("patients.edit")` on each route. Roles are just named bundles of
permissions, stored in DB (`roles`, `role_permissions`), not hardcoded enums — an org admin can
create custom roles for their own staff without a code change.

## Role list (scope = platform | org | hospital)

| Role | Scope |
|---|---|
| Super Admin | platform |
| Platform Admin | platform |
| Organization Owner | org |
| Hospital Admin | hospital |
| Department Manager | hospital |
| Doctor / Surgeon / Consultant | hospital |
| Nurse | hospital |
| Receptionist | hospital |
| Medical Interpreter | org |
| Patient Coordinator | org |
| Travel Coordinator | org |
| Insurance Executive | org |
| Finance Executive | org |
| Support Executive | platform |
| Patient | self |
| Patient Family | self (via patient grant) |
| Emergency Staff | hospital |

## Permission matrix (representative — full list lives in DB seed, not here)

| Permission | Super Admin | Org Owner | Hospital Admin | Doctor | Nurse | Receptionist | Interpreter | Coordinator | Insurance Exec | Finance Exec | Patient | Family |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `patients.view` | Y | Y | Y | Y* | Y* | Y | Y | Y | Y | - | self | grant |
| `patients.edit` | Y | Y | Y | Y* | - | partial | - | Y | - | - | self | - |
| `patients.delete` | Y | Y | - | - | - | - | - | - | - | - | - | - |
| `reports.view` | Y | Y | Y | Y* | Y* | - | - | Y | Y | - | self | grant |
| `reports.upload` | Y | Y | Y | Y | Y | Y | - | Y | - | - | - | - |
| `conversations.translate` | Y | Y | Y | Y | Y | Y | Y | Y | - | - | - | - |
| `conversations.generate_summary` | Y | Y | Y | Y | - | - | Y | Y | - | - | - | - |
| `doctors.manage` | Y | Y | Y | - | - | - | - | - | - | - | - | - |
| `hospitals.manage` | Y | Y | - | - | - | - | - | - | - | - | - | - |
| `billing.manage` | Y | Y | - | - | - | - | - | - | - | Y | - | - |
| `ai.manage_config` | Y | Y | - | - | - | - | - | - | - | - | - | - |
| `api.manage_keys` | Y | Y | - | - | - | - | - | - | - | - | - | - |
| `analytics.view` | Y | Y | Y | - | - | - | - | Y | - | Y | - | - |
| `analytics.export` | Y | Y | - | - | - | - | - | - | - | Y | - | - |
| `integrations.manage` | Y | Y | - | - | - | - | - | - | - | - | - | - |
| `audit.view` | Y | Y | - | - | - | - | - | - | - | - | - | - |
| `medical_twin.view` | Y | Y | Y | Y* | Y* | - | - | Y | - | - | self | grant |
| `medical_twin.edit_preferences` | Y | Y | - | - | - | - | - | Y | - | - | self | - |
| `ai.safety_override` | Y | - | - | Y* | - | - | - | - | - | - | - | - |
| `ai.view_confidence_flags` | Y | Y | Y | Y* | - | - | Y | Y | - | - | - | - |
| `consent.manage` | Y | Y | Y | - | - | Y | - | Y | - | - | self | - |

`Y*` = scoped to patients assigned to that doctor/nurse, enforced at the query layer via
`assigned_clinician_id`/care-team join, not just the permission check.

`ai.safety_override` is intentionally narrow: only Super Admin and the assigned clinician can
dismiss a Safety Agent escalation (e.g. a `needs_human_review` flag) — not Org Owner, not
Coordinator. Overriding a safety flag is a clinical judgment call, not an admin one.

`medical_twin.view` reuses the same Y*/self/grant shape as `patients.view`/`reports.view` because
the Medical Twin is a read view over those same records (see DATA_MODEL.md) — its access rule
can't be looser than the records it aggregates.

### Per-agent AI permissions

`MedLingoOrchestrator._dispatch_agents()` checks `ai.<agent_key>.run` (e.g. `ai.interpret.run`,
`ai.clinical_reasoning.run`, `ai.insurance.run`) before invoking each agent an intent routes to —
one permission per agent key in [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md#the-fourteen-agents),
checked in addition to the coarse `conversations.translate` gate that authorizes using the AI
orchestrator at all. Default grants follow the same pattern as `conversations.translate` above
(clinical roles get `ai.clinical_reasoning.run`/`ai.documentation.run`; coordinator-facing roles
get `ai.travel_concierge.run`/`ai.insurance.run`/`ai.concierge.run`. The `emergency` agent key is
explicitly exempted from this check in `_dispatch_agents()` — emergency response must never be
blockable by a missing permission grant, so there is no `ai.emergency.run` permission to forget to
assign. `ai.automation.run`/`ai.workflow.run` are invoked by the orchestrator and event
subscribers on the platform's behalf, not by an end user directly, so they default to Super
Admin/Org Owner only.

## Design rules

1. Every route declares exactly the permissions it needs — no role-name checks (`if role ==
   "doctor"`) in route/service code, only permission checks. This is what lets an org create a
   custom role like "Senior Nurse" with an extra permission without touching code.
2. Patient/Family access is row-scoped (their own record / explicitly granted record), never
   role-wide — a permission string alone isn't enough for these two roles, the query must also
   filter by ownership/grant.
3. `audit.view` and `audit.write` are separate; nothing above Super Admin gets `audit.write` —
   the audit log must stay tamper-evident even from org owners.
