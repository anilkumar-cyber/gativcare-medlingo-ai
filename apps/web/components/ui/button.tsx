import { type ButtonHTMLAttributes, forwardRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

export const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-[var(--radius-md)] font-medium transition-colors duration-[var(--duration-fast)] disabled:opacity-50 disabled:pointer-events-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-accent)]",
  {
    variants: {
      variant: {
        primary: "bg-[var(--color-accent)] text-[var(--color-accent-fg)] hover:opacity-90",
        secondary: "bg-[var(--color-bg-subtle)] text-[var(--color-fg)] border border-[var(--color-border)] hover:bg-[var(--color-border)]",
        ghost: "text-[var(--color-fg)] hover:bg-[var(--color-bg-subtle)]",
        destructive: "bg-[var(--color-emergency)] text-white hover:opacity-90",
      },
      size: {
        sm: "h-8 px-3 text-[var(--text-sm)]",
        md: "h-10 px-4 text-[var(--text-base)]",
        lg: "h-12 px-6 text-[var(--text-lg)]",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}

// Every interactive primitive ships with a focus-visible ring by default -- accessibility is a
// token-system property, not a follow-up pass. See docs/UX_ARCHITECTURE.md#accessibility--personalization.
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  ),
);
Button.displayName = "Button";
