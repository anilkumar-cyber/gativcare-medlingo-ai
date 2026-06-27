# Folder & Navigation Structure

```
.
├── PRD.md
├── docs/
│   ├── ARCHITECTURE.md      system/app/AI/security/deployment architecture
│   ├── MODULES.md           module boundaries & service interfaces
│   ├── RBAC.md              roles + permission matrix
│   ├── DATA_MODEL.md        ERD + table notes + tenant isolation
│   ├── WORKFLOWS.md         patient journey + AI pipeline + business workflows
│   ├── AI_ARCHITECTURE.md   orchestrator, 7 agents, memory, voice pipeline, Medical Twin
│   ├── AI_TESTING.md        AI quality testing strategy (unit/golden-set/red-team/monitoring)
│   ├── UX_ARCHITECTURE.md   design tokens, portal IA, navigation system, Journey Companion
│   └── FOLDER_STRUCTURE.md  this file
├── apps/
│   ├── web/                 Next.js — all portals, role-aware route groups
│   │   ├── app/
│   │   │   ├── (marketing)/
│   │   │   ├── (auth)/login|invite-accept|org-signup/
│   │   │   └── (dashboard)/super-admin|organization|hospital|coordinator|doctor|patient|interpreter|finance|support/
│   │   │       each with its own layout.tsx composing AppShell(portal=...)
│   │   ├── components/
│   │   │   ├── ui/            Button, Card, Badge, Dialog, Skeleton, EmptyState, MetricCard
│   │   │   ├── shell/         AppShell, CommandPalette, GlobalSearch, NotificationCenter, AIAssistantWidget, JourneyCompanion
│   │   │   └── workflow/      JourneyTimeline (21-stage patient journey stepper)
│   │   ├── lib/              api-client.ts, auth.ts, navigation.ts (per-portal nav config), utils.ts (cn)
│   │   └── hooks/             use-permissions.ts
│   └── api/                  FastAPI
│       ├── app/
│       │   ├── core/          config, security, tenancy, audit, deps, exceptions
│       │   ├── ai/
│       │   │   ├── engines/   14 engines, one file each
│       │   │   ├── agents/    14 specialized agents + orchestrator.py (MedLingoOrchestrator)
│       │   │   ├── tools/     Tool interface + registry + builtin tools (function-calling adapters)
│       │   │   ├── providers/ base.py, audio.py, ocr.py (interfaces) + claude_provider.py
│       │   │   └── voice_pipeline.py
│       │   ├── modules/       36 modules, 5-file shape each (router/service/schemas/models/permissions)
│       │   ├── core/           ... events.py (EventBus), workflow_engine.py (case-stage state machine)
│       │   └── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── packages/
│   └── shared-types/         types generated from the API's OpenAPI schema, consumed by web
└── infra/
    ├── docker/docker-compose.yml
    └── nginx/Caddyfile
```

## Navigation → dashboard mapping

Each `(dashboard)/<portal>/` route group is one row of [RBAC.md](RBAC.md)'s role list, gated by
`hooks/use-permissions.ts` reading permission strings — not a hardcoded role check. Every
dashboard (per the PRD's Dashboard Design section) ships the same widget set
(Overview, Recent Activity, Notifications, AI Insights, Tasks, Reports, Shortcuts, Widgets,
Performance Metrics) implemented once in `components/ui/` and composed per portal, not
reimplemented per portal.

## Why `packages/shared-types` exists

FastAPI emits an OpenAPI schema; types generated from it are the single source of truth for
request/response shapes on the frontend. This is what prevents the Next.js and FastAPI sides
(two different languages) from drifting out of sync as 35 modules grow.
