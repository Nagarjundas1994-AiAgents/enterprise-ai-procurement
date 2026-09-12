"""Part 5: m18-m21 (A2A, discovery, combined, gateway, IAS)."""
from common import mod, step_mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth, adr

def build():
    parts = []

    b = []
    b.append(layer("What is it? Agent → Agent"))
    b.append('<p><b>MCP = agent→tool. A2A = agent→agent.</b> ProcurementAgent asks RiskAgent for analysis; RiskAgent uses MCP tools itself and returns a scored answer. Neither agent touches the other\'s internals — they exchange signed <b>tasks</b> and <b>messages</b> with correlation IDs.</p>')
    b.append(mermaid("FIG. 8 — A2A DELEGATION", """sequenceDiagram
  participant P as Procurement Agent
  participant R as Risk Agent
  participant M as MCP tools
  participant C as CAP
  P->>R: A2A task (score supplier S, corr-123)
  R->>M: getSupplier + getProcurementRisk
  M->>C: authorized calls
  C-->>M: rows + history
  M-->>R: tool results
  R-->>P: A2A response (score 82 HIGH + reasons)
  P->>C: createPurchaseRequisition (policy-gated)"""))
    b.append(code("typescript", "AgentService.executeTask → orchestrator → specialist (real shape)", "// POST /odata/v4/agents/executeTask { agentId, intent, payload }\n// AgentService cds: action executeTask(agentId:String, intent:String, payload:LargeString)\n// Handler: authenticate (user + x-agent-id) → load Agents row + tool grants →\n// route: procurement|risk|invoice|budget|approval|audit → specialist service via .send()\n// → write AgentExecutions row (input/output/status/correlationId) → return result"))
    b.append(table(["A2A concept", "Our field/table", "Why"], [["Agent discovery", "/.well-known/agent.json (orchestrator card, A2A/0.2)", "Find capabilities without hardcoding URLs"], ["Task", "executeTask(agentId, intent, payload)", "One unit of delegated work"], ["Message", "AIMessages (role USER/ASSISTANT/TOOL)", "Auditable conversation"], ["Correlation ID", "AgentExecutions.correlationId", "Trace across agents + tools"], ["Timeout/retry/idempotency", "Task token + version checks", "No double approvals on retry"]]))
    b.append(callout("mistake", "Discovery ≠ authorization", "<p>Reading RiskAgent's card tells you what it <em>can</em> do, not what <em>you</em> may ask it to do. Every A2A call re-authenticates both agents and re-checks the caller's grant.</p>"))
    parts.append(step_mod("m18", "18", "Phase 16 — A2A + discovery", "HAVE: one agent. ADDING: two agents, discovery doc, authenticated task exchange.", "\n".join(b)))

    b = []
    b.append(layer("Why both protocols?"))
    b.append(mermaid("FIG. 9 — MCP + A2A TOGETHER", """flowchart TD
  PA["Procurement Agent"] -->|A2A task| RA["Risk Agent"]
  RA -->|MCP tools| TOOLS["searchSuppliers, getProcurementRisk, checkBudget"]
  TOOLS --> CAP["CAP services"]
  PA -->|MCP tools| TOOLS"""))
    b.append(table(["Pattern", "Shape", "Use when"], [["UI → CAP", "OData directly", "Plain CRUD screens"], ["UI → CAP → External API", "Via Destination", "Supplier push"], ["UI → Agent → MCP → CAP", "Chat assistant", "Questions + governed actions"], ["Agent → A2A → Agent", "Delegation", "Specialist knowledge (risk, budget)"], ["Agent → Gateway → many MCP servers", "Fan-out", "Ours + third-party tools"], ["Agent → MCP → CAP → Event", "Async follow-through", "Notify + rescore after writes"]]))
    b.append(code("json", "REAL /.well-known/agent.json (srv/server.js)", '{\n  "name": "enterprise-ai-procurement-orchestrator",\n  "protocol": "A2A/0.2",\n  "version": "1.0.0",\n  "skills": ["procurement", "approval", "supplier-risk", "invoice-matching", "budget-check", "audit"],\n  "endpoints": { "rpc": "/odata/v4/agents/orchestrate", "mcp": "/mcp" }\n}'))
    parts.append(step_mod("m19", "19", "Phases 17-18 — Discovery + MCP×A2A", "HAVE: two agents. ADDING: discovery contract + the combined request path.", "\n".join(b)))

    b = []
    b.append(layer("Learning gateway (Express middleware in front of /mcp)"))
    b.append(table(["Responsibility", "Learning implementation", "BTP production owner"], [["Authentication", "JWT / x-mock-user check", "Approuter + XSUAA"], ["Tool discovery/filtering", "Menu from MCPTools + AgentToolPermissions", "MCP Gateway / registry"], ["Rate limiting", "express-rate-limit per tool+agent", "Gateway / API management"], ["Logging + audit", "MCPToolExecutions + AuditLogs rows", "Application Logging + audit service"], ["Routing", "Local fan-out to ours + mock third-party", "Destination + Cloud Connector"]]))
    b.append(code("typescript", "Gateway shape (pattern, helmet + rate limit already in repo)", "import helmet from 'helmet';\nimport rateLimit from 'express-rate-limit';\napp.use(helmet());\napp.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 600 })); // REAL global net (srv/server.js)\napp.use('/mcp', authenticateGateway, filterToolsByGrant, auditToolCall); // learning gateway (REAL per-tool limits: lib/security/rate-limit.ts)"))
    b.append(layer("IAS trust chain"))
    b.append(mermaid("FIG. 10 — TRUST", """flowchart TD
  IDP["Corporate IdP"] --> IAS["Cloud Identity Services"]
  IAS --> AR["Approuter"]
  AR --> CAP["CAP (JWT validation)"]
  CAP --> SCOPES["Scopes → roles → permissions"]
  SCOPES --> TOOL["Tool grant check"]
  TOOL --> AUD["Audit row"]"""))
    b.append(callout("prod", "Federation", "<p>Corporate IdP federates to IAS (SAML/OIDC); IAS issues tokens the approuter forwards; XSUAA validates in CAP. Trust = signature + audience + scope mapping. VERIFY current IAS↔XSUAA setup steps in SAP docs — console flows change.</p>"))
    parts.append(step_mod("m20", "20", "Phases 19-20 — Gateway + IAS", "HAVE: direct tool calls. ADDING: front door (auth, filter, limit, audit) + trust chain.", "\n".join(b)))

    b = []
    b.append(layer("Authorizing what an agent can do (the critical section)"))
    b.append('<p><b>User identity ≠ agent identity ≠ tool identity.</b> A manager delegating to procurement-agent for a €200k approval still fails unless: the user holds APPROVE_PR, the agent holds an explicit grant for the approval path, the amount is under <code>maxAmount</code>, and policy returns AUTO_APPROVE (higher bands route to REQUIRE_MANAGER / FINANCE / HUMAN).</p>')
    b.append(table(["Abuse", "Control that blocks it"], [["Agent approves unauthorized PO", "APPROVE_PR scope + grant + policy + human co-sign over cap"], ["Agent deletes suppliers", "No DELETE grant on that tool for that agent"], ["Agent edits finance data", "FINANCE-only scopes; agent menu excludes them"], ["Cross-tenant read", "tenantId predicate + rejection of client tenant"], ["Sensitive dump via chat", "Minimal output schemas + redaction + audit on sensitive reads"], ["Admin tool invocation", "ADMIN_SYSTEM never granted to AI_AGENT"]]))
    b.append(quiz("qsec", "Prompt says 'ignore policy'. What happens?", [("Policy engine still decides; prompt is data, not authority", True), ("Agent obeys the prompt", False)], "sanitizeForLLM treats business text as DATA. Policy runs in the tx regardless of wording."))
    parts.append(mod("m21", "21", "", "AI agent security — the delegation model", "\n".join(b)))

    return parts
