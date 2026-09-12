"""Portal part 1: hero + s01 glance + s02 original diagram + s03 reading guide."""
import io
import os
from common import code, table, grid, steps, qa, quiz, mermaid
from ix import sec, off, con, ex, imp, srcbox, FLOW11

HERE = os.path.dirname(os.path.abspath(__file__))
SAP_SVG = io.open(os.path.join(HERE, "sap_svg_inline.frag"), encoding="utf-8").read()

HERO = (
'<header class="hero" id="top">'
'<div class="titleblock">'
'<div class="tb-row"><span class="tb-k">Source</span><span class="tb-v">SAP RA0029</span></div>'
'<div class="tb-row"><span class="tb-k">Updated</span><span class="tb-v">2026-08-27</span></div>'
'<div class="tb-row"><span class="tb-k">Protocols</span><span class="tb-v">A2A + MCP</span></div>'
'<div class="tb-row"><span class="tb-k">Sections</span><span class="tb-v">32</span></div>'
'</div>'
'<p class="kicker">A2A and MCP for Interoperability — Understanding SAP&apos;s Agentic AI Interoperability Architecture</p>'
'<h1>A2A + MCP</h1>'
'<p class="sub">How AI agents, tools and enterprise systems communicate — the official SAP reference architecture (RA0029), explained box by box for beginners. Based on the official SAP Architecture Center page; SAP&apos;s words stay SAP&apos;s words.</p>'
'<div class="statrow">'
'<div class="stat"><b>A2A</b><span>Agent to Agent collaboration</span></div>'
'<div class="stat"><b>MCP</b><span>Agent to Tool interaction</span></div>'
'<div class="stat"><b>2</b><span>gateways, different jobs</span></div>'
'<div class="stat"><b>7</b><span>architectural zones</span></div>'
'</div>'
'<div class="callout warn"><h4>IMPORTANT — CURRENT SAP AVAILABILITY</h4><p>SAP states this reference architecture reflects a <b>transitional state</b>: some components and capabilities are <b>not yet generally available</b>. In particular, <b>bidirectional communication with third-party and self-hosted agents through Agent Gateway is not yet supported</b> (full bidirectional capability is expected soon). The diagram is an architectural direction and reference pattern — not a promise that every box is deployable today exactly as shown. Where availability is uncertain anywhere in this portal: <b>check current SAP documentation before implementing in production</b>.</p></div>'
'<h3>The 30-second mental model</h3>'
'<p><b>A2A = Agent ↔ Agent</b> (ask another agent). <b>MCP = Agent ↔ Tool/Resource</b> (use a tool). MCP standardizes how agents discover and use tools; A2A lets independent agents collaborate and delegate. They are complementary, not competing.</p>'
+ mermaid(
"FIG. 0 — THE SHAPE OF EVERYTHING BELOW",
"flowchart TD\n  U[USER] --> A[AGENT]\n  A -->|A2A| OA[OTHER AGENT]\n  A -->|MCP| T[TOOL]\n  T --> E[ENTERPRISE SYSTEM]\n  OA -->|MCP| T"
)
+ '<div class="done-row"><label><input type="checkbox" data-done="m00"> Mark the introduction complete</label></div>'
'</header>'
)


def build():
    parts = [HERO]

    b = []
    b.append(off(
'<p>This portal explains <b>SAP Architecture Center RA0029 “A2A and MCP for Interoperability”</b> (last updated Aug 27, 2026): a decoupled architecture where <b>agents and tools are developed, deployed and updated independently</b>, using two open standards — <b>A2A for agent-to-agent collaboration</b>, <b>MCP for agent-to-tool interaction</b> — so the SAP agent ecosystem stays open and extensible without monolithic agent design.</p>'
))
    b.append(con(
'<p>Think of a hospital: <b>agents are specialists</b> (doctors who reason), <b>tools are instruments and labs</b> (things that DO), <b>A2A is the referral system</b> between doctors, <b>MCP is the standardized instrument tray</b> any doctor can use, and <b>gateways are reception desks</b> that check badges and log visits.</p>'
))
    b.append(table(
["Question this portal answers", "Where"],
[
("What do A2A and MCP each do?", "Sections 12, 14, 26 + hero above"),
("What are Agent Gateway vs MCP Gateway?", "Sections 10, 13, 26"),
("Who manages what (SAP / customer / third party)?", "Sections 04, 28, 35-36"),
("How does one request flow end to end?", "Section 25 (animated)"),
("What is NOT yet available?", "Availability box above + Section 29"),
]
))
    b.append(con("<p><b>Progressive simplification path — never delete context, peel it in order:</b> <a href=#s02>FULL ARCHITECTURE</a> → <a href=#s04>MAJOR ZONES</a> → <a href=#s10>AGENT LAYER</a> → <a href=#s14>A2A</a> → <a href=#s12>MCP</a> → <a href=#s20>IDENTITY</a> → <a href=#s25>END-TO-END FLOW</a> → <a href=#s30>SIMPLE EXAMPLE</a>. Each step hides one layer of detail and links back up — beginners descend, architects ascend.</p>"))
    b.append(quiz(
"q-glance", "Joule needs a capability that lives in another agent. Which protocol carries that request?",
[("MCP", False), ("A2A", True), ("OData", False), ("SMTP", False)],
"Agent-to-agent delegation is A2A. MCP would be used by the receiving agent to call tools."
))
    parts.append(sec("s01", "01", "Architecture at a Glance", "\n".join(b)))

    b = []
    b.append(off(
'<p>Below is SAP&apos;s official solution diagram (RA0029), inlined from SAP&apos;s published SVG with only technical ID-prefixing applied — no content changed. Use the controls to zoom, pan (drag), reset, or go fullscreen. Sibling files next to this HTML: <code>sap-a2a-mcp.svg</code> (official image) and <code>sap-a2a-mcp.drawio</code> (official editable source, also downloadable from SAP&apos;s page).</p>'
))
    b.append(
'<div class="treeq" style="display:flex;gap:.45rem;flex-wrap:wrap">'
'<button type="button" id="zin">Zoom in</button>'
'<button type="button" id="zout">Zoom out</button>'
'<button type="button" id="zreset">Reset</button>'
'<button type="button" id="zfull">Fullscreen</button>'
'<span style="align-self:center;color:var(--ink-3);font-size:12.5px">Drag the diagram to pan.</span>'
'</div>'
'<div id="origwrap" style="border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:2px;background:#fff;overflow:auto;max-height:640px;cursor:grab">'
+ SAP_SVG
+ '</div>'
)
    b.append(imp(
'<p>Display note: the 54 embedded icons make this image ~900&nbsp;KB, so it ships inlined in this file rather than hotlinked — it renders offline. Colors follow SAP&apos;s legend: blue, purple, green, magenta, teal and gray edges (see Section 31). If the image area appears blank, your browser blocked large inline SVG — open the sibling <code>sap-a2a-mcp.svg</code> directly.</p>'
))
    b.append(
'<script>(function(){'
'var w=document.getElementById("origwrap");if(!w)return;'
'var svg=w.querySelector("svg");if(!svg)return;'
'var z=1,px=0,py=0,drag=false,sx=0,sy=0;'
'svg.style.transformOrigin="0 0";svg.style.maxWidth="none";'
'function ap(){svg.style.transform="translate("+px+"px,"+py+"px) scale("+z+")";}'
'document.getElementById("zin").onclick=function(){z=Math.min(z*1.3,6);ap();};'
'document.getElementById("zout").onclick=function(){z=Math.max(z/1.3,0.4);ap();};'
'document.getElementById("zreset").onclick=function(){z=1;px=0;py=0;ap();};'
'document.getElementById("zfull").onclick=function(){if(w.requestFullscreen)w.requestFullscreen();};'
'w.addEventListener("mousedown",function(e){drag=true;sx=e.clientX-px;sy=e.clientY-py;w.style.cursor="grabbing";});'
'window.addEventListener("mouseup",function(){drag=false;w.style.cursor="grab";});'
'w.addEventListener("mousemove",function(e){if(!drag)return;px=e.clientX-sx;py=e.clientY-sy;ap();});'
'})();</script>'
)
    parts.append(sec("s02", "02", "The Original Diagram", "\n".join(b)))

    b = []
    b.append(con(
'<p>Read any SAP solution diagram with the same 11 moves. Practice them on the diagram above.</p>'
))
    b.append(steps([
"<b>Find the actors.</b> USER on one side, third-party clouds and agents on the other, Joule and SAP systems in the middle.",
"<b>Find the trust boundaries.</b> Green Trust edges and Authenticate labels: every crossing re-validates identity.",
"<b>Find the managed boundaries.</b> SAP-managed platform vs BTP subaccount (customer) vs 3rd party boxes.",
"<b>Find the protocols.</b> Edge labels: A2A (purple), MCP (teal), OData/REST, Discover and Govern.",
"<b>Find the data/tool layer.</b> Tools, Data, Products, Grounding, Knowledge Graph, MCP Servers.",
"<b>Find the agent layer.</b> Joule, orchestrator, custom agents, managed runtimes, external agents.",
"<b>Find identity.</b> SAP Cloud Identity Services — the trust anchor for users, agents and app-to-app calls.",
"<b>Follow arrows.</b> Direction = caller to callee. Trace USER to TOOL and back before reading any text.",
"<b>Separate sync from async.</b> Sync request/response vs callbacks and push notifications (BYOA long tasks).",
"<b>Ask who authenticates whom</b> on every arrow (Section 21).",
"<b>Ask who authorizes what</b> on every arrow (Section 22). Trust is not permission.",
]))
    b.append(quiz(
"q-read", "First move when opening the diagram?",
[("Memorize acronyms", False), ("Find the actors and trust boundaries", True), ("Count the boxes", False), ("Pick a favorite color", False)],
"Actors + boundaries orient every other question the diagram can answer."
))
    parts.append(sec("s03", "03", "Read the Diagram", "\n".join(b)))

    return parts
