"""Portal part 10: s32 FAQ (19 confusions, resolved)."""
from common import code, table, grid, steps, qa, quiz, mermaid
from ix import sec, off, con, ex, imp


def build():
    parts = []

    b = []
    b.append(off("<p>Short answers first; each points back to its full section.</p>"))
    b.append(qa([
("Is MCP the same as A2A?", "No. MCP = agent-to-tool; A2A = agent-to-agent. Complementary (Section 26). [OFFICIAL distinction]"),
("Does A2A call APIs?", "Only indirectly — an agent reached via A2A may itself call tools/APIs over MCP. A2A carries tasks, not API payloads. [CONCEPTUAL]"),
("Does MCP replace REST?", "No. MCP fronts REST (and OData, functions) with a uniform tool interface; the APIs stay and execute. [OFFICIAL]"),
("Does MCP replace OData?", "No — same answer, SAP-API flavored. The diagram shows ODATA/REST beneath MCP deliberately. [OFFICIAL]"),
("Is an MCP server an AI agent?", "No. Servers expose capabilities; agents reason and act. A system can host both roles, but the roles differ. [CONCEPTUAL]"),
("Is an AI agent an MCP server?", "Not by being an agent — though an agent system MAY also expose tools. Judge by role, not by box. [CONCEPTUAL]"),
("Is Agent Gateway the same as MCP Gateway?", "No. A2A door for agents (SAP-managed, inbound) vs MCP tool counter (customer-managed, Integration Suite). [OFFICIAL]"),
("Is discovery the same as authorization?", "No. Discovery lists what exists; authorization decides what you may use. Reading the menu never orders the dish. [OFFICIAL pairing, explained]"),
("Is authentication the same as authorization?", "No. Who-are-you vs what-may-you-do; 401 vs 403. Applies to users, agents, servers, callers. [CONCEPTUAL + standard]"),
("Does BTP automatically provide an AI agent?", "No. BTP provides the platform (subaccount, services); agents are built/deployed/integrated — Joule, custom, or third-party. [CONCEPTUAL]"),
("Can an agent directly access HANA?", "Not in this architecture — agents reach data through governed tools/services, with identity and authorization at each step. [ARCHITECTURE reading]"),
("Where does the LLM actually run?", "Inside agent runtimes (SAP-managed for Joule/custom-runtime agents; vendor runtimes for third-party agents) — the diagram shows placement, not model weights. [ARCHITECTURE reading]"),
("Where does the business data live?", "In enterprise systems behind APIs (and Knowledge Graph for semantics) — reached via MCP tools, never shipped into the diagram. [OFFICIAL]"),
("Who owns the MCP server?", "Depends which: SAP runs internal ones; customers run theirs (often via MCP Gateway); vendors run third-party ones. Ownership follows the zone. [OFFICIAL]"),
("Who owns the agent?", "Same zone rule: SAP (Joule), customer (custom/BYOA), vendor (third-party). [OFFICIAL]"),
("Can third-party agents communicate with SAP?", "Yes — over open A2A with IAS App2App trust; inbound via Agent Gateway, outbound via BYOA. Note the transitional-state caveat for full bidirectional Gateway support. [OFFICIAL + availability note]"),
("Why is A2A used between agents?", "Because delegation across independent, vendor-diverse agents needs one contract for tasks, capabilities and structured messages. [OFFICIAL]"),
("Why is MCP used between agents and tools?", "Because tools need one discoverable, versionable, implementation-hiding interface instead of N bespoke integrations. [OFFICIAL]"),
("If I remember one sentence?", "A2A asks another agent; MCP uses a tool; gateways govern each; IAS proves who is asking — and some boxes are still arriving, so verify docs before building. [SUMMARY]"),
]))
    parts.append(sec("s32", "32", "FAQ", "\n".join(b)))

    parts.append(
'<div id="pnnav" style="position:fixed;right:14px;bottom:14px;z-index:60;display:flex;gap:.4rem">'
'<button type="button" id="pnprev" class="iconbtn">Previous</button>'
'<button type="button" id="pnnext" class="iconbtn">Next</button>'
'</div>'
'<script>(function(){'
'function order(){return Array.from(document.querySelectorAll("#sidenav a[href^=\\"#\\"]")).map(function(a){return a.getAttribute("href");});}'
'function cur(){var h=location.hash||"#top";var o=order();return o.indexOf(h);}'
'function go(d){var o=order();var i=cur();if(i<0)i=0;var n=Math.min(o.length-1,Math.max(0,i+d));if(o[n])location.hash=o[n];}'
'var p=document.getElementById("pnprev"),n=document.getElementById("pnnext");'
'if(p&&n){p.onclick=function(){go(-1);};n.onclick=function(){go(1);};}'
'})();</script>'
)

    return parts
