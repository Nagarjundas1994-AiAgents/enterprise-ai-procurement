"""Portal part 2: s04 zones + interactive SVG + s05 BAIP + s06 Joule Work + s07 Joule Studio."""
import io
import os
from common import code, table, grid, steps, qa, quiz, mermaid, drawio
from ix import sec, off, con, ex, imp

HERE = os.path.dirname(os.path.abspath(__file__))
DRAWIO_XML = io.open(os.path.join(HERE, "simplified.drawio"), encoding="utf-8").read()

SVGAPP = (
'<div class="treeq" style="display:flex;gap:.45rem;flex-wrap:wrap">'
'<button type="button" data-protof="all">All</button>'
'<button type="button" data-protof="a2a">A2A</button>'
'<button type="button" data-protof="mcp">MCP</button>'
'<button type="button" data-protof="trust">Trust</button>'
'<button type="button" data-protof="odata">OData/REST</button>'
'<button type="button" id="svgzin">Zoom +</button>'
'<button type="button" id="svgzout">Zoom -</button>'
'<button type="button" id="svgzreset">Reset</button>'
'</div>'
'<div style="display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:.75rem" class="svgcols">'
'<div class="diagram" style="margin:0"><svg id="ixsvg" viewBox="0 0 980 600" style="width:100%;height:auto" role="img" aria-label="Interactive simplified A2A MCP architecture"></svg>'
'<p class="figcap">SIMPLIFIED INTERACTIVE MAP — CLICK ANY NODE. TEACHING AID, NOT THE OFFICIAL DIAGRAM.</p></div>'
'<div class="card" id="ixpanel"><h4>Component panel</h4><p>Click a node to see: what it is, why it exists, who manages it, connections, protocol, security, and source.</p></div>'
'</div>'
'<script>(function(){'
'var N=[["user",30,20,"User / App clients","#E7ECF8","#0B3D91","chat"],'
'["joule",30,110,"Joule",["a2a"],"#0B3D91","#fff"],'
'["studio",30,190,"Joule Studio",["a2a"],"#E7ECF8","#0B3D91"],'
'["orch",30,270,"Joule Orchestrator",["a2a"],"#0B3D91","#fff"],'
'["skills",30,350,"Skills",["a2a"],"#E7ECF8","#0B3D91"],'
'["runtimes",30,430,"Managed runtimes",["a2a","mcp"],"#E7ECF8","#0B3D91"],'
'["agentgw",290,190,"Agent Gateway (A2A)",["a2a","trust"],"#EEE9FD","#6B46E8"],'
'["mcpint",290,350,"Internal MCP use (KG+APIs)",["mcp"],"#E3F2F1","#0E7C86"],'
'["custom",550,110,"Custom agents",["a2a","mcp"],"#E7ECF8","#0B3D91"],'
'["byoa",550,190,"BYO agent (external)",["a2a","trust"],"#EEE9FD","#6B46E8"],'
'["mcpgw",550,350,"MCP Gateway (Suite)",["mcp","trust","odata"],"#E3F2F1","#0E7C86"],'
'["odata",550,440,"OData/REST APIs",["odata"],"#F9EEDC","#B5710A"],'
'["extag",800,190,"3rd-party agents",["a2a","trust"],"#EEE9FD","#6B46E8"],'
'["extmcp",800,350,"3rd-party MCP server",["mcp"],"#E3F2F1","#0E7C86"],'
'["clouds",800,440,"GCP Azure AWS IBM Others",["a2a"],"#F1EEE4","#47536A"],'
'["tools",290,440,"Tools+Data+Grounding+KG",["mcp","odata"],"#F9EEDC","#B5710A"],'
'["ias",290,520,"Cloud Identity Services",["trust"],"#E7F3EA","#2E7D46",410],'
'["autosuite",290,110,"Autonomous Suite apps",["a2a"],"#E7ECF8","#0B3D91"],'
'["mcpbuilder",200,270,"MCP Builder",["mcp"],"#E3F2F1","#0E7C86",70],'
'["signavio",200,60,"Signavio",["odata"],"#F1EEE4","#47536A",70],'
'["leanix",200,130,"LeanIX",["a2a"],"#F1EEE4","#47536A",70]];'
'var E=[["user","joule","chat","chat"],["joule","orch","route","ui"],["orch","custom","A2A delegate","a2a"],["custom","mcpint","MCP tools","mcp"],["mcpint","tools","read KG/APIs","mcp"],["joule","agentgw","A2A out","a2a"],["agentgw","byoa","A2A","a2a"],["agentgw","extag","A2A","a2a"],["byoa","extmcp","MCP","mcp"],["extag","extmcp","MCP","mcp"],["custom","mcpgw","MCP","mcp"],["mcpgw","odata","HTTPS","odata"],["agentgw","ias","trust","trust"],["mcpgw","ias","trust","trust"],["agentgw","autosuite","serves","a2a"],["studio","mcpbuilder","builds","ui"],["mcpbuilder","mcpint","publishes","mcp"],["signavio","joule","process truth","ui","ctx"],["leanix","agentgw","landscape","ui","ctx"]];'
'var C={'
'user:{n:"User / application clients",w:"The human (or calling app) starting the request.",y:"To consume outcomes, never internals.",m:"Customer",inc:"Answer from Joule/app",out:"Question to Joule/app",p:"UI/chat + SSO",s:"IAS login; user context propagates"},'
'joule:{n:"Joule",w:"SAP conversational and agent experience; acts as A2A CLIENT to remote agents.",y:"One front door instead of one door per agent.",m:"SAP-managed",inc:"User utterance",out:"A2A message/send",p:"A2A 0.3.0 HTTP+JSON",s:"User session + App2App trust"},'
'studio:{n:"Joule Studio",w:"Low-code build surface for custom agents and skills.",y:"Business teams compose agents without pro-code.",m:"SAP-managed",inc:"Builder intent",out:"Deployable agent/skill",p:"Studio tooling",s:"Builder identity + governance"},'
'orch:{n:"Joule Orchestrator (+ Agent Harness)",w:"Plans work, runs skills, fans out to agents.",y:"Separates planning from doing.",m:"SAP-managed",inc:"Goal from Joule",out:"Skill runs + A2A tasks",p:"Internal + A2A",s:"Scenario identity"},'
'skills:{n:"Skills",w:"Reusable capability packages the orchestrator can run.",y:"Reuse across scenarios.",m:"SAP/customer-built",inc:"Orchestrator call",out:"Result",p:"Internal",s:"Same as orchestrator"},'
'runtimes:{n:"Managed runtimes",w:"SAP-run homes for Joule agents, custom agents and MCP servers.",y:"Isolation + independent deploy/version.",m:"SAP-managed",inc:"Deployments",out:"Running endpoints",p:"HTTPS",s:"Platform identity"},'
'agentgw:{n:"Agent Gateway (inbound A2A)",w:"Externally reachable A2A endpoint exposing Joule agents to outside callers.",y:"One governed front door for inbound delegation.",m:"SAP-managed",inc:"External A2A tasks",out:"Joule agent results",p:"A2A 0.3.0 HTTP+JSON",s:"IAS App2App + named user"},'
'mcpint:{n:"Internal MCP consumption",w:"Joule agents read Knowledge Graph + business APIs via MCP.",y:"Semantic, governed data access.",m:"SAP internal use",inc:"Agent tool calls",out:"KG/API results",p:"MCP",s:"Agent identity"},'
'custom:{n:"Custom agents (BTP)",w:"Customer-built agents in the BTP subaccount.",y:"Customer IP as callable agents.",m:"Customer",inc:"A2A tasks",out:"MCP tool calls + answers",p:"A2A + MCP",s:"IAS trust + grants"},'
'byoa:{n:"Bring Your Own Agent (outbound)",w:"Code-based external agents Joule calls via A2A message/send (text).",y:"Any framework can join.",m:"Customer/third party",inc:"Joule A2A request",out:"Agent answer or webhook push",p:"A2A 0.3.0, 60s sync",s:"IAS App2App trust"},'
'mcpgw:{n:"MCP Gateway (Integration Suite)",w:"Customer-managed: turns SAP/non-SAP APIs, flows, data, external MCP into governed MCP tools.",y:"One governed tool front door.",m:"Customer",inc:"Agent MCP calls",out:"Tool results",p:"MCP over HTTPS",s:"OIDC, limits, payload guard"},'
'odata:{n:"OData/REST enterprise APIs",w:"The existing API layer tools ultimately execute.",y:"MCP reuses APIs; it does not delete them.",m:"Customer/SAP",inc:"Gateway calls",out:"Business data",p:"HTTPS + OAuth",s:"Service credentials"},'
'extag:{n:"Third-party agents",w:"Agents on other clouds/vendors reachable via open A2A.",y:"No vendor lock-in.",m:"Third party",inc:"A2A tasks",out:"Answers",p:"A2A",s:"Mutual IAS/federated trust"},'
'extmcp:{n:"Third-party MCP servers",w:"External tool endpoints agents may consume when governed.",y:"Ecosystem tools.",m:"Third party",inc:"MCP calls",out:"Tool results",p:"MCP",s:"Gateway policy"},'
'clouds:{n:"Hyperscaler clouds",w:"GCP, Azure, AWS, IBM, others: where external agents may run.",y:"Shows interoperability scope.",m:"Third party",inc:"-",out:"-",p:"A2A across clouds",s:"Presence is not a turnkey guarantee"},'
'tools:{n:"Tools, Data, Products, Grounding, Knowledge Graph",w:"Enterprise context agents reason over and act through.",y:"Authoritative facts beat model guesses.",m:"SAP/customer",inc:"Tool/MCP reads",out:"Grounded results",p:"MCP + APIs",s:"Data authorization"},'
'ias:{n:"SAP Cloud Identity Services",w:"Identity, tokens, trust anchor for users and app-to-app calls.",y:"Every arrow authenticates here.",m:"SAP-managed",inc:"Login/dependencies",out:"Tokens",p:"OIDC/OAuth2",s:"Trust root"},'
'autosuite:{n:"Autonomous Suite apps",w:"Finance, Spend, SCM, HCM, CX and Industry AI applications served by agents.",y:"Shows what the agent ecosystem is FOR.",m:"SAP",inc:"Agent results",out:"Business outcomes",p:"Suite APIs via tools",s:"Suite authorization"},'
'mcpbuilder:{n:"MCP Builder",w:"Turns an existing API into a discoverable MCP tool.",y:"Fastest path from API to agent-usable capability.",m:"SAP-managed surface, customer content",inc:"API + description",out:"Tool in catalog",p:"Build-time",s:"Builder identity"},'
'signavio:{n:"Signavio (process truth)",w:"Process knowledge and behavior mining: how work really flows.",y:"Agents consult how the business runs.",m:"SAP",inc:"-",out:"Process insight",p:"Reference",s:"Not specified in RA0029"},'
'leanix:{n:"LeanIX (landscape truth)",w:"AI Agent Hub: which agents exist, governed.",y:"Discovery + governance of the fleet.",m:"SAP/customer",inc:"-",out:"Catalog + policy",p:"Reference",s:"Not specified in RA0029"}};'
'var svg=document.getElementById("ixsvg");if(!svg)return;'
'var NS="http://www.w3.org/2000/svg";'
'var g=document.createElementNS(NS,"g");g.setAttribute("id","ixg");svg.appendChild(g);'
'var zones=[["SAP-MANAGED",10,8,260,"#0B3D91"],["BTP SUBACCOUNT (CUSTOMER)",280,8,500,"#B5710A"],["THIRD PARTY",790,8,180,"#6B46E8"]];zones.forEach(function(z){var r=document.createElementNS(NS,"rect");r.setAttribute("x",z[1]);r.setAttribute("y",z[2]);r.setAttribute("width",z[3]);r.setAttribute("height",584);r.setAttribute("rx",10);r.setAttribute("fill","#ffffff");r.setAttribute("opacity","0.4");r.setAttribute("stroke",z[4]);r.setAttribute("stroke-dasharray","7,5");g.appendChild(r);var t=document.createElementNS(NS,"text");t.setAttribute("x",z[1]+12);t.setAttribute("y",z[2]+18);t.setAttribute("font-size","11");t.setAttribute("font-weight","bold");t.setAttribute("fill",z[4]);t.textContent=z[0];g.appendChild(t);});'
'function box(n){var wd=n[7]||150;var r=document.createElementNS(NS,"rect");r.setAttribute("x",n[1]);r.setAttribute("y",n[2]);r.setAttribute("width",wd);r.setAttribute("height",52);r.setAttribute("rx",7);r.setAttribute("fill",n[4]);r.setAttribute("stroke",n[5]);r.setAttribute("stroke-width","1.6");r.setAttribute("data-k",n[0]);r.style.cursor="pointer";return r;}'
'function lab(n){var cx=n[1]+((n[7]||150)/2);var t=document.createElementNS(NS,"text");t.setAttribute("x",cx);t.setAttribute("y",n[2]+30);t.setAttribute("text-anchor","middle");t.setAttribute("font-size","11.5");t.setAttribute("fill",n[6]);t.setAttribute("data-k",n[0]);t.style.cursor="pointer";var w=n[3].split(" ");var l1=w.slice(0,Math.ceil(w.length/2)).join(" "),l2=w.slice(Math.ceil(w.length/2)).join(" ");var a=document.createElementNS(NS,"tspan");a.setAttribute("x",cx);a.setAttribute("dy","-4");a.textContent=l1;t.appendChild(a);if(l2){var b2=document.createElementNS(NS,"tspan");b2.setAttribute("x",cx);b2.setAttribute("dy","13");b2.textContent=l2;t.appendChild(b2);}return t;}'
'var pos={};N.forEach(function(n){pos[n[0]]=[n[1],n[2]];});'
'var wm={};N.forEach(function(n){wm[n[0]]=(n[7]||150);});var eix=0;'
'E.forEach(function(e){var a=pos[e[0]],b=pos[e[1]];var l=document.createElementNS(NS,"line");if(a[0]===b[0]){l.setAttribute("x1",a[0]+(wm[e[0]]/2));l.setAttribute("y1",a[1]+52);l.setAttribute("x2",b[0]+(wm[e[1]]/2));l.setAttribute("y2",b[1]);}else{l.setAttribute("x1",a[0]+wm[e[0]]);l.setAttribute("y1",a[1]+26);l.setAttribute("x2",b[0]);l.setAttribute("y2",b[1]+26);if(e[1]==="ias"){var cx2=a[0]+75;l.setAttribute("x1",cx2);l.setAttribute("x2",cx2);l.setAttribute("y2",b[1]);}}l.setAttribute("stroke","#8992A6");l.setAttribute("stroke-width","1.4");if(e[4]==="ctx")l.setAttribute("stroke-dasharray","5,4");l.setAttribute("data-p",e[3]);l.setAttribute("data-ei",eix++);l.setAttribute("marker-end","url(#ah)");l.style.cursor="pointer";g.appendChild(l);});'
'var defs=document.createElementNS(NS,"defs");defs.innerHTML="<marker id=\\"ah\\" markerWidth=\\"8\\" markerHeight=\\"8\\" refX=\\"7\\" refY=\\"4\\" orient=\\"auto\\"><path d=\\"M0,0 L8,4 L0,8\\" fill=\\"none\\" stroke=\\"#8992A6\\" stroke-width=\\"1.4\\"/></marker>";svg.insertBefore(defs,svg.firstChild);'
'N.forEach(function(n){g.appendChild(box(n));g.appendChild(lab(n));});'
'var panel=document.getElementById("ixpanel");'
'var EX={user:"A manager asks Joule about a delayed order.",joule:"Joule routes a refund question to the Order agent.",studio:"A pricing desk builds a quote-checker agent.",orch:"Refund flow: check order, check policy, approve, notify.",skills:"A sanctioned address-validation skill reused by 3 scenarios.",runtimes:"Custom agent v2 deploys without touching Joule.",agentgw:"Partner app calls a Joule scenario via A2A.",mcpint:"Joule reads Knowledge Graph product facts.",custom:"Customer warranty agent in the subaccount.",byoa:"LangGraph agent answering over A2A message/send.",mcpgw:"Vendor invoice API published as checkInvoice tool.",odata:"Product master read behind a tool.",extag:"Bedrock agent scoring risk over A2A.",extmcp:"Partner tariff lookup tool.",clouds:"Vertex AI agent joining over A2A.",tools:"Grounding an answer in KG facts.",ias:"App2App token minted for a gateway call.",autosuite:"Spend agent filing invoices autonomously.",mcpbuilder:"Purchase-order API wrapped as createPO tool.",signavio:"Bot compares live flow against mined process.",leanix:"Operator finds the approved refund agent."};'
'var NT={user:"Start every trace here.",joule:"Joule is a client outbound, a host inbound — never mix the two.",studio:"Low-code composes; pro-code integrates as A2A servers.",orch:"Conducting is not playing: orchestrator never calls tools directly.",skills:"Version skills; orchestrators pin versions.",runtimes:"Separate deploy unit per endpoint+version+identity.",agentgw:"Bidirectional use still arriving — verify docs.",mcpint:"Internal use differs from Gateway exposure.",custom:"Customer owns code, endpoint, identity registration.",byoa:"Text only, 60s sync, webhook for long tasks.",mcpgw:"One policy point for the whole tool landscape.",odata:"APIs stay; MCP fronts them.",extag:"Mutual trust negotiated per relationship.",extmcp:"Consumed only when gateway-governed.",clouds:"Presence is scope, not a turnkey guarantee.",tools:"Facts beat guesses; data authorization still applies.",ias:"Trust is recognition, never permission.",autosuite:"Suites consume agents; agents do not bypass suite auth.",mcpbuilder:"Descriptions make or break discoverability.",signavio:"Process truth informs, never authorizes.",leanix:"Catalog truth informs, never authorizes."};'
'var EI={"user>joule":{w:"Carry the question inward.",d:"out",a:"IAS login",z:"Session scopes",t:"Utterance",x:"Order question",f:"Login or validation error inline."},"joule>orch":{w:"Hand the goal to planning.",d:"in",a:"Scenario identity",z:"Scenario permission",t:"Goal",x:"Refund goal",f:"Not specified in the reference architecture."},"orch>custom":{w:"Delegate to a specialist.",d:"out",a:"IAS trust",z:"Capability grant",t:"Task + context",x:"Investigate shipment",f:"Specialist timeout; partial results."},"custom>mcpint":{w:"Use a tool.",d:"out",a:"Agent identity",z:"Tool grant",t:"Parameters",x:"getOrderStatus call",f:"Unknown tool or denied grant."},"mcpint>tools":{w:"Read facts/APIs.",d:"out",a:"Service identity",z:"Data authorization",t:"Query",x:"KG product facts",f:"Not explicitly specified in the reference architecture."},"joule>agentgw":{w:"Reach an outside agent.",d:"out",a:"IAS App2App",z:"Outbound permission",t:"message/send",x:"BYOA call",f:"60s timeout; webhook fallback."},"agentgw>byoa":{w:"Deliver to external agent.",d:"out",a:"IAS trust",z:"Endpoint permission",t:"A2A task",x:"LangGraph task",f:"Unreachable agent."},"agentgw>extag":{w:"Deliver to vendor agent.",d:"out",a:"Mutual trust",z:"Capability permission",t:"A2A task",x:"Risk scoring",f:"Vendor outage; breaker."},"byoa>extmcp":{w:"External agent uses a tool.",d:"out",a:"Agent identity",z:"Gateway policy",t:"Tool call",x:"Tariff lookup",f:"Tool error."},"extag>extmcp":{w:"Vendor agent uses a tool.",d:"out",a:"Agent identity",z:"Gateway policy",t:"Tool call",x:"Stock check",f:"Tool error."},"custom>mcpgw":{w:"Use a governed tool.",d:"out",a:"Agent identity",z:"OIDC + tool grant",t:"MCP call",x:"checkInvoice",f:"429 quota; 403 denied."},"mcpgw>odata":{w:"Execute the API.",d:"out",a:"Service credentials",z:"API scopes",t:"HTTPS request",x:"Invoice POST",f:"502/504 mapped."},"agentgw>ias":{w:"Validate trust.",d:"in",a:"IAS check",z:"Not applicable",t:"Token",x:"App2App validation",f:"401 invalid/expired."},"mcpgw>ias":{w:"Validate trust.",d:"in",a:"IAS check",z:"Not applicable",t:"Token",x:"OIDC validation",f:"401 invalid/expired."},"agentgw>autosuite":{w:"Serve suite scenarios.",d:"out",a:"Scenario identity",z:"Suite permission",t:"Result",x:"Filed invoices",f:"Not explicitly specified in the reference architecture."},"studio>mcpbuilder":{w:"Wrap capability.",d:"out",a:"Builder identity",z:"Build permission",t:"API + description",x:"createPO tool",f:"Poor description hurts discovery."},"mcpbuilder>mcpint":{w:"Publish tool.",d:"out",a:"Builder identity",z:"Catalog permission",t:"Manifest",x:"Tool listing",f:"Version conflict."},"signavio>joule":{w:"Inform with process truth.",d:"out",a:"Not specified in RA0029",z:"Not specified in RA0029",t:"Insight",x:"Flow comparison",f:"Not explicitly specified in the reference architecture."},"leanix>agentgw":{w:"Inform with landscape truth.",d:"out",a:"Not specified in RA0029",z:"Not specified in RA0029",t:"Catalog",x:"Approved agent lookup",f:"Not explicitly specified in the reference architecture."}};'
'function show(k){var c=C[k];if(!c)return;var conn=E.filter(function(e){return e[0]===k||e[1]===k;}).map(function(e){return e[0]+"-"+e[2]+"->"+e[1];});panel.innerHTML="<h4>"+c.n+"</h4><p><b>What.</b> "+c.w+"</p><p><b>Why.</b> "+c.y+"</p><p><b>Managed by.</b> "+c.m+"</p><p><b>Incoming.</b> "+conn.filter(function(s2){return s2.indexOf("->"+k)>-1;}).join("; ")+"</p><p><b>Outgoing.</b> "+conn.filter(function(s2){return s2.indexOf(k+"-")===0;}).join("; ")+"</p><p><b>Protocol.</b> "+c.p+"</p><p><b>Security.</b> "+c.s+"</p><p><b>Example.</b> "+(EX[k]||"-")+"</p><p><b>Important note.</b> "+(NT[k]||"-")+"</p><p><b>Source.</b> OFFICIAL where SAP states it; teaching text otherwise.</p>";'
'g.querySelectorAll("[data-k]").forEach(function(el){var kk=el.getAttribute("data-k");var keep=(kk===k)||E.some(function(e){return (e[0]===k&&e[1]===kk)||(e[1]===k&&e[0]===kk);});el.style.opacity=keep?"1":"0.2";if(el.tagName==="rect")el.setAttribute("stroke-width",kk===k?"3":"1.6");});'
'g.querySelectorAll("line").forEach(function(l){var ei=+(l.getAttribute("data-ei"));var e=E[ei];var on=e&&(e[0]===k||e[1]===k);l.style.opacity=on?"1":"0.12";});}'
'function showEdge(ix){var e=E[ix];if(!e)return;var info=EI[e[0]+">"+e[1]]||{w:"Not explicitly specified in the reference architecture.",d:"out",a:"Not explicitly specified in the reference architecture.",z:"Not explicitly specified in the reference architecture.",t:"Not explicitly specified in the reference architecture.",x:"-",f:"Not explicitly specified in the reference architecture."};panel.innerHTML="<h4>Arrow: "+C[e[0]].n+" to "+C[e[1]].n+"</h4><p><b>FROM.</b> "+C[e[0]].n+"</p><p><b>TO.</b> "+C[e[1]].n+"</p><p><b>WHY.</b> "+info.w+"</p><p><b>PROTOCOL.</b> "+e[3]+" ("+e[2]+")</p><p><b>DIRECTION.</b> "+info.d+"</p><p><b>AUTHENTICATION.</b> "+info.a+"</p><p><b>AUTHORIZATION.</b> "+info.z+"</p><p><b>DATA.</b> "+info.t+"</p><p><b>EXAMPLE.</b> "+info.x+"</p><p><b>FAILURE.</b> "+info.f+"</p>";}'
'g.addEventListener("click",function(e){var t=e.target;var k=t.getAttribute&&t.getAttribute("data-k");if(k){show(k);return;}var ei=t.getAttribute&&t.getAttribute("data-ei");if(ei!==null&&ei!==undefined&&ei!=="")showEdge(+ei);});'
'document.querySelectorAll("[data-protof]").forEach(function(btn){btn.onclick=function(){var f=btn.getAttribute("data-protof");N.forEach(function(n){var pros=Array.isArray(n[3])?n[3]:[n[3]];var on=(f==="all"||pros.indexOf(f)>-1||n[0]==="user"||n[0]==="ias");g.querySelectorAll("[data-k=\\""+n[0]+"\\"]").forEach(function(el){el.style.opacity=on?"1":"0.18";});});E.forEach(function(e){});g.querySelectorAll("line").forEach(function(l){var p=l.getAttribute("data-p");l.style.opacity=(f==="all"||p===f||((p==="chat"||p==="ui")&&(f==="all")))?"1":"0.12";});};});'
'var zz=1;function zap(){g.setAttribute("transform","scale("+zz+")");}'
'document.getElementById("svgzin").onclick=function(){zz=Math.min(zz*1.2,3);zap();};'
'document.getElementById("svgzout").onclick=function(){zz=Math.max(zz/1.2,0.6);zap();};'
'document.getElementById("svgzreset").onclick=function(){zz=1;zap();};'
'})();</script>'
)


def build():
    parts = []

    b = []
    b.append(off(
"<p>Seven zones tile the diagram. Own each zone before any box inside it.</p>"
))
    b.append(table(
["Zone", "What", "Owner", "Boundary"],
[
("1 User / app clients", "People and calling apps starting requests", "Customer", "SSO login"),
("2 SAP Business AI Platform", "Joule, Studio, orchestrator, runtimes, gateways (SAP side)", "SAP-managed", "Service endpoints + tokens"),
("3 Joule Work surface", "Where agents are built and run (Studio, orchestrator, skills, A2A, runtimes, gateway)", "SAP-managed", "Deployed endpoints"),
("4 BTP customer area", "Subaccount: custom agents, BYOA, MCP Gateway, OData/REST", "Customer", "Subaccount + bindings"),
("5 Third-party ecosystem", "External agents, MCP servers, APIs, hyperscalers, external IdP", "Third parties", "Mutual trust per call"),
("6 Identity and trust", "Cloud Identity Services spanning all zones", "SAP-managed", "Token validation everywhere"),
("7 Autonomous Suite", "Finance, Spend, SCM, HCM, CX, Industry AI apps agents serve", "SAP", "Suite APIs via tools"),
]
))
    b.append(con("<p>Explore the teaching map below — every node opens the Section-55 click panel (name, what, why, manager, connections, protocol, security). Filter by protocol to see only A2A, MCP, Trust or OData arrows.</p>"))
    b.append(SVGAPP)
    b.append(con("<p><b>Editable draw.io version</b> of the simplified map above (teaching aid — fully editable in diagrams.net or VS Code). SAP&apos;s <b>official</b> editable source is a separate download (link below).</p>"))
    b.append(drawio("Simplified A2A+MCP map (teaching aid, editable)", DRAWIO_XML, "Boxes and arrows mirror the official architecture at teaching size.", "a2a-mcp-simplified.drawio"))
    b.append(imp("<p>Diagram files: <code>a2a-mcp-simplified.drawio</code> (this portal&apos;s teaching map, sibling of the HTML) and SAP&apos;s official <code>sap-a2a-mcp.drawio</code> — also downloadable from <a href=https://architecture.learning.sap.com/architecture-94e69ed0b04d11c2.drawio>architecture.learning.sap.com</a>, editable online at draw.io (save locally to keep changes).</p>"))
    b.append(off("<p><b>Zone roster — every named item in the official diagram, mapped:</b></p>"))
    b.append(table(
["Diagram item", "Covered as", "Section"],
[
("User, Application clients", "user node (click it)", "04 here"),
("SAP Business AI Platform", "zone background + s05", "04/05"),
("Signavio, Agent/Behavior Mining", "signavio node + s05", "04/05"),
("LeanIX, AI Agent Hub", "leanix node + s05", "04/05"),
("Joule Work, Joule Studio", "studio node + s06/s07", "06/07"),
("Custom Agents, Intent-Based Development, MCP Builder", "custom + mcpbuilder nodes + s07/s16", "07/16"),
("Joule Orchestrator, Skills, A2A links", "orch + skills nodes + s08", "08"),
("Managed Runtimes (agents + MCP servers)", "runtimes node + s09", "09"),
("Agent Gateway", "agentgw node + s10", "10"),
("Tools, Data, Products, Grounding, Knowledge Graph", "tools node + s11", "11"),
("MCP Servers, MCP (protocol)", "mcpint/extmcp nodes + s12", "12"),
("MCP Gateway (Integration Suite)", "mcpgw node + s13", "13"),
("SAP BTP, Subaccount", "zone background + s15", "15"),
("Bring Your Own Agent", "byoa node + s17", "17"),
("Third party: MCP server, API, AI Agents and Clients", "extmcp/extag nodes + s18", "18"),
("Google, Azure, AWS, IBM, Others", "clouds node + s18", "18"),
("External identity provider", "s18 + s19 (federation)", "18/19"),
("OData/REST", "odata node + s12/s22", "12"),
("Autonomous Suite: Finance, Spend, SCM, HCM, CX, Industry AI", "autosuite node + grid below", "04 here"),
]
))
    b.append(off(
"<p><b>Autonomous Suite (conceptual):</b> SAP&apos;s autonomous business applications — the processes agents ultimately serve. Relation to the agent ecosystem: suite capabilities surface as governed tools/APIs that agents consume; agents never bypass suite authorization. Do not invent implementation wiring beyond this.</p>"
))
    b.append(grid([
("Autonomous Finance", "Agents reconcile, file and explain — via finance tools, not direct ledgers."),
("Autonomous Spend", "Procurement agents check policy, suppliers and budgets through tools."),
("Autonomous SCM", "Supply agents read schedules, stock and logistics APIs."),
("Autonomous HCM", "People-process agents act strictly within HR authorization."),
("Autonomous CX", "Service agents resolve cases across order and knowledge tools."),
("Industry AI", "Vertical capabilities composed from the same A2A+MCP fabric."),
], 3))
    parts.append(sec("s04", "04", "Major Architectural Zones", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>SAP Business AI Platform (BAIP)</b> is the SAP-managed platform layer in the diagram: Joule Work plus related AI capabilities. Two named neighbors matter architecturally:</p>"
"<p><b>Signavio (with Agent Mining / behavior mining):</b> process knowledge — how work really flows — which agentic behavior can consult. SAP lists Agent Behavior Mining among related architectures. <b>LeanIX (AI Agent Hub):</b> the agent landscape view — discovery of which agents exist and governance over them. SAP lists related discovery/governance guidance under LeanIX topics.</p>"
"<p>Relationship: Signavio explains <i>how the business runs</i>; LeanIX tracks <i>which agents exist and may run</i>; Joule Work <i>builds and runs</i> them. Do not invent APIs between them beyond what SAP documents.</p>"
))
    b.append(imp(
"<p>Practical reading: when a box says Signavio or LeanIX, ask which of the three questions it answers — process truth, landscape truth, or execution. That is the entire relationship the diagram asserts.</p>"
))
    parts.append(sec("s05", "05", "SAP Business AI Platform", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Joule Work</b> groups: <b>Joule Studio</b> (build), <b>Custom Agents</b> (built agents), <b>Intent-Based Development</b> (describe intent, get agent scaffolding), <b>MCP Builder</b> (wrap capabilities as MCP tools), <b>Joule Orchestrator</b> (plan + run), <b>Skills</b> (reusable capabilities), <b>A2A</b> (agent links), <b>Managed Runtimes</b> (where they execute), <b>Agent Gateway</b> (inbound A2A door). Flow inside: Studio builds → runtimes host → orchestrator plans → skills/agents execute → A2A links outward.</p>"
))
    b.append(con(
"<p>Think of a theater company: Studio is rehearsal+scripts, runtimes are stages, orchestrator is the director, skills are rehearsed acts, agents are actors, A2A is guest-artist contracts, Agent Gateway is the stage door.</p>"
))
    parts.append(sec("s06", "06", "Joule Work", "\n".join(b)))

    b = []
    b.append(con(
"<p><b>Beginner:</b> Joule Studio is the workshop where you describe what you want (intent) and assemble <b>custom agents</b> without writing all the plumbing. <b>MCP Builder</b> turns an existing API into a tool any agent can discover.</p>"
))
    b.append(off(
"<p><b>Enterprise:</b> intent-based development lowers build cost for departmental agents; custom agents deploy to managed runtimes with identity and lifecycle; MCP Builder feeds the internal tool catalog that orchestrator skills consume. Enterprises use these to productize tribal capability (a pricing desk, a compliance checker) as governed agents instead of one-off scripts.</p>"
))
    b.append(imp("<p>Studio-built vs pro-code: Studio covers low-code composition; pro-code agents integrate as A2A servers (see BYOA, Section 17).</p>"))
    parts.append(sec("s07", "07", "Joule Studio", "\n".join(b)))

    return parts
