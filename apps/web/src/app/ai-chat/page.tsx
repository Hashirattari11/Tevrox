"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { ArrowRight, ShieldAlert, Sparkles } from "lucide-react";
import { AGENT_ROLES, type AgentRole } from "@/lib/agent-roles";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

// Tevrox does not ship an AI backend yet. This page is a persona preview:
// responses are deterministic, offline, and clearly labelled as simulated.
function simulateReply(agent: AgentRole, userText: string): string {
  const question = userText.trim().replace(/\s+/g, " ").slice(0, 240);
  return (
    `Simulated response (AI provider not configured)\n\n` +
    `As ${agent.name}, ${agent.title}, I hear: “${question}”\n\n` +
    `Here’s how I’d think about it in Tevrox today:\n` +
    `• Check the verified catalogue before trusting any product — unverified records are labelled as such.\n` +
    `• Unknown ingredients go to the admin review queue; they are never silently accepted as safe.\n` +
    `• For anything affecting your skin or health, consult a qualified professional — Tevrox gives information, not medical advice.\n\n` +
    `Once an AI provider is selected and configured, this chat will answer with real reasoning grounded in your catalogue and review history.`
  );
}

export default function AIAgentChat() {
  const [currentAgent, setCurrentAgent] = useState<AgentRole>(AGENT_ROLES[0]);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "greeting",
      role: "assistant",
      content: `Hello! I'm ${AGENT_ROLES[0].name}, your ${AGENT_ROLES[0].title}. Ask me anything — responses are simulated until an AI provider is configured.`,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const text = input.trim();
    if (!text || isLoading) return;

    setMessages((prev) => [
      ...prev,
      { id: `${Date.now()}-user`, role: "user", content: text, timestamp: new Date() },
    ]);
    setInput("");
    setIsLoading(true);

    window.setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: `${Date.now()}-assistant`,
          role: "assistant",
          content: simulateReply(currentAgent, text),
          timestamp: new Date(),
        },
      ]);
      setIsLoading(false);
    }, 600);
  };

  return (
    <div className="flex h-screen flex-col bg-slate-50">
      {/* Header */}
      <header className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 sm:px-6">
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-600 to-emerald-800 text-xl text-white shadow-sm" aria-hidden>
          {currentAgent.avatar}
        </span>
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-lg font-bold text-slate-900">{currentAgent.name}</h1>
          <p className="truncate text-xs font-medium text-emerald-700">{currentAgent.title}</p>
        </div>
        <span className="hidden items-center gap-2 rounded-full bg-amber-50 px-3 py-1.5 text-[11px] font-semibold text-amber-900 ring-1 ring-amber-200 sm:inline-flex">
          <ShieldAlert size={12} aria-hidden />
          Offline simulation
        </span>
      </header>

      {/* Agent selector */}
      <div className="border-b border-slate-200 bg-white px-4 py-2 sm:px-6">
        <div className="flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Choose a Tevrox agent">
          {AGENT_ROLES.map((role) => {
            const selected = currentAgent.id === role.id;
            return (
              <button
                key={role.id}
                role="tab"
                aria-selected={selected}
                onClick={() => setCurrentAgent(role)}
                className={
                  selected
                    ? "flex items-center gap-2 whitespace-nowrap rounded-lg bg-emerald-700 px-3 py-2 text-sm font-semibold text-white shadow-sm"
                    : "flex items-center gap-2 whitespace-nowrap rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 hover:border-emerald-300 hover:text-emerald-800"
                }
              >
                <span aria-hidden>{role.avatar}</span>
                <span className="hidden sm:inline">{role.name}</span>
              </button>
            );
          })}
        </div>
        <p className="hidden px-1 pt-1 text-[11px] text-slate-500 md:block">{currentAgent.description}</p>
      </div>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-4 py-4 sm:px-6">
        <div className="mx-auto max-w-3xl space-y-4">
          {messages.map((message) => {
            const fromUser = message.role === "user";
            return (
              <div key={message.id} className={fromUser ? "flex justify-end" : "flex justify-start"}>
                <div
                  className={
                    fromUser
                      ? "max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-emerald-700 px-4 py-2.5 text-sm leading-6 text-white shadow-sm sm:max-w-[75%]"
                      : "max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-bl-md border border-slate-200 bg-white px-4 py-2.5 text-sm leading-6 text-slate-800 shadow-sm sm:max-w-[75%]"
                  }
                >
                  {message.content}
                  <div
                    className={
                      fromUser
                        ? "mt-1.5 text-right text-[10px] text-emerald-200"
                        : "mt-1.5 text-[10px] text-slate-400"
                    }
                  >
                    {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </div>
                </div>
              </div>
            );
          })}
          {isLoading && (
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-600" />
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-600" style={{ animationDelay: "150ms" }} />
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-600" style={{ animationDelay: "300ms" }} />
              <span className="ml-1 inline-flex items-center gap-1">
                <Sparkles size={12} aria-hidden />
                {currentAgent.name.split(" ")[0]} is composing…
              </span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <form onSubmit={sendMessage} className="border-t border-slate-200 bg-white p-3 sm:p-4">
        <div className="mx-auto flex max-w-3xl items-center gap-2">
          <label className="relative flex-1">
            <span className="sr-only">Message {currentAgent.name}</span>
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={`Ask ${currentAgent.name.split(" ")[0]} something…`}
              className="h-12 w-full rounded-xl border border-slate-300 bg-slate-50 px-4 text-sm focus:border-emerald-700 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-700/20"
            />
          </label>
          <button
            type="submit"
            disabled={isLoading || input.trim().length === 0}
            className="inline-flex h-12 items-center gap-2 rounded-xl bg-emerald-700 px-4 font-semibold text-white shadow-sm transition-colors hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Send
            <ArrowRight size={16} aria-hidden />
          </button>
        </div>
        <p className="mx-auto mt-2 max-w-3xl text-center text-[11px] text-slate-400">
          AI analysis and medical advice are not part of Tevrox yet; always check the label and consult a professional.
        </p>
      </form>
    </div>
  );
}
