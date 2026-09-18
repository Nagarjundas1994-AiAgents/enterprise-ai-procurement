"use client";

import { useState } from "react";
import { checkBudget, submitPR, fmtMoney } from "../lib/backend";

function statusPill(s) {
  const map = { APPROVED: "success", SUBMITTED: "info", DRAFT: "neutral", REJECTED: "error" };
  return <span className={`pill ${map[s] || "warn"}`}>{s}</span>;
}

function riskPill(s) {
  const map = { LOW: "success", MEDIUM: "warn", HIGH: "error", CRITICAL: "error" };
  return <span className={`pill ${map[s] || "neutral"}`}>{s || "—"}</span>;
}

export default function Worklist({ user, prs, pos, suppliers, loading, onReload, onAskAi, notify }) {
  const [tab, setTab] = useState("prs");
  const [acting, setActing] = useState(null);

  async function doBudget(pr) {
    setActing(pr.ID + ":budget");
    try {
      const ok = await checkBudget(user, pr.department_ID, pr.totalAmount);
      notify(ok === true ? `✅ Budget covers ${pr.requisitionNo}` : `⚠️ Budget INSUFFICIENT for ${pr.requisitionNo}`);
    } catch (e) {
      notify(`❌ ${e.message}`);
    } finally {
      setActing(null);
    }
  }

  async function doSubmit(pr) {
    setActing(pr.ID + ":submit");
    try {
      const res = await submitPR(user, pr.ID);
      notify(`✅ ${typeof res === "string" ? res : `Submitted ${pr.requisitionNo}`}`);
      onReload();
    } catch (e) {
      notify(`❌ ${e.message}`);
    } finally {
      setActing(null);
    }
  }

  const tabs = [
    { key: "prs", label: `Requisitions (${prs.length})` },
    { key: "pos", label: `Orders (${pos.length})` },
    { key: "suppliers", label: `Suppliers (${suppliers.length})` }
  ];

  return (
    <div>
      <div className="tabs">
        {tabs.map((t) => (
          <button key={t.key} className={`tab ${tab === t.key ? "active" : ""}`} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="panel">
        {loading && <div className="empty">Loading live data…</div>}

        {!loading && tab === "prs" && (
          <table className="tbl">
            <thead><tr><th>No.</th><th>Title</th><th>Status</th><th>Total</th><th>Actions</th></tr></thead>
            <tbody>
              {prs.map((pr) => (
                <tr key={pr.ID}>
                  <td><strong>{pr.requisitionNo}</strong></td>
                  <td>{pr.title}</td>
                  <td>{statusPill(pr.status)}</td>
                  <td>{fmtMoney(pr.totalAmount, pr.currency)}</td>
                  <td>
                    <div className="btn-row">
                      <button className="btn" disabled={!!acting} onClick={() => doBudget(pr)}>Budget</button>
                      <button className="btn" disabled={!!acting} onClick={() => doSubmit(pr)}>Submit</button>
                      <button className="btn gold" disabled={!!acting} onClick={() => onAskAi(pr)}>Ask AI ✨</button>
                    </div>
                  </td>
                </tr>
              ))}
              {prs.length === 0 && <tr><td colSpan={5}><div className="empty">No requisitions visible for this user.</div></td></tr>}
            </tbody>
          </table>
        )}

        {!loading && tab === "pos" && (
          <table className="tbl">
            <thead><tr><th>Order No.</th><th>Status</th><th>Total</th><th>Supplier</th></tr></thead>
            <tbody>
              {pos.map((po) => (
                <tr key={po.ID}>
                  <td><strong>{po.orderNo}</strong></td>
                  <td>{statusPill(po.status)}</td>
                  <td>{fmtMoney(po.totalAmount, po.currency)}</td>
                  <td>{po.supplier_ID}</td>
                </tr>
              ))}
              {pos.length === 0 && <tr><td colSpan={4}><div className="empty">No orders visible for this user.</div></td></tr>}
            </tbody>
          </table>
        )}

        {!loading && tab === "suppliers" && (
          <table className="tbl">
            <thead><tr><th>Name</th><th>Country</th><th>On-time</th><th>Risk</th></tr></thead>
            <tbody>
              {suppliers.map((s) => (
                <tr key={s.ID}>
                  <td><strong>{s.name}</strong></td>
                  <td>{s.country}</td>
                  <td>{s.onTimeRate} %</td>
                  <td>{riskPill(s.riskLevel)}</td>
                </tr>
              ))}
              {suppliers.length === 0 && <tr><td colSpan={4}><div className="empty">No suppliers visible for this user.</div></td></tr>}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
