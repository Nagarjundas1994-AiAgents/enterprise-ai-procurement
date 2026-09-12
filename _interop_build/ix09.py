"""Portal part 9: s30 beginner summary + s31 cheat sheet."""
from common import code, table, grid, steps, qa, quiz, mermaid
from ix import sec, off, con, ex, imp


def build():
    parts = []

    b = []
    b.append(con("<p>Climb in order — each level unlocks the next.</p>"))
    b.append(steps([
"<b>Agent:</b> a system acting toward goals with some autonomy.",
"<b>Tool:</b> a callable capability with inputs and outputs.",
"<b>MCP:</b> the standard menu + ordering protocol for tools.",
"<b>A2A:</b> the standard referral + delegation protocol between agents.",
"<b>Identity:</b> IAS-backed who-is-who for users, agents, services.",
"<b>Governance:</b> discovery, permissioning, lifecycle, audit.",
"<b>BTP:</b> your fenced area: subaccount, agents, gateway, APIs.",
"<b>Agent Gateway:</b> the governed inbound A2A door.",
"<b>MCP Gateway:</b> the governed tool counter.",
"<b>Enterprise agent architecture:</b> all of the above, traced end to end.",
]))
    b.append(ex(
"<p><b>Educational example 1 — Manufacturing Equipment Maintenance</b> (illustrates the architecture): a factory manager asks <i>Which production machine is at highest maintenance risk?</i> USER → APPLICATION/JOULE → AGENT → MCP TOOLS → EQUIPMENT DATA → ANALYSIS → RESULT. Multi-agent version: Maintenance Agent —A2A→ Inventory Agent —MCP→ Inventory Tool (A2A = delegation, MCP = capability).</p>"
"<p><b>Educational example 2 — Customer Service:</b> Customer Service Agent —A2A→ Order Agent —MCP→ SAP Order API. Same split, different domain.</p>"
))
    b.append(off(
"<p><b>60 seconds:</b> SAP connects agents and tools with two open standards — A2A lets agents collaborate across vendors, MCP lets any agent use governed tools over existing APIs — fronted by two gateways and anchored in IAS identity, with some capabilities still arriving.</p>"
"<p><b>5 minutes:</b> add: Joule as A2A client outbound and agent host inbound; MCP Gateway (customer, Integration Suite) vs internal MCP consumption (Knowledge Graph, business APIs); BYOA mechanics (message/send, 60s sync, webhook push, App2App trust); discovery-governance pairing; the six-step simplified flow.</p>"
"<p><b>To an architect:</b> add: A2A 0.3.0 HTTP+JSON with named-user App2App tokens and callback semantics; OIDC/rate-limit/payload/tracing posture of the MCP Gateway; trust establishment vs per-call validation vs authorization as distinct controls; transitional-state scoping (bidirectional Gateway pending); related RA (Joule Studio, BYOA, Agent Identity, Third-Party MCP Access) and sample repos (btp-joule-a2a-pro-code-agent, joule-a2a-agent-toolkit) as implementation on-ramps — all verified against current docs before commitment.</p>"
))
    b.append(off(
"<p><b>If you remember only 10 things:</b> 1. Agents reason and act toward goals. 2. Tools provide capabilities. 3. MCP standardizes agent/tool interaction. 4. A2A standardizes agent-to-agent collaboration. 5. A2A and MCP are complementary. 6. Agent Gateway and MCP Gateway serve different roles. 7. Authentication identifies the caller. 8. Authorization determines what the caller may do. 9. Trust establishes a security relationship; it does not mean unrestricted permission. 10. Enterprise agent architectures require interoperability, governance and security.</p>"
))
    parts.append(sec("s30", "30", "Beginner Summary", "\n".join(b)))

    b = []
    b.append(table(
["Term", "One line"],
[
("A2A", "Agent ↔ Agent collaboration and delegation"),
("MCP", "Agent ↔ Tool/Resource discovery and invocation"),
("Agent Gateway", "Governed A2A entry/integration point (inbound)"),
("MCP Gateway", "Governed MCP tool exposure/consumption (Integration Suite)"),
("BTP", "Customer-managed cloud platform area (subaccount)"),
("Cloud Identity Services", "Identity/trust layer (IAS, App2App, user context)"),
("Joule", "SAP conversational/agent experience + orchestration context; A2A client outbound"),
("MCP Server", "Exposes tools/resources via manifest"),
("Agent", "Reasons and performs tasks using capabilities"),
("Tool", "Executes a specific capability"),
]
))
    b.append(con(
"<p><b>Visual legend (SAP diagram semantics):</b> <b>Blue</b> — SAP platform/Joule surfaces. <b>Purple</b> — A2A agent links. <b>Green</b> — Trust relationships. <b>Magenta</b> — highlighted integration points (verify against legend in the official SVG). <b>Teal</b> — MCP tool links. <b>Gray</b> — neutral structure. Labels to look for: <b>A2A, MCP, Trust, Authenticate, Discover and Govern, OData/REST</b>. Never rely on color alone — every edge also carries a text label.</p>"
"<p><b>Memory trick:</b> A2A — <b>ASK ANOTHER AGENT</b>. MCP — <b>USE A TOOL</b>.</p>"
))
    b.append(imp("<p>Print this section: it is designed to stand alone as a one-page handout.</p>"))
    parts.append(sec("s31", "31", "Architecture Cheat Sheet", "\n".join(b)))

    return parts
