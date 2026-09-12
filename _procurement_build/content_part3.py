"""Part 3: m10-m13 (auth, destinations, external API, events)."""
from common import mod, step_mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth, adr

def build():
    parts = []

    b = []
    b.append(layer("What is it?"))
    b.append(depth(simple="Authentication = who are you (badge check). Authorization = what may you do (which doors your badge opens).", sap="Locally: x-mock-user + x-agent-id headers. BTP: IAS login → approuter → XSUAA JWT with scopes → CAP checks scopes.", technical="lib/auth/authentication.ts builds ctx {userId, tenantId, roles, isAgent}. AuthorizationService.requirePermission maps scopes→PERMISSIONS. Tenant always comes from ctx, never req.data."))
    b.append(code("json", "xs-security.json — scopes + AI_AGENT least privilege (real, excerpt)", '{\n  "xsappname": "enterprise-ai-procurement",\n  "tenant-mode": "dedicated",\n  "scopes": [\n    { "name": "$XSAPPNAME.APPROVE_PURCHASE_REQUISITION", "description": "Approve purchase requisitions" },\n    { "name": "$XSAPPNAME.CREATE_PURCHASE_ORDER", "description": "Create purchase orders" },\n    { "name": "$XSAPPNAME.EXECUTE_MCP_TOOL", "description": "Execute MCP tools" }\n  ],\n  "role-templates": [\n    { "name": "PROCUREMENT_MANAGER", "scope-references": [\n      "$XSAPPNAME.APPROVE_PURCHASE_REQUISITION", "$XSAPPNAME.CREATE_PURCHASE_ORDER"] },\n    { "name": "AI_AGENT", "description": "Empty by default; per-agent tool grants apply",\n      "scope-references": [] }\n  ]\n}'))
    b.append(code("bash", "Local auth drills (mocked)", "# buyer with EMPLOYEE role\ncurl -H 'x-mock-user: buyer:EMPLOYEE' http://localhost:4004/odata/v4/procurement/PurchaseRequisitions\n# manager approves (action, audited)\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: manager:PROCUREMENT_MANAGER' \\\n  -d '{\"ID\":\"<PR-ID>\",\"comment\":\"ok\"}' http://localhost:4004/odata/v4/procurement/approveRequisition\n# agent identity (least privilege + tool grants)\ncurl -H 'x-mock-user: julius:EMPLOYEE' -H 'x-agent-id: procurement-agent' http://localhost:4004/odata/v4/mcp/searchSuppliers(search=%27acme%27)"))
    b.append(table(["Role collection (BTP)", "Can do", "Cannot do"], [["Employee", "Create/edit own PRs", "Approve, MCP tools"], ["ProcurementManager", "Full lifecycle incl. approve", "Admin"], ["Approver", "Approve/reject only", "Create POs, finance"], ["Finance", "Invoices + payments", "Approve PRs"], ["AI_Agent (empty)", "Nothing by default; grants per agent", "Anything not explicitly granted"]]))
    b.append(callout("mistake", "Never trust client tenant", "<p><code>req.data.tenantId</code> is rejected if it disagrees with <code>ctx.tenantId</code>. Every READ adds <code>where({tenantId})</code>. Agents get no wildcard — <code>AgentToolPermissions</code> + <code>maxAmount</code> decide per tool.</p>"))
    b.append(quiz("q10", "An agent calls approveRequisition. What is checked?", [("User delegation + agent tool grant + APPROVE_PR scope + policy gate", True), ("Only that the agent exists", False), ("Only the LLM's confidence", False)], "Four checks: delegated user, tool grant, scope, policy. See Phase 16 security."))
    parts.append(step_mod("m10", "10", "Phase 7 — Authentication + authorization", "HAVE: open API. ADDING: identity, 9 role collections, empty-by-default AI_AGENT, tenant isolation.", "\n".join(b)))

    b = []
    b.append(layer("Why destinations?"))
    b.append('<p>External URLs, secrets and proxy config live in the <b>Destination service</b>, not in code. CAP looks up a named destination at runtime and propagates the user (principal propagation) so the far system can authorize too.</p>')
    b.append(mermaid("FIG. 4 — DESTINATION FLOW", """flowchart TD
  CAP["CAP action"] --> DST["Destination service"]
  DST --> XAPI["Supplier API"]
  IAS["IAS and XSUAA"] --> CAP
  CAP -->|"OAuth2 / mTLS / Basic (server-side)"| XAPI"""))
    b.append(code("bash", "Sample destination (BTP cockpit → Destinations)", "Name: SUPPLIER_API\nType: HTTP\nURL: https://supplier.example.com\nProxyType: Internet\nAuthType: OAuth2ClientCredentials\nClientID: <from vault>  # VERIFY: field names vs current cockpit UI\nTokenServiceURL: https://auth.example.com/oauth/token"))
    b.append(code("typescript", "lib/destinations.ts — never hardcode (pattern)", "const dest = await getDestination('SUPPLIER_API'); // URL + token from service\nconst res = await fetch(`${dest.url}/suppliers/${id}`, {\n  headers: { Authorization: `Bearer ${dest.token}` },\n  signal: AbortSignal.timeout(8000),\n});\nif (!res.ok) throw mapStatus(res.status); // 401/403/404/429/5xx handled in Phase 12"))
    b.append(callout("prod", "Production note", "<p>Locally: <code>.env</code> + mock supplier server. BTP: real Destination instance bound via <code>mta.yaml</code> + service binding. Code path identical — only the binding changes.</p>"))
    parts.append(step_mod("m11", "11", "Phase 8 — Destination service", "HAVE: self-contained app. ADDING: named, credential-free route to the outside world.", "\n".join(b)))

    b = []
    b.append(layer("Supplier integration with grown-up error handling"))
    b.append(code("typescript", "SupplierIntegrationService — retry + idempotency (pattern)", "async function postPO(dest: any, po: any, idemKey: string, tries = 3) {\n  for (let i = 0; i < tries; i++) {\n    const r = await fetch(`${dest.url}/purchase-orders`, {\n      method: 'POST',\n      headers: { Authorization: `Bearer ${dest.token}`, 'Idempotency-Key': idemKey },\n      body: JSON.stringify(po), signal: AbortSignal.timeout(8000),\n    });\n    if (r.ok) return r.json();\n    if ([400,401,403,404,409,422].includes(r.status)) throw await toBusinessError(r); // no retry\n    if (r.status === 429 || r.status >= 500) { await backoff(i); continue; }          // retryable\n    throw new Error(`supplier-api:${r.status}`);\n  }\n  throw reqError('UPSTREAM_TIMEOUT', 'Supplier API did not respond after retries');\n}"))
    b.append(table(["Status", "Meaning here", "Behavior"], [["401/403", "Destination credential or scope wrong", "Fail fast, alert, no retry"], ["404", "Supplier unknown remotely", "Fail with business message"], ["409", "Duplicate (idempotency hit)", "Treat as success, return existing"], ["429/5xx/timeout", "Overloaded or down", "Backoff + retry, then circuit-break"], ["422", "Remote validation failed", "Surface field errors to UI"]]))
    b.append(callout("insight", "Idempotency", "<p>Every retryable POST carries an <code>Idempotency-Key</code> (PO ID). Double-clicks and retried agent calls create exactly one remote order.</p>"))
    parts.append(step_mod("m12", "12", "Phase 9 — External API integration", "HAVE: destination lookup. ADDING: supplier calls with timeouts, retries, idempotency, validated responses.", "\n".join(b)))

    b = []
    b.append(layer("Sync vs async"))
    b.append('<p>Approvals need <b>synchronous</b> answers (action returns APPROVED now). Risk-flagging, notifications and supplier sync are <b>asynchronous events</b>: emit and continue; subscribers catch up. Learning implementation: CAP <code>emit</code> + local subscribers. Production: SAP Event Mesh (same event names).</p>')
    b.append(code("typescript", "Events — emit on lifecycle (pattern)", "// after approveRequisition succeeds:\nawait this.emit('PurchaseRequisitionApproved', { requisitionId: pr.ID, tenantId: ctx.tenantId, correlationId: ctx.correlationId });\n// subscriber (local; Event Mesh in prod):\nthis.on('PurchaseRequisitionApproved', async (msg: any) => {\n  await notifyManager(msg.data);        // try/catch inside — subscribers never break publishers\n  await riskAgent.rescore(msg.data);    // autonomous investigation trigger\n});"))
    b.append(table(["Event", "Publisher", "Subscribers"], [["PurchaseRequisitionCreated", "ProcurementService", "Budget reservation, notification"], ["PurchaseRequisitionApproved", "approveRequisition", "PO drafting hint, risk rescore"], ["PurchaseOrderCreated", "convertToPurchaseOrder", "Supplier API push, audit"], ["SupplierRiskDetected", "RiskAgent", "Buyer alert, policy review task"]]))
    b.append(callout("prod", "Background jobs", "<p>Retries, digest mails and rescoring run as jobs (BTP Jobscheduler in prod). Jobs carry the same <code>correlationId</code> so a 3am retry still traces to the original user click.</p>"))
    parts.append(step_mod("m13", "13", "Phase 10 — Events + background jobs", "HAVE: request/response only. ADDING: domain events with a production path to Event Mesh.", "\n".join(b)))

    return parts
