"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import { Dialog } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

/**
 * Present on every page. Handed the current page/user/patient/appointment/org as orchestrator
 * context (OrchestratorRequest.extra) so a question asked from a patient's report page is already
 * scoped to that report -- no disconnected chat window. See docs/UX_ARCHITECTURE.md
 * #navigation-system-every-portal. Phase 3: wires to POST /api/v1/conversations against
 * MedLingoOrchestrator.handle_request().
 */
export type AssistantContext = {
  patientId?: string;
  medicalCaseId?: string;
  conversationSessionId?: string;
  pageLabel: string;
};

export function AIAssistantWidget({ context }: { context: AssistantContext }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [input, setInput] = useState("");

  async function send() {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    setInput("");
    // Phase 3: POST to the orchestrator with `context` attached as OrchestratorRequest.extra.
  }

  return (
    <>
      <button
        aria-label={`Ask AI about ${context.pageLabel}`}
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 flex items-center gap-2 rounded-[var(--radius-full)] bg-[var(--color-accent)] px-[var(--space-4)] py-[var(--space-3)] text-[var(--color-accent-fg)] shadow-[var(--shadow-md)]"
      >
        <Sparkles className="h-4 w-4" />
        <span className="text-[var(--text-sm)] font-medium">Ask AI</span>
      </button>
      <Dialog open={open} onClose={() => setOpen(false)} className="w-full max-w-md">
        <h2 className="mb-[var(--space-2)] text-[var(--text-lg)] font-semibold">AI Assistant</h2>
        <p className="mb-[var(--space-4)] text-[var(--text-xs)] text-[var(--color-fg-muted)]">
          Scoped to: {context.pageLabel}
        </p>
        <ul className="mb-[var(--space-4)] flex max-h-64 flex-col gap-[var(--space-2)] overflow-auto">
          {messages.map((m, i) => (
            <li
              key={i}
              className={
                m.role === "user"
                  ? "self-end rounded-[var(--radius-md)] bg-[var(--color-accent-muted)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)]"
                  : "self-start rounded-[var(--radius-md)] bg-[var(--color-bg-subtle)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)]"
              }
            >
              {m.content}
            </li>
          ))}
        </ul>
        <div className="flex gap-[var(--space-2)]">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask anything about this page..."
            className="flex-1 rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] outline-none focus-visible:border-[var(--color-accent)]"
          />
          <Button size="sm" onClick={send}>
            Send
          </Button>
        </div>
      </Dialog>
    </>
  );
}
