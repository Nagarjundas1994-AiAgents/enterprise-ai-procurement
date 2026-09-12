"""Portal part 8: s28 production architecture + s29 limitations."""
from common import code, table, grid, steps, qa, quiz, mermaid
from ix import sec, off, con, ex, imp, QUIZ_BANK

Q = {q[0]: q for q in QUIZ_BANK}


def qx(qid):
    q = Q[qid]
    return quiz(q[0], q[1], q[2], q[3])


def build():
    parts = []

    b = []
    b.append(con("<p>This simplified production lens does not replace SAP&apos;s official diagram — it is the same content viewed by <b>who operates it</b>.</p>"))
    b.append(table(
["Side", "Contains", "Operated by"],
[
("SAP-managed", "Business AI Platform, Joule capabilities, managed runtimes, Identity Services", "SAP"),
("Customer-managed", "BTP subaccount, custom agents, customer integrations, MCP Gateway, customer APIs", "Customer"),
("Third-party", "External agents, MCP servers, APIs, clouds, external IdP", "Vendors"),
("Identity (spanning)", "Trust roots, App2App dependencies, token validation", "SAP + customer + vendors jointly"),
("Network", "SAP-managed domains, customer routes, vendor endpoints", "Each side its own"),
("Agent / Tool / Data", "Agents reason, tools execute, data grounds — everywhere", "Per owner above"),
]
))
    b.append(off(
"<p><b>Third-party area, operationally:</b> Tools, MCP Server, API, AI Agents and Clients, cloud platforms, identity provider — each relationship needs explicit trust, discovery and governance. <b>Production security, tied to the diagram:</b> identity (IAS everywhere), authentication (tokens per call), authorization (least privilege per tool/capability), token validation (signature/expiry/audience), trust (recognized, not permissive), API protection (gateway policy), MCP governance (lifecycle + monitoring), A2A security (App2App + named user), audit (who delegated what), monitoring/tracing (adoption + anomaly), rate limiting (quotas per caller).</p>"
))
    b.append(qx("xq11"))
    b.append(qx("xq12"))
    parts.append(sec("s28", "28", "Production Architecture", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Transitional-state reminder (SAP&apos;s own disclaimer):</b> some boxes are direction, not product. Bidirectional third-party/self-hosted communication through Agent Gateway is <b>not yet supported</b>; full capability <b>expected soon and will evolve the architecture</b>. Treat every HOW-TO here as pattern-plus-verification: <b>check current SAP documentation before implementing in production</b>. Never claim all customers can deploy every box today.</p>"
))
    b.append(con(
"<p><b>What the diagram does NOT show explicitly</b> (abstraction is intentional): network routing, token contents, exact API payloads, database schemas, LLM internals, prompt implementation, application code, CI/CD, detailed logging/monitoring implementations, exact customer app implementation. These live in product docs and your engineering — the diagram shows relationships, not implementations.</p>"
))
    parts.append(sec("s29", "29", "Current Limitations", "\n".join(b)))

    return parts
