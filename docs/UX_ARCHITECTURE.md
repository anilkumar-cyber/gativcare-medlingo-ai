# UX Architecture — The MedLingo Experience

Design before pages, per this round's brief. This doc is the IA/design-system contract; actual
screens are built against it in Phase 4, not before it.

## Design philosophy → concrete tokens

"Premium, modern, minimal, trustworthy, AI-native" isn't achievable as a vibe — it's achievable as
constraints applied consistently. Three decisions carry the whole feel:

1. **One type scale, one spacing scale, no exceptions.** Every portal (patient, doctor, hospital,
   admin) renders from the same `app/globals.css` tokens — see [Design tokens](#design-tokens).
   A platform that feels different per portal feels like a collection of admin pages, which is
   exactly what this brief says not to build.
2. **Calm color, not clinical-white-and-blue cliché.** A restrained neutral base (near-black/
   near-white, not pure) with one primary accent (deep clinical teal) and reserved semantic colors
   (emergency red, success green, warning amber) used *only* for their semantic meaning — never
   decoratively. Reserving color is what makes an emergency banner actually read as urgent.
3. **Motion is feedback, not decoration.** Every async action (AI response streaming, translation
   in progress, file upload) gets a state — loading skeleton, streaming text, progress — never a
   blank screen. This is also a trust mechanism specific to healthcare: a silent gap while AI
   "thinks" reads as broken, not premium.

## Design tokens

Defined once in `apps/web/app/globals.css` as CSS custom properties (Tailwind v4 `@theme`), consumed
by every component — no hardcoded hex/px values anywhere else in the codebase.

| Token group | Examples | Why these values |
|---|---|---|
| Color | `--color-bg`, `--color-fg`, `--color-accent` (teal), `--color-emergency`, `--color-success`, `--color-warning`, each with a `-muted` variant | Semantic naming (not `--blue-500`) so dark mode just remaps the variable, components never branch on theme |
| Typography | `--font-sans` (UI), `--font-mono` (data/IDs), a 7-step type scale `--text-xs`...`--text-3xl` | One scale shared by marketing and dashboards — a hospital admin's table and the marketing homepage's headline come from the same ruler |
| Spacing | 4px base unit, `--space-1`...`--space-16` | 4px base divides cleanly into the icon/touch-target sizes used across web and the future mobile app |
| Radius | `--radius-sm/md/lg/full` | Consistent rounding signals "one system"; cards/dialogs/buttons share `--radius-md` |
| Shadow | `--shadow-sm/md/lg` (low-opacity, large-blur — Linear/Stripe style, not Bootstrap-style hard shadows) | Soft shadows read as premium; hard drop-shadows read as 2015 admin template |
| Motion | `--duration-fast` (120ms, hover/press), `--duration-base` (200ms, panel/dialog), `--duration-slow` (320ms, page-level) | Fast feedback for direct manipulation, slower for spatial transitions — mismatched durations are why most admin UIs feel laggy even when they're not |

Dark mode: same variable names, remapped values under `[data-theme="dark"]` — components never
have `dark:` conditional logic, the token does the work. This is also what makes hospital/org
branding (logo, accent color override) a token override, not a component fork.

## Component system

`apps/web/components/ui/` — primitives every portal composes, built on the tokens above:

| Component | Notes |
|---|---|
| `Button` | variants: primary / secondary / ghost / destructive; sizes sm/md/lg; CVA-driven, not prop-soup conditionals |
| `Card` | base surface for every dashboard widget, patient/doctor/hospital/workflow cards all compose it |
| `Badge` | status pills (stage, urgency, confidence level) — color comes from semantic tokens only |
| `Dialog` | built on native `<dialog>` for built-in focus-trap/ESC/backdrop a11y instead of a heavy modal library |
| `Skeleton` | loading placeholder shape-matched to the content it's replacing, never a generic spinner for content areas |
| `EmptyState` | every list/table has one — "no appointments yet" is a designed state, not a blank table |
| `MetricCard` | analytics number + trend, the building block of every dashboard's top row |
| `Table`, `Timeline`, `Calendar`, `Chart` (wraps a charting lib) | data-display primitives, specced but not all built in this pass — see Extensibility |

Domain-specific cards (`PatientCard`, `DoctorCard`, `HospitalCard`, `WorkflowCard`) compose the
primitives above rather than introducing their own styling — this is the rule that keeps "everyone
follows one design system" true past the first 50 screens.

## Portal architecture

One Next.js app, role-aware route groups (decided in Phase 1, holds here) — not 12 separate apps.
Marketing is public; everything else sits behind `(dashboard)/<portal>/`, gated by
`hooks/use-permissions.ts` against [RBAC.md](RBAC.md) permission strings, never a role-name check.

```
apps/web/app/
  (marketing)/          public site — see Marketing site IA below
  (auth)/                login, MFA, invite-accept, org-signup
  (dashboard)/
    super-admin/         platform-wide
    organization/        org owner
    hospital/             hospital admin
    coordinator/          patient/international-patient coordinator
    doctor/                doctor/surgeon/consultant
    interpreter/          medical interpreter
    finance/              finance executive
    support/               support executive
    patient/               patient (+ family, via grant)
```

Mobile app and Tablet mode are **not separate codebases**: mobile is a future React Native app
sharing `packages/shared-types` and the same API; tablet mode is a responsive layout variant of
existing portals (reception desk = Hospital Portal's appointment view at a wider touch-target
scale; OR/ER stations = Interpreter Console in a kiosk layout). Building four more codebases for
the same data would violate the one-design-system rule before a single screen ships. Public
API Portal / Developer Portal are documentation+key-management surfaces over the already-versioned
`/api/v1` — see [AI_ARCHITECTURE.md §API versioning](AI_ARCHITECTURE.md#api-versioning).

## Screen hierarchy by portal

Every dashboard portal shares one shell (`components/shell/app-shell.tsx`): sidebar nav +
top bar (global search, notifications, AI assistant trigger, profile) + breadcrumbs + content
area. What differs is the sidebar's item list and the dashboard's widget composition:

**Patient Portal** — Dashboard (Journey Companion front and center, see below) · Appointments ·
Medical Reports · Documents · Conversation History · AI Interpreter · Video Consultation ·
Invoices/Payments · Medical Timeline · Recovery Timeline · Medication Reminders · Insurance ·
Travel/Visa/Hotel/Airport Pickup · Family Access · Messages · Settings (incl. Language/Voice/
Accessibility) · persistent Emergency Button (always visible, not nested in a menu).

**Doctor Portal** — Today's Appointments · Upcoming Patients · Video Consultation · SOAP
Notes/Prescriptions · Medical Reports · Patient Timeline · Conversation History · AI Assistant ·
Tasks · Calendar · Analytics · Availability · Knowledge Search/Clinical References.

**Hospital Portal** — Departments · Doctors · Patients · Beds · Appointments · International
Desk · Admissions · Billing · Laboratory · Radiology · Pharmacy · Emergency · Insurance · Travel
Coordination · Staff · Analytics/Performance.

**Organization Portal** — Hospitals/Branches/Departments · Users/Permissions · Branding · AI
Configuration · API Keys · Billing/Subscriptions/Usage · Analytics · Integrations · Audit Logs ·
Compliance.

**Coordinator Portal** — New Leads · Active Patients · Pending Documents · Travel/Visa/Hotel/
Airport Pickup · Insurance · Appointments · Tasks · AI Suggestions · Workflow view (the journey
timeline, staff-facing).

**Interpreter Console** — Current/Upcoming Sessions · Language Queue · Video/Phone Calls ·
Conversation Logs · Escalations (HITL inbox — see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md#human-in-the-loop-hitl)) ·
Medical Terminology reference · Performance · Availability.

**Finance Portal** — Invoices · Payments · Refunds · Revenue · Subscriptions · Insurance Claims ·
Hospital/Doctor Payments · Reports/Analytics.

**Support Portal** — Tickets · Chats/Calls · Patient/Hospital/Org Support · Escalations · AI
Suggestions · Knowledge Base.

**Admin Console** (Super Admin) — cross-org views of all of the above, plus platform feature
flags and tenant provisioning.

## Marketing site IA

Home · About · Hospitals · Doctors · Treatments · Medical Tourism · Countries · Success Stories ·
AI Platform · Pricing · Contact · Blog · FAQ · Partners · Careers · Investor Relations · Media ·
Privacy · Terms. Integrates with the platform via the same `lib/api-client.ts` (e.g. a "Start your
inquiry" form on the marketing site calls the same `medical_tourism.qualify_lead()` endpoint the
Coordinator Portal's "New Leads" list reads from) — marketing is a front door to the real
pipeline, not a disconnected brochure site.

## Navigation system (every portal)

`components/shell/`:

- `app-shell.tsx` — sidebar + top bar + breadcrumbs, the one layout every `(dashboard)/<portal>`
  composes (see code).
- `command-palette.tsx` — ⌘K, fuzzy-jumps to any nav item or recent record, built on native
  `<dialog>`.
- `global-search.tsx` — searches across patients, doctors, hospitals, treatments, reports,
  appointments, messages, invoices, documents, organizations, conversations, knowledge, settings;
  same search-as-you-type component, scope determined by the user's permissions (a receptionist's
  search never returns a record `patients.view` wouldn't already let them open).
- `notification-center.tsx` — appointments, messages, emergency alerts, travel/visa/insurance/
  payment updates, AI suggestions, system updates, approval requests, tasks — one feed, filterable
  by type, backed by the event catalog in [WORKFLOWS.md](WORKFLOWS.md#event-catalog) (a
  notification is a rendered `Event`, not a separate data model).
- `ai-assistant-widget.tsx` — present on every page, context-aware: it's handed the current
  page/user/patient/appointment/org as orchestrator context (`OrchestratorRequest.extra`) so "what
  does this lab value mean" asked from a patient's report page is already scoped to that report —
  no separate chat window disconnected from what's on screen.

## Workflow visualization

`components/workflow/journey-timeline.tsx` — interactive horizontal stepper rendering the 21-stage
journey from [WORKFLOWS.md](WORKFLOWS.md#patient-journey), current stage highlighted, future
stages dimmed, past stages checked. Same component renders in the Patient Portal (patient-facing
copy, reassuring tone) and the Coordinator Portal (staff-facing, with stage-owner and blocking-task
annotations) — one data source (`WorkflowEngine`/`medical_case.stage`), two copy/permission
variants, not two components.

## The Journey Companion (Healthcare OS, not a dashboard)

This is the concrete UI answer to "the patient never feels lost." `components/shell/
journey-companion.tsx` is a persistent panel in the Patient Portal — not a feature buried in a
menu — that always shows: current stage (via `journey-timeline.tsx`), the single next action
(book this, upload that, confirm this slot), and an always-available AI assistant pre-scoped to
"help me with my current stage." Behind it: the **same agents already built**, nothing new on the
backend —

- stage/next-action comes from the **Workflow Agent**
- "what do I need to do for my visa" comes from the **Travel Concierge** / **Insurance** agents
- "explain this report" comes from **Clinical Intelligence** + **Medical Interpreter**
- if the patient's question gets complex, **HITL** quietly brings in a human coordinator

The UX work here is making one panel feel like a companion instead of exposing 14 agents as 14
buttons — composition at the UI layer mirrors the merge-then-present model already used at the
orchestration layer.

## Key user flows

**Patient: report upload → understanding.** Upload (drag-drop, `FileManager`) → processing state
(skeleton + "AI is reading your report" — never a silent spinner) → structured result: extracted
findings, patient-friendly explanation, suggested questions for their doctor, disclaimer — same
shape as `medical_documents.service.DocumentAnalysis`, rendered, not re-derived in the frontend.

**Doctor: consultation with live interpretation.** Doctor opens today's appointment → starts
video/voice session → live captions in doctor's language regardless of patient's spoken language
→ session ends → AI-drafted SOAP note appears in a clearly-marked "draft, needs your sign-off"
state (never auto-saved as final) → doctor edits/signs → note locks.

**Coordinator: new lead to first consultation.** Lead appears in pipeline (Kanban-style, CRM
section) → AI-suggested hospital/doctor match shown inline with confidence → coordinator
confirms or overrides → documents-needed checklist auto-populates from case stage → once complete,
"Schedule consultation" surfaces available slots (doctor availability + interpreter availability
intersected) in one action, not three separate lookups.

## Accessibility & personalization

Accessibility is a token-system property, not a separate "accessible mode": font scaling and high
contrast are theme variants of the same CSS variables; keyboard navigation and screen-reader labels
are required on every primitive in `components/ui/` before it ships (a `Button` without an
accessible label is a bug, not a follow-up ticket). Voice navigation reuses the Voice Intelligence
agent's STT path already built for conversations.

Personalization (language, voice, theme, dashboard/widget layout, saved searches, favorites,
pinned items) is stored per-user in a `user_preferences` row (Phase 3), read once at shell mount —
no portal re-implements its own preferences storage.

## Settings architecture

One settings shell, sectioned (General/Profile, Organization, Hospital, Notifications, AI
Preferences, Voice/Translation Preferences, Security, Privacy, Devices, API, Billing,
Integrations, Audit), with section visibility driven by RBAC permissions — a doctor never sees
"API Keys," a patient never sees "Audit Logs," without a single `if (role === ...)` branch
anywhere in the settings UI.

## Extensibility

New portal = new route group under `(dashboard)/` + sidebar item list + permission strings, reusing
the existing `AppShell`. New primitive = new file in `components/ui/`, token-driven by
construction. New dashboard widget = composes `Card`/`MetricCard`, never introduces ad-hoc
styling. This pass builds the shell, the token system, and a first primitive set
(`Button`, `Card`, `Badge`, `Dialog`, `Skeleton`, `EmptyState`, `MetricCard`) plus the navigation
system and Journey Companion — full per-portal page implementations are the next pass, deliberately,
per this round's "design before implementing pages" instruction.
