"""Assemble the A2A+MCP interop portal HTML."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import build_tpl
import ix01
import ix02
import ix03
import ix04
import ix05
import ix06
import ix07
import ix08
import ix09
import ix10

build_tpl.OUT = os.path.join(os.path.dirname(__file__), "..", "a2a-mcp-sap-architecture-explained.html")

build_tpl.NAV = [
    ("Read", [
        ("top", "00", "Hero: A2A + MCP"),
        ("roadmap", "&#9679;", "Portal map"),
        ("s01", "01", "Architecture at a glance"),
        ("s02", "02", "The original diagram"),
        ("s03", "03", "Read the diagram"),
        ("s04", "04", "Major architectural zones"),
    ]),
    ("SAP platform", [
        ("s05", "05", "SAP Business AI Platform"),
        ("s06", "06", "Joule Work"),
        ("s07", "07", "Joule Studio"),
        ("s08", "08", "Joule Orchestrator"),
        ("s09", "09", "Managed Runtimes"),
        ("s10", "10", "Agent Gateway"),
        ("s11", "11", "Tools"),
    ]),
    ("Protocols", [
        ("s12", "12", "MCP"),
        ("s13", "13", "MCP Gateway"),
        ("s14", "14", "A2A"),
    ]),
    ("Landscape", [
        ("s15", "15", "SAP BTP"),
        ("s16", "16", "Custom Agents"),
        ("s17", "17", "Bring Your Own Agent"),
        ("s18", "18", "Third-Party Agents"),
        ("s19", "19", "SAP Cloud Identity Services"),
    ]),
    ("Trust & flow", [
        ("s20", "20", "Trust"),
        ("s21", "21", "Authentication"),
        ("s22", "22", "Authorization"),
        ("s23", "23", "Discovery"),
        ("s24", "24", "Invocation"),
        ("s25", "25", "Complete Request Flow"),
        ("s26", "26", "A2A vs MCP"),
        ("s27", "27", "Inbound vs Outbound"),
    ]),
    ("Produce & revise", [
        ("s28", "28", "Production Architecture"),
        ("s29", "29", "Current Limitations"),
        ("s30", "30", "Beginner Summary"),
        ("s31", "31", "Architecture Cheat Sheet"),
        ("s32", "32", "FAQ"),
    ]),
]

build_tpl.CONTENT_MODULES = [ix01, ix02, ix03, ix04, ix05, ix06, ix07, ix08, ix09, ix10]

build_tpl.ROADMAP = [
    ("R1", "Glance + original + reading guide", "Hero, official diagram, 11 architect steps", "done"),
    ("R2", "Zones + SAP platform", "7 zones, BAIP, Joule Work/Studio", "done"),
    ("R3", "Runtime + gateways + tools", "Orchestrator, runtimes, Agent Gateway, tools layer", "done"),
    ("R4", "Protocols", "MCP, MCP Gateway, A2A", "done"),
    ("R5", "Landscape + identity", "BTP, custom/BYO/third-party, IAS", "done"),
    ("R6", "Trust + flow", "Trust, authN/Z, discovery, invocation, animated flow, comparison", "done"),
    ("R7", "Production + revision", "Prod view, limitations, summary, cheat sheet, FAQ", "done"),
]

build_tpl.FOOTER = """
<footer class="site"><div class="wrap">
  <p><strong>A2A and MCP for Interoperability &mdash; Interactive Learning Portal.</strong> Based on the official SAP Architecture Center reference architecture RA0029 (<a href="https://architecture.learning.sap.com/docs/ref-arch/76ec36">ref-arch/76ec36</a>, last updated Aug 27, 2026). Open standards: <a href="https://a2a-protocol.org/latest/">A2A</a>, <a href="https://modelcontextprotocol.io/">MCP</a>. Labels OFFICIAL / CONCEPTUAL / EXAMPLE / IMPLEMENTATION NOTE separate SAP statements from teaching aids. Availability uncertain anywhere: verify current SAP documentation.</p>
</div></footer>
</main>
<aside class="rail"><h2>On this page</h2><nav id="railLinks"></nav>
  <p class="mode-note">Toggle <strong>Architect mode</strong> in the top bar to hide beginner scaffolding.</p>
</aside>
</div>
"""

if __name__ == "__main__":
    build_tpl.main()
