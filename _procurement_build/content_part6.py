"""Part 6: m22-m26 (UI5, chat UI, audit, observability, errors)."""
from common import mod, step_mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth

def build():
    parts = []

    b = []
    b.append(layer("Fiori-style UI5 over our OData"))
    b.append('<p>Pages: Dashboard, Suppliers, Purchase Requisitions, Purchase Orders, Risk Dashboard, AI Assistant, Agent Monitoring. One OData V4 model + routing + fragments + i18n. Never put secrets or tokens in frontend code.</p>')
    b.append(code("json", "app/procurement-ui/manifest.json (pattern)", '{\n  "sap.app": { "id": "procurement.ui", "type": "application" },\n  "sap.ui5": { "routing": { "routes": [\n    { "name": "Suppliers", "pattern": "suppliers", "target": "Suppliers" },\n    { "name": "PRs", "pattern": "requisitions", "target": "PRs" },\n    { "name": "Assistant", "pattern": "assistant", "target": "Assistant" }\n  ] } },\n  "sap.cloud": { "public": true }\n}'))
    b.append(code("javascript", "Component.js + OData V4 model (pattern)", "sap.ui.define(['sap/ui/core/UIComponent','sap/ui/model/odata/v4/ODataModel'], (UIComponent, ODataModel) =>\n  UIComponent.extend('procurement.ui.Component', {\n    init() {\n      UIComponent.prototype.init.apply(this, arguments);\n      this.setModel(new ODataModel({ serviceUrl: '/odata/v4/procurement/', synchronizationMode: 'None' }));\n      this.getRouter().initialize();\n    }\n  }));"))
    b.append(code("xml", "View fragment - PR table (pattern)", "<Table id=\"prTable\" items=\"{/PurchaseRequisitions}\"><headerToolbar><Toolbar><SearchField search=\".onSearch\"/><Button text=\"Create\" press=\".onCreate\" type=\"Emphasized\"/></Toolbar></headerToolbar><columns><Column><Text text=\"Number\"/></Column><Column><Text text=\"Title\"/></Column><Column><Text text=\"Status\"/></Column><Column><Text text=\"Amount\"/></Column></columns><items><ColumnListItem><ObjectNumber number=\"{requisitionNo}\"/><Text text=\"{title}\"/><ObjectStatus text=\"{status}\"/><ObjectNumber number=\"{totalAmount}\" unit=\"{currency}\"/></ColumnListItem></items></Table>"))
    b.append(table(["File", "Does what"], [["manifest.json", "Routes, models, targets"], ["Component.js", "Bootstraps ODataModel + router"], ["controllers/*.js", "CRUD, dialogs, validation, MessageManager"], ["fragments/*.xml", "Create/edit dialogs"], ["formatter.js", "Status→state colors"], ["i18n/*.properties", "All UI strings (no hardcoding)"], ["css/style.css", "Fiori spacing, responsive tables"]]))
    parts.append(step_mod("m22", "22", "Phase 21 — SAPUI5 frontend", "HAVE: API only. ADDING: 7-page Fiori app bound to our OData.", "\n".join(b)))

    b = []
    b.append(layer("Chat page → Agent API → MCP → CAP → DB → answer"))
    b.append(mermaid("FIG. 11 — CHAT PATH", """flowchart TD
  UI["Assistant view"] --> AGAPI["POST /agents/chat"]
  AGAPI --> AG["Procurement Agent"]
  AG --> MCP["MCP tools"]
  MCP --> CAP["CAP"]
  CAP --> DB["DB"]
  AG --> UI2["messages + tool indicator"]"""))
    b.append(code("javascript", "Assistant.controller.js — streaming-safe chat (pattern)", "onSend: async function () {\n  const msg = this.byId('input').getValue().trim();\n  if (!msg) return;\n  this.addBubble('user', msg);\n  const indicator = this.addBubble('assistant', 'Working…', { busy: true, tools: [] });\n  try {\n    const res = await fetch('/odata/v4/agents/chat', {\n      method: 'POST', headers: { 'Content-Type': 'application/json' },\n      body: JSON.stringify({ conversationId: this._convId, message: msg })\n    });\n    if (!res.ok) throw new Error(await res.text());\n    const { reply, toolCalls, conversationId } = await res.json();\n    this._convId = conversationId;\n    indicator.setText(reply); indicator.setTools(toolCalls); // which tools ran = trust UI\n  } catch (e) { indicator.setText('Sorry — ' + e.message); }\n}"))
    parts.append(step_mod("m23", "23", "Phase 22 — AI assistant UI", "HAVE: screens for facts. ADDING: chat with loading, tool indicator, conversation ID, errors.", "\n".join(b)))

    b = []
    b.append(layer("Every sensitive action leaves a row"))
    b.append(code("typescript", "lib/audit/audit.ts — writeAudit (real pattern)", "await writeAudit(tx, ctx, {\n  action: 'PURCHASE_ORDER_CREATED', entity: 'PurchaseOrders', entityId: orderNo,\n  oldValue: pr.status, newValue: 'APPROVED',\n  // + actorType/userId/agentId/delegatedUserId/correlationId/requestId/ipAddress\n});"))
    b.append(table(["Field", "Example"], [["actorType/userId/agentId", "USER buyer-7 via AGENT procurement-agent"], ["action/entity/entityId", "PURCHASE_REQUISITION_APPROVED / PurchaseRequisitions / <ID>"], ["correlationId", "One ID across UI→agent→MCP→CAP→A2A"], ["result/reason", "DENIED / POLICY_REQUIRES_HUMAN_APPROVAL"]]))
    b.append('<p>Why AI makes audit non-negotiable: natural-language actions are ambiguous ("approve the usual one") — the audit row records what was <em>actually</em> executed, by whom, under which policy, with which inputs.</p>')
    parts.append(step_mod("m24", "24", "Phase 23 — Audit logging", "HAVE: actions. ADDING: proof — who/what/when/why for every sensitive call.", "\n".join(b)))

    b = []
    b.append(layer("One ID to trace them all"))
    b.append('<p><code>lib/security/observability.ts → log(ctx, msg, fields)</code> emits structured JSON with <code>correlationId</code> (user journey), <code>requestId</code> (single HTTP call), <code>agentTaskId</code> and <code>toolInvocationId</code>. Locally: console JSON. BTP: Application Logging + Alert Notification.</p>')
    b.append(code("bash", "Follow one journey", "curl -H 'x-mock-user: buyer:EMPLOYEE' -H 'x-correlation-id: demo-001' http://localhost:4004/odata/v4/procurement/PurchaseRequisitions\n# grep demo-001 across cap log + MCPToolExecutions + AgentExecutions + AuditLogs"))
    parts.append(step_mod("m25", "25", "Phase 24 — Observability", "HAVE: logs. ADDING: correlation across five hops.", "\n".join(b)))

    b = []
    b.append(layer("Central error map"))
    b.append(table(["Code", "HTTP", "When"], [["VALIDATION_FAILED", "400", "quantity <= 0, missing fields"], ["UNAUTHORIZED", "401", "No/mocked identity, bad JWT"], ["FORBIDDEN / TENANT_ACCESS_DENIED", "403", "Missing scope or cross-tenant"], ["RESOURCE_NOT_FOUND", "404", "Wrong ID or OData parenthesis syntax"], ["VERSION_CONFLICT", "409", "Stale version on approve/convert"], ["POLICY_REQUIRES_HUMAN_APPROVAL", "403", "Agent over cap without human"], ["BUDGET_EXCEEDED", "422", "Insufficient budget"], ["RATE_LIMITED", "429", "Gateway throttle"], ["UPSTREAM_TIMEOUT", "504", "Supplier API down after retries"]]))
    b.append(code("typescript", "lib/security/errors.ts — toHttpError + reqError (pattern)", "throw reqError('BUDGET_EXCEEDED', `need ${need}, have ${have}`);\n// handler catch: catch (e) { req.reject(toHttpError(e)); } // maps code→HTTP, stable shape"))
    b.append(callout("mistake", "CSRF + CORS", "<p>UI5 OData V4 needs <code>x-csrf-token: Fetch</code> handshake on mutating calls; CORS allow-lists the approuter origin only. Test mutating calls with cookies + token, not bare curl, before blaming CAP.</p>"))
    parts.append(step_mod("m26", "26", "Phase 25 — Error handling", "HAVE: happy paths. ADDING: stable error contract + status discipline.", "\n".join(b)))

    return parts
