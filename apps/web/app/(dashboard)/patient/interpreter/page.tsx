"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api, ApiError } from "@/lib/api-client";

type ChatMessage = { role: "user" | "assistant" | "error"; content: string; intent?: string; emergency?: boolean; confidence?: number };

// Real-time AI Interpreter -- talks to MedLingoOrchestrator via
// POST /api/v1/conversations/{session}/messages. See docs/AI_ARCHITECTURE.md.
export default function PatientInterpreterPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [targetLang, setTargetLang] = useState("");
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
        const session = await api.startSession({ mode: "text" });
        sid = session.id;
        setSessionId(sid);
      }
      const response = await api.sendMessage(sid, { text, target_lang: targetLang || undefined });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.content, intent: response.intent, emergency: response.emergency, confidence: response.confidence },
      ]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", content: err instanceof ApiError ? err.message : "Something went wrong" }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Interpreter</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-[var(--space-4)]">
        <div className="flex items-center gap-[var(--space-2)]">
          <label className="text-[var(--text-sm)] text-[var(--color-fg-muted)]">Reply in:</label>
          <input
            placeholder="e.g. es, hi, fr (leave blank for same language)"
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] outline-none focus-visible:border-[var(--color-accent)]"
          />
        </div>

        <ul className="flex min-h-[200px] max-h-[420px] flex-col gap-[var(--space-2)] overflow-auto rounded-[var(--radius-md)] bg-[var(--color-bg-subtle)] p-[var(--space-4)]">
          {messages.length === 0 && (
            <li className="text-[var(--text-sm)] text-[var(--color-fg-muted)]">
              Ask anything -- symptoms, appointments, travel, insurance. Real pipeline runs end to end; the final response needs a configured Anthropic API key.
            </li>
          )}
          {messages.map((m, i) => (
            <li
              key={i}
              className={
                m.role === "user"
                  ? "self-end max-w-[80%] rounded-[var(--radius-md)] bg-[var(--color-accent)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-accent-fg)]"
                  : m.role === "error"
                    ? "self-start max-w-[80%] rounded-[var(--radius-md)] bg-[var(--color-emergency-muted)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] text-[var(--color-emergency)]"
                    : "self-start max-w-[80%] rounded-[var(--radius-md)] bg-[var(--color-bg)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] shadow-[var(--shadow-sm)]"
              }
            >
              {m.intent && (
                <div className="mb-[var(--space-1)] flex gap-[var(--space-1)]">
                  <Badge variant={m.emergency ? "emergency" : "neutral"}>{m.intent}</Badge>
                  {typeof m.confidence === "number" && <Badge variant="accent">confidence {m.confidence.toFixed(2)}</Badge>}
                </div>
              )}
              <div>{m.content}</div>
            </li>
          ))}
          {sending && <li className="text-[var(--text-xs)] text-[var(--color-fg-muted)]">AI is thinking...</li>}
        </ul>

        <div className="flex gap-[var(--space-2)]">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Type a message..."
            className="flex-1 rounded-[var(--radius-md)] border border-[var(--color-border)] px-[var(--space-3)] py-[var(--space-2)] text-[var(--text-sm)] outline-none focus-visible:border-[var(--color-accent)]"
          />
          <Button onClick={send} disabled={sending}>Send</Button>
        </div>
      </CardContent>
    </Card>
  );
}
