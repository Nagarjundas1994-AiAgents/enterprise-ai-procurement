/** Minimal A2A (JSON-RPC) client — how our orchestrator talks to REMOTE agents.
 *
 * Protocol (a2a-protocol.org, compatible with @a2a-js/sdk which @cap-js/agents uses):
 *   GET  {base}/.well-known/agent-card.json  -> discovery card
 *   POST {rpcUrl} { jsonrpc:"2.0", id, method:"message/send",
 *                     params:{ message:{ kind:"message", role:"user",
 *                     parts:[{kind:"text",text}], messageId } } }
 *   <- { jsonrpc:"2.0", id, result:{ kind:"task", id, artifacts:[{parts:[{kind:"text",text}]}] } }
 *
 * Remote payloads are UNTRUSTED data: callers must sanitizeForLLM() them and
 * never let them bypass AuthorizationService / PolicyEngine.
 */

export interface A2AReply {
  text: string;
  taskId?: string;
  raw: unknown;
}

const uid = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;

async function postJson(url: string, body: unknown, timeoutMs: number): Promise<any> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    });
    if (!res.ok) throw Object.assign(new Error(`A2A ${res.status} from ${url}`), { code: 'A2A_TRANSPORT_ERROR', status: 502 });
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

/** Fetch + validate the remote agent's discovery card. */
export async function fetchAgentCard(baseUrl: string, timeoutMs = 8000): Promise<any> {
  const base = baseUrl.replace(/\/+$/, '');
  for (const path of ['/.well-known/agent-card.json', '/.well-known/agent.json']) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(`${base}${path}`, { signal: ctrl.signal });
      if (res.ok) return await res.json();
    } catch { /* try next alias */ } finally {
      clearTimeout(timer);
    }
  }
  throw Object.assign(new Error(`A2A agent card not found at ${base}`), { code: 'A2A_TRANSPORT_ERROR', status: 502 });
}

/** Send one user message to a remote A2A agent, return its completed text. */
export async function sendA2AMessage(rpcUrl: string, text: string, timeoutMs = 15000): Promise<A2AReply> {
  const reqId = uid();
  const envelope = {
    jsonrpc: '2.0', id: reqId, method: 'message/send',
    params: { message: { kind: 'message', role: 'user', parts: [{ kind: 'text', text }], messageId: `msg-${reqId}` } },
  };
  const data = await postJson(rpcUrl, envelope, timeoutMs);
  if (data?.error) throw Object.assign(new Error(`A2A error ${data.error.code}: ${data.error.message}`), { code: 'A2A_REMOTE_ERROR', status: 502 });
  return parseA2AResult(data?.result);
}

function collectParts(parts: any[]): string {
  return (parts || []).filter((p) => p?.kind === 'text' && typeof p.text === 'string').map((p) => p.text).join('\n');
}

/** Normalize task- or message-shaped results into plain text. */
export function parseA2AResult(result: any): A2AReply {
  if (!result) return { text: '', raw: result };
  if (result.kind === 'task') {
    const text = (result.artifacts || []).map((a: any) => collectParts(a.parts)).filter(Boolean).join('\n')
      || (result.status?.message ? collectParts(result.status.message.parts) : '');
    return { text, taskId: result.id, raw: result };
  }
  if (result.kind === 'message') return { text: collectParts(result.parts), raw: result };
  if (typeof result === 'string') return { text: result, raw: result };
  return { text: JSON.stringify(result).slice(0, 8000), raw: result };
}
