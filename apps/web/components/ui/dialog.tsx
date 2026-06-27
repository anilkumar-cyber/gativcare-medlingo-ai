"use client";

import { type ReactNode, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

// Built on native <dialog> for free focus-trap/ESC/backdrop accessibility instead of pulling in
// a modal library -- see docs/UX_ARCHITECTURE.md#component-system.
export function Dialog({
  open,
  onClose,
  className,
  children,
}: {
  open: boolean;
  onClose: () => void;
  className?: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (open && !node.open) node.showModal();
    if (!open && node.open) node.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onCancel={onClose}
      className={cn(
        "rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-bg)] p-[var(--space-6)] shadow-[var(--shadow-lg)] backdrop:bg-black/40",
        className,
      )}
    >
      {children}
    </dialog>
  );
}
