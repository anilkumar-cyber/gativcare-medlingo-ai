import { type HTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// Color comes from semantic tokens only -- never decorative. "emergency" must always mean
// emergency, everywhere it appears. See docs/UX_ARCHITECTURE.md#design-tokens.
const badgeVariants = cva(
  "inline-flex items-center rounded-[var(--radius-full)] px-[var(--space-3)] py-[var(--space-1)] text-[var(--text-xs)] font-medium",
  {
    variants: {
      variant: {
        neutral: "bg-[var(--color-bg-subtle)] text-[var(--color-fg-muted)]",
        accent: "bg-[var(--color-accent-muted)] text-[var(--color-accent)]",
        success: "bg-[var(--color-success-muted)] text-[var(--color-success)]",
        warning: "bg-[var(--color-warning-muted)] text-[var(--color-warning)]",
        emergency: "bg-[var(--color-emergency-muted)] text-[var(--color-emergency)]",
      },
    },
    defaultVariants: { variant: "neutral" },
  },
);

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
