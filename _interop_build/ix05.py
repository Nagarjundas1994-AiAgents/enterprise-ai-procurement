"""Portal part 5: s15 BTP + s16 custom + s17 BYOA + s18 third-party + s19 IAS."""
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
"<p>The <b>BTP customer-managed area</b> holds: the <b>BTP subaccount</b> (your fenced cloud plot), <b>custom agents</b> you build, <b>bring-your-own agents</b> you host, the <b>MCP Gateway</b> (Integration Suite), and your <b>OData/REST APIs</b>. Customer controls: deployments, integrations, gateway policy, destinations, subaccount users. SAP manages: the platform underneath, BAIP, Joule, Identity Services, managed runtimes.</p>"
))
    b.append(mermaid("WHO RUNS WHAT", "flowchart LR\n  SAP[SAP-managed: BAIP, Joule, runtimes, IAS] --- BTP[BTP subaccount: YOUR agents, gateway, APIs]"))
    parts.append(sec("s15", "15", "SAP BTP", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Custom agents</b> are customer-built agents living in the BTP area — low-code from Studio or pro-code exposing an <b>A2A server endpoint</b>, which is the primary mechanism making them discoverable and usable by Joule and others. What the customer deploys: agent code, its A2A endpoint, its tool needs, its identity registration.</p>"
))
    b.append(qx("xq04"))
    parts.append(sec("s16", "16", "Custom Agents", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>Bring Your Own Agent (outbound):</b> Joule calls <b>external code-based agents</b> built with any A2A-supporting framework. <b>Pro-code vs low-code:</b> low-code (Joule Studio) composes prebuilt blocks fast but within Studio guardrails; pro-code agents (any language/framework) implement fully custom logic and integrate as A2A servers — A2A makes the two interchangeable to callers. Mechanics per SAP: Joule sends an A2A <code>message/send</code> request carrying the user utterance (<b>text type only, currently</b>); <b>synchronous answers expected within 60 seconds</b> (handling delegated to capability/scripting); <b>async push</b> to a Joule-provided webhook for long tasks; <b>multi-turn</b> via server-generated context/task IDs stored in runtime variables; <b>IAS App2App trust</b> between Joule and the agent server secures inbound validation.</p>"
))
    b.append(ex(
"<p><b>Conceptual illustration</b> of the pattern:</p>"
))
    b.append(mermaid(
"BYOA CHAIN (CONCEPTUAL)",
"flowchart TD\n  J[SAP Joule] -->|A2A| C[Customer-built Agent]\n  C -->|MCP| S[Customer MCP Server]\n  S --> E[Enterprise API]"
))
    parts.append(sec("s17", "17", "Bring Your Own Agent", "\n".join(b)))

    b = []
    b.append(off(
"<p>The <b>3rd Party area</b>: external <b>Tools, MCP Servers, APIs, AI Agents and clients</b>, the <b>clouds they run on (Google Cloud, Microsoft Azure, AWS, IBM Cloud, others)</b>, and their <b>identity provider</b>. The boundary matters because trust, discovery and governance must be negotiated per relationship — nothing is implied. Clouds appear to state <b>interoperability scope</b>: agents built on Vertex AI, Copilot Studio or Bedrock AgentCore collaborate over open A2A. Presence in the picture is <b>not a turnkey availability guarantee</b> — verify current SAP documentation per integration.</p>"
))
    b.append(mermaid("SAME CONTRACT, ANY CLOUD", "flowchart TD\n  S[SAP Agent] <-->|A2A| G[Google Agent]\n  S <-->|A2A| A[Azure Agent]\n  S <-->|A2A| W[AWS Agent]"))
    b.append(qx("xq15"))
    b.append(qx("xq13"))
    parts.append(sec("s18", "18", "Third-Party Agents", "\n".join(b)))

    b = []
    b.append(off(
"<p><b>SAP Cloud Identity Services (IAS)</b> is the identity layer: <b>identity</b> (who/what something is), <b>authentication</b> (proving it), <b>trust</b> (relationships letting tokens cross boundaries), <b>token handling</b> (App2App tokens with user context), <b>user context</b> (on whose behalf), and <b>application-to-application communication</b> (service identities). Three inequalities to memorize: <b>Identity is not authorization. Authentication is not authorization. Trust is not permission.</b></p>"
))
    b.append(con("<p>Passport office: IAS <b>issues and verifies passports</b> (identity). Each country (service) still decides <b>visas</b> (authorization). A passport alliance (trust) only means passports are <i>recognized</i> — never automatic entry.</p>"))
    parts.append(sec("s19", "19", "SAP Cloud Identity Services", "\n".join(b)))

    return parts
