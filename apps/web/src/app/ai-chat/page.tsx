"use client";

import { useState, useEffect, useRef } from "react";
import { ArrowRight, Sparkles, ShieldCheck, Flame, Layout, Pill, Settings } from "lucide-react";
import { AGENT_ROLES, AgentRole, getAgentRole } from "@/lib/agent-roles";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  agentId: string | null;
  timestamp: Date;
}

export default function AIAgentChat() {
  const [currentAgent, setCurrentAgent] = useState<AgentRole | null>(AGENT_ROLES[0]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: `Hello! I'm ${currentAgent.name}, your ${currentAgent.title}. How can I help you today?`,
        agentId: currentAgent.id,
        timestamp: new Date(),
      }),
    ]);
  }, [currentAgent]);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      agentId: currentAgent.id,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8010/api/v1/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          agentId: currentAgent.id,
          agentRole: currentAgent.systemPrompt,
          conversationHistory: messages.slice(-10),
        }),
      });

      if (!response.ok) throw new Error("Failed to get response");

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.response || "I'm sorry, I couldn't process that.",
          agentId: currentAgent.id,
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content:
            "I'm sorry, I'm having trouble connecting. Please make sure the backend server is running on port 8010.",
          agentId: currentAgent.id,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const agentColor = currentAgent?.color || "emerald-600";

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 bg-white border-b border-gray-200">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br from-emerald-500 to-emerald-700 text-white text-xl font-bold shadow-lg">
          {currentAgent?.avatar}
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-slate-900">{currentAgent?.name}</h1>
          <p className="text-sm text-emerald-600 font-medium">{currentAgent?.title}</h1>
          <p className="text-xs text-gray-500 mt-1">{currentAgent?.description}</p>
        </div>
        <div className="ml-auto flex gap-2">
          <button
            onClick={() => setIsLoading(false)}
            className="px-3 py-1.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
          >
            Clear Chat
          </button>
          <button
            className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors"
          >
            New Chat
          </button>
        </div>
      </div>

      {/* Agent Selector */}
      <div className="px-6 py-3 bg-white border-b border-gray-200">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {AGENT_ROLES.map((role) => (
            <button
              key={role.id}
              onClick={() => {
                setCurrentAgent(role);
                setMessages([
                  {
                    id: "1",
                    role: "assistant",
                    content: `Hello! I'm ${role.name}, your ${role.title}. How can I help you today?`,
                    agentId: role.id,
                    timestamp: new Date(),
                  }),
                ]);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border border-transparent text-sm font-medium transition-all ${
                currentAgent?.id === role.id
                  ? "bg-emerald-600 text-white shadow-md"
                  : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50 hover:border-gray-300"
              }`}
            >
              <span>{role.avatar}</span>
              <span className="hidden sm:inline">{role.name}</span>
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-2 px-2">
          {currentAgent?.description}
        </p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} max-w-[85%]`}
          >
            {message.role === "assistant" && (
              <div className="flex items-start gap-2">
                <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 text-sm font-bold">
                  {currentAgent?.avatar}
                </div>
                <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm max-w-[80%]">
                  <p className="text-gray-800 leading-relaxed">{message.content}</p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="text-[10px] text-gray-400 font-medium">
                      {currentAgent?.name}
                    </span>
                    <span className="text-[10px] text-gray-400">•</span>
                    <span className="text-[10px] text-gray-400">
                      {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </div>
              </div>
            )}
            {message.role === "user" && (
              <div className="bg-emerald-600 text-white rounded-2xl p-4 shadow-md max-w-[80%]">
                <p className="text-gray-50 leading-relaxed">{message.content}</p>
                <div className="flex justify-end mt-2">
                  <span className="text-[10px] text-emerald-200 font-medium">
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start max-w-[80%]">
            <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm max-w-[80%]">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-emerald-600 animate-pulse" />
                <div className="w-3 h-3 rounded-full bg-emerald-600 animate-pulse" style={{ animationDelay: "0.2s" }} />
                <div className="w-3 h-3 rounded-full bg-emerald-600 animate-pulse" style={{ animationDelay: "0.4s" }} />
              </div>
              <p className="text-sm text-gray-500 mt-2">${currentAgent?.name} is typing...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={sendMessage} className="max-w-4xl mx-auto flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask ${currentAgent?.name} anything..."
              className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 focus:ring-2 focus:ring-emerald-500 focus:border-transparent outline-none transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:bg-gray-300 transition-all"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
