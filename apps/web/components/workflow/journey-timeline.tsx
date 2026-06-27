import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Mirrors app/core/workflow_engine.py::DEFAULT_STAGE_SEQUENCE on the backend -- must stay in
 * sync; once packages/shared-types is generated from the OpenAPI schema this constant moves
 * there instead of being duplicated. See docs/UX_ARCHITECTURE.md#workflow-visualization.
 */
export const DEFAULT_STAGE_SEQUENCE = [
  "inquiry",
  "qualification",
  "records_upload",
  "clinical_review",
  "second_opinion",
  "treatment_planning",
  "quotation",
  "insurance",
  "visa",
  "travel_planning",
  "airport_pickup",
  "hotel",
  "admission",
  "consultation",
  "diagnosis",
  "treatment",
  "surgery",
  "recovery",
  "discharge",
  "follow_up",
  "long_term_care",
] as const;

export type Stage = (typeof DEFAULT_STAGE_SEQUENCE)[number];

const STAGE_LABELS: Record<Stage, string> = {
  inquiry: "Inquiry",
  qualification: "Qualification",
  records_upload: "Documents",
  clinical_review: "Doctor Review",
  second_opinion: "Second Opinion",
  treatment_planning: "Treatment Planning",
  quotation: "Quotation",
  insurance: "Insurance",
  visa: "Visa",
  travel_planning: "Travel",
  airport_pickup: "Airport Pickup",
  hotel: "Hotel",
  admission: "Admission",
  consultation: "Consultation",
  diagnosis: "Diagnosis",
  treatment: "Treatment",
  surgery: "Surgery",
  recovery: "Recovery",
  discharge: "Discharge",
  follow_up: "Follow-up",
  long_term_care: "Long-term Care",
};

/**
 * Same component renders patient-facing (reassuring tone, current+next only expanded) and
 * staff-facing (full strip with stage-owner annotations) via the `variant` prop -- one data
 * source, two copy/permission variants, not two components.
 */
export function JourneyTimeline({
  currentStage,
  stages = DEFAULT_STAGE_SEQUENCE,
  variant = "patient",
}: {
  currentStage: Stage;
  stages?: readonly Stage[];
  variant?: "patient" | "staff";
}) {
  const currentIndex = stages.indexOf(currentStage);

  return (
    <ol
      className={cn(
        "flex overflow-x-auto",
        variant === "patient" ? "gap-[var(--space-4)]" : "gap-[var(--space-2)]",
      )}
      aria-label="Patient journey progress"
    >
      {stages.map((stage, index) => {
        const status = index < currentIndex ? "done" : index === currentIndex ? "current" : "upcoming";
        return (
          <li key={stage} className="flex shrink-0 flex-col items-center gap-[var(--space-1)]">
            <span
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-[var(--radius-full)] text-[var(--text-xs)] font-medium",
                status === "done" && "bg-[var(--color-success-muted)] text-[var(--color-success)]",
                status === "current" && "bg-[var(--color-accent)] text-[var(--color-accent-fg)]",
                status === "upcoming" && "bg-[var(--color-bg-subtle)] text-[var(--color-fg-muted)]",
              )}
            >
              {status === "done" ? <Check className="h-4 w-4" /> : index + 1}
            </span>
            <span
              className={cn(
                "whitespace-nowrap text-[var(--text-xs)]",
                status === "current" ? "font-semibold text-[var(--color-fg)]" : "text-[var(--color-fg-muted)]",
              )}
            >
              {STAGE_LABELS[stage]}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
