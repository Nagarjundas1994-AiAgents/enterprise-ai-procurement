"""Portal part 6: s20 trust + s21 authentication + s22 authorization + s23 discovery/governance + s24 invocation."""
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
"<p>Green <b>Trust</b> edges answer <b>who trusts whom</b>: an IAS-mediated relationship (App2App dependencies, federated IdPs) letting one side <b>recognize the other&apos;s tokens</b>. Establishment (register dependency, exchange metadata) comes before any call; at call time: <b>authentication</b> (prove identity), <b>token validation</b> (signature, expiry, audience), then <b>authorization</b> (separate decision). <b>Trust never equals full permission</b> — it only means the bouncer recognizes your ID card.</p>"
))
    b.append(mermaid("TRUST LADDER", "flowchart TD\n  T[Trust established] --> A[Authenticate] --> V[Validate token] --> Z[Authorize action]"))
    b.append(qx("xq10"))
    parts.append(sec("s20", "20", "Trust", "\n".join(b)))

    b = []
    b.append(con("<p><b>AUTHENTICATION — “Who are you?”</b> vs <b>AUTHORIZATION — “What may you do?”</b> Apply to all six: <b>User</b> (SSO login, then scopes), <b>Agent</b> (registered identity + delegation, then tool grants), <b>MCP server</b> (service identity, then which tools it may expose), <b>A2A caller</b> (App2App token, then capability permission), <b>External system</b> (mutual trust, then API scopes), <b>Third-party cloud</b> (federated identity, then per-call permission).</p>"))
    b.append(off(
"<p>Mechanically: IAS issues/validates (users, App2App with named user context); services check signatures, expiry and audience on every call; failures surface as 401 (who) vs 403 (allowed) — never merged, never skipped for agents.</p>"
))
    b.append(qx("xq08"))
    parts.append(sec("s21", "21", "Authentication", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Authorization</b> is the per-call permission decision AFTER authentication: scopes/roles on APIs, tool grants on MCP servers, capability permissions on A2A endpoints, least-privilege service identities between systems. Agents are authorized like any caller — “because the AI called it” authorizes nothing.</p>"
))
    parts.append(sec("s22", "22", "Authorization", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Discover and Govern:</b> <b>discovery</b> = learning what exists (agent cards, MCP tool manifests, capability catalogs) — necessary because independently deployed things cannot be hardcoded. <b>Governance</b> = the lifecycle around them: who may publish, version, permission, monitor, audit and retire agents, tools, APIs and identities. <b>Discovery never implies authorization</b>: reading the menu does not order the dish.</p>"
))
    b.append(table(
["Governed object", "Discovery artifact", "Governance questions"],
[
("Agents", "Agent cards, capability + scenario IDs", "Who published? Who may call? Which version?"),
("Tools", "MCP manifests (tools/list)", "Who exposes? Rate limits? Payload rules?"),
("APIs", "Gateway catalogs", "Which scopes? Which quota?"),
("Identity", "Trust registries, App2App dependencies", "Which relationships? Still valid?"),
("Behavior", "Monitoring, tracing, analytics", "Who called what? Anomalies? Audit-ready?"),
]
))
    b.append(qx("xq07"))
    parts.append(sec("s23", "23", "Discovery", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Invocation</b> patterns in the diagram: <b>A2A task call</b> (message/send with task + context, sync confirmation or async callback), <b>MCP tool call</b> (tools/call with validated parameters, structured result), <b>API execution</b> underneath (HTTPS + service credentials). Every invocation carries identity, checks permission, and leaves a trace — the Section-25 flow shows all three in sequence.</p>"
))
    parts.append(sec("s24", "24", "Invocation", "\n".join(b)))

    return parts
