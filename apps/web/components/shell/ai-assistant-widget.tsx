"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import { Dialog } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api, ApiError } from "@/lib/api-client";

/**
 * Present on every page. Handed the current page/user/patient/appointment/org as orchestrator
 * context (OrchestratorRequest.extra) so a question asked from a patient's report page is already
 * scoped to that report -- no disconnected chat window. See docs/UX_ARCHITECTURE.md
 * #navigation-system-every-portal. Wired to MedLingoOrchestrator via
 * POST /api/v1/conversations/{session}/messages -- real pipeline (intent/language/speaker/
 * emotion/safety/memory all run), the only piece that can fail is the final LLM call if
 * ANTHROPIC_API_KEY isn't a real key, surfaced here as an inline error, not a silent no-op.
 */
export type AssistantContext = {
  patientId?: string;
  medicalCaseId?: string;
  pageLabel: string;
};

type ChatMessage = { role: "user" | "assistant" | "error"; content: string; flags?: string[]; emergency?: boolean };

export function AIAssistantWidget({ context }: { context: AssistantContext }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  async function send() {
    const text = input.trim();
    if (!text || sending) return;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    try {
      let sid = sessionId;
      if (!sid) {
        const session = await api.startSession({ medical_case_id: context.medicalCaseId });
        sid = session.id;
        setSessionId(sid);
      }
      const response = await api.sendMessage(sid, {
        text,
        patient_id: context.patientId,
        medical_case_id: context.medicalCaseId,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: response.content, flags: response.flags, emergency: response.emergency }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", content: err instanceof ApiError ? err.message : "Something went wrong" }]);
    } finally {
      setSending(false);
    }
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
                  : m.role === "error"
                    ? "self-start rounded-[var(--radius-md)] bg-[var(--color-emergency-muted)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-emergency)]"
                    : "self-start rounded-[var(--radius-md)] bg-[var(--color-bg-subtle)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)]"
              }
            >
              {m.emergency && <Badge variant="emergency" className="mb-[var(--space-1)]">emergency</Badge>}
              <div>{m.content}</div>
            </li>
          ))}
          {sending && <li className="self-start text-[var(--text-xs)] text-[var(--color-fg-muted)]">AI is thinking...</li>}
        </ul>
        <div className="flex gap-[var(--space-2)]">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask anything about this page..."
            className="flex-1 rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] outline-none focus-visible:border-[var(--color-accent)]"
          />
          <Button size="sm" onClick={send} disabled={sending}>
            Send
          </Button>
        </div>
      </Dialog>
    </>
  );
}
