"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { answer, QUICK_QUESTIONS, WELCOME } from "@/lib/assistant";

interface Message {
  role: "user" | "assistant";
  text: string;
}

const INITIAL: Message[] = [{ role: "assistant", text: WELCOME }];

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>(INITIAL);
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length > 1) endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const ask = (prompt: string) => {
    const q = prompt.trim();
    if (!q) return;
    setMessages((m) => [...m, { role: "user", text: q }, { role: "assistant", text: answer(q) }]);
    setInput("");
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    ask(input);
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-3" aria-live="polite">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-3xl rounded-xl border px-4 py-3 text-sm leading-relaxed ${
              m.role === "user"
                ? "self-end border-[#1e4a80] bg-[#112747] text-white"
                : "self-start border-line bg-panel text-ink-soft"
            }`}
          >
            {m.role === "assistant" ? (
              <div className="md">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    a: ({ href, children }) => (
                      <Link href={href ?? "#"} className="font-semibold text-accent underline">{children}</Link>
                    ),
                  }}
                >
                  {m.text}
                </ReactMarkdown>
              </div>
            ) : (
              m.text
            )}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <div>
        <div className="mb-2 text-[11px] font-bold uppercase tracking-wider text-muted">Önerilen sorular</div>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {QUICK_QUESTIONS.map((q) => (
            <button
              key={q.label}
              type="button"
              onClick={() => ask(q.prompt)}
              className="rounded-lg border border-[#1e4a80] bg-[#0d2446] px-3 py-2 text-left text-xs font-semibold text-ink transition-colors hover:border-accent hover:text-accent"
            >
              {q.label}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={onSubmit} className="flex gap-2">
        <label htmlFor="chat-input" className="sr-only">Sorunuz</label>
        <input
          id="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Bir il veya konu yazın (ör. Bursa, en temiz bölge, OSB ilişkisi)…"
          className="min-w-0 flex-1 rounded-lg border border-[#1e4a80] bg-[#0b1a30] px-3 py-2 text-sm text-white placeholder:text-muted"
        />
        <button type="submit" className="rounded-lg bg-accent px-4 py-2 text-sm font-bold text-[#031322] hover:brightness-110">
          Sor
        </button>
        <button
          type="button"
          onClick={() => setMessages(INITIAL)}
          className="rounded-lg border border-line px-3 py-2 text-sm text-muted hover:text-white"
        >
          Temizle
        </button>
      </form>
    </div>
  );
}
