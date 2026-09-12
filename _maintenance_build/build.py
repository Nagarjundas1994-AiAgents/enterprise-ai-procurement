"""Assemble the AssetOps Maintenance masterclass HTML (91 chapters, CH00-CH90)."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import build_tpl
import content_m01
import content_m02
import content_m03
import content_m04
import content_m05
import content_m06
import content_m07
import content_m08
import content_m09
import content_m10
import content_m11
import content_m12
import content_m13

build_tpl.OUT = os.path.join(os.path.dirname(__file__), "..", "Autonomous-Asset-Maintenance-Control-Tower-Masterclass.html")

build_tpl.NAV = [
    ("Start", [
        ("top", "00", "Welcome &amp; master model"),
        ("roadmap", "&#9679;", "Journey &amp; build status"),
        ("c00", "00", "Prerequisites &amp; environment"),
        ("c01", "01", "What are we building?"),
        ("c02", "02", "SAP architecture diagram"),
        ("c03", "03", "App architecture fundamentals"),
    ]),
    ("CAP project", [
        ("c04", "04", "Create the CAP project"),
        ("c05", "05", "Folder structure"),
        ("c06", "06", "CDS fundamentals"),
        ("c07", "07", "Database model"),
        ("c08", "08", "Associations &amp; compositions"),
        ("c09", "09", "Seed business data"),
    ]),
    ("Services", [
        ("c10", "10", "Create CAP services"),
        ("c11", "11", "Implement CRUD"),
        ("c12", "12", "OData V4"),
        ("c13", "13", "CAP validation"),
        ("c14", "14", "CAP transactions"),
        ("c15", "15", "Error handling"),
        ("c16", "16", "Paging, filter, sort"),
        ("c17", "17", "PostgreSQL local DB"),
        ("c18", "18", "HANA Cloud"),
    ]),
    ("UI5", [
        ("c19", "19", "Build the UI5 app"),
        ("c20", "20", "UI5 routing"),
        ("c21", "21", "UI5 models"),
        ("c22", "22", "OData V4 from UI5"),
        ("c23", "23", "UI5 CRUD"),
        ("c24", "24", "Fragments &amp; dialogs"),
        ("c25", "25", "Formatters &amp; types"),
        ("c26", "26", "UI5 validation &amp; errors"),
        ("c27", "27", "Equipment dashboard"),
        ("c28", "28", "Equipment details"),
        ("c29", "29", "Sensor monitoring"),
        ("c30", "30", "Maintenance orders"),
        ("c31", "31", "Technician management"),
        ("c32", "32", "Spares &amp; inventory"),
        ("c33", "33", "Production scheduling"),
    ]),
    ("Trust & integration", [
        ("c34", "34", "Authentication"),
        ("c35", "35", "Authorization"),
        ("c36", "36", "OAuth2 &amp; JWT"),
        ("c37", "37", "Destination service"),
        ("c38", "38", "External API integration"),
        ("c39", "39", "Event-driven CAP"),
    ]),
    ("Agents & MCP", [
        ("c40", "40", "AI architecture"),
        ("c41", "41", "Maintenance agent"),
        ("c42", "42", "MCP fundamentals"),
        ("c43", "43", "Build an MCP server"),
        ("c44", "44", "Build MCP tools"),
        ("c45", "45", "MCP tool security"),
    ]),
    ("A2A fleet", [
        ("c46", "46", "A2A communication"),
        ("c47", "47", "Inventory agent"),
        ("c48", "48", "Workforce agent"),
        ("c49", "49", "Production agent"),
        ("c50", "50", "Agent discovery"),
        ("c51", "51", "Agent authentication"),
        ("c52", "52", "Agent authorization"),
        ("c53", "53", "A2A orchestration"),
        ("c54", "54", "Human-in-the-loop"),
    ]),
    ("Agent ops", [
        ("c55", "55", "Agent audit logging"),
        ("c56", "56", "Agent observability"),
        ("c57", "57", "AI failure handling"),
        ("c58", "58", "Retry &amp; idempotency"),
        ("c59", "59", "Prompt injection &amp; AI security"),
        ("c60", "60", "Multi-tenant security"),
    ]),
    ("Testing", [
        ("c61", "61", "Testing strategy"),
        ("c62", "62", "Unit testing"),
        ("c63", "63", "Integration testing"),
        ("c64", "64", "API testing"),
        ("c65", "65", "Security testing"),
        ("c66", "66", "MCP testing"),
        ("c67", "67", "A2A testing"),
        ("c68", "68", "Agent testing"),
    ]),
    ("Ship", [
        ("c69", "69", "Docker"),
        ("c70", "70", "Production-like local env"),
        ("c71", "71", "CI/CD"),
        ("c72", "72", "GitHub Actions"),
        ("c73", "73", "BTP Cloud Foundry"),
        ("c74", "74", "mta.yaml"),
        ("c75", "75", "BTP service config"),
        ("c76", "76", "HANA Cloud deployment"),
        ("c77", "77", "Auth deployment"),
        ("c78", "78", "Destination deployment"),
    ]),
    ("Produce", [
        ("c79", "79", "Deploy to DEV"),
        ("c80", "80", "DEV smoke testing"),
        ("c81", "81", "STAGING environment"),
        ("c82", "82", "Production readiness"),
        ("c83", "83", "Production deployment"),
        ("c84", "84", "Post-deployment validation"),
        ("c85", "85", "Monitoring"),
        ("c86", "86", "Troubleshooting"),
        ("c87", "87", "Rollback"),
        ("c88", "88", "Incident handling"),
        ("c89", "89", "Final end-to-end scenario"),
        ("c90", "90", "Production go-live checklist"),
    ]),
]

build_tpl.CONTENT_MODULES = [content_m01, content_m02, content_m03, content_m04, content_m05,
                             content_m06, content_m07, content_m08, content_m09, content_m10,
                             content_m11, content_m12, content_m13]

build_tpl.ROADMAP = [
    ("P0", "Foundation (00-03)", "Env, scenario, SAP diagram, fundamentals", "done"),
    ("P1", "CAP project (04-05)", "Scaffold + folder tour", "done"),
    ("P2", "CDS + data (06-09)", "Model, relations, seed", "done"),
    ("P3", "Services (10-16)", "CRUD, OData, validation, tx, errors, paging", "done"),
    ("P4", "Databases (17-18)", "Postgres local, HANA Cloud", "done"),
    ("P5", "UI5 core (19-26)", "App, routing, models, CRUD, dialogs, format", "done"),
    ("P6", "Plant screens (27-33)", "Dashboard, equipment, sensors, orders, crew", "done"),
    ("P7", "Trust + events (34-39)", "Auth, OAuth, destination, API, events", "done"),
    ("P8", "Agents + MCP (40-45)", "Maintenance agent, MCP server + tools", "done"),
    ("P9", "A2A fleet (46-54)", "3 agents, discovery, auth, orchestration, HITL", "done"),
    ("P10", "Agent ops (55-60)", "Audit, tracing, failure, retry, security", "done"),
    ("P11", "Testing (61-68)", "Unit to agent tests", "done"),
    ("P12", "Ship (69-78)", "Docker, CI/CD, CF, MTA, services", "done"),
    ("P13", "Produce (79-90)", "DEV to prod, rollback, incident, E2E", "done"),
]

build_tpl.FOOTER = """
<footer class="site"><div class="wrap">
  <p><strong>Autonomous Asset Maintenance &amp; Operations Control Tower &mdash; SAP CAP from Zero to Production, Chapters 00-90.</strong> Domain: industrial asset maintenance (CNC-MACHINE-102, Bangalore plant). Sources: official CAP docs, npm <code>@cap-js/mcp</code> / <code>@cap-js/agents</code>, modelcontextprotocol.io, a2a-protocol.org, SAP Architecture Center RA0029. Verify fast-moving SAP service APIs against current SAP documentation. Labels CURRENT / LEGACY / LEARNING-MOCK mark every environment claim.</p>
  <p>No application can guarantee zero production defects. This course reduces defects and surprises through testing, observability, readiness gates and rollback planning.</p>
</div></footer>
</main>
<aside class="rail"><h2>On this page</h2><nav id="railLinks"></nav>
  <p class="mode-note">Toggle <strong>Architect mode</strong> in the top bar to hide beginner scaffolding on concept modules.</p>
</aside>
</div>
"""

if __name__ == "__main__":
    build_tpl.main()
