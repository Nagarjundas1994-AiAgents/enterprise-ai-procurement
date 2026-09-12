"""Part 1: hero + CH00-CH03."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done

HERO = '''<header class="hero" id="top">
  <div class="titleblock">
    <div class="tb-row"><span class="tb-k">Course</span><span class="tb-v">ASSETOPS-2026</span></div>
    <div class="tb-row"><span class="tb-k">Chapters</span><span class="tb-v">00-90</span></div>
    <div class="tb-row"><span class="tb-k">Stack</span><span class="tb-v">CAP + UI5 + PG</span></div>
    <div class="tb-row"><span class="tb-k">Domain</span><span class="tb-v">Maintenance</span></div>
  </div>
  <p class="kicker">Autonomous Asset Maintenance and Operations Control Tower</p>
  <h1>SAP CAP from Zero to Production</h1>
  <p class="sub">91 chapters. One factory story: <b>CNC-MACHINE-102</b> in the <b>Bangalore Manufacturing Plant</b> develops abnormal vibration. You build the system that detects it, investigates it with AI agents, gets human approval, and fixes it — then you ship that system to SAP BTP production.</p>
  <div class="statrow">
    <div class="stat"><b>91</b><span>chapters, 17 sections each</span></div>
    <div class="stat"><b>30</b><span>CDS entities, one domain</span></div>
    <div class="stat"><b>17</b><span>governed MCP tools</span></div>
    <div class="stat"><b>4</b><span>agents: maintenance + 3 specialists</span></div>
  </div>
  <p>Open this file in a browser and start at Chapter 00. Every chapter ends with a STOP checkpoint: what exists, how to run it, how to test it, what can go wrong. Environment labels: <span class="pill on">CURRENT SAP APPROACH</span> <span class="pill">LEGACY APPROACH</span> <span class="pill">LEARNING-MOCK APPROACH</span></p>
  <div class="callout concept"><h4>The rule of this course</h4><p>Agents never touch the database. They call <b>governed CAP services</b> through <b>MCP tools</b>, delegate through <b>A2A</b>, and stop at <b>human approval</b> for anything that moves money, metal, or people.</p></div>''' + mermaid(
    "FIG. 0 — WHERE WE END UP (EVERY ARROW EXPLAINED IN CH02 AND BUILT BY CH90)",
    """flowchart TD
  U["User"] --> F["UI5 app"]
  F --> AR["Approuter"]
  AR --> AU["Auth (IAS and XSUAA)"]
  AU --> CAP["CAP services"]
  CAP --> HANA["HANA Cloud"]
  CAP --> DST["Destination service"]
  DST --> EXT["External sensor API"]
  CAP --> EV["Events"]
  CAP --> AG["Maintenance Agent"]
  AG --> IA["Inventory Agent"]
  AG --> WA["Workforce Agent"]
  AG --> PA["Production Agent"]
  IA --> MCP["MCP tools"]
  WA --> MCP
  PA --> MCP
  MCP --> CAP""",
  ) + '''
  <div class="done-row"><label><input type="checkbox" data-done="m00"> Mark the introduction complete</label></div>
</header>'''


def build():
    parts = [HERO]

    parts.append(ch("c00", "00", "Chapter 00 — Prerequisites and Development Environment", "", {
        "What are we learning?": "<p><b>Simple:</b> which tools you need on your Windows PC before writing a line of code. <b>Enterprise:</b> the standard CAP developer workstation (Node 20+, CAP CLI, VS Code, Git, Docker, CF CLI). <b>Example:</b> like a mechanic laying out tools before opening the machine — miss one and you stop mid-job.</p>",
        "Why is this important?": "<p>Every later chapter assumes these exact tools. A wrong Node version causes cryptic build errors in Chapter 04 that look like CAP bugs but are environment bugs.</p>",
        "Where does this fit in the architecture?": "<p>Nowhere in the runtime — this is the factory floor where you build everything else (Chapters 04-90).</p>",
        "Prerequisites": "<p>Windows 10/11, admin rights to install software, internet access.</p>",
        "Folder/file changes": "<p>None yet. We only install tools in this chapter.</p>",
        "Exact commands": PWR + code("powershell", "Install + verify (run each, confirm output)", "node -v          # want v20 or higher\nnpm -v           # want 10 or higher\nnpm install -g @sap/cds-dk\ncds --version    # proves the CAP CLI works\ngit --version\ndocker --version   # needed from Chapter 17\ncf --version       # needed from Chapter 73; install CF CLI v8 if missing\ncds --help | Select-Object -First 5"),
        "Complete code": "<p>No code in this chapter — tooling only. Your first code lands in Chapter 04.</p>",
        "Explanation of every important line": table(["Command", "What it does"], [["node -v", "Checks the JavaScript runtime CAP runs on"], ["npm install -g @sap/cds-dk", "Installs the CAP compiler + generators globally"], ["cds --version", "Smoke test: CLI loads without errors"], ["cf --version", "Cloud Foundry CLI for Chapters 73-90"]]),
        "Expected output": code("text", "Healthy workstation", "v20.x.x\n10.x.x\n@sap/cds-dk 8.x\ncf version 8.x"),
        "How to test it": std_test("re-run every version command in a NEW terminal (PATH updates need a fresh shell)."),
        "Negative test cases": neg([["Node 16 installed", "node -v", "Upgrade: Chapters 04+ fail on modern syntax"], ["cds not found", "cds --version", "Reinstall CLI, reopen terminal"]]),
        "Common mistakes": "<p>Installing the CLI with an old npm cache (run <code>npm cache clean --force</code>), or verifying in the same terminal that installed it.</p>",
        "How to troubleshoot": "<p><code>npm list -g --depth=0</code> shows what is really installed. Corporate proxy errors need <code>npm config set proxy</code> — ask your IT for the proxy URL.</p>",
        "Production considerations": "<p>Pin versions per developer (<code>.nvmrc</code> / <code>engines</code> in package.json, Chapter 04) so builds are reproducible.</p>",
        "Security considerations": "<p>Never run installs as Administrator unless required; prefer user scope. Verify installer signatures on shared machines.</p>",
        "What we have completed": "<p>A verified workstation. Nothing built yet — correctly.</p>",
        "What comes next": "<p>Chapter 01: the factory story and the machine we are saving.</p>",
    }))

    parts.append(ch("c01", "01", "Chapter 01 — What Are We Building?", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> the product in one story — a vibrating CNC machine and the crew that fixes it. <b>Enterprise:</b> an asset-maintenance control tower: master data (plants, lines, equipment, sensors, technicians, spares), documents (alerts, orders, assignments, schedules), intelligence (agents, tools, recommendations), governance (audit, approvals).</p>",
        "Why is this important?": "<p>Every entity, screen, tool and agent in Chapters 07-54 exists to serve this story. When lost, return here.</p>",
        "Where does this fit in the architecture?": "<p>This chapter is the map legend for the FIG. 0 poster: USER → UI5 → CAP → HANA, with agents on the side.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>None. Reading + orientation only.</p>",
        "Exact commands": "<p>None. From Chapter 04 every command runs in <code>C:\\Projects\\autonomous-maintenance</code>.</p>",
        "Complete code": '<div class="chat"><div class="msg user"><p class="who">Alert</p><p>CNC-MACHINE-102 · Abnormal Vibration · HIGH · Bangalore Manufacturing Plant</p></div><div class="msg user"><p class="who">User asks</p><p>Investigate this machine and recommend what maintenance action we should take.</p></div><div class="msg ai"><p class="who">System (by Chapter 89)</p><p>Bearing failure likely (87%). Spare in stock. Technician Ravi Kumar free on night shift. Line 3 free 22:00-02:00. Approve: create order + reserve part + assign + schedule?</p></div></div>',
        "Explanation of every important line": "<p>The alert carries <b>equipment + symptom + severity + plant</b> — the four facts every downstream step (tools, agents, approval, audit) reuses.</p>",
        "Expected output": "<p>You can retell the story in one minute: alert → investigate → recommend → approve → execute → audit.</p>",
        "How to test it": std_test("explain the story to a colleague without notes."),
        "Negative test cases": neg([["Wrong domain", "Build procurement instead", "Chapters 07+ entities will not match — stay in maintenance"]]),
        "Common mistakes": "<p>Skipping this chapter and modeling entities without the story — you get tables nobody queries.</p>",
        "How to troubleshoot": "<p>Confused later? Re-read the chat above, then check the chapter's architecture pointer.</p>",
        "Production considerations": "<p>The scenario doubles as the UAT script in Chapter 89 — same machine, same alert, same acceptance bar.</p>",
        "Security considerations": "<p>Note the sensitivity early: vibration data + schedules + technician identities are need-to-know (Chapters 34-36).</p>",
        "What we have completed": "<p>Shared vocabulary: plant, line, equipment, sensor, alert, order, technician, spare, schedule, agent, tool, approval, audit.</p>",
        "What comes next": "<p>Chapter 02: decode the SAP A2A+MCP reference diagram box by box.</p>",
    }))

    parts.append(ch("c02", "02", "Chapter 02 — Understanding the SAP Architecture Diagram", "", {
        "What are we learning?": "<p><b>Simple:</b> read the reference poster like a subway map. <b>Enterprise:</b> map SAP Business AI Platform concepts (Joule, orchestrator, Agent Gateway, MCP Builder, MCP/A2A fabrics, Identity Services, hyperscalers) to our build-vs-buy split. <b>Example:</b> Joule is SAP's train; we build a compatible station, not our own train.</p>",
        "Why is this important?": "<p>Prevents the two classic failures: rebuilding SAP products locally, or treating mocks as production.</p>",
        "Where does this fit in the architecture?": "<p>This chapter labels every box of FIG. 0 with an owner: SAP-managed, we-build, or mock-now.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>None. Conceptual chapter.</p>",
        "Exact commands": "<p>None.</p>",
        "Complete code": table(["Diagram box", "Owner", "Our counterpart"], [["Joule / Studio / Orchestrator", "SAP-managed", "Our orchestrate action (LEARNING-MOCK APPROACH)"], ["Agent Gateway", "SAP-managed in prod", "Express auth + tool filter (LEARNING-MOCK APPROACH)"], ["MCP Builder / Gateway", "SAP-managed in prod", "13-17 governed tools on MCPService"], ["Custom / BYO agents", "We build", "4 agents in AgentService (Chapters 41, 47-49)"], ["OData / REST", "We build", "6 CAP services (Chapter 10)"], ["Identity Services", "SAP-managed in prod", "Mock headers local; IAS/XSUAA in prod (34-36)"], ["Third-party MCP/APIs/agents", "External", "Mock sensor API local; Destination in prod (37-38)"], ["HANA / Postgres", "We configure", "Postgres local (17); HANA Cloud prod (18, 76)"]]),
        "Explanation of every important line": "<p>Owner column is the whole point: <b>CURRENT SAP APPROACH</b> where SAP owns it, <b>LEARNING-MOCK APPROACH</b> where we simulate with the same interface.</p>",
        "Expected output": "<p>You can point at any FIG. 0 box and state its owner and our counterpart.</p>",
        "How to test it": std_test("cover the Owner column and recite it from the diagram alone."),
        "Negative test cases": neg([["Claim mock gateway IS SAP gateway", "Deploy review", "Rejected: mocks are labelled LEARNING-MOCK everywhere"]]),
        "Common mistakes": "<p>Assuming Joule is downloadable software. It is a managed BTP capability — we integrate, not install.</p>",
        "How to troubleshoot": "<p>Version drift: SAP docs beat this course. Anything marked VERIFY wins over memory.</p>",
        "Production considerations": "<p>Every LEARNING-MOCK has a production owner named in Chapters 73-78 — no orphan mocks reach prod.</p>",
        "Security considerations": "<p>Trust, Authentication, Discovery, Governance cut across ALL boxes — they become Chapters 34-36 and 50-52.</p>",
        "What we have completed": "<p>A labeled map. Chapters 04+ color it in, one box at a time.</p>",
        "What comes next": "<p>Chapter 03: the engineering fundamentals underneath the map.</p>",
    }))

    parts.append(ch("c03", "03", "Chapter 03 — Enterprise Application Architecture Fundamentals", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> client vs server, HTTP verbs, JSON, databases, layers. <b>Enterprise:</b> why UI → API → service → DB layering lets 4 agents share one governed core. <b>Example:</b> ordering food — menu (API), kitchen (service), pantry (DB); agents are waiters, never cooks.</p>",
        "Why is this important?": "<p>Chapters 10-16 translate these five ideas into CAP code. Without them, handlers look like magic.</p>",
        "Where does this fit in the architecture?": "<p>Horizontal foundation under every vertical box in FIG. 0.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>None. Conceptual + one paper exercise.</p>",
        "Exact commands": "<p>None. Draw the layer stack on paper: UI5 → OData/REST → CAP handlers → lib → DB.</p>",
        "Complete code": mermaid("FIG. 1 — LAYER STACK WE BUILD ALL COURSE", """flowchart TD
  UI["UI5 browser app"] --> HTTP["HTTP + OData V4 + JSON"]
  HTTP --> CAP["CAP services (auth, validation, tx)"]
  CAP --> LIB["lib: pure business logic"]
  LIB --> DB["PostgreSQL local, HANA prod"]""") + grid([("HTTP verbs", "GET reads, POST creates, PATCH updates, DELETE removes — Chapters 11-12."), ("JSON", "The envelope every layer speaks — Chapter 12."), ("Layering", "UI never touches DB; agents never touch DB — Chapters 40-41."), ("Stateless API", "Every request carries identity; server keeps no session — Chapters 34-36.")], 2),
        "Explanation of every important line": "<p>Arrow direction = dependency direction. Nothing bypasses its lower layer — the rule Chapters 45 and 52 enforce for agents.</p>",
        "Expected output": "<p>Your paper stack matches FIG. 1, and you can place any Chapter 10-16 concept on it.</p>",
        "How to test it": std_test("place each term (OData, handler, lib, Postgres) on your paper stack."),
        "Negative test cases": neg([["UI calls DB directly", "Architecture review", "Rejected: bypasses auth + audit"]]),
        "Common mistakes": "<p>Confusing REST (style) with OData (typed protocol) — Chapter 12 separates them.</p>",
        "How to troubleshoot": "<p>Stuck on a later error? Identify which layer it belongs to first, then open that chapter.</p>",
        "Production considerations": "<p>Layers map to independently scalable BTP modules in mta.yaml (Chapter 74).</p>",
        "Security considerations": "<p>Trust boundaries sit BETWEEN layers — each crossing re-authenticates (Chapters 34, 51).</p>",
        "What we have completed": "<p>Mental scaffolding. STOP: can you draw FIG. 1 from memory? If not, re-read before Chapter 04.</p>",
        "What comes next": "<p>Chapter 04: scaffold the real project from an empty directory.</p>",
    }))

    return parts
