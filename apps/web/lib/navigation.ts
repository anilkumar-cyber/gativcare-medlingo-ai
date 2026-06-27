/**
 * One sidebar-item list per portal. AppShell renders from this config -- a new portal means a
 * new entry here, not a new layout component. Item visibility is filtered by permission string
 * at render time (hasPermission), never a role-name check. See docs/UX_ARCHITECTURE.md
 * #screen-hierarchy-by-portal.
 */

export type NavItem = {
  label: string;
  href: string;
  permission?: string;
};

export type PortalKey =
  | "super-admin"
  | "organization"
  | "hospital"
  | "coordinator"
  | "doctor"
  | "interpreter"
  | "finance"
  | "support"
  | "patient";

export const PORTAL_NAV: Record<PortalKey, NavItem[]> = {
  patient: [
    { label: "Dashboard", href: "/patient" },
    { label: "Appointments", href: "/patient/appointments" },
    { label: "Medical Reports", href: "/patient/reports", permission: "reports.view" },
    { label: "Documents", href: "/patient/documents" },
    { label: "Conversations", href: "/patient/conversations" },
    { label: "AI Interpreter", href: "/patient/interpreter" },
    { label: "Video Consultation", href: "/patient/video" },
    { label: "Invoices & Payments", href: "/patient/billing" },
    { label: "Medical Timeline", href: "/patient/timeline" },
    { label: "Recovery Timeline", href: "/patient/recovery" },
    { label: "Medication Reminders", href: "/patient/medications" },
    { label: "Insurance", href: "/patient/insurance" },
    { label: "Travel & Visa", href: "/patient/travel" },
    { label: "Family Access", href: "/patient/family" },
    { label: "Messages", href: "/patient/messages" },
    { label: "Settings", href: "/patient/settings" },
  ],
  doctor: [
    { label: "Today", href: "/doctor" },
    { label: "Upcoming Patients", href: "/doctor/patients" },
    { label: "Video Consultation", href: "/doctor/video" },
    { label: "SOAP Notes & Prescriptions", href: "/doctor/notes" },
    { label: "Medical Reports", href: "/doctor/reports", permission: "reports.view" },
    { label: "Conversations", href: "/doctor/conversations" },
    { label: "AI Assistant", href: "/doctor/ai" },
    { label: "Tasks", href: "/doctor/tasks" },
    { label: "Calendar", href: "/doctor/calendar" },
    { label: "Analytics", href: "/doctor/analytics", permission: "analytics.view" },
    { label: "Availability", href: "/doctor/availability" },
    { label: "Knowledge Search", href: "/doctor/knowledge" },
  ],
  hospital: [
    { label: "Overview", href: "/hospital" },
    { label: "Departments", href: "/hospital/departments" },
    { label: "Doctors", href: "/hospital/doctors", permission: "doctors.manage" },
    { label: "Patients", href: "/hospital/patients", permission: "patients.view" },
    { label: "Beds", href: "/hospital/beds" },
    { label: "Appointments", href: "/hospital/appointments" },
    { label: "International Desk", href: "/hospital/international" },
    { label: "Admissions", href: "/hospital/admissions" },
    { label: "Billing", href: "/hospital/billing", permission: "billing.manage" },
    { label: "Laboratory", href: "/hospital/lab" },
    { label: "Radiology", href: "/hospital/radiology" },
    { label: "Pharmacy", href: "/hospital/pharmacy" },
    { label: "Emergency", href: "/hospital/emergency" },
    { label: "Insurance", href: "/hospital/insurance" },
    { label: "Travel Coordination", href: "/hospital/travel" },
    { label: "Staff", href: "/hospital/staff" },
    { label: "Analytics", href: "/hospital/analytics", permission: "analytics.view" },
  ],
  organization: [
    { label: "Overview", href: "/organization" },
    { label: "Hospitals & Branches", href: "/organization/hospitals", permission: "hospitals.manage" },
    { label: "Departments", href: "/organization/departments" },
    { label: "Users & Permissions", href: "/organization/users" },
    { label: "Branding", href: "/organization/branding" },
    { label: "AI Configuration", href: "/organization/ai-config", permission: "ai.manage_config" },
    { label: "API Keys", href: "/organization/api-keys", permission: "api.manage_keys" },
    { label: "Billing & Subscriptions", href: "/organization/billing", permission: "billing.manage" },
    { label: "Analytics", href: "/organization/analytics", permission: "analytics.view" },
    { label: "Integrations", href: "/organization/integrations", permission: "integrations.manage" },
    { label: "Audit Logs", href: "/organization/audit", permission: "audit.view" },
    { label: "Settings", href: "/organization/settings" },
  ],
  coordinator: [
    { label: "New Leads", href: "/coordinator" },
    { label: "Active Patients", href: "/coordinator/patients" },
    { label: "Pending Documents", href: "/coordinator/documents" },
    { label: "Travel & Visa", href: "/coordinator/travel" },
    { label: "Hotel & Airport Pickup", href: "/coordinator/logistics" },
    { label: "Insurance", href: "/coordinator/insurance" },
    { label: "Appointments", href: "/coordinator/appointments" },
    { label: "Tasks", href: "/coordinator/tasks" },
    { label: "AI Suggestions", href: "/coordinator/ai-suggestions" },
    { label: "Workflow", href: "/coordinator/workflow" },
  ],
  interpreter: [
    { label: "Current Sessions", href: "/interpreter" },
    { label: "Upcoming Sessions", href: "/interpreter/upcoming" },
    { label: "Language Queue", href: "/interpreter/queue" },
    { label: "Conversation Logs", href: "/interpreter/logs" },
    { label: "Escalations", href: "/interpreter/escalations" },
    { label: "Medical Terminology", href: "/interpreter/terminology" },
    { label: "Performance", href: "/interpreter/performance" },
    { label: "Availability", href: "/interpreter/availability" },
  ],
  finance: [
    { label: "Invoices", href: "/finance" },
    { label: "Payments", href: "/finance/payments" },
    { label: "Refunds", href: "/finance/refunds" },
    { label: "Revenue", href: "/finance/revenue" },
    { label: "Subscriptions", href: "/finance/subscriptions" },
    { label: "Insurance Claims", href: "/finance/insurance-claims" },
    { label: "Hospital & Doctor Payments", href: "/finance/payouts" },
    { label: "Reports & Analytics", href: "/finance/reports", permission: "analytics.view" },
  ],
  support: [
    { label: "Tickets", href: "/support" },
    { label: "Chats & Calls", href: "/support/conversations" },
    { label: "Escalations", href: "/support/escalations" },
    { label: "AI Suggestions", href: "/support/ai-suggestions" },
    { label: "Knowledge Base", href: "/support/knowledge-base" },
    { label: "Reports", href: "/support/reports" },
  ],
  "super-admin": [
    { label: "Platform Overview", href: "/super-admin" },
    { label: "Organizations", href: "/super-admin/organizations" },
    { label: "Feature Flags", href: "/super-admin/feature-flags" },
    { label: "Audit Logs", href: "/super-admin/audit", permission: "audit.view" },
    { label: "Analytics", href: "/super-admin/analytics", permission: "analytics.view" },
  ],
};
