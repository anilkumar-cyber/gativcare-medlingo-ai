import { type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

// Shape-matched to the content it replaces -- pass width/height via className per use site.
// Never a generic spinner for content areas. See docs/UX_ARCHITECTURE.md design philosophy #3.
export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]",
        className,
      )}
      {...props}
    />
  );
}
