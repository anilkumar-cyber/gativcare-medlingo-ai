import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { JourneyTimeline, type Stage } from "@/components/workflow/journey-timeline";

/**
 * The concrete UI answer to "the patient never feels lost" -- a persistent panel, not a feature
 * buried in a menu. Nothing new on the backend: stage/next-action comes from the Workflow Agent,
 * travel/visa guidance from Travel Concierge/Insurance agents, report explanations from Clinical
 * Intelligence + Medical Interpreter, complex questions quietly get HITL. See
 * docs/UX_ARCHITECTURE.md#the-journey-companion-healthcare-os-not-a-dashboard.
 */
export function JourneyCompanion({
  currentStage,
  nextAction,
}: {
  currentStage: Stage;
  nextAction: { label: string; href: string } | null;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Your journey</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-[var(--space-4)]">
        <JourneyTimeline currentStage={currentStage} variant="patient" />
        {nextAction && (
          <div className="flex items-center justify-between rounded-[var(--radius-md)] bg-[var(--color-accent-muted)] p-[var(--space-4)]">
            <span className="text-[var(--text-sm)] text-[var(--color-fg)]">{nextAction.label}</span>
            <a href={nextAction.href} className={buttonVariants({ size: "sm" })}>
              Continue
            </a>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
