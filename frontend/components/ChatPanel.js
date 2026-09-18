"use client";

import { useEffect, useRef, useState } from "react";
import { chat } from "../lib/backend";
import { a2aSend, A2A_AGENTS } from "../lib/a2a";
import MermaidDiagram from "./MermaidDiagram";

const SUGGESTIONS = [
  "How many open requisitions are there?",
  "Which suppliers have the best on-time rate?",
  "Summarize the budget situation for IT"
];

function inlineRich(text, keyPrefix) {
  // Escape, then **bold** and `code` — never raw HTML from the model.
  const parts = String(text).split(/(\*\*.+?\*\*|`.+?`)/g);
  return parts.map((p, i) => {
    const k = `${keyPrefix}-${i}`;
    if (p.startsWith("**") && p.endsWith("**") && p.length > 4) return <strong key={k}>{p.slice(2, -2)}</strong>;
    if (p.startsWith("`") && p.endsWith("`") && p.length > 2) return <code key={k}>{p.slice(1, -1)}</code>;
    return <span key={k}>{p}</span>;
  });
}

function isTableSep(line) {
  return /^\|?[\s:|-]+\|?[\s:|.-]*$/.test(line.trim()) && line.includes("|") && /-|:/.test(line);
}

function renderRich(text) {
  const lines = String(text).split("\n");
  const blocks = [];
  let i = 0, key = 0;
  while (i < lines.length) {
    const line = lines[i];
    // Markdown table: consecutive | lines (skip the |---| separator row)
    if (line.trim().startsWith("|") && line.includes("|")) {
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        if (!isTableSep(lines[i])) {
          rows.push(lines[i].trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
        }
        i++;
      }
      if (rows.length) {
        const [head, ...rest] = rows;
        blocks.push(
          <div key={key++} className="md-table-wrap">
            <table className="md-table">
              <thead><tr>{head.map((c, j) => <th key={j}>{inlineRich(c, `h${key}-${j}`)}</th>)}</tr></thead>
              <tbody>{rest.map((r, ri) => <tr key={ri}>{r.map((c, j) => <td key={j}>{inlineRich(c, `r${ri}-${j}`)}</td>)}</tr>)}</tbody>
            </table>
          </div>
        );
        continue;
      }
    }
    // Blockquote "> ..."
    if (/^\s*>\s?/.test(line)) {
      blocks.push(<div key={key++} className="md-quote">{inlineRich(line.replace(/^\s*>\s?/, ""), `q${key}`)}</div>);
      i++;
      continue;
    }
    // Fenced code — ```mermaid renders as a live diagram, everything else as plain pre
    if (/^\s*```/.test(line)) {
      const lang = (line.match(/^\s*```(\w*)/) || [])[1] || "";
      const buf = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++;
      const src = buf.join("\n");
      if (lang.toLowerCase() === "mermaid" && src.trim()) {
        blocks.push(<MermaidDiagram key={key++} code={src} />);
      } else {
        blocks.push(<pre key={key++} className="md-pre">{src}</pre>);
      }
      continue;
    }
    blocks.push(<div key={key++} className="md-line">{inlineRich(line || " ", `l${key}`)}</div>);
    i++;
  }
  return blocks;
}

export default function ChatPanel({ user, externalAsk, onConsumedAsk, full = false }) {
  // NOTE: greeting timestamp starts empty and is stamped on mount (see below).
  // Rendering `new Date().toLocaleTimeString()` here would break hydration:
  // the server and the client render at different seconds/locales.
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I am your procurement assistant, powered by **DeepSeek**. Ask about requisitions, budgets or suppliers — or use **Ask AI** on any requisition row.",
      time: ""
    }
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [agent, setAgent] = useState("catalog");
  const feedRef = useRef(null);
  // A2A conversation continuity: one contextId per agent.
  const ctxRef = useRef({});
  const convRef = useRef(`ui-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`);

  // Client-only: stamp the greeting time after hydration (SSR renders "").
  useEffect(() => {
    setMessages((prev) =>
      prev.length === 1 && prev[0].role === "assistant" && !prev[0].time
        ? [{ ...prev[0], time: new Date().toLocaleTimeString() }]
        : prev
    );
  }, []);

  useEffect(() => {
    const el = feedRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);

  // "Ask AI" row action from the worklist posts a question here.
  useEffect(() => {
    if (externalAsk) {
      send(externalAsk);
      onConsumedAsk && onConsumedAsk();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [externalAsk]);

  async function send(text) {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    setInput("");
    setBusy(true);
    const withUser = [...messages, { role: "user", text: q, time: new Date().toLocaleTimeString() }];
    setMessages(withUser);
    try {
      // Primary path: A2A protocol to the selected agent (tool-grounded, DeepSeek).
      const r = await a2aSend(agent, { text: q, contextId: ctxRef.current[agent] || null, user });
      if (r.contextId) ctxRef.current[agent] = r.contextId;
      if (r.state === "input-required" && r.taskId) {
        // HITL pause: same card as the SAP agent preview — Approve/Reject resumes the task.
        setMessages([
          ...withUser,
          { role: "approval", text: r.text, taskId: r.taskId, decided: null, time: new Date().toLocaleTimeString() }
        ]);
      } else {
        setMessages([
          ...withUser,
          { role: "assistant", text: r.text, time: new Date().toLocaleTimeString() }
        ]);
      }
    } catch (a2aErr) {
      // Transparent fallback: direct chat action (data-grounded snapshot).
      try {
        const reply = await chat(user, convRef.current, q);
        setMessages([
          ...withUser,
          {
            role: "assistant",
            text: `*(via direct chat — A2A ${agent} unavailable: ${a2aErr.message})*\n\n${reply}`,
            time: new Date().toLocaleTimeString()
          }
        ]);
      } catch (e) {
        setMessages([
          ...withUser,
          { role: "error", text: `Request failed: ${e.message}`, time: new Date().toLocaleTimeString() }
        ]);
      }
    } finally {
      setBusy(false);
    }
  }

  function clearAll() {
    setMessages([]);
    ctxRef.current = {};
  }

  // HITL resume: approve/reject continues the paused task (same contextId + taskId).
  async function decide(msgIndex, decision) {
    const msg = messages[msgIndex];
    if (!msg || msg.decided || busy) return;
    setBusy(true);
    setMessages((prev) => prev.map((m, i) => (i === msgIndex ? { ...m, decided: decision } : m)));
    try {
      const r = await a2aSend(agent, {
        text: decision,
        contextId: ctxRef.current[agent] || null,
        taskId: msg.taskId,
        user
      });
      if (r.contextId) ctxRef.current[agent] = r.contextId;
      const followUp =
        r.state === "input-required" && r.taskId
          ? { role: "approval", text: r.text, taskId: r.taskId, decided: null, time: new Date().toLocaleTimeString() }
          : { role: "assistant", text: r.text, time: new Date().toLocaleTimeString() };
      setMessages((prev) => [...prev, followUp]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "error", text: `Approval ${decision} failed: ${e.message}`, time: new Date().toLocaleTimeString() }
      ]);
      // Allow retry on transport failure.
      setMessages((prev) => prev.map((m, i) => (i === msgIndex ? { ...m, decided: null } : m)));
    } finally {
      setBusy(false);
    }
  }

  const agentHint = (A2A_AGENTS.find((a) => a.id === agent) || {}).hint || "";

  return (
    <div className={full ? "panel chat-full" : "panel"}>
      <div className="panel-head">
        <h3>✨ AI assistant</h3>
        <span className="pill success">A2A · DeepSeek live</span>
        <span className="spacer" />
        <select
          className="agent-select"
          value={agent}
          disabled={busy}
          title={agentHint}
          onChange={(e) => setAgent(e.target.value)}>
          {A2A_AGENTS.map((a) => (
            <option key={a.id} value={a.id}>{a.label}</option>
          ))}
        </select>
        <button className="btn" onClick={clearAll}>Clear</button>
      </div>
      <div className="chat-wrap">
        <div className="chat-feed" ref={feedRef}>
          {messages.length === 0 && <div className="empty">No messages yet — say hi below.</div>}
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role === "approval" ? "assistant approval" : m.role}`}>
              <div className="mini-avatar">{m.role === "user" ? "YOU" : m.role === "error" ? "!" : "AI"}</div>
              {m.role === "approval" ? (
                <div className="bubble approval-card">
                  <div className="approval-label">ACTION REQUIRED</div>
                  <div className="approval-text">{renderRich(m.text)}</div>
                  {m.decided ? (
                    <div className="approval-decided">
                      {m.decided === "approve" ? "✓ Approved — continuing…" : "✕ Rejected."}
                    </div>
                  ) : (
                    <div className="approval-actions">
                      <button className="btn gold" disabled={busy} onClick={() => decide(i, "approve")}>Approve</button>
                      <button className="btn" disabled={busy} onClick={() => decide(i, "reject")}>Reject</button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bubble">{renderRich(m.text)}</div>
              )}
            </div>
          ))}
          {busy && (
            <div className="msg assistant">
              <div className="mini-avatar">AI</div>
              <div className="bubble typing-dots"><span /><span /><span /></div>
            </div>
          )}
        </div>
        <div className="suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="chip" disabled={busy} onClick={() => send(s)}>{s}</button>
          ))}
        </div>
        <div className="chat-input-row">
          <input
            value={input}
            disabled={busy}
            placeholder="Ask about requisitions, budgets, suppliers…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button className="btn gold" disabled={busy || !input.trim()} onClick={() => send()}>
            {busy ? "…" : "Send ➤"}
          </button>
        </div>
      </div>
    </div>
  );
}
