"""Part 1: hero + m01-m04 (business, architect mindset, architecture map, setup)."""
from common import mod, step_mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth, adr, glossary

HERO = '''<header class="hero" id="top">
  <div class="titleblock">
    <div class="tb-row"><span class="tb-k">Doc No.</span><span class="tb-v">AC-PROC-2026</span></div>
    <div class="tb-row"><span class="tb-k">Rev.</span><span class="tb-v">2026.09</span></div>
    <div class="tb-row"><span class="tb-k">Stack</span><span class="tb-v">CAP Node.js + PG</span></div>
    <div class="tb-row"><span class="tb-k">Phases</span><span class="tb-v">P0-P41</span></div>
  </div>
  <p class="kicker">Building a Production-Grade Autonomous Procurement Control Tower with SAP CAP, BTP, MCP and A2A</p>
  <h1>Autonomous Procurement Control Tower</h1>
  <p class="sub">End-to-End SAP CAP + AI Agent + MCP + A2A Hands-On Workshop. You build ONE application from a plain UI-CAP-DB triple into an AI-enabled, MCP-enabled, A2A-enabled enterprise system — and you learn every acronym on the way because you type it, run it, break it, and secure it.</p>
  <div class="statrow">
    <div class="stat"><b>41</b><span>modules, beginner to production</span></div>
    <div class="stat"><b>30+</b><span>domain entities in db/schema.cds</span></div>
    <div class="stat"><b>7</b><span>specialist agents behind one orchestrator</span></div>
    <div class="stat"><b>13</b><span>governed MCP tools, zero raw DB access</span></div>
  </div>
  <p>This document is the course. Open it in a browser (no server needed), follow it top to bottom, and copy the code into the <b>same</b> repository at every step. Nothing is thrown away: Phase 4's OData service is still there in Phase 33's BTP deployment, with agents wrapped around it.</p>
  <div class="callout concept"><h4>The one rule, repeated all course</h4><p>An AI agent <b>never touches the database directly</b>. It calls a <b>governed CAP service</b>. CAP owns business logic and authorization. MCP, A2A and the gateway are how agents <em>reach</em> that governed layer — never a way around it. Every diagram below is a variation on that sentence.</p></div>
  <h3>The master mental model</h3>
  <p>Every phase zooms into one arrow of this picture. Keep it in your head from here on.</p>''' + mermaid(
    "FIG. 0 — MASTER MENTAL MODEL: ONE GOVERNED PATH",
    """flowchart TD
  U["User"] --> F["SAPUI5 Fiori app"]
  F --> CAP["SAP CAP services"]
  CAP --> DB["PostgreSQL, HANA Cloud in prod"]
  F --> AG["AI Agent"]
  AG --> MCP["MCP Gateway + MCP tools"]
  MCP --> CAP
  AG --> A2A["A2A to Risk Agent"]
  A2A --> AG2["Risk Agent"]
  AG2 --> MCP
  CAP --> EXT["External APIs via Destination"]
  CAP --> EV["Events + background jobs"]
  CAP --> IAS["IAS and XSUAA"]

  classDef user fill:#E7ECF8,stroke:#0B3D91,color:#0B3D91,stroke-width:1.4px;
  classDef gov fill:#F9EEDC,stroke:#B5710A,color:#B5710A,stroke-width:1.4px;
  classDef agent fill:#0B3D91,stroke:#0B3D91,color:#fff,stroke-width:1.4px;
  classDef proto fill:#EEE9FD,stroke:#6B46E8,color:#6B46E8,stroke-width:1.4px;
  class U,F user;
  class CAP,DB,EXT,EV,IAS gov;
  class AG,AG2 agent;
  class MCP,A2A proto;""",
  ) + '''
  <div class="callout beginner"><h4>How to use this document</h4><p>Each module follows <b>What is it / Why / Where in our app / How it works / Code / Test it / Expected result / Production note</b>. Toggle <b>Architect mode</b> (top bar) to hide beginner scaffolding. Tick <b>Mark complete</b> to track progress (stored locally). Press <b>/</b> to search. Every code block has a <b>Copy</b> button.</p></div>
  <div class="done-row"><label><input type="checkbox" data-done="m00"> Mark the introduction complete</label></div>
</header>'''


def build():
    parts = [HERO]

    b = []
    b.append(layer("What is it? The scenario"))
    b.append('<p><b>Autonomous Procurement Control Tower</b> is a realistic enterprise procurement platform. A factory buyer raises a <b>purchase requisition</b> (I need 500 brake pads), a manager <b>approves</b> it, the system converts it to a <b>purchase order</b> against a <b>supplier</b>, tracks <b>goods receipts</b>, <b>invoices</b> and <b>payments</b>, watches <b>budgets</b>, and flags <b>risks</b> (late delivery, abnormal price). Then AI arrives: buyers ask questions in plain English, a <b>procurement agent</b> answers using governed tools, and a <b>risk agent</b> supplies risk analysis over <b>A2A</b>.</p>')
    b.append(grid([("Requisitions to payment", "PR with items, approvals, PO with items, receipts, invoices, payments — the document flow auditors actually check."),("Master data + money", "Suppliers with risk scores, materials, departments, budgets with committed and consumed amounts."),("Risk + policy", "RiskAssessments, Policies as data, PolicyViolations — policy gates decide, the LLM only recommends."),("Agents + audit", "Agents, AgentExecutions, MCPTools, MCPToolExecutions, AIConversations, AuditLogs — every AI action traceable.")], 2))
    b.append(layer("Why do we need it? The pain today"))
    b.append(steps(["Buyer emails spreadsheets; nobody knows the PR status or remaining budget.","Manager approves by gut feel; no policy check, no risk score, no audit proof.","Invoice arrives for a different amount; 3-way match (PO vs receipt vs invoice) is manual.","Supplier keeps delivering late; the signal hides in past orders nobody queries.","Leadership asks 'which suppliers are risky?' — the answer takes a week of SQL."]))
    b.append('<div class="chat"><div class="msg user"><p class="who">User asks</p><p>Which suppliers have high procurement risk, and why?</p></div><div class="msg ai"><p class="who">Governed answer (end of course)</p><p>Risk Agent scores suppliers from live POs, receipts and disputes via MCP tools — with policy citations and an audit row — instead of a week of SQL.</p></div><div class="msg user"><p class="who">User asks</p><p>Create a requisition for 200 brake pads and route it for approval.</p></div><div class="msg ai"><p class="who">Governed action</p><p>Procurement Agent calls createPurchaseRequisition + submitForApproval through the MCP gateway — RBAC, tenant check, budget check, audit write — then shows the approval task.</p></div></div>')
    b.append(callout("mistake", "Common mistake", "<p>Building 'a chatbot with direct database access'. It demos well and fails the first audit: no authorization, no tenant isolation, no policy gate, no trace of who approved what. This course builds the opposite — the agent is the <em>least</em> privileged actor in the system.</p>"))
    b.append(qa([("Is this a real working project or disconnected demos?", "One project, extended phase by phase. Phase 4's OData URLs still work in Phase 33's BTP deployment."),("Do I need a paid LLM key?", "No. Local development uses a MockLLM provider with deterministic responses. Real providers (SAP AI Core / Generative AI Hub) plug in later behind the same interface."),("Do I need BTP on day one?", "No. Everything runs locally (SQLite/Postgres, mocked auth, mock LLM, mock destination) until the deployment phases.")]))
    b.append(quiz("q01", "Where does authorization live in this architecture?", [("In the CAP service layer, enforced before every read and action", True), ("In the MCP protocol itself", False), ("In the LLM prompt", False)], "MCP is transport. CAP owns who-can-do-what — see Phase 7 and Phase 16."))
    parts.append(mod("m01", "01", "", "The business problem", "\n".join(b)))

    b = []
    b.append(layer("The mindset shift"))
    b.append('<div class="compare"><div><p class="vs">Novice approach</p><div class="card"><p>"I will add an AI agent, an MCP server, and A2A to my app." Technology list first — authorization, tenancy and audit discovered during the incident review.</p></div></div><div><p class="vs">Architect approach</p><div class="card"><p>"The capability is <em>governed procurement execution</em>. The system of record is CAP + Postgres. Agents reach it through tools with explicit grants, every write audited, every cross-agent call authenticated. Then I pick protocols." Capability, owner, failure mode first.</p></div></div></div>')
    b.append(callout("insight", "Architect insight", "<p>For every box in any AI architecture diagram, ask: <b>who calls it, with whose identity, checked against what policy, and where is the audit row?</b> If any answer is 'the agent just can', the diagram is a demo, not a design.</p>"))
    b.append(layer("Concept to production ladder (used for every technology)"))
    b.append('<p>Each technology in this course climbs the same ladder: <b>CONCEPT → MINIMAL EXAMPLE → OUR APPLICATION → PRODUCTION VERSION</b>. At each rung you see <b>WHAT WE HAVE BUILT SO FAR</b> and <b>WHAT WE ARE ADDING NOW</b>, so the final BTP poster in Phase 35 is the sum of small understood steps, not a leap.</p>')
    b.append(table(["Rung", "MCP example", "A2A example"], [["CONCEPT", "Host / client / server / tools in one paragraph", "Agent Card, task, message, discovery in one paragraph"], ["MINIMAL", "One-tool server (getSupplier), no auth", "Two agents exchanging one JSON task"], ["OUR APP", "13 tools on MCPService with RBAC + audit", "ProcurementAgent delegates risk scoring to RiskAgent"], ["PRODUCTION", "Gateway: OAuth, rate limit, tool filtering, audit", "Signed discovery, scoped delegation, timeouts, idempotency"]]))
    parts.append(mod("m02", "02", "", "How a Solution Architect thinks about this", "\n".join(b)))

    b = []
    b.append(layer("What the SAP diagram shows"))
    b.append('<p>The reference architecture ("A2A and MCP for Interoperability") shows SAP Business AI Platform layers: Joule / Joule Studio / orchestrator, Agent Gateway, managed runtimes, MCP Builder, MCP + A2A fabrics, SAP Autonomous Suite, custom and bring-your-own agents, MCP Gateway, OData/REST services, Cloud Identity Services, third-party MCP servers/APIs, hyperscalers, external agents — with Trust, Authentication, Discovery and Governance as cross-cutting concerns.</p>')
    b.append(mermaid("FIG. 1 — REFERENCE MAP TRANSLATED TO OUR BUILD", """flowchart LR
  subgraph WE_BUILD["A. We build locally"]
    UI["UI5 app"] --> CAP["CAP services"]
    CAP --> PG["PostgreSQL"]
    CAP --> MCP["MCP server (13 tools)"]
    MCP --> GW["Gateway (learning)"]
    GW --> PA["Procurement Agent"]
    PA --> RA["Risk Agent"]
  end
  subgraph SAP_MANAGED["B. SAP-managed (BTP prod)"]
    AR["Approuter"] --- IAS["IAS and XSUAA"]
    HM["HANA Cloud"] --- EM["Event Mesh"]
    DST["Destination"] --- LOG["Logging + Monitoring"]
    AIC["AI Core / GenAI Hub"]
  end
  subgraph EXTERNAL["D. External"]
    XMCP["Third-party MCP"] --- XAPI["Third-party APIs"]
    XAG["External agents"]
  end
  PA --> AIC
  GW --> XMCP
  PA --> XAG
  CAP --> DST
  CAP --> EM
  UI --> AR
  AR --> CAP"""))
    b.append(table(["Box in SAP diagram", "What it is", "We implement?", "How we connect / protocol / auth"], [["Joule / Studio / Orchestrator", "SAP-managed agent runtime + UX", "No — simulate. Our orchestrator action plays the role locally", "Conceptual mapping; real integration later via AI Core"], ["Agent Gateway", "Single audited agent entry point", "Learning implementation in AgentService.orchestrate", "HTTPS + JWT; user identity propagated"], ["MCP Builder / MCP Gateway", "Tool registry, routing, policy", "Learning gateway (Express middleware)", "MCP JSON-RPC; OAuth; tool filtering per agent"], ["Custom / BYO agents", "Our specialist agents", "Yes: 7 agents in db.Agents + handlers", "A2A JSON tasks; agent IDs + grants"], ["OData / REST services", "Business APIs", "Yes: ProcurementService, Catalog, Supplier, Invoice, Approval", "OData V4 + REST; JWT scopes"], ["Cloud Identity Services", "Users, trust, tokens", "Simulated locally (x-mock-user); real IAS/XSUAA in prod", "OAuth2 JWT; xs-security.json scopes"], ["Third-party MCP / APIs / agents", "Outside world", "Mocked locally; Destination in prod", "Destination service + mTLS/OAuth"], ["HANA / Postgres", "System of record", "Postgres local; HANA Cloud prod", "CAP db layer; tenantId on every row"]]))
    b.append(callout("prod", "Learning vs production", "<p>Anything labelled <b>learning implementation</b> (gateway, orchestrator, mock LLM, mock destination, EventEmitter events) is explicitly a stand-in with the same interface as the SAP-managed service. The production notes in each phase say exactly what replaces it on BTP. Never present the stand-in as the SAP product.</p>"))
    b.append(callout("warn", "Accuracy rule", "<p>SAP BTP, CAP, MCP and A2A evolve fast. Where an API is version-dependent, the code carries a <b>VERIFY:</b> comment telling you to check current SAP docs instead of asserting a possibly-stale signature.</p>"))
    parts.append(mod("m03", "03", "", "Mapping the SAP A2A + MCP architecture to our build", "\n".join(b)))

    b = []
    b.append(layer("Prerequisites"))
    b.append(table(["Tool", "Version", "Check"], [["Node.js", ">= 20", "<code>node -v</code>"], ["CAP CLI", "latest (@sap/cds-dk)", "<code>cds --version</code>"], ["Git", "any", "<code>git --version</code>"], ["Docker", "any (for Postgres)", "<code>docker --version</code>"], ["PostgreSQL", "15+ via Docker", "<code>pg_isready</code> or Docker ps"], ["CF CLI", "v8 (deploy phases only)", "<code>cf --version</code>"], ["VS Code + REST client", "any", "Postman or .http files"]]))
    b.append(code("bash", "Install CLI + scaffold (run once)", "npm install -g @sap/cds-dk\ncds --version\ncds init enterprise-ai-procurement --cap-js\ncd enterprise-ai-procurement\nnpm install"))
    b.append(layer("Exact folder structure (this repo)"))
    b.append(code("text", "WHAT WE HAVE: repository layout", "enterprise-ai-procurement/\n  app/                  # UI5 frontend (Phase 21-22)\n  approuter/            # BTP approuter (Phase 32)\n  db/schema.cds         # domain model (Phase 5)\n  db/common.cds         # shared types/aspects\n  db/data/              # seed CSVs\n  srv/*-service.cds|ts  # Procurement, Catalog, Supplier, Invoice, Approval, MCP, Agent\n  srv/server.js         # CDS_TYPESCRIPT=true bootstrap (do not delete)\n  lib/auth|authorization|audit|validation|workflow|security/  # business plumbing\n  test/                 # vitest suites (Phase 26)\n  scripts/              # pg deploy helpers\n  mta.yaml xs-security.json Dockerfile docker-compose.yml"))
    b.append(table(["Path", "Purpose"], [["srv/server.js", "Sets CDS_TYPESCRIPT=true so .ts handlers resolve; app runs under tsx. Deleting it breaks handler resolution."], ["lib/*", "Business logic. Handlers call lib; MCP/agents never touch SQL."], ["xs-security.json", "Scopes + role templates + collections. Mirrors lib/auth/rbac.ts 1:1."], ["mta.yaml", "BTP deployment descriptor (Phase 32)."], ["docker-compose.yml", "Local Postgres + adminer (Phase 29)."]]))
    b.append(callout("mistake", "Gotcha: handler base class", "<p>Handlers MUST extend <code>cds.ApplicationService</code> — raw <code>cds.Service</code> has no CRUD executors: entity reads return empty and <code>after CREATE</code> receives <code>undefined</code>. Every <code>srv/*.ts</code> in this repo already does this.</p>"))
    b.append(qa([("cds command not found?", "Reinstall the CLI globally and reopen the terminal so npm's bin dir is on PATH. Then verify with cds --version."), ("Which files do I never invent?", "Entity/service names. Always verify with the compiled model (cds compile --to csn) before editing CDS or handlers.")]))
    parts.append(step_mod("m04", "04", "Phase 1 — Project setup", "WHAT WE HAVE BUILT SO FAR: empty repo. WHAT WE ARE ADDING NOW: toolchain + layout you will extend for 40 phases.", "\n".join(b)))

    return parts
