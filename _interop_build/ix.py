"""Helpers for the A2A+MCP interop portal: source labels, quiz bank, flow steps."""
from common import mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth

SRC = "https://architecture.learning.sap.com/docs/ref-arch/76ec36"

def off(body):
    return '<p><span class="badge ga">OFFICIAL SAP ARCHITECTURE</span></p>' + body

def con(body):
    return '<p><span class="badge beta">CONCEPTUAL EXPLANATION</span></p>' + body

def ex(body):
    return '<p><span class="badge verify">EXAMPLE</span></p>' + body

def imp(body):
    return '<p><span class="badge verify">IMPLEMENTATION NOTE</span></p>' + body

def srcbox():
    return ('<p class="mode-note" style="border:1px solid var(--line);border-radius:8px;padding:.6rem .8rem">'
            'Primary source: SAP Architecture Center, <a href="' + SRC + '" target="_blank" rel="noopener">'
            'A2A and MCP for Interoperability (RA0029)</a>, last updated Aug 27, 2026. '
            'Open standards: <a href="https://a2a-protocol.org/latest/" target="_blank" rel="noopener">A2A</a>, '
            '<a href="https://modelcontextprotocol.io/" target="_blank" rel="noopener">MCP</a>.</p>')

def sec(mid, num, title, body):
    return mod(mid, num, "", title, srcbox() + "\n" + body)

FLOW11 = [
    ("User asks Joule", "A person types a business question into Joule or an app.", "UI / chat", "User SSO via IAS"),
    ("Joule picks a specialist", "Orchestration decides a remote agent owns this task.", "Internal routing", "User context carried"),
    ("Joule calls the agent (A2A)", "Joule as A2A client sends message/send to the remote A2A server.", "A2A 0.3.0 HTTP+JSON", "IAS App2App trust"),
    ("Agent reasons, needs data", "The remote agent plans and finds it needs a business capability.", "Agent-internal", "Agent identity"),
    ("Agent discovers MCP tools", "It queries MCP servers for tool manifests matching the need.", "MCP tools/list", "Agent auth to gateway"),
    ("Agent invokes the tool", "It calls the chosen tool with structured parameters.", "MCP tools/call (JSON-RPC)", "Tool-level authZ"),
    ("MCP server runs the API", "The server executes the underlying OData/REST API or integration flow.", "OData/REST, HTTPS", "Service credentials"),
    ("Tool result returns", "Structured output flows back to the agent.", "MCP result", "Logged + traced"),
    ("Agent reasons over result", "The agent completes its task and formulates an answer.", "Agent-internal", "Audit row"),
    ("A2A response to Joule", "The remote agent replies; sync (<60s) or async push to Joule webhook.", "A2A response / webhook", "IAS trust validated"),
    ("Joule answers the user", "Joule presents the result in the conversation.", "UI / chat", "User session"),
]

QUIZ_BANK = [
    ("xq01", "Which protocol is primarily intended for agent-to-agent collaboration?", [("REST", False), ("OData", False), ("A2A", True), ("MCP", False)], "A2A standardizes task delegation and messaging between independent agents (SAP source: A2A section)."),
    ("xq02", "What does an agent use MCP for?", [("Talking to other agents", False), ("Discovering and calling tools/resources", True), ("Logging users in", False), ("Storing passwords", False)], "MCP standardizes how agents discover tool manifests and invoke tools (SAP source: MCP section)."),
    ("xq03", "Agent Gateway vs MCP Gateway: which statement is correct?", [("They are the same thing", False), ("Agent Gateway = governed A2A entry for agents; MCP Gateway = governed MCP tool exposure", True), ("MCP Gateway replaces Agent Gateway", False), ("Neither uses authentication", False)], "SAP defines them as complementary: A2A collaboration vs MCP tool lifecycle (SAP source: both gateway sections)."),
    ("xq04", "Joule in the A2A pattern is…", [("Always the server", False), ("An A2A client calling remote A2A servers (outbound), and exposing agents inbound via Agent Gateway", True), ("A database", False), ("An MCP server only", False)], "Outbound Joule calls external A2A servers; inbound external clients call Joule agents through Agent Gateway."),
    ("xq05", "Does MCP replace OData/REST?", [("Yes, delete all APIs", False), ("No — MCP provides an agent-friendly tool interface OVER existing APIs", True), ("Only on Tuesdays", False), ("MCP and OData cannot coexist", False)], "SAP: tools abstract REST/OData/functions behind a uniform interface; the APIs stay."),
    ("xq06", "Is an MCP server an AI agent?", [("Yes, identical", False), ("No — a server exposes tools; an agent reasons and acts using capabilities", True), ("Only on SAP BTP", False), ("Only for finance", False)], "Reasoning vs capability: different roles, complementary."),
    ("xq07", "Discovery vs authorization:", [("Finding a tool means you may call it", False), ("Discovery lists capabilities; authorization separately decides permission", True), ("Authorization is automatic", False), ("Discovery requires admin rights", False)], "SAP governance: Discover and Govern are paired but distinct."),
    ("xq08", "Authentication vs authorization:", [("Same thing", False), ("Authentication = who are you; Authorization = what may you do", True), ("Authorization happens first", False), ("Agents skip both", False)], "Identity, then permission — for users, agents, servers and callers alike."),
    ("xq09", "Inbound vs outbound A2A:", [("Inbound = external callers reach Joule agents via Agent Gateway; Outbound = Joule (BYOA) calls external agents", True), ("There is only inbound", False), ("Outbound means offline", False), ("Both bypass identity", False)], "SAP supports both directions; each has its own trust setup."),
    ("xq10", "Where does product trust come from?", [("The diagram colors", False), ("IAS-issued tokens validated at each boundary (App2App, user context)", True), ("IP addresses only", False), ("Trust is implied by A2A", False)], "Trust = issued token + validation + scoped permission, never color or implication."),
    ("xq11", "A2A 0.3.0 transport per the reference architecture:", [("SMTP", False), ("HTTP+JSON", True), ("Carrier pigeon", False), ("FTP", False)], "Agent Gateway: A2A 0.3.0 with HTTP+JSON transport."),
    ("xq12", "Joule outbound sync expectation:", [("No limit", False), ("Response within 60 seconds; longer tasks use async push", True), ("5 milliseconds", False), ("Only batch", False)], "BYOA: 60s sync window, webhook push for long tasks."),
    ("xq13", "Who manages the MCP Gateway?", [("SAP exclusively", False), ("The customer, in SAP Integration Suite", True), ("Google", False), ("Nobody", False)], "SAP source: customer-managed platform for governed tool exposure."),
    ("xq14", "Can an agent directly access HANA?", [("Yes, always", False), ("Only through governed tools/services — never a raw direct path in this architecture", True), ("Only on weekends", False), ("HANA calls agents instead", False)], "Agents reach data via MCP tools over APIs, with auth and governance."),
    ("xq15", "Why do Google/Azure/AWS/IBM appear in the diagram?", [("SAP owns them", False), ("Interoperability: agents built on different clouds collaborate via open A2A", True), ("Decoration", False), ("They replace BTP", False)], "Open standards exist so vendor-diverse agents interoperate; presence is not a turnkey guarantee."),
    ("xq16", "Which TWO gateways does SAP recommend, and for what?", [("Two firewalls", False), ("Agent Gateway (A2A multi-agent collaboration) + MCP Gateway in Integration Suite (governed tool exposure)", True), ("Joule + HANA", False), ("OAuth + SAML", False)], "SAP source: two complementary governed approaches."),
]
