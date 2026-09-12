"""Assemble the __PROJECT_SHORT_NAME__ masterclass HTML.

This file grows incrementally: NAV lists only sections that actually exist
(content_partN.build() is real, non-placeholder content). Sections not yet
written are not linked from the sidebar — they are tracked honestly in the
"roadmap" section instead (status column). Add one `import content_partN`
line and one entry to CONTENT_MODULES each time you write a new file; add
matching entries to NAV (once the module is real) and ROADMAP (as soon as
the level is planned, before it's written — see ROADMAP's own comment).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import common
# NOTE: content modules are injected by build.py (maintenance course); no static imports here.

OUT = os.path.join(os.path.dirname(__file__), "..", "__PROJECT_SLUG__-Masterclass.html")

# (group label, [(id, num, short nav label)]) — list ONLY modules that are
# actually written (see SKILL.md). Add a group/entry the same commit you add
# the content_partN.py module that implements it.
NAV = [
    ("Start", [
        ("top", "00", "Welcome &amp; the master model"),
        ("roadmap", "&#9679;", "Journey &amp; build status"),
        ("m01", "01", "The business problem"),
        ("m02", "02", "How an architect thinks"),
        ("m03", "03", "The central architecture"),
    ]),
    # ("SAP BTP & CAP foundations", [("m04", "04", "SAP BTP foundation"), ...]),
    # ... one group per NAV section in the master-prompt template's Level list.
]

CONTENT_MODULES = []  # injected by build.py
# CONTENT_MODULES = [content_part1, content_part2, ...]  # append as you go

# Full intended 20-level journey — matches SAP-Agentic-Masterclass-Prompt-Template.md's
# Section 13. Renders as the honest roadmap table/pills near the top of the document;
# flip a row to "done" the same commit its level's modules land in NAV above. Reword
# the middle column with this project's own domain nouns as you fill in the template.
# (level, title, what-it-adds, status: "done" | "pending")
ROADMAP = [
    ("L0", "The business problem", "Why this project exists; the business scenario", "done"),
    ("L1", "Architecture thinking", "How a Solution Architect approaches this build", "done"),
    ("L2", "SAP BTP foundation", "Cloud Foundry, HANA Cloud, destinations, auth", "pending"),
    ("L3", "CAP foundation", "CDS domain model, services, handlers, XSUAA", "pending"),
    ("L4", "S/4HANA integration", "cds import, remote services, Destination, Cloud Connector", "pending"),
    ("L5", "RAG platform", "Chunking, embeddings, HANA Vector Engine, hybrid search", "pending"),
    ("L6", "SAP AI Core &amp; Gen AI Hub", "Model orchestration, deployments, prompt config", "pending"),
    ("L7", "First LangGraph agent", "StateGraph, tools, reasoning loop, guardrails", "pending"),
    ("L8", "MCP tool layer", "MCP server, domain-specific governed tools", "pending"),
    ("L9", "Multi-agent + A2A", "Supervisor + specialist agents, Agent Cards", "pending"),
    ("L10", "A2UI &amp; MCP Apps", "Declarative UI specs + sandboxed interactive apps, both rendered by a trusted host", "pending"),
    ("L11", "Human-in-the-loop", "Autonomy levels, approval workflow", "pending"),
    ("L12", "Security &amp; AI security", "XSUAA/IAS chain, prompt-injection defence, control matrix", "pending"),
    ("L13", "Event-driven architecture", "Event Mesh, the domain's triggering event, autonomous investigation", "pending"),
    ("L14", "Multi-tenancy", "MTX, tenant-isolated data and vector stores", "pending"),
    ("L15", "Observability", "Tracing, cost, correlation IDs, agent runs", "pending"),
    ("L16", "Testing strategy", "Unit &#8594; agent &#8594; RAG &#8594; E2E, golden datasets", "pending"),
    ("L17", "DevOps &amp; deployment", "CI/CD, MTA, BTP, command reference", "pending"),
    ("L18", "Production hardening", "Resilience, failure modes, cost, performance", "pending"),
    ("L19", "Capstone &amp; final architecture", "The flagship end-to-end scenario, production poster", "pending"),
]


def _status_badge(status):
    return ('<span class="badge ga">Built</span>' if status == "done"
            else '<span class="badge verify">Coming next</span>')


def build_roadmap_section():
    done_count = sum(1 for r in ROADMAP if r[3] == "done")
    pills = "".join(
        f'<span class="pill{" on" if status == "done" else ""}">{lvl} &middot; {title}</span>'
        for lvl, title, desc, status in ROADMAP
    )
    rows = "".join(
        f'<tr><td>{lvl}</td><td>{title}</td><td>{desc}</td><td>{_status_badge(status)}</td></tr>'
        for lvl, title, desc, status in ROADMAP
    )
    return f'''<section class="mod" id="roadmap" data-mod="roadmap">
  <div class="modhead"><span class="modnum">{done_count}/{len(ROADMAP)} LEVELS BUILT</span></div>
  <h2>The twenty-level journey &mdash; and where this document is right now</h2>
  <p>This course is written level by level, in the same one-repository, nothing-thrown-away spirit Level 2 preaches
  for the codebase itself. Every row below either has a real module in the sidebar you can read right now, or is
  honestly marked as not written yet &mdash; there is no placeholder content hiding behind a &ldquo;coming soon&rdquo;
  link anywhere in this document.</p>
  <div class="pills">{pills}</div>
  <div class="table-wrap"><table><thead><tr><th>Level</th><th>Title</th><th>What it adds</th><th>Status</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
</section>'''


def build_sidenav():
    out = []
    for i, (label, items) in enumerate(NAV):
        openattr = " open" if i < 4 else ""
        links = "".join(
            f'<a href="#{mid}"><span class="n">{num}</span><span class="dot"></span>{title}</a>'
            for mid, num, title in items
        )
        out.append(f'<details class="navg"{openattr}><summary class="g">{label}</summary>{links}</details>')
    return "".join(out)


def build_main():
    sections = []
    for m in CONTENT_MODULES:
        sections.append(m.build())
    flat = []
    for group in sections:
        flat.extend(group)
    flat.insert(1, build_roadmap_section())   # right after the hero (flat[0])
    return "\n".join(flat)


FOOTER = """
<footer class="site"><div class="wrap">
  <p><strong>__PROJECT_FULL_NAME__ &mdash; __PROJECT_ONE_LINE_DESCRIPTION__.</strong> One domain: __PROJECT_DOMAIN_ONE_PHRASE__. Sources: official CAP docs, SAP Business Accelerator Hub, SAP Cloud SDK for AI, npm <code>@cap-js/mcp</code> / <code>@cap-js/agents</code>, a2ui.org, a2a-protocol.org, architecture.learning.sap.com (RA0029 &mdash; Agentic AI &amp; AI Agents; A2A + MCP Interoperability).</p>
  <p>Protocol concepts (MCP, A2A, A2UI, MCP Apps, AG-UI) are described per their public specifications. Statements about specific SAP product capabilities (Joule, AI Core, Fiori integrations) are marked conceptual where they extend beyond current public SAP documentation.</p>
</div></footer>
</main>
<aside class="rail"><h2>On this page</h2><nav id="railLinks"></nav>
  <p class="mode-note">Toggle <strong>Architect mode</strong> in the top bar to hide beginner scaffolding on concept modules.</p>
</aside>
</div>
"""

JS = r"""
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>
<script>
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  /* Mermaid diagrams render on a fixed light "drafting sheet" (see .diagram CSS),
     so one static light theme covers both page themes — no re-render-on-toggle needed. */
  if (window.mermaid) {
    mermaid.initialize({
      startOnLoad: false,
      theme: "base",
      fontFamily: '"IBM Plex Mono", monospace',
      flowchart: { htmlLabels: true, useMaxWidth: true },
      themeVariables: {
        primaryColor: "#E7ECF8", primaryTextColor: "#1A2333", primaryBorderColor: "#0B3D91",
        lineColor: "#47536A", secondaryColor: "#E3F2F1", tertiaryColor: "#F9EEDC",
        background: "transparent", mainBkg: "#E7ECF8",
        actorBkg: "#E7ECF8", actorBorder: "#0B3D91", actorTextColor: "#1A2333",
        signalColor: "#47536A", signalTextColor: "#1A2333",
        labelBoxBkgColor: "#F9EEDC", labelBoxBorderColor: "#B5710A",
        noteBkgColor: "#F9EEDC", noteBorderColor: "#B5710A",
        activationBkgColor: "#E3F2F1", sequenceNumberColor: "#1A2333",
        textColor: "#1A2333", nodeTextColor: "#1A2333",
        clusterBkg: "#E7ECF8", clusterTextColor: "#1A2333",
        titleColor: "#1A2333",
      },
      securityLevel: "strict",
    });
    function mermaidFillIsDark(raw) {
      if (!raw) return false;
      const s = String(raw).trim().toLowerCase();
      if (!s || s === "none" || s === "transparent") return false;
      let r, g, b;
      const hex = s.match(/^#([0-9a-f]{3,8})$/);
      const rgb = s.match(/^rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)/);
      if (hex) {
        let h = hex[1];
        if (h.length === 3) h = h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
        r = parseInt(h.slice(0,2), 16); g = parseInt(h.slice(2,4), 16); b = parseInt(h.slice(4,6), 16);
      } else if (rgb) {
        r = +rgb[1]; g = +rgb[2]; b = +rgb[3];
      } else return false;
      return (0.2126*r + 0.7152*g + 0.0722*b) < 140;
    }
    function fixMermaidContrast() {
      $$(".diagram svg, svg[id^='mermaid']").forEach((svg) => {
        if (!svg.closest(".diagram")) return;
        svg.querySelectorAll("g.node, g.actor, g.cluster").forEach((g) => {
          const shapes = Array.from(g.querySelectorAll("rect.label-container, circle.label-container, rect, circle, polygon, ellipse"));
          const shape = shapes.find((el) => /fill\s*:\s*#|fill\s*:\s*rgb/i.test(el.getAttribute("style") || "") || (el.getAttribute("fill") && el.getAttribute("fill") !== "none")) || shapes[0];
          if (!shape) return;
          const fill = ((shape.getAttribute("style") || "").match(/fill:\s*([^;!]+)/) || [])[1] || shape.getAttribute("fill") || getComputedStyle(shape).fill;
          const dark = mermaidFillIsDark(fill);
          g.classList.toggle("darklabel", dark);
          const color = dark ? "#FFFFFF" : "#1A2333";
          g.querySelectorAll("foreignObject, foreignObject *").forEach((el) => { el.style.setProperty("color", color, "important"); });
          g.querySelectorAll("text, tspan").forEach((el) => { el.style.setProperty("fill", color, "important"); });
        });
      });
    }
    // Render each diagram independently (rather than one shared querySelector batch) so a
    // syntax error in one diagram can't make every other diagram on the page report failed.
    Promise.allSettled($$(".mermaid").map((el) =>
      mermaid.run({ nodes: [el] }).catch((err) => {
        el.insertAdjacentHTML("afterend", "<p style='color:#B23A2E;font-size:12px'>Diagram failed to render: " + String(err?.message || err).slice(0, 160) + "</p>");
        throw err;
      })
    )).then(fixMermaidContrast);
  }

  const KEY = "__STORAGE_KEY__";
  let store = {};
  try { store = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { /* storage disabled (e.g. sandboxed file:// preview) */ }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch { /* ignore */ } }

  /* theme + mode */
  const themeBtn = $("#themeBtn");
  const modeBtn = $("#modeBtn");
  function applyTheme(t) {
    document.documentElement.dataset.theme = t;
    themeBtn.textContent = t === "night" ? "Day" : "Night";
    themeBtn.setAttribute("aria-pressed", t === "night" ? "true" : "false");
    document.querySelector('meta[name="theme-color"]').setAttribute("content", t === "night" ? "#0A1220" : "#F4F7FA");
  }
  function applyMode(m) {
    document.documentElement.dataset.mode = m;
    modeBtn.textContent = m === "architect" ? "Beginner mode" : "Architect mode";
    modeBtn.setAttribute("aria-pressed", m === "architect" ? "true" : "false");
  }
  applyTheme(store.theme || "day");
  applyMode(store.mode || "beginner");
  themeBtn.addEventListener("click", () => { store.theme = document.documentElement.dataset.theme === "night" ? "day" : "night"; applyTheme(store.theme); save(); });
  modeBtn.addEventListener("click", () => { store.mode = document.documentElement.dataset.mode === "architect" ? "beginner" : "architect"; applyMode(store.mode); save(); });

  /* nav + burger */
  const sidenav = $("#sidenav");
  const burger = $("#burger");
  const scrim = $("#scrim");
  function closeNav() { sidenav.classList.remove("open"); burger.setAttribute("aria-expanded", "false"); scrim.classList.remove("on"); scrim.hidden = true; }
  burger.addEventListener("click", () => {
    const open = sidenav.classList.toggle("open");
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    scrim.hidden = !open; scrim.classList.toggle("on", open);
  });
  scrim.addEventListener("click", closeNav);
  sidenav.addEventListener("click", (e) => { if (e.target.closest("a")) closeNav(); });

  /* progress */
  store.done = store.done || {};
  function paintProgress() {
    const boxes = $$("input[data-done]");
    let n = 0;
    boxes.forEach((box) => {
      const id = box.dataset.done;
      box.checked = !!store.done[id];
      if (box.checked) n += 1;
      const href = "#"+id;
      $$('.sidenav a[href="'+href+'"]').forEach((a) => a.classList.toggle("done", box.checked));
    });
    const total = boxes.length;
    $("#labprog").textContent = n + "/" + total;
  }
  document.addEventListener("change", (e) => {
    const box = e.target.closest("input[data-done]");
    if (!box) return;
    store.done[box.dataset.done] = box.checked;
    save(); paintProgress();
  });
  paintProgress();

  /* production readiness checklist — separate from module progress on purpose:
     "I checked this off" and "I read this module" are different claims */
  store.checked = store.checked || {};
  function paintReadiness() {
    const boxes = $$("input[data-check]");
    if (!boxes.length) return;
    let n = 0;
    boxes.forEach((box) => { box.checked = !!store.checked[box.dataset.check]; if (box.checked) n += 1; });
    const pct = Math.round((n / boxes.length) * 100);
    $("#readinessScore").textContent = `Production readiness: ${n}/${boxes.length} (${pct}%)`;
  }
  document.addEventListener("change", (e) => {
    const box = e.target.closest("input[data-check]");
    if (!box) return;
    store.checked[box.dataset.check] = box.checked;
    save(); paintReadiness();
  });
  paintReadiness();

  /* quizzes */
  document.addEventListener("change", (e) => {
    const inp = e.target.closest('.quiz input[type="radio"]');
    if (!inp) return;
    const box = inp.closest(".quiz");
    box.querySelectorAll(".ok,.no").forEach((n) => n.remove());
    const p = document.createElement("p");
    const right = inp.value === "ok";
    p.className = right ? "ok" : "no";
    p.textContent = (right ? "Correct. " : "Not quite. ") + (box.dataset.why || "");
    box.appendChild(p);
  });

  /* syntax highlighting */
  const HL = {
    cds:        { c: /\/\/[^\n]*|\/\*[\s\S]*?\*\//, k: /\b(namespace|using|from|service|entity|as|projection|on|action|function|returns|array|of|key|type|aspect|extend|annotate|not|null|default|excluding|Composition|Association|many|to|UUID|String|Decimal|Integer|Date|Timestamp|Boolean)\b/ },
    javascript: { c: /\/\/[^\n]*|\/\*[\s\S]*?\*\//, k: /\b(const|let|var|function|async|await|return|if|else|for|while|new|this|module|exports|require|try|catch|throw|null|true|false|undefined|class|extends|SELECT|INSERT|UPDATE|DELETE|from|into|where|with|one)\b/ },
    typescript: { c: /\/\/[^\n]*|\/\*[\s\S]*?\*\//, k: /\b(const|let|var|function|async|await|return|if|else|for|while|new|this|import|export|from|interface|type|extends|implements|try|catch|throw|null|true|false|undefined|class|public|private|readonly)\b/ },
    python:     { c: /#[^\n]*/,                     k: /\b(def|async|await|return|import|from|class|if|elif|else|for|while|try|except|raise|with|as|None|True|False|and|or|not|in|is|lambda|yield|pass)\b/ },
    bash:       { c: /#[^\n]*/,                     k: /\b(cd|mkdir|npm|npx|pip|python|git|curl|cf|cds|mbt|source|export|echo|install|init|run|watch|build|deploy)\b/ },
    json:       { c: null,                          k: /\b(true|false|null)\b/ },
    yaml:       { c: /#[^\n]*/,                     k: /\b(true|false|null|modules|resources|requires|provides|parameters|properties|type|name|path|version|service)\b/ },
    sql:        { c: /--[^\n]*/,                    k: /\b(SELECT|FROM|WHERE|ORDER|BY|LIMIT|AS|DESC|ASC|JOIN|ON|AND|OR|NOT|NULL|INSERT|INTO|UPDATE|SET|DELETE)\b/i },
    html:       { c: new RegExp("<" + "!--[\\s\\S]*?--" + ">"), k: /\b(script|button|div|span|type|module|import|const|await|document)\b/ },
  };
  function escHtml(s) { return s.replace(/&/g, "&amp;").replace(/[<]/g, "&lt;").replace(/>/g, "&gt;"); }
  $$(".codeblock").forEach((fig) => {
    const lang = (fig.querySelector(".flang")?.textContent || "").trim().toLowerCase();
    const spec = HL[lang];
    const codeEl = fig.querySelector("pre > code");
    if (!spec || !codeEl) return;
    const src = codeEl.textContent;
    const parts = [
      spec.c ? spec.c.source : null,
      /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/.source,
      spec.k ? spec.k.source : null,
      /\b\d+(?:\.\d+)?\b/.source,
    ];
    const groups = [];
    const rxSrc = parts.filter((p, i) => { if (p) { groups.push(i); return true; } return false; })
                       .map((p) => "(" + p + ")").join("|");
    let rx;
    try { rx = new RegExp(rxSrc, "g"); } catch { return; }
    let out = "", last = 0, m;
    while ((m = rx.exec(src)) !== null) {
      out += escHtml(src.slice(last, m.index));
      const gi = m.slice(1).findIndex((g) => g !== undefined);
      const kind = ["tok-c", "tok-s", "tok-k", "tok-n"][groups[gi]];
      out += '<span class="' + kind + '">' + escHtml(m[0]) + "</span>";
      last = m.index + m[0].length;
    }
    out += escHtml(src.slice(last));
    codeEl.innerHTML = out;
  });

  /* copy */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".copy-btn");
    if (!btn) return;
    const pre = btn.closest("figure").querySelector("pre");
    try {
      await navigator.clipboard.writeText(pre.innerText);
      btn.textContent = "Copied"; btn.classList.add("ok");
      setTimeout(() => { btn.textContent = "Copy"; btn.classList.remove("ok"); }, 1400);
    } catch { btn.textContent = "Select + copy"; }
  });

  /* search */
  const q = $("#q");
  const status = document.createElement("p");
  status.id = "searchstatus";
  $(".hero")?.after(status);
  function clearHits() { $$("mark.hit").forEach((m) => m.replaceWith(document.createTextNode(m.textContent))); }
  function search(term) {
    clearHits();
    const t = term.trim().toLowerCase();
    const links = $$("#sidenav a[href^='#']");
    if (!t) { links.forEach((a) => a.hidden = false); status.textContent = ""; return; }
    let shown = 0, hits = 0;
    $$("section.mod, header.hero").forEach((sec) => {
      const text = sec.textContent.toLowerCase();
      const ok = text.includes(t);
      const id = sec.id ? "#"+sec.id : "";
      links.forEach((a) => { if (a.getAttribute("href") === id) { a.hidden = !ok; if (ok) shown += 1; } });
    });
    $$("section.mod h2, section.mod h3, section.mod p, .card p, td, .callout p, dt, dd").forEach((el) => {
      if (!el.childElementCount && el.textContent.toLowerCase().includes(t)) {
        const rx = new RegExp(t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "ig");
        el.innerHTML = el.textContent.replace(rx, (m) => { hits += 1; return "<mark class='hit'>"+m+"</mark>"; });
      }
    });
    status.textContent = hits ? `Highlighted ${hits} matches. Sidebar filtered to ${shown} sections.` : `No matches for "${term}".`;
  }
  q.addEventListener("input", () => search(q.value));
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== q && !e.metaKey && !e.ctrlKey && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
      e.preventDefault(); q.focus();
    }
    if (e.key === "Escape") { q.value = ""; search(""); q.blur(); }
  });

  /* scroll spy + readbar */
  const sections = $$("section.mod, header.hero");
  const navLinks = $$("#sidenav a[href^='#']");
  const rail = $("#railLinks");
  function buildRail() {
    rail.innerHTML = "";
    $$(".wrap > section.mod, .wrap > header.hero").forEach((sec) => {
      const h = sec.querySelector("h1, h2");
      if (!h || !sec.id) return;
      const a = document.createElement("a");
      a.href = "#"+sec.id;
      a.textContent = h.textContent.replace(/^MODULE.*/, "").slice(0, 44);
      rail.appendChild(a);
    });
  }
  buildRail();
  const io = new IntersectionObserver((ents) => {
    ents.forEach((en) => {
      if (!en.isIntersecting) return;
      const id = "#"+en.target.id;
      navLinks.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === id));
      $$("#railLinks a").forEach((a) => a.classList.toggle("active", a.getAttribute("href") === id));
    });
  }, { rootMargin: "-40% 0px -50% 0px", threshold: 0.01 });
  sections.forEach((s) => { if (s.id) io.observe(s); });
  window.addEventListener("scroll", () => {
    const el = $("#readbar > i");
    const max = document.documentElement.scrollHeight - innerHeight;
    el.style.width = (max > 0 ? (scrollY / max) * 100 : 0) + "%";
  }, { passive: true });

  /* tabs (used by playground + JSON explorer + capstone trace) */
  document.addEventListener("click", (e) => {
    const tab = e.target.closest(".tab[data-tabs]");
    if (!tab) return;
    const group = tab.dataset.tabs;
    $$('.tab[data-tabs="'+group+'"]').forEach((t) => t.setAttribute("aria-selected", t === tab ? "true" : "false"));
    $$('.tabpanel[data-tabs="'+group+'"]').forEach((p) => { p.hidden = p.id !== tab.dataset.panel; });
  });

  /* reference repo file explorer (populated once the build-it steps exist) */
  const FILES = __FILES_JSON__;
  function showFile(key) {
    $$("#repoExplorer nav button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.file === key ? "true" : "false"));
    const f = FILES[key];
    if (!f) return;
    $("#filePane").innerHTML = "<h4>"+f.title+"</h4><div class='meta'><div><b>Purpose.</b> "+f.purpose+"</div><div><b>Inputs.</b> "+f.inputs+"</div><div><b>Outputs.</b> "+f.outputs+"</div><div><b>Dependencies.</b> "+f.deps+"</div><div><b>Who calls it.</b> "+f.who+"</div><div><b>What runs next.</b> "+f.next+"</div>"+(f.extra ? "<div><b>Note.</b> "+f.extra+"</div>" : "")+"</div>";
  }
  $$("#repoExplorer nav button").forEach((b) => b.addEventListener("click", () => showFile(b.dataset.file)));
  if ($("#repoExplorer")) showFile($$("#repoExplorer nav button")[0]?.dataset.file);

  /* protocol decision tree */
  const TREE = __TREE_JSON__;
  const VERDICTS = __VERDICTS_JSON__;
  function renderTree(id) {
    const node = TREE[id];
    $("#treeVerdict").hidden = true;
    if (!node) return;
    $("#treeQ").textContent = node.q;
    $("#treeOpts").innerHTML = "";
    node.opts.forEach(([label, next]) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = label;
      btn.addEventListener("click", () => {
        if (TREE[next]) { renderTree(next); return; }
        const v = VERDICTS[next];
        if (!v) return;
        $("#decisionTree").hidden = true;
        const box = $("#treeVerdict");
        box.className = "verdict " + (v[0] === "a2a" ? "violet" : v[0] === "hana" ? "gold" : v[0] === "mcpapp" || v[0] === "a2ui" ? "teal" : "");
        box.innerHTML = "<strong>"+v[1]+"</strong><p style='margin-top:.5rem'>"+v[2]+"</p>";
        box.hidden = false;
      });
      $("#treeOpts").appendChild(btn);
    });
  }
  if ($("#decisionTree")) renderTree("start");
  $("#treeReset")?.addEventListener("click", () => { $("#decisionTree").hidden = false; renderTree("start"); });

  /* agent trace explorer */
  const TRACE = __TRACE_JSON__;
  const traceNodes = $$("#traceNodes button");
  function showTraceStage(key) {
    traceNodes.forEach((btn) => btn.classList.toggle("on", btn.dataset.stage === key));
    const s = TRACE[key];
    if (!s) return;
    $("#tracePane").innerHTML = "<b>"+s.title+"</b><span>"+s.body+"</span>"
      + (s.module ? "<span style='display:block;margin-top:.5rem'><a href='#"+s.module+"'>See "+s.moduleLabel+" &rarr;</a></span>" : "");
  }
  traceNodes.forEach((btn) => btn.addEventListener("click", () => showTraceStage(btn.dataset.stage)));
  if (traceNodes.length) showTraceStage(traceNodes[0].dataset.stage);

  /* roadmap timeline */
  const ROADTL = __ROADMAPTL_JSON__;
  const road = $("#roadTime");
  if (road) {
    ROADTL.forEach((lvl, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.innerHTML = '<span class="dot"></span><span class="lab"><b>'+lvl[0]+'</b><span>Click for the exercise</span></span>';
      b.addEventListener("click", () => {
        $$("#roadTime button").forEach((x) => x.classList.toggle("on", x === b));
        $("#roadExplain").innerHTML = "<strong>"+lvl[0]+".</strong> "+lvl[1];
      });
      road.appendChild(b);
    });
    road.querySelector("button")?.click();
  }
})();
</script>
"""


def main():
    import json
    sidenav = build_sidenav()
    main_html = build_main()
    # These four power optional interactive widgets (repo file explorer, protocol
    # decision tree, agent trace explorer) — {} is a safe no-op default. Once you
    # write the content_partN.py module that defines each dict (see SKILL.md's
    # helper API notes / the ProcureX AI build for the shape: FILES keyed by a
    # short id -> {title,purpose,inputs,outputs,deps,who,next}; TREE keyed by node
    # id -> {q, opts:[[label,next_id]]}; VERDICTS keyed by leaf id ->
    # [css_class, headline, body]; TRACE_STAGES keyed by stage id ->
    # {title,body,module,moduleLabel}), swap in `content_partN.FILES` etc. here.
    files_json = json.dumps({})
    tree_json = json.dumps({})
    verdicts_json = json.dumps({})
    trace_json = json.dumps({})
    js = (JS
          .replace("__STORAGE_KEY__", common.STORAGE_KEY)
          .replace("__FILES_JSON__", files_json)
          .replace("__TREE_JSON__", tree_json)
          .replace("__VERDICTS_JSON__", verdicts_json)
          .replace("__TRACE_JSON__", trace_json)
          .replace("__ROADMAPTL_JSON__", json.dumps([])))

    html = (common.HEAD
            + f'<nav class="sidenav" id="sidenav" aria-label="Course contents">{sidenav}</nav>\n'
            + '<main id="content"><div class="wrap">\n'
            + main_html
            + "\n</div>"
            + FOOTER
            + js
            + "\n</body>\n</html>\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote", os.path.abspath(OUT), len(html), "bytes")


if __name__ == "__main__":
    main()
