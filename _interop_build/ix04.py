"""Portal part 4: s12 MCP + s13 MCP Gateway + s14 A2A."""
from common import code, table, grid, steps, qa, quiz, mermaid
from ix import sec, off, con, ex, imp, QUIZ_BANK

Q = {q[0]: q for q in QUIZ_BANK}


def qx(qid):
    q = Q[qid]
    return quiz(q[0], q[1], q[2], q[3])


def build():
    parts = []

    b = []
    b.append(con("<p><b>Without MCP</b>, every agent hand-wires every system. <b>With MCP</b>, systems publish one standard menu; any agent reads it.</p>"))
    b.append(mermaid(
"WITHOUT MCP: N AGENTS TIMES M SYSTEMS",
"flowchart TD\n  A[Agent] -->|custom integration| S1[System 1]\n  A -->|custom integration| S2[System 2]\n  A -->|custom integration| S3[System 3]"
))
    b.append(mermaid(
"WITH MCP: ONE MENU, MANY DISHES",
"flowchart TD\n  A[Agent] --> M[MCP]\n  M --> T1[Tool A]\n  M --> T2[Tool B]\n  M --> T3[Tool C]"
))
    b.append(off(
"<p><b>MCP (Model Context Protocol)</b> defines how agents <b>discover</b> (manifest with tool descriptions + input/output schemas), <b>understand</b> (uniform call/result format hiding REST/OData/function specifics) and <b>invoke</b> external tools and context. <b>Decoupling</b> lets tools version and deploy independently of agents. At SAP, MCP gives Joule Agents semantically enriched access to business capabilities and Knowledge Graph content.</p>"
"<p><b>MCP Server:</b> hosts the manifest + executes tools. <b>Discovery:</b> agent reads tools/list. <b>Call:</b> agent sends tools/call with parameters, receives structured output.</p>"
))
    b.append(ex(
"<p><b>Conceptual example</b> (teaching aid, not from SAP): tool <code>getCustomerOrders</code>, input <code>{customerId: 'C-1024'}</code>, output <code>{orders: [...]}</code>. The agent never learns the underlying API — only the manifest.</p>"
))
    b.append(code("json", "EXAMPLE: conceptual MCP tools/call (JSON-RPC shape)", '{\n  "jsonrpc": "2.0",\n  "id": 7,\n  "method": "tools/call",\n  "params": { "name": "getCustomerOrders", "arguments": { "customerId": "C-1024" } }\n}'))
    b.append(off(
"<p><b>OData/REST underneath:</b> the diagram shows ODATA/REST below MCP because <b>MCP does not replace APIs</b> — it is an agent-friendly standardized interface OVER them:</p>"
))
    b.append(mermaid(
"MCP OVER APIS, NOT INSTEAD OF THEM",
"flowchart TD\n  AG[AI Agent] --> M[MCP]\n  M --> G[MCP Gateway]\n  G --> O[OData and REST]\n  O --> E[Enterprise API]"
))
    b.append(qx("xq02"))
    b.append(qx("xq05"))
    parts.append(sec("s12", "12", "MCP", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>MCP Gateway in SAP Integration Suite</b> is the <b>customer-managed</b> platform for governed, enterprise-grade exposure AND consumption of tools — SAP APIs, third-party APIs, external MCP servers, integration flows and data sources, all as MCP-compliant tools behind one entry point. This is <b>distinct from SAP&apos;s internal MCP use</b> (Joule consuming Knowledge Graph/business capabilities directly).</p>"
+ table(
["Gateway duty", "What it means"],
[
("Tool lifecycle", "Create MCP servers from existing APIs/integrations; document and enrich; publish; retire"),
("Authentication / authorization", "OIDC-based, per-tool, regardless of underlying source"),
("Rate limiting + traffic management", "Quotas and shaping so one agent cannot starve others"),
("Payload protection", "Size/shape inspection against malicious or leaking payloads"),
("Monitoring, tracing, analytics", "Who called which tool, when, how long — adoption and compliance evidence"),
("Governance", "One policy point for the whole customer tool landscape"),
]
)
))
    b.append(imp("<p>Build-versus-buy reading: you do not hand-roll auth, throttling or audit per tool — the gateway owns them once, every tool inherits them.</p>"))
    b.append(qx("xq16"))
    b.append(qx("xq03"))
    parts.append(sec("s13", "13", "MCP Gateway", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>A2A (Agent2Agent)</b> is the open standard for collaboration between autonomous agents: <b>delegate tasks</b>, <b>inquire capabilities</b>, <b>exchange structured information</b> across vendors and frameworks. SAP uses it as the <b>preferred standard for external interoperability</b> (multi-agent collaboration, vendor-to-vendor), while MCP enriches agents internally.</p>"
))
    b.append(mermaid("ONE DELEGATION", "flowchart TD\n  A[Agent A] -->|task| B[Agent B]"))
    b.append(mermaid("FAN-OUT", "flowchart TD\n  A[Agent A] --> B[Agent B]\n  A --> C[Agent C]\n  A --> D[Agent D]"))
    b.append(con("<p>Concepts: <b>task</b> (unit of delegated work), <b>capabilities</b> (what an agent advertises), <b>discovery</b> (learning what exists), <b>structured messages</b> (machine-readable requests/responses), <b>multi-agent workflows</b> (orchestrated specialists), <b>interoperability</b> (different frameworks, one contract).</p>"))
    b.append(code("json", "EXAMPLE: conceptual A2A message/send (shape per A2A 0.3.0 pattern)", '{\n  "jsonrpc": "2.0",\n  "id": 3,\n  "method": "message/send",\n  "params": { "message": { "role": "user", "parts": [{ "kind": "text", "text": "Check order O-9918 status" }] } }\n}'))
    parts.append(sec("s14", "14", "A2A", "\n".join(b)))

    return parts
