"use client";

/**
 * A2A protocol client (JSON-RPC) for the CAP agents.
 * Browser -> /backend/a2a/<agent>/ -> http://localhost:4004/a2a/<agent>/
 * (Next.js rewrite proxy; same-origin, x-mock-user forwarded for local dev.)
 *
 * Agents: catalog | procurement | suppliers | invoices | approval | agents.
 * Multi-turn: the server returns a contextId — pass it back on the next
 * message to continue the same conversation.
 */

function partsText(parts) {
  return (parts || [])
    .filter((p) => p && (p.kind === "text" || typeof p.text === "string"))
    .map((p) => p.text)
    .join("\n")
    .trim();
}

function rid(prefix) {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export async function a2aSend(agent, { text, contextId, user }) {
  // No trailing slash: Next.js 308-redirects ".../catalog/" to ".../catalog",
  // which would drop the POST on non-followed requests.
  const res = await fetch(`/backend/a2a/${agent}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-mock-user": user || "admin@example.com"
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: rid("rpc"),
      method: "message/send",
      params: {
        message: {
          messageId: rid("m"),
          role: "user",
          ...(contextId ? { contextId } : {}),
          parts: [{ kind: "text", text }]
        }
      }
    })
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    throw new Error(`A2A transport failed (${res.status})`);
  }
  if (data && data.error) {
    throw new Error(data.error.message || "A2A error");
  }
  const task = data && data.result;
  if (!task) throw new Error("Empty A2A response");

  const state = task.status && task.status.state;
  const nextContext = task.contextId || contextId || null;
  const reply =
    partsText(task.status && task.status.message && task.status.message.parts) ||
    (task.artifacts || []).map((a) => partsText(a.parts)).join("\n").trim();

  if (state === "failed") {
    throw new Error(reply || "Agent execution failed");
  }
  // completed | input-required (HITL pause) | working — surface text either way.
  return { text: reply || `(agent state: ${state || "unknown"})`, contextId: nextContext, state };
}

export const A2A_AGENTS = [
  { id: "catalog", label: "Catalog", hint: "Users, budgets, master data" },
  { id: "procurement", label: "Procurement", hint: "Requisitions & orders" },
  { id: "suppliers", label: "Suppliers", hint: "Supplier network" }
];
