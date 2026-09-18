"use client";

/**
 * Same-origin calls to the CAP backend via the Next.js rewrite proxy:
 *   /backend/odata/... -> http://localhost:4004/odata/...
 * The demo-user header authenticates local dev (ALLOW_MOCK_AUTH=true).
 */

export async function api(path, { method = "GET", body, user } = {}) {
  const res = await fetch(`/backend${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "x-mock-user": user || "admin@example.com"
    },
    body: body ? JSON.stringify(body) : undefined
  });
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    const msg = (data && data.error && data.error.message) || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data && data.value !== undefined ? data.value : data;
}

export const listPRs = (user) =>
  api(`/odata/v4/procurement/PurchaseRequisitions?$top=50&$orderby=createdAt%20desc`, { user });

export const listPOs = (user) =>
  api(`/odata/v4/procurement/PurchaseOrders?$top=50&$orderby=createdAt%20desc`, { user });

export const listSuppliers = (user) =>
  api(`/odata/v4/suppliers/Suppliers?$top=50`, { user });

export const checkBudget = (user, departmentID, amount) =>
  api(
    `/odata/v4/catalog/checkBudget(departmentID='${String(departmentID).replace(/'/g, "''")}',amount=${Number(amount)})`,
    { user }
  );

export const submitPR = (user, ID) =>
  api(`/odata/v4/procurement/submitRequisition`, { method: "POST", user, body: { ID } });

export const chat = (user, conversationId, message) =>
  api(`/odata/v4/agents/chat`, {
    method: "POST",
    user,
    body: { conversationId, message }
  });

export const USERS = [
  { email: "admin@example.com", label: "Admin", role: "Full access" },
  { email: "manager@example.com", label: "Manager", role: "Approvals + POs" },
  { email: "procurement@example.com", label: "Officer", role: "Procurement" },
  { email: "employee@example.com", label: "Employee", role: "Requester" },
  { email: "approver@example.com", label: "Approver", role: "Approvals" },
  { email: "auditor@example.com", label: "Auditor", role: "Read + audit" }
];

export function fmtMoney(n, currency) {
  const v = Number(n || 0);
  return v.toLocaleString("en-US", { maximumFractionDigits: 2 }) + (currency ? ` ${currency}` : "");
}
