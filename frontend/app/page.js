"use client";

import { useCallback, useEffect, useState } from "react";
import ChatPanel from "../components/ChatPanel";
import Worklist from "../components/Worklist";
import { listPRs, listPOs, listSuppliers, USERS, fmtMoney } from "../lib/backend";

const NAV = [
  { key: "overview", label: "Overview", ico: "◈" },
  { key: "worklist", label: "Worklist", ico: "▦" },
  { key: "chat", label: "AI Assistant", ico: "✨" }
];

export default function Home() {
  const [nav, setNav] = useState("overview");
  const [user, setUser] = useState(USERS[0].email);
  const [prs, setPrs] = useState([]);
  const [pos, setPos] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [askQ, setAskQ] = useState(null);
  const [theme, setTheme] = useState("dark");

  // Theme: the blocking script in layout.js already applied the persisted
  // (or OS) theme to <html data-theme> before hydration. Here we only sync
  // React state to it — post-hydration, so server and client first render
  // always agree ("dark") and hydration can never mismatch.
  useEffect(() => {
    try {
      const applied = document.documentElement.dataset.theme;
      if (applied === "light" || applied === "dark") setTheme(applied);
    } catch { /* non-critical */ }
  }, []);

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    try {
      document.documentElement.dataset.theme = next;
      localStorage.setItem("pc-theme", next);
    } catch { /* non-critical */ }
    window.dispatchEvent(new Event("pc-theme-change"));
  }

  const notify = useCallback((text) => {
    setToast(text);
    setTimeout(() => setToast(null), 4200);
  }, []);

  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const [r1, r2, r3] = await Promise.all([listPRs(user), listPOs(user), listSuppliers(user)]);
      setPrs(r1.value || r1 || []);
      setPos(r2.value || r2 || []);
      setSuppliers(r3.value || r3 || []);
    } catch (e) {
      notify(`❌ ${e.message}`);
      setPrs([]); setPos([]); setSuppliers([]);
    } finally {
      setLoading(false);
    }
  }, [user, notify]);

  useEffect(() => { reload(); }, [reload]);

  function askAbout(pr) {
    setAskQ(
      `PR ${pr.requisitionNo} '${pr.title}' (${pr.status}, ${fmtMoney(pr.totalAmount, pr.currency)}): ` +
      `summarize status, budget outlook and recommended next step.`
    );
    setNav("chat");
  }

  const openPRs = prs.filter((p) => p.status === "DRAFT" || p.status === "SUBMITTED").length;
  const apprPRs = prs.filter((p) => p.status === "APPROVED").length;
  const totalSpend = prs.reduce((a, p) => a + Number(p.totalAmount || 0), 0);
  const riskySup = suppliers.filter((s) => s.riskLevel === "HIGH" || s.riskLevel === "CRITICAL").length;
  const me = USERS.find((u) => u.email === user);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">P</div>
          <div><h1>ProcureChat</h1><small>AI Procurement</small></div>
        </div>
        <div className="nav-label">Workspace</div>
        {NAV.map((n) => (
          <button key={n.key} className={`nav-item ${nav === n.key ? "active" : ""}`} onClick={() => setNav(n.key)}>
            <span className="ico">{n.ico}</span>{n.label}
          </button>
        ))}
        <div className="nav-label">Backend</div>
        <button className="nav-item" onClick={reload}><span className="ico">↻</span>Refresh data</button>
        <div className="side-foot">
          CAP backend :4004<br />DeepSeek · MCP · A2A<br />RBAC + tenant isolation
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <div>
            <h2>{nav === "overview" ? "Command center" : nav === "worklist" ? "Procurement worklist" : "AI assistant"}</h2>
            <p>Live data from your CAP backend — every action is RBAC-checked and audited.</p>
          </div>
          <div className="user-chip">
            <div className="avatar">{me.label.slice(0, 2).toUpperCase()}</div>
            <select value={user} onChange={(e) => setUser(e.target.value)}>
              {USERS.map((u) => (
                <option key={u.email} value={u.email}>{u.label} — {u.role}</option>
              ))}
            </select>
            <span className="user-chip-divider" />
            <button
              className="theme-toggle-icon"
              onClick={toggleTheme}
              suppressHydrationWarning
              aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
              title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}>
              {theme === "dark" ? "☀" : "◐"}
            </button>
          </div>
        </div>

        {(nav === "overview") && (
          <>
            <div className="grid-kpi">
              <div className="card"><div className="kpi-label">Open requisitions</div><div className="kpi-value gold">{openPRs}</div><div className="kpi-sub">{prs.length} total · {apprPRs} approved</div></div>
              <div className="card"><div className="kpi-label">Requisition volume</div><div className="kpi-value">{fmtMoney(totalSpend)}</div><div className="kpi-sub">across {prs.length} PRs</div></div>
              <div className="card"><div className="kpi-label">Purchase orders</div><div className="kpi-value">{pos.length}</div><div className="kpi-sub">created from approvals</div></div>
              <div className="card"><div className="kpi-label">Risky suppliers</div><div className="kpi-value">{riskySup}</div><div className="kpi-sub">{suppliers.length} suppliers tracked</div></div>
            </div>
            <div className="content-grid">
              <Worklist user={user} prs={prs} pos={pos} suppliers={suppliers} loading={loading} onReload={reload} onAskAi={askAbout} notify={notify} />
              <ChatPanel user={user} externalAsk={askQ} onConsumedAsk={() => setAskQ(null)} />
            </div>
          </>
        )}

        {nav === "worklist" && (
          <Worklist user={user} prs={prs} pos={pos} suppliers={suppliers} loading={loading} onReload={reload} onAskAi={askAbout} notify={notify} />
        )}

        {nav === "chat" && (
          <ChatPanel full user={user} externalAsk={askQ} onConsumedAsk={() => setAskQ(null)} />
        )}

        {toast && <div className="toast">{toast}</div>}
      </main>
    </div>
  );
}
