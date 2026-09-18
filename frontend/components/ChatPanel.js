"use client";

import { useEffect, useRef, useState } from "react";
import { chat } from "../lib/backend";
import { a2aSend, A2A_AGENTS } from "../lib/a2a";

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
          <table key={key++} className="md-table">
            <thead><tr>{head.map((c, j) => <th key={j}>{inlineRich(c, `h${key}-${j}`)}</th>)}</tr></thead>
            <tbody>{rest.map((r, ri) => <tr key={ri}>{r.map((c, j) => <td key={j}>{inlineRich(c, `r${ri}-${j}`)}</td>)}</tr>)}</tbody>
          </table>
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
    // Fenced code — render as plain preformatted text (no code execution)
    if (/^\s*```/.test(line)) {
      const buf = [];
      i++;
      while (i < lines.length && !/^\s*```/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++;
      blocks.push(<pre key={key++} className="md-pre">{buf.join("\n")}</pre>);
      continue;
    }
    blocks.push(<div key={key++} className="md-line">{inlineRich(line || " ", `l${key}`)}</div>);
    i++;
  }
  return blocks;
}

export default function ChatPanel({ user, externalAsk, onConsumedAsk }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I am your procurement assistant, powered by **DeepSeek**. Ask about requisitions, budgets or suppliers — or use **Ask AI** on any requisition row.",
      time: new Date().toLocaleTimeString()
    }
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [agent, setAgent] = useState("catalog");
  const feedRef = useRef(null);
  // A2A conversation continuity: one contextId per agent.
  const ctxRef = useRef({});
  const convRef = useRef(`ui-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`);

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
      setMessages([
        ...withUser,
        { role: "assistant", text: r.text, time: new Date().toLocaleTimeString() }
      ]);
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

  const agentHint = (A2A_AGENTS.find((a) => a.id === agent) || {}).hint || "";

  return (
    <div className="panel">
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
            <div key={i} className={`msg ${m.role}`}>
              <div className="mini-avatar">{m.role === "user" ? "YOU" : m.role === "error" ? "!" : "AI"}</div>
              <div className="bubble">{renderRich(m.text)}</div>
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
