"""Shared CSS/JS/HTML scaffold + tiny render helpers for the __PROJECT_SHORT_NAME__
masterclass build. Part of the sap-masterclass-builder skill's design system —
copy this file per-project (don't share/import across projects) so each course
can evolve independently.

TODO before first build: fill in TITLE, SUBTITLE, STORAGE_KEY below, and the
brand <span> in HEAD's topbar (search this file for __BRAND_NAME__ /
__BRAND_TAGLINE__). Nothing else in this file should need to change — the CSS
and every helper function are project-agnostic and already debugged.
"""

TITLE = "Building a Production-Grade Autonomous Procurement Control Tower with SAP CAP, BTP, MCP &amp; A2A"
SUBTITLE = "End-to-End SAP CAP + AI Agent + MCP + A2A Hands-On Workshop"
STORAGE_KEY = "sap-procurement-control-tower-v1"

CSS = """
:root{
  --blue:#0B3D91;--blue-h:#092C6B;--blue-ink:#082253;--blue-soft:#E7ECF8;--blue-mid:#5C86D6;
  --teal:#0E7C86;--teal-soft:#E3F2F1;--green:#2E7D46;--green-soft:#E7F3EA;
  --violet:#6B46E8;--violet-soft:#EEE9FD;
  --gold:#B5710A;--gold-soft:#F9EEDC;
  --ink:#1A2333;--ink-2:#47536A;--ink-3:#6B7690;--mute:#8992A6;
  --bg:#F6F4EC;--bg-2:#EEEADE;--surf:#FCFBF6;--surf-2:#F1EEE4;
  --line:#DCD6C3;--line-2:#E7E2D2;--focus:#0B3D91;
  --ok:#2E7D46;--ok-bg:#E7F3EA;--warn:#B5710A;--warn-bg:#F9EEDC;--bad:#B23A2E;--bad-bg:#F8E7E4;
  --navy:#0B2545;--code:#0E1B33;--code-fg:#D9E2F3;
  --a2ui:#0B3D91;--mcpapp:#0E7C86;--mcp:#25539E;--a2a:#6B46E8;--cap:#0B3D91;--hana:#B5710A;
  --r:6px;--r-sm:3px;
  --sans:"IBM Plex Sans","Segoe UI",system-ui,sans-serif;
  --display:"Space Grotesk","IBM Plex Sans",system-ui,sans-serif;
  --mono:"IBM Plex Mono","Cascadia Code","Consolas",ui-monospace,monospace;
  --shadow:0 0 0 1px rgba(20,30,50,.05),0 2px 8px rgba(20,30,50,.05);
  --shadow-lg:0 0 0 1px rgba(20,30,50,.06),0 20px 46px rgba(20,30,50,.12);
  --navw:288px;--railw:236px;--max:800px;
  --grid-line:rgba(11,61,145,.07);
  color-scheme:light;
}
html[data-theme="night"]{
  --blue:#6FB1FF;--blue-h:#9FCBFF;--blue-ink:#BFDCFF;--blue-soft:#132D57;--blue-mid:#2C4E86;
  --teal:#54D6C9;--teal-soft:#0E322F;--green:#7FD79A;--green-soft:#123321;
  --violet:#B79CFF;--violet-soft:#241B4D;
  --gold:#F0B25A;--gold-soft:#332305;
  --ink:#E9EFFB;--ink-2:#B9C6E0;--ink-3:#8CA0C4;--mute:#6F84AC;
  --bg:#0B2545;--bg-2:#0F2E56;--surf:#0E2A4F;--surf-2:#123162;
  --line:#254374;--line-2:#1B3762;--focus:#6FB1FF;
  --grid-line:rgba(111,177,255,.09);
  --ok:#81C995;--ok-bg:#14301C;--warn:#FDD663;--warn-bg:#332200;--bad:#F28B82;--bad-bg:#3A1212;
  --navy:#7FB6EE;--code:#080E18;--code-fg:#D7DEE8;
  --a2ui:#7FB6EE;--mcpapp:#5EC8C2;--mcp:#9DB4FF;--a2a:#B09CFF;--cap:#7FB6EE;--hana:#F0B27A;
  --shadow:0 0 0 1px rgba(255,255,255,.04),0 2px 10px rgba(0,0,0,.28);
  --shadow-lg:0 0 0 1px rgba(255,255,255,.05),0 16px 40px rgba(0,0,0,.4);
  color-scheme:dark;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:76px}
html,body{margin:0;padding:0}
body{font-family:var(--sans);color:var(--ink);background:var(--bg);font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
a{color:var(--blue);text-decoration-thickness:1px;text-underline-offset:3px}
a:hover{color:var(--blue-h)}
code,kbd{font-family:var(--mono);font-size:.84em;background:var(--blue-soft);color:var(--blue-ink);padding:.08em .36em;border-radius:3px}
kbd{border:1px solid var(--line);background:var(--surf)}
.skip{position:absolute;left:-999px;top:8px;background:var(--blue);color:#fff;padding:.5rem 1rem;z-index:80;border-radius:var(--r-sm)}
.skip:focus{left:8px}
#readbar{position:fixed;inset:0 0 auto 0;height:3px;background:transparent;z-index:70;pointer-events:none}
#readbar>i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--blue),var(--teal));transition:width .12s linear}

.topbar{position:sticky;top:0;z-index:50;height:56px;display:flex;align-items:center;gap:.7rem;padding:0 1rem;background:color-mix(in srgb,var(--surf) 90%,transparent);backdrop-filter:saturate(150%) blur(14px);border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:.65rem;min-width:0;text-decoration:none;color:inherit}
.brand-mark{width:30px;height:30px;border-radius:3px;flex:none;background:linear-gradient(145deg,#0B3D91,#B5710A);color:#fff;display:grid;place-items:center}
.brand b{display:block;font-family:var(--display);font-size:13.5px;letter-spacing:.01em;line-height:1.15}
.brand small{display:block;font-size:11px;color:var(--mute);font-weight:400}
.searchwrap{flex:1;max-width:440px;position:relative}
#q{width:100%;height:36px;border:1px solid var(--line);border-radius:999px;background:var(--bg);color:var(--ink);padding:0 2.4rem 0 2.15rem;font:500 13.5px/1 var(--sans)}
#q::placeholder{color:var(--mute)}
.searchwrap .ico{position:absolute;left:.72rem;top:50%;transform:translateY(-50%);color:var(--mute);pointer-events:none}
.searchwrap .hint{position:absolute;right:.75rem;top:50%;transform:translateY(-50%);font:11px var(--mono);color:var(--mute)}
.toggles{margin-left:auto;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;justify-content:flex-end}
.iconbtn{height:34px;min-width:34px;padding:0 .7rem;border:1px solid var(--line);border-radius:8px;background:var(--surf);color:var(--ink-2);cursor:pointer;font:600 12px var(--sans);display:inline-flex;align-items:center;gap:.35rem}
.iconbtn:hover,.iconbtn[aria-pressed="true"]{border-color:var(--blue);color:var(--blue)}
.burger{display:none}
.progchip{font:600 11px var(--mono);color:var(--ink-3);border:1px solid var(--line);background:var(--surf);border-radius:999px;padding:.28rem .65rem}

.layout{display:grid;grid-template-columns:var(--navw) minmax(0,1fr) var(--railw);min-height:calc(100vh - 56px)}
.sidenav{position:sticky;top:56px;height:calc(100vh - 56px);overflow:auto;border-right:1px solid var(--line);background:var(--surf);padding:.85rem .6rem 3rem}
.sidenav .g,details.navg>summary{font:600 10px/1 var(--display);letter-spacing:.16em;text-transform:uppercase;color:var(--mute);padding:.85rem .5rem .3rem}
details.navg{border:0;background:transparent;margin:0}
details.navg>summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center}
details.navg>summary::-webkit-details-marker{display:none}
details.navg>summary::after{content:"+";font:600 12px var(--mono);color:var(--mute)}
details.navg[open]>summary::after{content:"\\2013"}
.navg.locked>summary{opacity:.55;cursor:default}
.navg.locked>summary::after{content:"\\1F512";font-size:10px}
.crumbs{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center;font-size:12.5px;color:var(--ink-3);margin:0 0 1rem}
.crumbs b{color:var(--ink-2);font-weight:650}
.layer{font:650 10px/1 var(--display);letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:1.1rem 0 .35rem}
.quiz{border:1px solid var(--line);border-radius:var(--r);background:var(--surf);padding:.9rem 1rem;margin:.7rem 0}
.quiz p{margin:0 0 .55rem;font-weight:650}
.quiz label{display:block;margin:.28rem 0;cursor:pointer;color:var(--ink-2);font-weight:400}
.quiz .ok{color:var(--ok);font-size:13.5px;margin:.45rem 0 0}
.quiz .no{color:var(--bad);font-size:13.5px;margin:.45rem 0 0}
.sm{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:1rem 0}
.sm i{display:block;padding:.55rem .4rem;border-radius:8px;border:1px solid var(--line);background:var(--surf);font-style:normal;text-align:center;font-size:11.5px}
.sm i b{display:block;font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);margin-bottom:.15rem}
.sm i.on{border-color:var(--blue);background:var(--blue-soft)}
#bread{position:sticky;top:56px;z-index:20;padding:.35rem 0;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(8px);font-size:12.5px;color:var(--ink-3);border-bottom:1px solid transparent}
.sidenav a{display:flex;align-items:flex-start;gap:.45rem;color:var(--ink-2);text-decoration:none;border-radius:7px;padding:.36rem .5rem .36rem .4rem;font-size:13px;line-height:1.35}
.sidenav a .n{flex:none;font:500 10px var(--mono);color:var(--mute);width:1.65rem;padding-top:.12rem}
.sidenav a:hover{background:var(--bg-2);color:var(--ink)}
.sidenav a.active{background:var(--blue-soft);color:var(--blue-ink);font-weight:600}
.sidenav a.active .n{color:var(--blue)}
.sidenav a.done .n{color:var(--ok)}
.sidenav a[hidden]{display:none}
.dot{width:8px;height:8px;border-radius:50%;border:1.5px solid var(--line);flex:none;margin-top:.38rem}
.sidenav a.done .dot{background:var(--ok);border-color:var(--ok)}
main{min-width:0;padding:0 2.1rem 7rem}
.wrap{max-width:var(--max);margin:0 auto}
.rail{position:sticky;top:56px;height:calc(100vh - 56px);overflow:auto;border-left:1px solid var(--line);padding:1.05rem .8rem 3rem;font-size:12.5px}
.rail h2{margin:0 0 .55rem;font:600 10px/1 var(--display);letter-spacing:.16em;text-transform:uppercase;color:var(--mute)}
.rail a{display:block;color:var(--ink-3);text-decoration:none;padding:.22rem 0 .22rem .6rem;border-left:2px solid transparent}
.rail a:hover,.rail a.active{color:var(--blue);border-left-color:var(--blue)}
.rail .mode-note{margin-top:1.2rem;padding:.7rem .75rem;border:1px solid var(--line);border-radius:8px;background:var(--surf-2);color:var(--ink-3);font-size:12px}

.kicker{font:600 11px/1 var(--display);letter-spacing:.16em;text-transform:uppercase;color:var(--blue);margin:0 0 .55rem}
h1{font-family:var(--display);font-weight:650;font-size:clamp(1.9rem,4.2vw,2.7rem);line-height:1.12;letter-spacing:-.03em;margin:0 0 .7rem;text-wrap:balance}
h2{font-family:var(--display);font-weight:650;font-size:1.42rem;letter-spacing:-.02em;line-height:1.25;margin:0 0 .5rem;scroll-margin-top:80px;text-wrap:balance}
h3{font-family:var(--display);font-weight:600;font-size:1.08rem;margin:1.7rem 0 .45rem;scroll-margin-top:80px}
h4{font-weight:650;font-size:.96rem;margin:1.25rem 0 .35rem}
p{margin:0 0 .95rem;color:var(--ink);max-width:70ch}
.lede{font-size:1.12rem;color:var(--ink-2);max-width:64ch}
section.mod{padding:2.6rem 0 2.1rem;border-top:1px solid var(--line);position:relative}
section.mod::before{content:"";position:absolute;top:-1px;left:0;width:46px;height:3px;background:var(--blue)}
.modhead{display:flex;align-items:center;gap:.7rem;margin-bottom:.4rem;flex-wrap:wrap}
.modnum{font:650 11px/1 var(--mono);color:var(--surf);letter-spacing:.06em;background:var(--ink);padding:.32rem .55rem;border-radius:2px}
.modnum.step{color:#fff;background:var(--blue);border-radius:999px;padding:.25rem .7rem;font-weight:700}
.stepgoal{font-size:1.02rem;color:var(--ink-2);font-weight:500;margin:0 0 1.1rem}
.modtag{font:650 10px var(--display);letter-spacing:.08em;text-transform:uppercase;padding:.15rem .5rem;border-radius:999px;border:1px solid var(--line);color:var(--ink-3)}
.modtag.cap{border-color:color-mix(in srgb,var(--cap) 45%,var(--line));color:var(--cap);background:var(--blue-soft)}
.modtag.mcp{border-color:color-mix(in srgb,var(--mcp) 45%,var(--line));color:var(--mcp);background:var(--blue-soft)}
.modtag.a2a{border-color:color-mix(in srgb,var(--a2a) 45%,var(--line));color:var(--a2a);background:var(--violet-soft)}
.modtag.a2ui{border-color:color-mix(in srgb,var(--a2ui) 45%,var(--line));color:var(--a2ui);background:var(--blue-soft)}
.modtag.hana{border-color:color-mix(in srgb,var(--hana) 45%,var(--line));color:var(--hana);background:var(--gold-soft)}
.runlabel{display:inline-block;font:600 9.5px/1 var(--sans);letter-spacing:.05em;text-transform:uppercase;padding:.28rem .55rem;border-radius:999px;vertical-align:middle;margin-left:.15rem}
.runlabel.ok{background:var(--ok-bg);color:var(--ok)}
.runlabel.chk{background:var(--warn-bg);color:var(--warn)}
.runlabel.des{background:var(--violet-soft);color:var(--violet)}
h2 .runlabel{font-size:9.5px}
ul,ol{margin:0 0 1.05rem;padding-left:1.2rem;max-width:70ch}
li{margin:.26rem 0}
.done-row{display:flex;align-items:center;gap:.55rem;margin:1.1rem 0 0}
.done-row label{font-size:13.5px;color:var(--ink-2);cursor:pointer}
.done-row input{accent-color:var(--blue)}

.callout{border:1px solid var(--line);border-left-width:4px;border-radius:var(--r);padding:.85rem 1rem;margin:1rem 0 1.2rem;background:var(--surf);max-width:74ch}
.callout h4{margin:.05rem 0 .3rem;font-size:.8rem;letter-spacing:.06em;text-transform:uppercase}
.callout p:last-child,.callout ul:last-child{margin:0}
.callout.takeaway{border-left-color:var(--ok);background:var(--ok-bg)}
.callout.mistake{border-left-color:var(--bad);background:var(--bad-bg)}
.callout.try{border-left-color:var(--blue);background:var(--blue-soft)}
.callout.insight{border-left-color:var(--violet);background:var(--violet-soft)}
.callout.warn{border-left-color:var(--warn);background:var(--warn-bg)}
.callout.concept{border-left-color:var(--teal);background:var(--teal-soft)}
.callout.beginner{border-left-color:var(--blue-mid);background:var(--blue-soft)}
.callout.prod{border-left-color:var(--gold);background:var(--gold-soft)}
.grid2,.grid3{display:grid;gap:.75rem;margin:1rem 0 1.2rem}
.grid2{grid-template-columns:1fr 1fr}
.grid3{grid-template-columns:1fr 1fr 1fr}
.card{background:var(--surf);border:1px solid var(--line);border-radius:var(--r);padding:1rem 1.05rem;box-shadow:var(--shadow)}
.card h3,.card h4{margin:.05rem 0 .35rem}
.card p{margin:0;color:var(--ink-2);font-size:.95rem}
.card p+p{margin-top:.45rem}

.stack{display:flex;flex-direction:column;align-items:stretch;gap:0;margin:1.05rem 0 1.3rem;max-width:540px}
.stack .box{background:var(--surf);border:1px solid var(--line);border-radius:var(--r);padding:.65rem .85rem;text-align:center;box-shadow:var(--shadow);cursor:pointer}
.stack .box:hover,.stack .box.on{border-color:var(--blue);background:var(--blue-soft)}
.stack .box b{display:block;font-size:.95rem}
.stack .box span{display:block;font-size:.78rem;color:var(--ink-3);margin-top:.08rem}
.stack .arr{text-align:center;color:var(--mute);font:12px var(--mono);padding:.12rem 0;letter-spacing:.08em}
.flowline{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:1rem 0 1.2rem}
.chip{display:inline-flex;align-items:center;gap:.35rem;border:1px solid var(--line);background:var(--surf);border-radius:999px;padding:.28rem .7rem;font-size:12.5px;color:var(--ink-2)}
.chip.hot{border-color:color-mix(in srgb,var(--blue) 40%,var(--line));color:var(--blue-ink);background:var(--blue-soft)}
.chip.teal{border-color:color-mix(in srgb,var(--teal) 40%,var(--line));color:var(--teal);background:var(--teal-soft)}
.chip.violet{border-color:color-mix(in srgb,var(--violet) 40%,var(--line));color:var(--violet);background:var(--violet-soft)}
.chip.gold{border-color:color-mix(in srgb,var(--gold) 40%,var(--line));color:var(--gold);background:var(--gold-soft)}

.ascii{font:12px/1.55 var(--mono);background:var(--surf-2);border:1px solid var(--line);border-top:3px solid var(--blue);border-radius:2px;padding:1rem 1.1rem;overflow:auto;white-space:pre;color:var(--ink-2);margin:1rem 0 1.25rem;position:relative}
.codeblock{margin:1rem 0 1.3rem;border:1px solid var(--line);border-top:3px solid var(--blue);border-radius:2px;background:var(--code);color:var(--code-fg);overflow:hidden;box-shadow:var(--shadow)}
.codeblock figcaption{display:flex;justify-content:space-between;align-items:center;gap:.6rem;padding:.45rem .75rem;background:rgba(255,255,255,.04);border-bottom:1px solid rgba(255,255,255,.07);font:600 11px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#9AA8B8}
.copy-btn{border:1px solid rgba(255,255,255,.14);background:transparent;color:#C5D0DC;border-radius:4px;font:600 10px var(--sans);letter-spacing:.08em;text-transform:uppercase;padding:.25rem .45rem;cursor:pointer}
.copy-btn:hover,.copy-btn.ok{border-color:#7FB6EE;color:#7FB6EE}
.codeblock pre{margin:0;padding:.9rem .95rem;overflow:auto;font:12.5px/1.65 var(--mono)}
.codeblock code{background:none;color:inherit;padding:0;font-size:inherit;border-radius:0}
.tok-k{color:#7EC8FF}.tok-s{color:#A8E6A1}.tok-c{color:#8B98A8;font-style:italic}.tok-n{color:#F0C674}.tok-p{color:#E8B4D4}

.table-wrap{overflow:auto;margin:1rem 0 1.35rem;border:1px solid var(--line);border-top:3px solid var(--ink-3);border-radius:2px;background:var(--surf)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:.62rem .72rem;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);background:var(--surf-2);font-weight:650}
td{color:var(--ink-2)}
tr:last-child td{border-bottom:0}
tr.hl td{background:var(--blue-soft)}

.steps{counter-reset:st;margin:1rem 0 1.3rem;padding:0;list-style:none;max-width:none}
.steps>li{position:relative;padding:.15rem 0 .85rem 2.35rem;border-left:2px solid var(--line);margin-left:.7rem}
.steps>li:last-child{border-left-color:transparent}
.steps>li::before{counter-increment:st;content:counter(st);position:absolute;left:-.72rem;top:.12rem;width:1.35rem;height:1.35rem;border-radius:50%;background:var(--blue);color:#fff;display:grid;place-items:center;font:650 11px var(--sans)}

details.qa{border:1px solid var(--line);border-radius:var(--r);background:var(--surf);margin:.4rem 0;padding:.1rem .85rem}
details.qa summary{cursor:pointer;font-weight:650;padding:.55rem 0;list-style:none}
details.qa summary::-webkit-details-marker{display:none}
details.qa summary::after{content:"\\FF0B";float:right;color:var(--mute);font-weight:500}
details.qa[open] summary::after{content:"\\2013"}
details.fold{margin:1rem 0;border:1px solid var(--line);border-radius:var(--r);background:var(--surf)}
details.fold>summary{cursor:pointer;padding:.7rem 1rem;font-weight:650}
.glossary{max-width:74ch;margin:0 0 1.2rem}
.glossary dt{font-weight:650;margin-top:.85rem}
.glossary dd{margin:.15rem 0 0;color:var(--ink-2)}

.hero{padding:2.6rem 0 1.5rem;margin:0 -1.4rem 0;padding-left:1.4rem;padding-right:1.4rem;background-image:linear-gradient(var(--grid-line) 1px,transparent 1px),linear-gradient(90deg,var(--grid-line) 1px,transparent 1px);background-size:26px 26px;background-position:center top}
.hero .sub{font-size:1.08rem;color:var(--ink-2);margin:0 0 1.1rem;max-width:64ch}
.statrow{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;margin:1.3rem 0;border:1px solid var(--ink);background:var(--ink)}
.stat{background:var(--surf);padding:.85rem .9rem}
.stat b{display:block;font-family:var(--mono);font-size:1.5rem;font-weight:650;letter-spacing:-.01em;color:var(--blue)}
.stat span{display:block;font-size:11px;letter-spacing:.02em;color:var(--ink-3);margin-top:.2rem}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin:1rem 0 1.2rem}
.vs{font:650 11px var(--display);letter-spacing:.12em;text-transform:uppercase;color:var(--mute);margin:0 0 .35rem}
.chat{border:1px solid var(--line);border-radius:var(--r);background:var(--surf);overflow:hidden;margin:1rem 0 1.2rem}
.chat .msg{padding:.75rem 1rem;border-bottom:1px solid var(--line-2)}
.chat .msg:last-child{border-bottom:0}
.chat .who{font:650 11px var(--display);letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:0 0 .25rem}
.chat .user .who{color:var(--blue)}
.chat .ai .who{color:var(--ink-3)}
.chat .good .who{color:var(--ok)}

.tabs{display:flex;flex-wrap:wrap;gap:.35rem;margin:1rem 0 .7rem}
.tab{border:1px solid var(--line);background:var(--surf);color:var(--ink-2);border-radius:999px;padding:.32rem .75rem;font:650 12.5px var(--sans);cursor:pointer}
.tab[aria-selected="true"]{background:var(--blue);border-color:var(--blue);color:#fff}
.tabpanel[hidden]{display:none}
.filetree{display:grid;grid-template-columns:220px 1fr;gap:0;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;margin:1rem 0 1.25rem;background:var(--surf);min-height:280px}
.filetree nav{border-right:1px solid var(--line);background:var(--surf-2);padding:.5rem}
.filetree nav button{display:block;width:100%;text-align:left;border:0;background:transparent;color:var(--ink-2);font:500 12.5px var(--mono);padding:.4rem .55rem;border-radius:6px;cursor:pointer}
.filetree nav button:hover,.filetree nav button[aria-pressed="true"]{background:var(--blue-soft);color:var(--blue-ink)}
.filetree .pane{padding:1rem 1.05rem}
.filetree .pane h4{margin:.1rem 0 .35rem;font-family:var(--mono);font-size:13px}
.filetree .meta{display:grid;gap:.3rem;font-size:13.5px;color:var(--ink-2)}
.filetree .meta b{color:var(--ink)}

.seq{display:grid;gap:.45rem;margin:1rem 0 1.2rem}
.seq .row{display:grid;grid-template-columns:36px 1fr;gap:.7rem;align-items:start}
.seq .n{width:28px;height:28px;border-radius:50%;background:var(--blue-soft);color:var(--blue-ink);display:grid;place-items:center;font:650 12px var(--mono)}
.seq .row.on .n{background:var(--blue);color:#fff}
.seq .body{border:1px solid var(--line);border-radius:8px;padding:.55rem .75rem;background:var(--surf)}
.seq .body b{display:block;font-size:.92rem}
.seq .body span{display:block;font-size:.82rem;color:var(--ink-3)}

.treeq{border:1px solid var(--line);border-radius:var(--r);padding:1.05rem 1.1rem;background:var(--surf);margin:1rem 0}
.treeq h3{margin:.1rem 0 .55rem}
.treeq .opts{display:flex;flex-wrap:wrap;gap:.45rem}
.treeq .opts button{border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:8px;padding:.5rem .8rem;font:650 13.5px var(--sans);cursor:pointer}
.treeq .opts button:hover{border-color:var(--blue);color:var(--blue)}
.verdict{border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:var(--r);padding:1rem 1.1rem;background:var(--blue-soft);margin:1rem 0}
.verdict.teal{border-left-color:var(--teal);background:var(--teal-soft)}
.verdict.violet{border-left-color:var(--violet);background:var(--violet-soft)}
.verdict.gold{border-left-color:var(--gold);background:var(--gold-soft)}

.archsel{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:.55rem;margin:1rem 0}
.archsel button{text-align:left;border:1px solid var(--line);background:var(--surf);border-radius:var(--r);padding:.75rem .8rem;cursor:pointer;color:inherit}
.archsel button[aria-pressed="true"]{border-color:var(--blue);background:var(--blue-soft);box-shadow:0 0 0 2px color-mix(in srgb,var(--blue) 25%,transparent)}
.archsel b{display:block;font-size:.9rem}
.archsel span{display:block;font-size:12px;color:var(--ink-3);margin-top:.15rem}

.timeline{display:grid;gap:0;margin:1.1rem 0 1.3rem;border-left:2px solid var(--line);padding-left:0}
.timeline button{display:grid;grid-template-columns:16px 1fr;gap:.75rem;width:100%;text-align:left;border:0;background:transparent;color:inherit;padding:.45rem 0 .45rem .15rem;cursor:pointer}
.timeline button .dot{width:12px;height:12px;border-radius:50%;background:var(--surf);border:2px solid var(--blue);margin-left:-23px;margin-top:.25rem}
.timeline button.on .dot{background:var(--blue)}
.timeline button .lab b{display:block;font-size:.92rem}
.timeline button .lab span{display:block;font-size:.8rem;color:var(--ink-3)}
#roadExplain{border:1px solid var(--line);border-radius:var(--r);padding:.85rem 1rem;background:var(--surf);margin:.2rem 0 1.2rem}

.nodegrid{display:grid;grid-template-columns:repeat(3,1fr);gap:.45rem;margin:1rem 0}
.nodegrid button{border:1px solid var(--line);background:var(--surf);border-radius:8px;padding:.6rem .65rem;cursor:pointer;text-align:left;color:inherit}
.nodegrid button:hover,.nodegrid button.on{border-color:var(--blue);background:var(--blue-soft)}
.nodegrid b{display:block;font-size:.82rem}
.nodegrid span{display:block;font-size:11.5px;color:var(--ink-3)}
#tracePane{border:1px solid var(--line);border-radius:var(--r);padding:.9rem 1rem;background:var(--surf);min-height:140px}

.giant{font:11.5px/1.45 var(--mono);background:var(--navy);color:#E8EEF4;border-radius:2px;padding:1.15rem 1.1rem;overflow:auto;white-space:pre;margin:1rem 0 1.3rem;border-top:3px solid var(--gold)}
html[data-theme="night"] .giant{background:#071C38;border:1px solid var(--line);border-top:3px solid var(--gold)}
.legend{display:flex;flex-wrap:wrap;gap:.4rem;margin:.4rem 0 1rem}

html[data-mode="architect"] .beginner-only{display:none}
html[data-mode="beginner"] .architect-only{display:none}
mark.hit{background:#FDD663;color:#152536;padding:0 .1em;border-radius:2px}

/* Diagrams stay on fixed light "drafting paper" regardless of page theme — a printed
   sheet reads the same whether the room is lit or dark, and it lets Mermaid's default
   light rendering always stay legible without re-theming on toggle. */
.diagram{margin:1.1rem 0 1.35rem;border:1px solid #DCD6C3;border-top:3px solid #0B3D91;border-radius:2px;background:#FCFBF6;background-image:linear-gradient(rgba(11,61,145,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(11,61,145,.07) 1px,transparent 1px);background-size:22px 22px;padding:1.1rem 1.1rem .7rem;overflow:auto;box-shadow:var(--shadow);color:#1A2333}
.diagram svg{display:block;max-width:100%;height:auto;margin:0 auto;color:#1A2333}
.diagram svg foreignObject,
.diagram svg foreignObject div,
.diagram svg foreignObject span,
.diagram svg foreignObject p,
.diagram svg .nodeLabel,
.diagram svg .edgeLabel,
.diagram svg .label,
.diagram svg .actor>text{color:#1A2333!important}
.diagram svg text,
.diagram svg tspan{fill:#1A2333}
.diagram svg .node.darklabel foreignObject,
.diagram svg .node.darklabel foreignObject *,
.diagram svg .node.darklabel .nodeLabel{color:#FFFFFF!important}
.diagram svg .node.darklabel text,
.diagram svg .node.darklabel tspan{fill:#FFFFFF}
.diagram .figcap{margin:.7rem -1.1rem 0;padding:.5rem 1.1rem 0;border-top:1px dashed #DCD6C3;font:650 10px/1 var(--mono);letter-spacing:.07em;text-transform:uppercase;color:#6B7690;background:transparent}
.srconly{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}

/* --- title block (drafting stamp) --- */
.titleblock{display:inline-grid;grid-template-columns:auto auto;column-gap:1.3rem;row-gap:.3rem;border:1.5px solid var(--ink);padding:.7rem 1rem;margin:0 0 1.3rem;background:var(--surf);box-shadow:3px 3px 0 var(--gold)}
.titleblock .tb-row{display:contents}
.titleblock .tb-k{font:650 9px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);align-self:center}
.titleblock .tb-v{font:650 12px/1 var(--mono);color:var(--ink);align-self:center}

/* --- official SAP Architecture Center embeds --- */
.acfig{margin:1.4rem 0;border:1px solid var(--line);border-top:3px solid var(--gold);border-radius:2px;overflow:hidden;background:var(--surf)}
.acfig .achead{padding:.9rem 1.05rem .3rem}
.acfig .achead .badge{display:inline-block;font:650 9.5px/1 var(--mono);letter-spacing:.07em;text-transform:uppercase;padding:.22rem .55rem;border-radius:999px;background:var(--gold-soft);color:var(--gold)}
.acfig .achead strong{display:block;margin:.5rem 0 .3rem;font-family:var(--display);font-size:1.05rem;font-weight:650;color:var(--ink)}
.acfig .achead p{margin:0 0 .85rem;font-size:.9rem;color:var(--ink-2)}
.acframe{display:block;width:100%;height:420px;border:0;border-top:1px solid var(--line);background:#fff}
.aclinks{display:flex;flex-wrap:wrap;gap:.4rem .9rem;padding:.75rem 1.05rem;font-size:12.5px;border-top:1px solid var(--line);background:var(--surf-2)}
.acfig .acnote{margin:0;padding:0 1.05rem .9rem;font-size:11.5px;color:var(--ink-3)}
.ccard{border:1px solid var(--line);border-radius:var(--r);background:var(--surf);margin:1.1rem 0 1.3rem;overflow:hidden}
.cchead{display:flex;align-items:baseline;gap:.6rem;padding:.9rem 1.1rem;border-bottom:1px solid var(--line);background:var(--bg-2);flex-wrap:wrap}
.cchead strong{font-family:var(--display);font-size:1.05rem;font-weight:700}
.cchead span{font-size:.85rem;color:var(--ink-3);font-family:var(--mono)}
.ccrow{padding:.75rem 1.1rem;border-bottom:1px solid var(--line-2)}
.ccrow b{display:block;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);margin-bottom:.2rem}
.ccrow p,.ccrow ul{margin:0;color:var(--ink-2);font-size:.94rem}
.ccrow ul{padding-left:1.1rem}
.ccrow:last-child{border-bottom:0}
.depth{margin:.4rem 0 1rem}
.pills{display:flex;flex-wrap:wrap;gap:.4rem;margin:1.1rem 0}
.pill{border:1px solid var(--line);background:var(--surf);color:var(--ink-3);border-radius:999px;padding:.32rem .8rem;font:600 12px var(--sans)}
.pill.on{border-color:var(--ok);background:var(--ok-bg);color:var(--ok)}
.badge{display:inline-block;font:650 9.5px/1 var(--mono);letter-spacing:.07em;text-transform:uppercase;padding:.22rem .5rem;border-radius:999px;vertical-align:middle;margin:0 .15rem}
.badge.verify{background:var(--warn-bg);color:var(--warn)}
.badge.ga{background:var(--ok-bg);color:var(--ok)}
.badge.beta{background:var(--violet-soft);color:var(--violet)}
@media(max-width:700px){.acframe{height:320px}}

footer.site{border-top:1px solid var(--line);padding:2rem 0 4rem;color:var(--ink-3);font-size:.88rem}
#searchstatus{min-height:0;font-size:13px;color:var(--mute);margin:.15rem 0 .6rem}

@media (max-width:1180px){
  .layout{grid-template-columns:var(--navw) minmax(0,1fr)}
  .rail{display:none}
}
@media (max-width:880px){
  .burger{display:inline-flex}
  .layout{grid-template-columns:1fr}
  .sidenav{position:fixed;inset:56px auto 0 0;width:min(88vw,310px);z-index:40;transform:translateX(-105%);transition:transform .2s ease;box-shadow:var(--shadow-lg)}
  .sidenav.open{transform:none}
  .scrim{display:none;position:fixed;inset:56px 0 0;background:rgba(10,16,28,.45);z-index:35}
  .scrim.on{display:block}
  main{padding:0 1rem 5rem}
  .grid2,.grid3,.compare,.statrow,.archsel,.filetree,.nodegrid{grid-template-columns:1fr}
  .searchwrap{max-width:none}
  .searchwrap .hint{display:none}
  .brand small{display:none}
}
@media print{
  .topbar,.sidenav,.rail,#readbar,.toggles,.copy-btn,.burger,.scrim,.done-row{display:none!important}
  .layout{display:block}
  main{padding:0}
  body{background:#fff;color:#111;font-size:11.5pt}
  .codeblock,.giant{break-inside:avoid}
  a{color:inherit}
  html[data-mode="beginner"] .architect-only,html[data-mode="architect"] .beginner-only{display:block}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *{transition:none!important;animation:none!important}
}
"""


def esc(s: str) -> str:
    # Escapes quotes too (not just &<>) so this is safe inside an attribute value,
    # e.g. data-mxgraph="{esc(json_string)}" — a bare &<> escape let a literal "
    # inside the JSON prematurely terminate the attribute. &quot;/&#x27; still just
    # render as "/' in ordinary text-node use, so this is a no-op there.
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#x27;"))


def mod(mid: str, num: str, tag: str, title: str, body: str) -> str:
    """Wrap body html in a standard section.mod with heading + done checkbox."""
    tagcls = {"CAP": "cap", "MCP": "mcp", "A2A": "a2a", "A2UI": "a2ui", "HANA/S4": "hana"}.get(tag, "")
    tagspan = f'<span class="modtag {tagcls}">{tag}</span>' if tag else ""
    return f'''<section class="mod" id="{mid}" data-mod="{mid}">
  <div class="modhead"><span class="modnum">MODULE {num}</span>{tagspan}</div>
  <h2>{title}</h2>
{body}
  <div class="done-row"><label><input type="checkbox" data-done="{mid}"> Mark module {num} complete</label></div>
</section>'''


def layer(name: str) -> str:
    return f'<p class="layer">{name}</p>'


def ascii_diagram(text: str) -> str:
    return f'<div class="ascii">{esc(text)}</div>'


def mermaid(caption: str, code: str) -> str:
    """A real Mermaid.js diagram, framed as a drawing sheet with a figure caption."""
    return f'<div class="diagram"><pre class="mermaid">{esc(code)}</pre><p class="figcap">{caption}</p></div>'


def callout(kind: str, title: str, body: str) -> str:
    return f'<div class="callout {kind}"><h4>{title}</h4>{body}</div>'


def code(lang: str, caption: str, text: str) -> str:
    return f'''<figure class="codeblock"><figcaption><span class="flang">{lang}</span><span>{caption}</span><button class="copy-btn" type="button">Copy</button></figcaption><pre><code>{esc(text)}</code></pre></figure>'''


def table(headers, rows) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def grid(items, n=2) -> str:
    cls = "grid2" if n == 2 else "grid3"
    cards = "".join(f'<article class="card"><h4>{t}</h4><p>{b}</p></article>' for t, b in items)
    return f'<div class="{cls}">{cards}</div>'


def steps(items) -> str:
    lis = "".join(f"<li>{s}</li>" for s in items)
    return f'<ol class="steps">{lis}</ol>'


def qa(pairs, box_id="") -> str:
    idattr = f' id="{box_id}"' if box_id else ""
    items = "".join(f"<details class='qa'><summary>{q}</summary><p>{a}</p></details>" for q, a in pairs)
    return f'<div{idattr}>{items}</div>'


def quiz(qid: str, question: str, options, why: str = "") -> str:
    """options: list of (label, is_correct). Optional why is shown after the learner picks."""
    labs = "".join(
        f'<label><input type="radio" name="{qid}" value="{"ok" if ok else "no"}"> {lab}</label>'
        for lab, ok in options
    )
    whyattr = f' data-why="{esc(why)}"' if why else ""
    return f'<div class="quiz" data-quiz="{qid}"{whyattr}><p>{question}</p>{labs}</div>'


def glossary(items) -> str:
    dts = "".join(f"<dt>{t}</dt><dd>{d}</dd>" for t, d in items)
    return f'<dl class="glossary">{dts}</dl>'


def step_mod(mid: str, num: str, title: str, goal: str, body: str) -> str:
    return f'''<section class="mod" id="{mid}" data-mod="{mid}">
  <div class="modhead"><span class="modnum step">STEP {num}</span></div>
  <h2>{title}</h2>
  <p class="stepgoal">{goal}</p>
{body}
  <div class="done-row"><label><input type="checkbox" data-done="{mid}"> Mark step {num} complete</label></div>
</section>'''


def drawio(title: str, xml: str, note: str = "", file_link: str = "") -> str:
    """Embed an editable draw.io diagram authored here, via draw.io's official static-
    viewer embed (a `data-mxgraph` div + viewer-static.min.js) — renders as inline SVG,
    no iframe, no percent-encoded multi-hundred-KB URL. The raw XML travels inside this
    HTML's own markup (HTML-attribute-escaped JSON), so no hosted file is required to
    render; pass `file_link` (a relative path) to also link the standalone .drawio
    sibling file for "open to edit," instead of a second huge encoded URL.
    """
    import json
    config = json.dumps({"highlight": "#0A6ED1", "nav": True, "resize": True,
                          "toolbar": "zoom layers lightbox", "edit": "_blank", "xml": xml})
    return f'''<figure class="acfig drawio">
  <div class="achead">
    <span class="badge dio">Editable draw.io diagram</span>
    <strong>{title}</strong>
    {f"<p>{note}</p>" if note else ""}
  </div>
  <div class="mxgraph" style="max-width:100%;border:0;" data-mxgraph="{esc(config)}"></div>
  <div class="aclinks">
    {f'<a href="{file_link}" target="_blank" rel="noopener">Open the .drawio source file &#8599;</a>' if file_link else ""}
  </div>
  <p class="acnote">Authored for this guide, not an official SAP diagram. The source file is fully editable in diagrams.net or VS Code&#39;s Draw.io extension &mdash; use it as the starting point for your own landscape drawing. Needs internet access to render.</p>
</figure>'''


def depth(simple: str, sap: str, technical: str) -> str:
    return (
        '<div class="depth">'
        f'<p class="beginner-only"><strong>Simple.</strong> {simple}</p>'
        f'<p><strong>SAP-specific.</strong> {sap}</p>'
        f'<p class="architect-only"><strong>Technical.</strong> {technical}</p>'
        "</div>"
    )


def concept_card(name: str, relation: str, problem: str, solution: str, sap: str, use: str, dont: str) -> str:
    return (
        '<div class="ccard"><div class="cchead"><strong>' + name + "</strong><span>" + relation + "</span></div>"
        '<div class="ccrow"><b>Problem</b><p>' + problem + "</p></div>"
        '<div class="ccrow"><b>Solution</b><p>' + solution + "</p></div>"
        '<div class="ccrow"><b>SAP application</b><p>' + sap + "</p></div>"
        '<div class="ccrow"><b>Use when</b><p>' + use + "</p></div>"
        '<div class="ccrow"><b>Don\'t use when</b><p>' + dont + "</p></div></div>"
    )


def adr(num: str, title: str, context: str, problem: str, options, decision: str, why: str, tradeoffs: str, consequences: str) -> str:
    """Architecture Decision Record card. options: list of (name, note) strings."""
    opts_html = "".join(f"<li><b>{o[0]}.</b> {o[1]}</li>" for o in options)
    return (
        f'<div class="ccard adr"><div class="cchead"><strong>ADR-{num}</strong><span>{title}</span></div>'
        f'<div class="ccrow"><b>Context</b><p>{context}</p></div>'
        f'<div class="ccrow"><b>Problem</b><p>{problem}</p></div>'
        f'<div class="ccrow"><b>Options considered</b><ul>{opts_html}</ul></div>'
        f'<div class="ccrow"><b>Decision</b><p>{decision}</p></div>'
        f'<div class="ccrow"><b>Why</b><p>{why}</p></div>'
        f'<div class="ccrow"><b>Trade-offs</b><p>{tradeoffs}</p></div>'
        f'<div class="ccrow"><b>Consequences</b><p>{consequences}</p></div></div>'
    )


HEAD = f"""<!DOCTYPE html>
<html lang="en" data-theme="day" data-mode="beginner">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F6F4EC">
<meta name="description" content="A complete, interactive masterclass building __PROJECT_FULL_NAME__, __PROJECT_ONE_LINE_DESCRIPTION__: SAP CAP/CDS, S/4HANA integration, HANA Cloud Vector Engine RAG, SAP AI Core &amp; Generative AI Hub, LangGraph multi-agent orchestration, MCP, MCP Apps, A2UI, A2A, Event Mesh, XSUAA/IAS security, multi-tenancy and production operations. With Mermaid diagrams, a full reference codebase and official SAP Architecture Center references.">
<title>{TITLE} — Masterclass</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%230B3D91'/%3E%3Cpath d='M6 6h20v20H6z' fill='none' stroke='white' stroke-width='1.4'/%3E%3Cpath d='M8 16h16M16 8v16' stroke='white' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<div id="readbar" aria-hidden="true"><i></i></div>
<header class="topbar">
  <button class="iconbtn burger" type="button" aria-expanded="false" aria-controls="sidenav" id="burger">Menu</button>
  <a class="brand" href="#top">
    <span class="brand-mark" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="14" height="14" stroke="white" stroke-width="1.1"/><path d="M3 8h10M8 3v10" stroke="white" stroke-width="1.6" stroke-linecap="round"/></svg></span>
    <span><b>ProcureX Control Tower</b><small>CAP + MCP + A2A Workshop</small></span>
  </a>
  <div class="searchwrap">
    <svg class="ico" width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/><path d="M20 20l-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    <input id="q" type="search" placeholder="Search modules, protocols, terms…" autocomplete="off" aria-label="Search this course">
    <span class="hint">/</span>
  </div>
  <div class="toggles">
    <button class="iconbtn" type="button" id="modeBtn" aria-pressed="false" title="Switch explanation depth">Architect mode</button>
    <button class="iconbtn" type="button" id="themeBtn" aria-pressed="false">Night</button>
    <span class="progchip" id="labprog" title="Modules marked complete">0/0</span>
    <button class="iconbtn" type="button" onclick="window.print()">Print</button>
  </div>
</header>
<div class="scrim" id="scrim" hidden></div>

<div class="layout">
"""
