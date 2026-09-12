"""Portal part 3: s08 orchestrator + s09 runtimes + s10 Agent Gateway + s11 tools."""
from common import code, table, grid, steps, qa, quiz, mermaid
from ix import sec, off, con, ex, imp, QUIZ_BANK

Q = {q[0]: q for q in QUIZ_BANK}


def qx(qid):
    q = Q[qid]
    return quiz(q[0], q[1], q[2], q[3])


def build():
    parts = []

    b = []
    b.append(off(
"<p><b>Joule Orchestrator</b> (with the <b>Agent Harness</b>) plans multi-step work and runs it: it executes <b>Skills</b>, calls agents, and links outward over <b>A2A</b>. Four different verbs — do not merge them:</p>"
+ table(
["Verb", "Means", "Example"],
[
("Orchestration", "Decompose a goal, sequence the steps, join results", "Refund request becomes: check order, check policy, approve, notify"),
("Agent execution", "One agent reasoning toward its delegated task", "Order agent investigates the shipment"),
("Tool invocation", "Calling ONE capability with parameters", "getOrderStatus(orderId) via MCP"),
("Agent-to-agent communication", "Delegating/asking across agent boundaries", "Joule asks the order agent over A2A"),
]
)
))
    b.append(con("<p>Orchestra: the <b>orchestrator conducts</b>, <b>agents play instruments</b>, <b>tool calls are individual notes</b>, <b>A2A is one section cueing another</b>. Confusing conducting with playing is the root of most A2A/MCP mixups.</p>"))
    b.append(qx("xq06"))
    parts.append(sec("s08", "08", "Joule Orchestrator", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Managed Runtimes</b> host <b>Joule Agents, Custom Agents and MCP Servers</b> as separately deployed, versioned units. Runtime separation matters for three reasons: <b>isolation</b> (one crashing agent cannot take down others), <b>independent lifecycle</b> (update a tool server without redeploying agents), and <b>clear deployment ownership</b> (SAP runs these; customers run their BTP subaccount side).</p>"
))
    b.append(imp("<p>Deployment reading: an agent endpoint URL + version + identity = a runtime unit. If two things share all three, they are the same unit; if any differs, updating one must not silently change the other.</p>"))
    parts.append(sec("s09", "09", "Managed Runtimes", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Agent Gateway</b> exposes Joule Agents to the outside world as an <b>externally reachable A2A endpoint</b> — the <b>inbound</b> direction (external clients, third-party agents, partner systems and custom apps consuming SAP agents). Per SAP: <b>A2A 0.3.0 with HTTP+JSON transport</b>, <b>SAP-managed domain</b>, authentication via <b>IAS App2App tokens with named user context</b>, task submission confirmed synchronously with <b>asynchronous callback-based responses</b> for long executions. Callers address a capability + scenario; the gateway routes, authenticates and governs.</p>"
"<p>Discovery: external clients learn capabilities/scenarios from published metadata, then invoke. Invocation: A2A task with user context; result sync confirmation or async callback. Identity and trust ride IAS App2App on every call.</p>"
))
    b.append(table(
["", "Agent Gateway", "MCP Gateway"],
[
("Job", "Governed A2A entry/integration point for AGENTS", "Governed MCP tool exposure/consumption for TOOLS"),
("Direction", "Inbound: outside callers reach Joule agents", "Both: agents consume tools; customers expose APIs as tools"),
("Protocol", "A2A 0.3.0 HTTP+JSON", "MCP (JSON-RPC) over HTTPS"),
("Managed by", "SAP (managed domain)", "Customer (Integration Suite)"),
("Identity", "IAS App2App + named user", "OIDC + per-tool authorization"),
]
))
    b.append(con("<p>Airport vs seaport: both are guarded gates, but <b>planes (agents) never dock at piers (tool berths)</b>. Merging them in your head guarantees misconfigured security later.</p>"))
    b.append(qx("xq07"))
    parts.append(sec("s10", "10", "Agent Gateway", "\n".join(b)))

    b = []
    b.append(off(
"<p>The <b>Tools</b> area (with <b>Data, Products, Grounding, Knowledge Graph</b>) is the enterprise context agents act through. Why agents need it: models predict text; tools <b>execute capability</b> (check stock, post order) and data grounds answers in <b>authoritative facts</b> (Knowledge Graph semantics, product masters). Three distinct acts: <b>reasoning</b> (agent decides), <b>tool execution</b> (capability runs), <b>enterprise data</b> (facts consulted).</p>"
))
    b.append(qx("xq14"))
    parts.append(sec("s11", "11", "Tools", "\n".join(b)))

    return parts
