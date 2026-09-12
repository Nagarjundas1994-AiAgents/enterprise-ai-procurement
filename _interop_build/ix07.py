"""Portal part 7: s25 flow+animation+failures+game + s26 comparison + s27 directions."""
from common import code, table, grid, steps, qa, quiz, mermaid
from ix import sec, off, con, ex, imp, FLOW11, QUIZ_BANK

FULL16 = [
("USER asks", "Chat/UI + SSO", "IAS login, user session"),
("JOULE receives", "Chat/UI", "Session + user context"),
("ORCHESTRATOR plans", "Internal routing", "Scenario identity"),
("AGENT delegated", "Internal/A2A", "Agent identity + grant"),
("A2A call placed", "A2A 0.3.0 HTTP+JSON", "IAS App2App trust"),
("EXTERNAL AGENT reasoning", "Agent-internal", "Agent identity"),
("MCP discovery", "MCP tools/list", "Agent auth to server"),
("MCP SERVER invoked", "MCP tools/call JSON-RPC", "Tool-level grant"),
("TOOL executes", "Runtime call", "Service identity"),
("API called", "HTTPS OData/REST", "OAuth scopes"),
("BUSINESS SYSTEM commits", "System transaction", "Audit write"),
("RESULT returns", "MCP result", "Logged + traced"),
("AGENT reasons over result", "Agent-internal", "Audit row"),
("A2A response sent", "A2A response/webhook", "Trust re-validated"),
("JOULE presents", "Chat/UI", "User session"),
("USER decides next", "Chat/UI", "Session continues"),
]

Q = {q[0]: q for q in QUIZ_BANK}


def qx(qid):
    q = Q[qid]
    return quiz(q[0], q[1], q[2], q[3])


def build():
    parts = []

    b = []
    b.append(off(
"<p>The SAP simplified flow, expanded arrow by arrow. For each: <b>WHO</b> calls, <b>WHAT</b> travels, <b>PROTOCOL</b>, <b>AUTHENTICATION</b>, <b>AUTHORIZATION</b>, <b>DATA</b>, <b>RESPONSE</b>, <b>FAILURE MODE</b>. Fields the source does not specify say so explicitly.</p>"
+ table(
["#", "Arrow", "Who / What / Protocol / Auth / Data / Failure"],
[
("1", "USER to JOULE", "Who: person. What: business question. Protocol: chat/UI + SSO. Auth: IAS login. Data: utterance. Failure: login/validation error shown inline."),
("2", "JOULE to AGENT (A2A)", "Who: Joule as A2A client. What: message/send task + context. Protocol: A2A 0.3.0 HTTP+JSON. Auth: IAS App2App trust. Failure: unreachable agent, 60s sync timeout."),
("3", "AGENT to MCP SERVER", "Who: remote agent. What: tools/list discovery + tools/call. Protocol: MCP (JSON-RPC). Auth: agent identity + gateway policy. Failure: unknown tool, denied grant."),
("4", "MCP SERVER to TOOL/API", "Who: server runtime. What: OData/REST call, integration flow. Protocol: HTTPS + service credentials. Auth: OIDC/service identity. Failure: API error, timeout, rate limit."),
("5", "TOOL to AGENT", "Who: server. What: structured result. Protocol: MCP result. Data: business payload only. Failure: malformed result handled by agent."),
("6", "AGENT to JOULE (A2A)", "Who: remote agent. What: answer. Protocol: A2A response or webhook push. Auth: trust re-validated. Failure: late push correlated by task ID."),
("7", "JOULE to USER", "Who: Joule. What: presented result. Protocol: chat/UI. Data: rendered answer. Failure: partial results labeled as partial."),
]
)
))
    b.append(con("<p>Replay the same journey as an animation — protocol, identity and data direction narrated per step.</p>"))
    b.append(
'<div class="treeq"><div class="opts" style="display:flex;gap:.45rem;flex-wrap:wrap">'
'<button type="button" id="fprev">Previous</button>'
'<button type="button" id="fnext">Next</button>'
'<button type="button" id="fplay">Play Flow</button>'
'<button type="button" id="freset">Reset</button>'
'<span id="fcount" style="align-self:center;color:var(--ink-3);font-size:12.5px"></span></div>'
'<h3 id="ftitle" style="margin:.6rem 0 .3rem"></h3><p id="fbody"></p>'
'<div class="pills" style="display:flex;gap:.35rem;flex-wrap:wrap" id="fdots"></div></div>'
'<script>(function(){'
'var S=[' + ",".join('["' + t.replace('"', "") + '","' + d.replace('"', "") + '","' + p.replace('"', "") + '","' + s.replace('"', "") + '"]' for (t, d, p, s) in FLOW11) + '];'
'var i=0,timer=null;var T=document.getElementById("ftitle"),B=document.getElementById("fbody"),C=document.getElementById("fcount"),D=document.getElementById("fdots");'
'function r(){T.textContent="Step "+(i+1)+"/"+S.length+": "+S[i][0];B.innerHTML="<b>What.</b> "+S[i][1]+"<br><b>Protocol.</b> "+S[i][2]+"<br><b>Identity/security.</b> "+S[i][3];C.textContent="Step "+(i+1)+" of "+S.length;D.innerHTML="";S.forEach(function(s2,k){var sp=document.createElement("span");sp.className="pill"+(k===i?" on":"");sp.textContent=(k+1);D.appendChild(sp);});}'
'document.getElementById("fprev").onclick=function(){stop();i=(i+S.length-1)%S.length;r();};'
'document.getElementById("fnext").onclick=function(){stop();i=(i+1)%S.length;r();};'
'document.getElementById("freset").onclick=function(){stop();i=0;r();};'
'function stop(){if(timer){clearInterval(timer);timer=null;document.getElementById("fplay").textContent="Play Flow";}}'
'document.getElementById("fplay").onclick=function(){if(timer){stop();return;}document.getElementById("fplay").textContent="Pause";timer=setInterval(function(){i=(i+1)%S.length;r();if(i===S.length-1)stop();},2400);};'
'r();})();</script>'
)
    b.append(off("<p><b>What happens if?</b> Failure handling below is a <b>CONCEPTUAL EXPLANATION</b> of sensible behavior (retries, timeouts, user messaging) — the reference architecture specifies the components and trust, not exact product failover semantics. Verify product behavior in current SAP documentation.</p>"))
    b.append(table(
["Scenario", "Where / detected by / response / user sees"],
[
("MCP server unavailable", "Agent-to-tool hop; detected by calling agent via timeout; retry with backoff or alternative tool; user sees: capability temporarily unavailable"),
("External agent unavailable", "A2A hop; detected by Joule client via timeout; sync-or-callback per BYOA rules; user sees: specialist unreachable, partial answer if any"),
("Invalid token", "Any boundary; detected by validator (401); refresh or re-login; user sees: session expired, sign in again"),
("No permission", "Authorization check; denied with audit (403); no retry; user sees: not permitted, request access"),
("Tool error", "Tool execution; detected by server/agent; agent reasons or escalates; user sees: step failed with reason"),
("Agent timeout", "Long task; detected by caller timer; async push continues if supported; user sees: still working, notified on completion"),
("Third-party down", "Vendor hop; detected by gateway/client; breaker + fallback; user sees: degraded data labeled as such"),
]
))
    b.append(con("<p><b>Trace-the-request game:</b> a user asks Joule about a delayed order. At each stop, pick what happens next.</p>"))
    b.append(
'<div class="treeq" id="gamebox"><h3 id="gq" style="margin:.1rem 0 .55rem"></h3><div class="opts" id="gopts" style="display:flex;flex-wrap:wrap;gap:.45rem"></div><p id="gfb" style="min-height:1.4em"></p><p id="gsc" style="color:var(--ink-3);font-size:12.5px"></p></div>'
'<script>(function(){'
'var G=[["Joule needs order facts held by the Order agent. What carries the request?",["MCP tools/call","A2A message/send","SMTP","FTP"],1],'
'["The Order agent needs live stock data. What does it consult first?",["Its own database password","MCP tool discovery","The user manual","A coin flip"],1],'
'["The stock tool lives behind which governed door?",["Agent Gateway","MCP Gateway","Firewall rule 7","The lobby"],1],'
'["The Order agent finishes. How does Joule get the answer?",["A2A response or webhook push","Fax","MCP replaces the answer","It guesses"],0],'
'["Who authenticated the external call?",["Nobody","IAS App2App trust + named user","The diagram colors","The firewall"],1],'
'["The tool call fails with 403. Meaning?",["Retry 50 times","Authenticated but not permitted; do not retry blindly","Success","Delete the agent"],1]];'
'var i=0,score=0,box=document.getElementById("gamebox");if(!box)return;'
'var Q=document.getElementById("gq"),O=document.getElementById("gopts"),F=document.getElementById("gfb"),S=document.getElementById("gsc");'
'function r(){if(i>=G.length){Q.textContent="Done.";O.innerHTML="";F.textContent="";S.textContent="Score "+score+"/"+G.length+". ";var b=document.createElement("button");b.textContent="Play again";b.onclick=function(){i=0;score=0;r();};S.appendChild(b);return;}'
'Q.textContent="Q"+(i+1)+": "+G[i][0];O.innerHTML="";F.textContent="";S.textContent="Score "+score+"/"+G.length;'
'G[i][1].forEach(function(op,k){var btn=document.createElement("button");btn.textContent=op;btn.onclick=function(){if(k===G[i][2]){score++;F.textContent="Correct.";F.style.color="var(--ok)";}else{F.textContent="Not quite — the section above explains why.";F.style.color="var(--bad)";}i++;setTimeout(r,900);};O.appendChild(btn);});}'
'r();})();</script>'
)
    b.append(con("<p><b>Final full-chain visual:</b> the complete USER-to-USER journey across both SAP and external legs — each stop shows protocol, identity and data direction.</p>"))
    b.append(
'<div class="treeq"><div class="opts" style="display:flex;gap:.45rem;flex-wrap:wrap">'
'<button type="button" id="g2prev">Previous</button>'
'<button type="button" id="g2next">Next</button>'
'<button type="button" id="g2play">Play Flow</button>'
'<button type="button" id="g2reset">Reset</button>'
'<span id="g2count" style="align-self:center;color:var(--ink-3);font-size:12.5px"></span></div>'
'<h3 id="g2title" style="margin:.6rem 0 .3rem"></h3><p id="g2body"></p>'
'<div class="pills" style="display:flex;gap:.35rem;flex-wrap:wrap" id="g2dots"></div></div>'
'<script>(function(){'
'var S=[' + ",".join('["' + t.replace('"', "") + '","' + p.replace('"', "") + '","' + s.replace('"', "") + '"]' for (t, p, s) in FULL16) + '];'
'var i=0,timer=null;var T=document.getElementById("g2title"),B=document.getElementById("g2body"),C=document.getElementById("g2count"),D=document.getElementById("g2dots");'
'function r(){T.textContent="Stop "+(i+1)+"/"+S.length+": "+S[i][0];B.innerHTML="<b>Protocol.</b> "+S[i][1]+"<br><b>Identity/security.</b> "+S[i][2]+"<br><b>Data direction.</b> "+(i<11?"Outward: request flows toward the system.":"Return: result flows back to the user.");C.textContent="Stop "+(i+1)+" of "+S.length;D.innerHTML="";S.forEach(function(s2,k){var sp=document.createElement("span");sp.className="pill"+(k===i?" on":"");sp.textContent=(k+1);D.appendChild(sp);});}'
'document.getElementById("g2prev").onclick=function(){stop();i=(i+S.length-1)%S.length;r();};'
'document.getElementById("g2next").onclick=function(){stop();i=(i+1)%S.length;r();};'
'document.getElementById("g2reset").onclick=function(){stop();i=0;r();};'
'function stop(){if(timer){clearInterval(timer);timer=null;document.getElementById("g2play").textContent="Play Flow";}}'
'document.getElementById("g2play").onclick=function(){if(timer){stop();return;}document.getElementById("g2play").textContent="Pause";timer=setInterval(function(){i=(i+1)%S.length;r();if(i===S.length-1)stop();},2200);};'
'r();})();</script>'
)
    b.append(qx("xq01"))
    parts.append(sec("s25", "25", "Complete Request Flow", "\n".join(b)))

    b = []
    b.append(table(
["Concept", "A2A", "MCP"],
[
("Main purpose", "Agent-to-agent collaboration", "Agent-to-tool/resource interaction"),
("Communication", "Agent to Agent", "Agent to Tool/Resource"),
("Delegation", "Yes", "Not its primary purpose"),
("Tool discovery", "Not primary", "Yes"),
("Multi-agent collaboration", "Yes", "No"),
("Tool abstraction", "No", "Yes"),
("Enterprise APIs", "Indirectly", "Yes"),
("Example", "Maintenance Agent to Inventory Agent", "Agent to checkStock tool"),
]
))
    b.append(off(
"<p><b>Most important: A2A and MCP are complementary, not competing.</b> Agent-to-agent: A2A. Agent-to-tool: MCP. Memory trick — <b>A2A: ASK ANOTHER AGENT</b> (delegation/collaboration). <b>MCP: USE A TOOL</b> (capability/tool access).</p>"
))
    parts.append(sec("s26", "26", "A2A vs MCP", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>INBOUND:</b> external system calls IN — through <b>Agent Gateway</b> to a <b>Joule Agent</b> (A2A, IAS App2App, named user). <b>OUTBOUND (BYOA):</b> <b>Joule calls OUT</b> to an external/self-hosted agent (A2A message/send, 60s sync or webhook push). Difference: direction of initiation, which side exposes the endpoint, and which trust relationship is exercised — both use A2A, neither bypasses identity. Note SAP&apos;s current-state remark: full bidirectional Gateway support is still arriving (Section 29).</p>"
))
    b.append(mermaid("DIRECTIONS", "flowchart TD\n  EXT[External] -->|inbound via Agent Gateway| J[Joule Agent]\n  J -->|outbound BYOA| EXT2[External agent]"))
    b.append(qx("xq09"))
    parts.append(sec("s27", "27", "Inbound vs Outbound", "\n".join(b)))

    return parts
