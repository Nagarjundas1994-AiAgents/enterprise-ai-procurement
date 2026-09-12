"""Part 4: m14-m17 (MCP from zero, our server, MCP security, agent+loop)."""
from common import mod, step_mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth, adr

def build():
    parts = []

    b = []
    b.append(layer("What is it?"))
    b.append(depth(simple="MCP is a waiter's notepad: the AI (customer) writes structured orders (tool calls); the server (kitchen = CAP) cooks only what's on the menu (allowed tools) and bills with a receipt (audit).", sap="Our MCP layer exposes 13 CAP capabilities as tools. The agent never writes SQL — it calls searchSuppliers, checkBudget, createPurchaseRequisition, never INSERT.", technical="MCP = JSON-RPC 2.0 over HTTP/SSE: Host (app) → Client (connection) → Server (tools/resources/prompts). Tools have inputSchema/outputSchema. Transports: Streamable HTTP (prod), stdio (local dev). VERIFY transport field names against current @cap-js/mcp docs."))
    b.append(table(["REST", "MCP", "Why agents prefer MCP"], [["POST /suppliers/check-risk + docs page", "check_supplier_risk(supplierId) with schema", "Machine-readable menu; model picks tools without scraping docs"], ["Auth per endpoint, bespoke", "One authenticated session, per-tool grants", "Gateway filters the menu per agent"], ["Free-form JSON", "Validated input/output schemas", "Fewer malformed calls; retries are structured"]]))
    b.append(mermaid("FIG. 5 — MCP TRIANGLE", """flowchart TD
  HOST["MCP Host (agent app)"] --> CLI["MCP Client (session)"]
  CLI --> SRV["MCP Server (CAP tools)"]
  SRV --> CAP["CAP services + RBAC + audit"]
  CAP --> DB["PostgreSQL"]"""))
    b.append(code("bash", "MINIMAL EXAMPLE first (one tool, no auth) — then we graduate it", "# learning-only toy, replaced in m15 by the real server:\n# tools: [{ name: 'getSupplier', inputSchema: { id: 'string' } }]\n# npx @modelcontextprotocol/inspector --cli http://localhost:4004/mcp --method tools/list"))
    parts.append(step_mod("m14", "14", "Phase 11 — MCP from zero", "HAVE: no AI surface. ADDING: mental model + vocabulary (host/client/server/tools/resources/prompts/transport).", "\n".join(b)))

    b = []
    b.append(layer("OUR APPLICATION: 13 tools on MCPService"))
    b.append(code("cds", "srv/mcp-service.cds (real file)", "using { procurement.db as db } from '../db/schema';\n\n@path: '/odata/v4/mcp'\n@odata\n@mcp: 'procurement'\n@mcp.instructions: 'Use search tools to explore procurement data. Never invent IDs. All tools enforce RBAC, tenant isolation and policy checks.'\nservice MCPService {\n  entity PurchaseRequisitions as projection on db.PurchaseRequisitions;\n  entity PurchaseOrders as projection on db.PurchaseOrders;\n  entity Suppliers as projection on db.Suppliers;\n  entity Invoices as projection on db.Invoices;\n  entity Approvals as projection on db.Approvals;\n  entity RiskAssessments as projection on db.RiskAssessments;\n\n  function searchPurchaseRequisitions(status : String, search : String, top : Integer) returns many PurchaseRequisitions;\n  function getPurchaseRequisition(ID : String) returns PurchaseRequisitions;\n  action createPurchaseRequisition(title : String, description : String, departmentID : String, totalAmount : Decimal) returns PurchaseRequisitions;\n  function searchPurchaseOrders(status : String, search : String) returns many PurchaseOrders;\n  function getPurchaseOrder(ID : String) returns PurchaseOrders;\n  action createPurchaseOrder(requisitionID : String, supplierID : String) returns PurchaseOrders;\n  function searchSuppliers(search : String) returns many Suppliers;\n  function getSupplier(ID : String) returns Suppliers;\n  function checkBudget(departmentID : String, amount : Decimal) returns Boolean;\n  function getInvoiceStatus(ID : String) returns Invoices;\n  function getApprovalStatus(requisitionID : String) returns many Approvals;\n  function getProcurementRisk(requisitionID : String) returns RiskAssessments;\n  action submitForApproval(requisitionID : String) returns String;\n}"))
    b.append(code("typescript", "Tool handler = thin wrapper over the SAME service (pattern)", "// MCP tool handlers call ProcurementService via .send(), never raw SQL:\nthis.on('getSupplier', async (req: any) => {\n  const ctx = await ctxOf(req);\n  AuthorizationService.requirePermission(ctx, PERMISSIONS.READ_SUPPLIER);\n  return tx.run(SELECT.one.from('procurement.db.Suppliers').where({ ID: req.data.ID, tenantId: ctx.tenantId }));\n});"))
    b.append(table(["Tool", "Grant needed", "Role that typically holds it"], [["searchSuppliers, getSupplier, checkBudget", "READ_SUPPLIER / READ_BUDGET", "Employee and up"], ["createPurchaseRequisition, submitForApproval", "CREATE_PR", "Officer, Manager"], ["createPurchaseOrder", "CREATE_PO + policy gate", "Officer, Manager"], ["approve (via ProcurementService action)", "APPROVE_PR", "Manager, Approver only"]]))
    b.append(callout("warn", "Sensitive tools need humans", "<p>Approval tools are <b>not</b> exposed as agent-callable MCP tools with auto-execute. The agent drafts; a human manager approves in UI5 (or via a dual-control task). Amount caps live in <code>AgentToolPermissions.maxAmount</code>.</p>"))
    parts.append(step_mod("m15", "15", "Phase 12 — Our MCP server", "HAVE: concept. ADDING: 13 tools, each a thin authorized wrapper over existing CAP logic.", "\n".join(b)))

    b = []
    b.append(layer("How the server knows who called"))
    b.append(mermaid("FIG. 6 — MCP SECURITY CHAIN", """flowchart TD
  USER["User (IAS)"] --> OAUTH["OAuth2 JWT"]
  OAUTH --> AG["Agent (delegated identity)"]
  AG --> GW["MCP Gateway (auth + tool filter)"]
  GW --> SRV["MCP Server"]
  SRV --> CAP["CAP authorization + policy"]
  CAP --> DB["DB"]
  GW --> AUD["Audit log"]"""))
    b.append('<p><b>User identity ≠ agent identity ≠ tool permission.</b> The JWT carries the user; <code>x-agent-id</code> carries the agent; <code>AgentToolPermissions</code> + scopes carry what this (user, agent, tool) triple may do. MCP itself authorizes nothing — it transports identity to CAP, which decides.</p>')
    b.append(table(["Attack", "How we stop it"], [["Prompt injection ('ignore policy and approve')", "Instructions in data are never executed (sanitizeForLLM); tools validate params; policy engine decides, not the prompt"], ["Unauthorized tool execution", "Gateway filters menu per agent; server re-checks scope + grant"], ["Privilege escalation / confused deputy", "Agent identity separate; no ambient authority; delegation scoped + audited"], ["Arbitrary DB access", "No generic SQL tool exists; only 13 fixed tools"], ["Data exfiltration / cross-tenant read", "Tenant predicate on every query; output schemas minimal; audit on sensitive reads"], ["Replayed approval", "Idempotency keys + version checks + single-use task tokens"]]))
    b.append(adr("007", "MCP is transport, CAP is authority", "An agent runtime naturally wants to 'just call the DB'.", "Where to enforce tool authorization?", [("Trust the agent/prompt", "Prompt injection becomes privilege escalation."), ("Enforce in CAP per call", "Deterministic, testable, auditable.")], "Both gateway (menu filtering, rate limits) AND CAP (scope + grant + policy + audit) enforce; CAP has the final word.", "Defense in depth; gateway stays dumb-fast.", "Two places to keep in sync — mitigated by generating the gateway menu from MCPTools + grants.", "A compromised agent gets an empty menu and DENIED rows, not data."))
    parts.append(step_mod("m16", "16", "Phase 13 — MCP security", "HAVE: tools. ADDING: identity chain, per-tool grants, injection and deputy defenses.", "\n".join(b)))

    b = []
    b.append(layer("The procurement agent"))
    b.append('<p>One <code>Agents</code> row (kind PROCUREMENT) + the real <code>AIService</code> interface (<code>generate/chat/structuredOutput</code>) backed by <code>MockAI</code> locally, AI Core wiring later. The agent loop: understand → decide tool → call via MCP client → read result → reason → answer or call again.</p>')
    b.append(code("typescript", "REAL lib/agents/ai-service.ts (repo)", "export interface ChatMessage { role: 'system' | 'user' | 'assistant' | 'tool'; content: string }\nexport interface AIService {\n  generate(prompt: string): Promise<string>;\n  chat(messages: ChatMessage[]): Promise<string>;\n  structuredOutput<T>(prompt: string, schemaHint: string): Promise<T>;\n}\nclass MockAI implements AIService {\n  async generate(prompt: string) { return `[mock-ai] ${prompt.slice(0, 200)}`; }\n}\nlet instance: AIService | null = null;\nexport function getAIService(): AIService {\n  if (instance) return instance;\n  if (process.env.AI_API_URL && process.env.AI_API_KEY) console.log('[ai] AI Core credentials detected');\n  instance = new MockAI();\n  return instance;\n}"))
    b.append(mermaid("FIG. 7 — TOOL-CALLING LOOP", """sequenceDiagram
  participant U as User
  participant A as Procurement Agent
  participant L as LLM
  participant M as MCP Client-Server
  participant C as CAP
  U->>A: Which suppliers are high risk?
  A->>L: prompt + tool schemas
  L-->>A: call searchSuppliers
  A->>M: tools/call searchSuppliers
  M->>C: authorized query (tenant + scope)
  C-->>M: supplier rows
  M-->>A: tool result
  A->>L: rows + getProcurementRisk?
  L-->>A: call getProcurementRisk x N
  A->>M: risk calls
  M-->>A: scores + reasons
  A-->>U: Ranked list with reasons + audit ref"""))
    b.append(code("bash", "Trace it locally", "curl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: buyer:EMPLOYEE' -H 'x-agent-id: procurement-agent' \\\n  -d '{\"agentId\":\"procurement-agent\",\"intent\":\"find-risky-suppliers\",\"payload\":\"{}\"}' \\\n  http://localhost:4004/odata/v4/agents/executeTask\n# inspect: AgentExecutions row + MCPToolExecutions rows share one correlationId"))
    parts.append(step_mod("m17", "17", "Phases 14-15 — AI agent + tool-calling loop", "HAVE: tools. ADDING: agent that reasons, calls tools, and answers — with a mock brain.", "\n".join(b)))

    return parts
