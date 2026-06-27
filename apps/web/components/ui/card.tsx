import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

// Base surface for every dashboard widget. PatientCard/DoctorCard/HospitalCard/WorkflowCard
// compose this rather than styling themselves -- see docs/UX_ARCHITECTURE.md#component-system.
export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-bg)] shadow-[var(--shadow-sm)] p-[var(--space-6)]",
        className,
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-[var(--space-4)] flex items-center justify-between", className)} {...props} />;
}

export function CardTitle({ className, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-[var(--text-lg)] font-semibold text-[var(--color-fg)]", className)} {...props} />;
}

export function CardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("text-[var(--text-base)] text-[var(--color-fg-muted)]", className)} {...props} />;
}
