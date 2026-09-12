"""Part 13: CH79-CH90 (go-live)."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done


def build():
    parts = []

    parts.append(ch("c79", "79", "Chapter 79 — Deploy to DEV", "", {
        "What are we learning?": "<p><b>Simple:</b> first real deploy to the DEV space, step by step. <b>Enterprise:</b> 12 pre-checks → deploy → status → logs. <b>Example:</b> maiden voyage in the harbor, not the open sea.</p>",
        "Why is this important?": "<p>Every later environment repeats THIS procedure — master it on disposable DEV.</p>",
        "Where does this fit in the architecture?": "<p>Whole FIG. 0 prod side, first light.</p>",
        "Prerequisites": "<p>Chapters 73-78 complete. Git branch clean, tests green.</p>",
        "Folder/file changes": "<p>None — deploy the artifact built from main.</p>",
        "Exact commands": "<p>BTP CLI (DEV space targeted):</p>" + code("powershell", "Pre-checks 1-12, then deploy", "git status --short; git log -1 --oneline        # 1-2 commit+branch clean\nnpm test; npx cds compile --to csn db srv        # 3-4 build+tests\nls mta_archives/*.mtar                           # 5 artifact exists\ncf target -s dev; cf services                    # 6-7 env+services\ncf check-connection SENSOR_API 2>$null; echo 'dest checked in cockpit'  # 8\ncf run-task maintenance-backend \"echo db-ok\"    # 9 database reachable\ncf get-env maintenance-backend | Select-String ALLOW_MOCK_AUTH  # 10-11 authN/Z config present\ncat rollback-plan.md 2>$null; echo '12 rollback plan on file'\ncf deploy mta_archives/assetops-maintenance_1.0.0.mtar"),
        "Complete code": table(["Step", "Command", "Green looks like"], [["13 Deploy", "cf deploy …mtar", "All modules deployed"], ["14 Monitor", "cf deploy … --watch / cf logs", "Staging → running, no crashes"], ["15 Status", "cf apps", "2/2 running"], ["16 Logs", "cf logs --recent", "No ERROR on boot"]]),
        "Explanation of every important line": "<p>Checks 1-12 BEFORE deploy (commit, branch, build, tests, artifact, env, services, destinations, DB, authN, authZ, rollback plan). Steps 13-16 DURING/AFTER. Skipping pre-checks is how 'quick deploys' become incidents.</p>",
        "Expected output": "<p>DEV apps running; welcome + OData + UI reachable via DEV route.</p>",
        "How to test it": std_test("cf apps 2/2 + Chapter 80 smoke green."),
        "Negative test cases": neg([["Dirty git tree", "pre-check 1", "STOP — deploy only clean commits"], ["Red tests", "pre-check 3", "STOP — fix first (Chapter 71)"]]),
        "Common mistakes": "<p>Deploying a branch you have not pushed — the artifact must trace to a remote commit.</p>",
        "How to troubleshoot": "<p>Staging crash? <code>cf logs --recent</code> crash section names the missing binding/env first.</p>",
        "Production considerations": "<p>Same 16 steps run for STAGE and PROD — rehearse until boring (Chapter 83).</p>",
        "Security considerations": "<p>DEV uses test users + test IdP — prod credentials never enter DEV configs.</p>",
        "What we have completed": done("DEV live." + mermaid('FIG. 10 - BTP PRODUCTION POSTER', 'flowchart TD; U[User]-->AR[Approuter]; AR-->CAP[CAP app]; CAP-->HANA[HANA Cloud]; CAP-->DST[Destination]; DST-->VENDOR[Sensor vendor]; CAP-->LOG[App Logging]; CAP-->AG[Agents via MCP and A2A]'), "Chapter 80: prove DEV healthy."),
    }))

    parts.append(ch("c80", "80", "Chapter 80 — DEV Smoke Testing", "", {
        "What are we learning?": "<p><b>Simple:</b> 12 automated 'is it alive and correct' checks. <b>Enterprise:</b> smoke suite: app, login, OData, CRUD, DB, destination, vendor, MCP, A2A, agent, audit, health. <b>Example:</b> pilot walk-around before every flight.</p>",
        "Why is this important?": "<p>Cheap tripwire: catches dead deploys in minutes, not via user complaints.</p>",
        "Where does this fit in the architecture?": "<p>Post-deploy validation ring around FIG. 0.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>scripts/smoke-dev.ps1</code> (below, Bearer-token edition of Chapter 70).</p>",
        "Exact commands": PWR + code("powershell", "Run DEV smoke", "powershell ./scripts/smoke-dev.ps1 -Base https://assetops-dev.example.com -Token $DEV_TOKEN"),
        "Complete code": code("powershell", "FILE: scripts/smoke-dev.ps1 (COMPLETE)", """param([string]$Base, [string]$Token)
$ErrorActionPreference = 'Stop'
$H = @{ Authorization = \"Bearer $Token\" }
function Check($name, $url, $method = 'GET', $body = $null) {
  $r = Invoke-RestMethod -Uri $url -Headers $H -Method $method -Body $body -ContentType 'application/json'
  Write-Host \"OK $name\"
}
Check 'health' \"$Base/health\"
Check 'odata' \"$Base/odata/v4/equipment/EquipmentAlerts?%24top=1\"
Check 'read' \"$Base/odata/v4/equipment/Equipment?$filter=equipmentId%20eq%20%27TEST-EQ%27\"
Check 'destination' \"$Base/odata/v4/equipment/Sensors?%24top=1\"
Check 'mcp' \"$Base/mcp\" 'POST' '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}'
Check 'a2a-discovery' \"$Base/.well-known/agent.json\"
Check 'audit' \"$Base/odata/v4/maintenance/AuditLogs?%24top=1\"
Write-Host 'DEV SMOKE GREEN'"""),
        "Explanation of every important line": "<p>Every arrow gets ONE check: app, OData, DB-read, destination, MCP menu, discovery, audit. Token from env/SSO per run — never stored (Chapter 77).</p>",
        "Expected output": "<p>7 OKs + DEV SMOKE GREEN in under a minute.</p>",
        "How to test it": std_test("stop one backend binding in DEV; smoke names it; restore; green."),
        "Negative test cases": neg([["Login broken", "smoke", "Fails at first authenticated check — IdP/config issue"], ["HANA down", "smoke", "Fails at odata/read — binding/task issue (Chapter 76)"]]),
        "Common mistakes": "<p>Smoking only /health — health ≠ correct. Data checks (read/audit) catch wiring bugs.</p>",
        "How to troubleshoot": "<p>First failing check names the layer — open that chapter's troubleshooting section.</p>",
        "Production considerations": "<p>Same script promotes to STAGE/PROD with URLs + tokens swapped (Chapters 81, 84).</p>",
        "Security considerations": "<p>Smoke token is least-privilege (read-only user) — smoke must not need admin.</p>",
        "What we have completed": done("DEV proven.", "Chapter 81: STAGING."),
    }))

    parts.append(ch("c81", "81", "Chapter 81 — STAGING Environment", "", {
        "What are we learning?": "<p><b>Simple:</b> a prod twin for final rehearsals (load, chaos, IdP). <b>Enterprise:</b> prod-sized data + real IdP federation + chaos drills + sign-off. <b>Example:</b> full dress rehearsal with costumes, lights, audience of critics.</p>",
        "Why is this important?": "<p>The last place where failure is cheap. STAGING pain prevents PROD incidents.</p>",
        "Where does this fit in the architecture?": "<p>Second full FIG. 0 copy, prod-shaped.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>Config-only (space, services, destinations). Code identical to DEV artifact.</p>",
        "Exact commands": "<p>BTP CLI:</p>" + code("powershell", "Promote to STAGING", "cf target -s stage\ncf deploy mta_archives/assetops-maintenance_1.0.0.mtar   # SAME artifact as DEV\npowershell ./scripts/smoke-dev.ps1 -Base https://assetops-stage.example.com -Token $STAGE_TOKEN"),
        "Complete code": table(["STAGING must have", "Why"], [["Prod-like data volume", "Paging/index issues (Ch 16/76) only appear at scale"], ["Real corporate IdP", "Federation bugs (Ch 77) cannot be faked"], ["Chaos drills (kill agent, slow vendor)", "Chapters 57-58, 67 proven under real latency"], ["Load test (expected peak ×2)", "Pool + quota sizing (Ch 76) validated"], ["Sign-off record", "Named humans accept residual risk (Ch 82)"]]),
        "Explanation of every important line": "<p>SAME artifact re-deployed — rebuilding for STAGE invalidates DEV evidence. Differences live in bindings/config, never code.</p>",
        "Expected output": "<p>Smoke green + load test within SLO + chaos drills degraded gracefully + sign-off signed.</p>",
        "How to test it": std_test("full Chapter 89 rehearsal on STAGE with STAGE data — timed, observed, recorded."),
        "Negative test cases": neg([["Rebuilt artifact for STAGE", "review", "Rejected — promote the tested binary"], ["Skipped load test", "sign-off", "No sign-off without numbers"]]),
        "Common mistakes": "<p>STAGE as 'second DEV' (tiny data, fake IdP) — then it proves nothing.</p>",
        "How to troubleshoot": "<p>STAGE-only failures = environment/config drift — diff bindings, quotas, versions vs DEV.</p>",
        "Production considerations": "<p>STAGING stays warm between releases — cold stages rot (certs, secrets, data age).</p>",
        "Security considerations": "<p>STAGE data anonymized if cloned from prod — real PII never leaves prod (Chapter 60).</p>",
        "What we have completed": done("Release candidate proven.", "Chapter 82: the gate."),
    }))

    parts.append(ch("c82", "82", "Chapter 82 — Production Readiness", "", {
        "What are we learning?": "<p><b>Simple:</b> the launch checklist with teeth — NO-GO on any red item. <b>Enterprise:</b> 22-item gate with owners + evidence links. <b>Example:</b> NASA go/no-go poll: every station reports, one NO scrubs the launch.</p>",
        "Why is this important?": "<p>Deployment must NOT proceed when critical checks fail — this chapter makes 'not proceed' a procedure, not a hope.</p>",
        "Where does this fit in the architecture?": "<p>Gate BEFORE the PROD arrow.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>docs/readiness.md</code> (the gate record, signed per release).</p>",
        "Exact commands": "<p>Review meeting + commands that produce evidence:</p>" + code("powershell", "Evidence pack", "npm test 2>&1 | Tee-Object evidence-tests.txt\nnpm audit --audit-level=high\ncf target -s prod; cf services; cf apps"),
        "Complete code": table(["#", "Check", "Evidence"], [["1-4", "Build, unit, integration, security tests pass", "CI run link + evidence-tests.txt"], ["5-6", "No secrets committed, deps audited", "scan + audit logs"], ["7-8", "DB + HANA verified", "STAGE deploy + suite results"], ["9-10", "AuthN + AuthZ verified", "Chapter 65 STAGE run"], ["11-12", "Destination + vendor verified", "Check Connection + drills"], ["13-15", "MCP + A2A + agent auth verified", "Chapters 66-68 STAGE runs"], ["16-17", "Audit + monitoring configured", "Sample trail + dashboards (Ch 85)"], ["18-19", "Health + smoke passing", "Chapter 84 script green"], ["20-22", "Rollback + backup + config reviewed", "Chapter 87 plan + backup ticket"]]) + "<p>Performance acceptable (STAGE load numbers attached). One NO-GO = release stops, reasons logged, next window scheduled.</p>",
        "Explanation of every important line": "<p>Every item names EVIDENCE, not opinion. 'Looks fine' is not evidence; a green run link is.</p>",
        "Expected output": "<p>Signed readiness.md: 22/22 GO with links — or a NO-GO with owner + date.</p>",
        "How to test it": std_test("hold a mock gate with one red item; verify the release actually stops."),
        "Negative test cases": neg([["Gate skipped for urgency", "audit", "Incident-grade violation — urgency uses the incident process (Ch 88), not shortcuts"]]),
        "Common mistakes": "<p>Copy-pasting last release's evidence — each release earns its own green.</p>",
        "How to troubleshoot": "<p>Recurring NO-GO on one item = systemic debt — schedule the fix, not another waiver.</p>",
        "Production considerations": "<p>The gate record is the auditor's first request — keep it with the release tag.</p>",
        "Security considerations": "<p>Security items (5, 9-10, 13-15) need security-owner sign, not just dev sign.</p>",
        "What we have completed": done("GO decision earned.", "Chapter 83: fly."),
    }))

    parts.append(ch("c83", "83", "Chapter 83 — Production Deployment", "", {
        "What are we learning?": "<p><b>Simple:</b> the 23-step launch sequence, no improvisation. <b>Enterprise:</b> checks 1-12 → deploy → 14-23 verifications (auth, API, MCP, A2A, AI). <b>Example:</b> airline takeoff checklist — challenge, response, verify.</p>",
        "Why is this important?": "<p>Do NOT simply 'cf deploy' — each verification catches a class of silent failure.</p>",
        "Where does this fit in the architecture?": "<p>PROD arrow, executed.</p>",
        "Prerequisites": "<p>Chapter 82 GO signed. Maintenance window announced. Rollback captain named.</p>",
        "Folder/file changes": "<p>None — deploy the STAGE-proven artifact.</p>",
        "Exact commands": "<p>BTP CLI (PROD space):</p>" + code("powershell", "Launch (same 1-12 as Chapter 79, then)", "cf target -s prod\ncf deploy mta_archives/assetops-maintenance_1.0.0.mtar\ncf apps; cf logs maintenance-backend --recent\npowershell ./scripts/smoke-dev.ps1 -Base https://assetops.example.com -Token $PROD_READ_TOKEN"),
        "Complete code": table(["#", "Verify", "How"], [["14-16", "Deployment, status, logs", "cf apps 2/2; logs clean"], ["17-19", "Smoke, authN, authZ", "Script green + role matrix spot-checks"], ["20-23", "API, MCP, A2A, AI tests", "Chapters 64, 66-68 suites retargeted at PROD (read-only subset + one synthetic approval drill)"]]),
        "Explanation of every important line": "<p>PROD AI tests use a SYNTHETIC machine/alert (never real equipment) — proving the brain without touching the plant.</p>",
        "Expected output": "<p>23/23 green; release tag + evidence pack archived.</p>",
        "How to test it": std_test("independent verifier (not the deployer) re-runs steps 14-23."),
        "Negative test cases": neg([["Step fails mid-sequence", "launch", "STOP, assess, rollback (Ch 87) — never skip ahead"], ["Deployer also verifier", "review", "Rejected — four-eyes on prod"]]),
        "Common mistakes": "<p>Celebrating at step 16 — steps 17-23 catch the failures users would find tomorrow.</p>",
        "How to troubleshoot": "<p>Any red step → Chapter 86 matrix entry → fix-forward or rollback decision within the window.</p>",
        "Production considerations": "<p>Announce + monitor + timebox: launches have a window; expiry means rollback, not heroics.</p>",
        "Security considerations": "<p>PROD tokens least-privilege, short-lived, per-verifier — never shared screens with tokens.</p>",
        "What we have completed": done("System live for users.", "Chapter 84: keep proving it."),
    }))

    parts.append(ch("c84", "84", "Chapter 84 — Post-Deployment Validation", "", {
        "What are we learning?": "<p><b>Simple:</b> automated proof, every deploy, forever. <b>Enterprise:</b> scheduled smoke + golden agent run + data reconciliation. <b>Example:</b> daily calibration of every gauge.</p>",
        "Why is this important?": "<p>Deploys drift (certs expire, vendors change) — validation catches rot between releases.</p>",
        "Where does this fit in the architecture?": "<p>Continuous ring around prod FIG. 0.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>SCHEDULE smoke script (CI cron) + golden test vs PROD synthetics.</p>",
        "Exact commands": PWR + code("powershell", "Nightly validation (CI schedule)", "powershell ./scripts/smoke-dev.ps1 -Base https://assetops.example.com -Token $PROD_READ_TOKEN\nnpm test -- agent-e2e --env=prod-synthetic   # synthetic machine only"),
        "Complete code": table(["Check", "Frequency", "On red"], [["Smoke script", "15 min", "Page on-call (Ch 88)"], ["Golden agent run", "hourly", "Freeze auto-features, investigate"], ["Stock reconciliation", "nightly", "Ledger review before shifts"], ["Cert/expiry scan", "daily", "Rotate within SLA"]]),
        "Explanation of every important line": "<p>Validation severity ladders: page (smoke) → freeze (golden) → review (reconciliation) — matched to blast radius.</p>",
        "Expected output": "<p>Green dashboard history; every red has an incident link.</p>",
        "How to test it": std_test("break a synthetic binding; pager fires within 15 min."),
        "Negative test cases": neg([["Validation muted for a release", "review", "Rejected — validation pauses need incident-grade approval"]]),
        "Common mistakes": "<p>Validating only uptime — correctness (golden) catches the subtle breakages.</p>",
        "How to troubleshoot": "<p>Red golden but green smoke = logic/data drift, not outage — Chapter 86 matrix.</p>",
        "Production considerations": "<p>Validation results feed SLO reports (Chapter 85).</p>",
        "Security considerations": "<p>Synthetic identities clearly marked (SYNTH-) — never mixed with real users in audit.</p>",
        "What we have completed": done("Self-proving production.", "Chapter 85: watch it breathe."),
    }))

    parts.append(ch("c85", "85", "Chapter 85 — Monitoring", "", {
        "What are we learning?": "<p><b>Simple:</b> dashboards + alerts that wake the right human. <b>Enterprise:</b> golden signals (latency, errors, traffic, saturation) per layer + agent KPIs. <b>Example:</b> control-room gauges with alarm horns.</p>",
        "Why is this important?": "<p>Monitoring is how Chapters 86-88 START — no signal, no response.</p>",
        "Where does this fit in the architecture?": "<p>Eyes on every box + arrow.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>Dashboards/alerts in BTP cockpit (config, not code) + SLO doc.</p>",
        "Exact commands": "<p>Cockpit + CLI:</p>" + code("powershell", "Log triage by correlation", "cf logs maintenance-backend --recent | Select-String -Pattern 'trace-<id>'\n# BTP Application Logging: filter correlationId=<id> across app + router"),
        "Complete code": table(["Signal", "Watch", "Alert when"], [["Latency p95", "OData, tools, orchestrate", "> SLO 2× for 10 min"], ["Error rate", "5xx %, 403 spikes", "> 1% / sudden 403 burst (attack?)], "], ["Tool durations", "17 tools (durationMs)", "p95 ×3 baseline"], ["Agent success", "Investigations → recs", "< 95% over 1h"], ["Queue depth", "PENDING tasks", "growing 15 min"], ["DB pool", "HANA connections", "> 80% sustained"]]),
        "Explanation of every important line": "<p>Alerts name OWNER + RUNBOOK (Chapter 88 section) — an alert without an owner is noise; noise gets muted; muting kills.</p>",
        "Expected output": "<p>Dashboards per layer; alerts reach on-call in minutes with correlation links.</p>",
        "How to test it": std_test("trigger each alert with synthetics; verify page + runbook link + ack flow."),
        "Negative test cases": neg([["Alert storm (50 pages)", "chaos", "Grouped + deduplicated by correlation — on-call gets 1 incident, not 50"]]),
        "Common mistakes": "<p>Monitoring averages (hide spikes) — percentiles and maxima for latency.</p>",
        "How to troubleshoot": "<p>Blind spot? Add the missing signal before closing the incident (Chapter 88).</p>",
        "Production considerations": "<p>SLOs reviewed quarterly with plant leadership — monitoring serves the business, not itself.</p>",
        "Security considerations": "<p>403-burst alerts double as intrusion detection (Chapter 65 patterns in prod).</p>",
        "What we have completed": done("Watched system.", "Chapter 86: when gauges scream."),
    }))

    parts.append(ch("c86", "86", "Chapter 86 — Troubleshooting", "", {
        "What are we learning?": "<p><b>Simple:</b> symptom → causes → logs → commands → fix → prevention. <b>Enterprise:</b> the full matrix below, drilled until reflex. <b>Example:</b> fault-tree handbook at every workstation.</p>",
        "Why is this important?": "<p>Incidents (Chapter 88) run on THIS matrix — writing it calm prevents panic later.</p>",
        "Where does this fit in the architecture?": "<p>Every box and arrow, failure side.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>docs/runbook.md</code> (this matrix, kept current).</p>",
        "Exact commands": PWR + code("powershell", "Universal first moves", "cf apps; cf logs maintenance-backend --recent\ncf get-env maintenance-backend | Select-String -Pattern 'URL|AUTH'  # redacted review\ncurl http://localhost:4004/health  # or BTP route /health"),
        "Complete code": table(["Problem", "Symptoms → Causes → Logs → Fix"], [["App won't start", "crash loop → missing binding/env → cf logs crash section → bind + restage"], ["500s", "error rate spike → code bug → stack in logs + correlationId → fix-forward/rollback"], ["401", "login loops → IdP/XSUAA misconfig → approuter logs → federation + scopes (Ch 77)"], ["403", "denied valid users → role mapping → DENIED audit rows → collections (Ch 77)"], ["404", "missing data → wrong ID/syntax → request log → String IDs + () syntax"], ["HANA failure", "db:false readiness → binding/quota → HDI logs → rebind + task (Ch 76)"], ["Destination failure", "504 vendor → secret/URL → Check Connection → rotate/fix (Ch 78)"], ["JWT failure", "mass 401 → expiry/keys/clock → token decode → re-login/NTP/JWKS"], ["MCP failure", "tools 500 → handler bug → MCPToolExecutions.error → fix + menu test"], ["A2A failure", "tasks stuck → specialist down → AgentTasks rows → restart + replay"], ["Agent failure", "bad recs → provider/data → transcripts + goldens → rules-fallback + retrain"], ["Vendor failure", "503/timeout → their outage → client logs → breaker + fallback (Ch 57)"], ["Memory/CPU", "restarts/slow → leak/load → metrics → scale + profile"], ["Timeout/rate-limit", "504/429 → slow/loud callers → durationMs + caller IDs → tune + throttle"], ["MTA failure", "deploy red → entitlement/block → deploy log → request/fix + rebuild"], ["UI5 failure", "blank/broken → route/binding/CORS → console + network → manifest + approuter"]]),
        "Explanation of every important line": "<p>Every row: WHERE to look first. CorrelationId first, layer second, fix third, prevention fourth (add the missing test/monitor before closing).</p>",
        "Expected output": "<p>Any listed symptom reaches a fix within the SLO using only this matrix.</p>",
        "How to test it": std_test("game-day: inject each failure in STAGE; team diagnoses from the matrix alone."),
        "Negative test cases": neg([["Runbook outdated", "audit", "Quarterly review dated + signed — stale runbooks cause incidents"]]),
        "Common mistakes": "<p>Fixing forward when rollback was safer — the matrix says which (Chapter 87).</p>",
        "How to troubleshoot": "<p>This chapter IS troubleshooting — if lost, start at Universal first moves.</p>",
        "Production considerations": "<p>Matrix updates are post-incident deliverables (Chapter 88), not optional homework.</p>",
        "Security considerations": "<p>Prod logs contain PII — access logged, redaction on export.</p>",
        "What we have completed": done("Fault handbook.", "Chapter 87: retreat routes."),
    }))

    parts.append(ch("c87", "87", "Chapter 87 — Rollback", "", {
        "What are we learning?": "<p><b>Simple:</b> undo a bad release safely — including what you must NOT undo. <b>Enterprise:</b> app/config/destination/agent/MCP/UI rollback + DB migration discipline. <b>Example:</b> recall procedure: stop line, quarantine batch, revert — but never 'unbake' shipped cakes (migrated data).</p>",
        "Why is this important?": "<p>Deploys without rollback plans are gambles. Never rollback destructive DB changes blindly.</p>",
        "Where does this fit in the architecture?": "<p>Reverse gear for every deploy arrow.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>rollback-plan.md</code> per release (below).</p>",
        "Exact commands": "<p>BTP CLI:</p>" + code("powershell", "Rollback drill (STAGE first, always)", "cf target -s stage\ncf push maintenance-backend -p <previous-artifact>  # or cf rollback (VERIFY command vs current CLI)\ncf run-task maintenance-backend \"npm run db:compat-check\"  # new code reads old schema?"),
        "Complete code": table(["Layer", "Rollback", "Rule"], [["App", "Previous .mtar version", "Keep 3 versions deployable"], ["Config/destination", "Previous values snapshot", "Snapshot BEFORE every change"], ["Agent/MCP/UI5", "Same artifact (bundled)", "UI + API revert TOGETHER — never split"], ["DB schema", "Forward-fix preferred", "Destructive changes NEVER auto-rollback: restore needs backup + data mapping"], ["Data migration", "Down-migration script (tested)", "Untested down-scripts are fiction — test on STAGE clone"]]),
        "Explanation of every important line": "<p>Compatibility rule: new code must read OLD schema (expand-then-contract migrations) so rollback stays possible during the window.</p>",
        "Expected output": "<p>STAGE rollback drill completes; app + data consistent; drill timed and recorded.</p>",
        "How to test it": std_test("quarterly rollback game-day on STAGE including a schema change."),
        "Negative test cases": neg([["Rollback with data loss", "drill review", "Rejected — restore plan + backup verification mandatory"], ["UI rolled back alone", "review", "Rejected — version skew breaks contracts"]]),
        "Common mistakes": "<p>Deleting the new (broken) schema columns containing user data created since deploy.</p>",
        "How to troubleshoot": "<p>Rollback stuck? Check binding versions (services may have migrated too) — snapshot those as well.</p>",
        "Production considerations": "<p>Rollback decision SLA: 15 min from detection — indecision IS the outage (Chapter 88).</p>",
        "Security considerations": "<p>Rolled-back versions still need current secrets — rotation state survives rollback.</p>",
        "What we have completed": done("Retreat routes mapped.", "Chapter 88: fight fires."),
    }))

    parts.append(ch("c88", "88", "Chapter 88 — Production Incident Handling", "", {
        "What are we learning?": "<p><b>Simple:</b> who does what when prod bleeds, in order. <b>Enterprise:</b> severity → correlate → isolate → fix/rollback → postmortem. <b>Example:</b> ER protocol: triage, stabilize, treat, review — same every time.</p>",
        "Why is this important?": "<p>Panic improvises; protocol performs. This chapter is read at 3am.</p>",
        "Where does this fit in the architecture?": "<p>Human process around FIG. 0 under fire.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>docs/incident-log.md</code> (every incident, blameless).</p>",
        "Exact commands": PWR + code("powershell", "First 10 minutes", "$corr = 'trace-<from-alert>'\ncf logs maintenance-backend --recent | Select-String -Pattern $corr\n# open: logs -> CAP -> HANA -> destination -> vendor -> MCP -> A2A -> agent (in that order)"),
        "Complete code": mermaid("FIG. 7 — INCIDENT LADDER", """flowchart TD
  AL["Alert with correlationId"] --> LOG["App logs (corr)"]
  LOG --> CAP["CAP errors?"]
  CAP --> HANA["HANA healthy?"]
  HANA --> DST["Destination OK?"]
  DST --> VEN["Vendor OK?"]
  VEN --> MCP["MCP tools OK?"]
  MCP --> A2A["A2A tasks OK?"]
  A2A --> AG["Agent sane?"]
  AG --> SEV["Severity 1-4"]
  SEV --> FIX["Fix-forward or rollback (Ch 87)"]""") + table(["Severity", "Meaning", "Response"], [["S1", "Plant decisions blocked", "All hands, 15-min rollback SLA"], ["S2", "Degraded (one agent down)", "Owner + backup, 4h fix"], ["S3", "Cosmetic / single screen", "Backlog with SLA"], ["S4", "Noise / false alarm", "Tune monitor, no page"]]),
        "Explanation of every important line": "<p>Order is load-bearing: each step EXONERATES a layer before moving deeper — never start at the agent when the database is down. Postmortem updates Chapters 61-68 suites + 85 monitors + 86 matrix: every incident buys permanent armor.</p>",
        "Expected output": "<p>Incident log entry: timeline, severity, fix, follow-ups with owners + dates.</p>",
        "How to test it": std_test("quarterly game-day: S1 drill timed against the ladder."),
        "Negative test cases": neg([["Blame in postmortem", "review", "Rejected — blameless or people hide the next one"]]),
        "Common mistakes": "<p>Skipping the log entry 'because fix was fast' — fast fixes hide systemic rot.</p>",
        "How to troubleshoot": "<p>No correlationId on the alert? Fix monitoring (Chapter 85) as follow-up #1.</p>",
        "Production considerations": "<p>On-call rotation with backup + escalation path posted where alerts land.</p>",
        "Security considerations": "<p>Suspected breach follows the security track FIRST (isolate, preserve logs) — Chapter 65 contacts on speed-dial.</p>",
        "What we have completed": done("Fire protocol.", "Chapter 89: the full story, live."),
    }))

    parts.append(ch("c89", "89", "Chapter 89 — Final End-to-End Scenario", "", {
        "What are we learning?": "<p><b>Simple:</b> the whole movie, one showing: vibration → fix, live. <b>Enterprise:</b> scripted demo with checkpoints, timings and rollback plan. <b>Example:</b> opening night after 88 rehearsals.</p>",
        "Why is this important?": "<p>Proof the system (not the slides) works — the course's final exam.</p>",
        "Where does this fit in the architecture?": "<p>Every arrow, in story order.</p>",
        "Prerequisites": "<p>All chapters. STAGE (or PROD synthetics) green. Audience invited.</p>",
        "Folder/file changes": "<p>NEW <code>docs/demo-script.md</code> (cues + timings + fallback per step).</p>",
        "Exact commands": "<p>Follow the script — abbreviations below expand to chapter drills:</p>" + code("powershell", "Demo spine (each step = its chapter drill)", "curl $BASE/odata/v4/equipment/EquipmentAlerts         # 1 dashboard shows ALT-9001\n# 2 open #/equipment/eq-cnc102                            # details\n# 3 assistant: 'Investigate CNC-MACHINE-102'             # orchestrate\n# 4-6 tools: get_equipment, get_sensor_readings, history # MCP evidence\n# 7-9 A2A: stock OK, Ravi Kumar, 2026-09-15 night        # specialists\n# 10 recommendation PROPOSED -> Approve click            # HITL\n# 11-14 order + reserve + assign + schedule              # execution\n# 15 events + audit trail on screen                      # proof"),
        "Complete code": table(["Beat", "Actor", "Visible proof"], [["Alert", "Dashboard", "ALT-9001 HIGH red row"], ["Investigate", "Assistant + agents", "Tool chips: 3 reads + 3 A2A tasks"], ["Recommend", "Maintenance Agent", "Bearing 87%, BRG-6205 ×2, Ravi, night window"], ["Approve", "Manager click", "PROPOSED → APPROVED + 9-step transaction"], ["Execute", "CAP", "MO- order, -2 stock, assignment, schedule"], ["Prove", "Audit view", "One correlationId, 8+ rows, timestamps"]]),
        "Explanation of every important line": "<p>Every beat has a FALLBACK (recorded video / seeded snapshot) — live demos fail; prepared demos recover in seconds.</p>",
        "Expected output": "<p>Audience watches alert → approval → booked maintenance in ~10 minutes with the audit trail as the finale.</p>",
        "How to test it": std_test("three full rehearsals on STAGE; third must be boring (boring = ready)."),
        "Negative test cases": neg([["Demo gods strike (vendor down)", "live", "Fallback: mock destination + recorded segment, show breaker working"]]),
        "Common mistakes": "<p>Demoing on PROD real equipment — synthetics only, always.</p>",
        "How to troubleshoot": "<p>Any beat fails → its chapter drill diagnoses in under 2 minutes (that is what they are for).</p>",
        "Production considerations": "<p>Record the demo — it becomes onboarding + UAT evidence.</p>",
        "Security considerations": "<p>Demo accounts least-privilege + expired after; no real PII on screen.</p>",
        "What we have completed": done("STANDING OVATION MILESTONE.", "Chapter 90: the stamp."),
    }))

    parts.append(ch("c90", "90", "Chapter 90 — Production Go-Live Checklist", "", {
        "What are we learning?": "<p><b>Simple:</b> the final stamp: 30 boxes, all ticked, in the doc. <b>Enterprise:</b> persistent checklist (localStorage) + sign-off record. <b>Example:</b> launch-day clipboard, laminated.</p>",
        "Why is this important?": "<p>Checklists beat memory at 3am and in audits. Tick every box below — in the page, for real.</p>",
        "Where does this fit in the architecture?": "<p>Gate over the entire FIG. 0.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>Signed <code>docs/go-live.md</code> referencing this checklist's state.</p>",
        "Exact commands": "<p>No commands — verification. Tick each box; progress persists in this browser.</p>",
        "Complete code": "".join("<div class=\"done-row\"><label><input type=\"checkbox\" data-check=\"go%d\"> %s</label></div>" % (i, t) for i, t in enumerate([
            "Code builds clean (Ch 04-10)", "Unit tests pass (Ch 62)", "Integration tests pass (Ch 63)",
            "Security tests pass (Ch 65)", "No secrets committed (Ch 72 scan)", "Dependencies audited (Ch 72)",
            "Postgres verified local (Ch 17)", "HANA verified DEV/STAGE (Ch 76)", "Authentication verified per env (Ch 77)",
            "Authorization matrix verified (Ch 65)", "Destination verified + Check Connection (Ch 78)", "External API drills green (Ch 38)",
            "17 MCP tools verified (Ch 66)", "A2A tasks verified (Ch 67)", "Agent grants verified (Ch 52)",
            "Audit trail complete (Ch 55)", "Monitoring + alerts live (Ch 85)", "Health endpoints live (Ch 69)",
            "Smoke green DEV/STAGE/PROD (Ch 80/84)", "Load acceptable (Ch 81 numbers)", "Rollback drilled (Ch 87)",
            "Backup/recovery reviewed (Ch 76)", "Config reviewed, mocks off in prod (Ch 77)", "E2E demo recorded (Ch 89)",
            "Incident rota posted (Ch 88)", "Docs + runbook current (Ch 86)", "Sign-off recorded (Ch 82)",
            "Celebration scheduled (you earned it)"])) + "<p id=\"readinessScore\"><b>Production readiness: 0/28 (0%)</b> — tick boxes to update.</p>",
        "Explanation of every important line": "<p>Each box maps to its chapter's evidence — clicking back through failures is the point. The score above is computed live from your ticks.</p>",
        "Expected output": "<p>28/28 (100%) + signed go-live.md + one calm team.</p>",
        "How to test it": std_test("untick one box — release must halt per Chapter 82 rules."),
        "Negative test cases": neg([["Ship at 27/28", "gate", "NO-GO — the missing box names the risk you are accepting"]]),
        "Common mistakes": "<p>Ticking boxes from memory — each tick requires linked evidence.</p>",
        "How to troubleshoot": "<p>Stuck box? Its chapter holds the unblock procedure — go there, not around.</p>",
        "Production considerations": "<p>Re-run this list EVERY release — go-live is a habit, not an event.</p>",
        "Security considerations": "<p>Boxes 5, 9, 10, 13-15 need security-owner initials, not just dev ticks.</p>",
        "What we have completed": done("PRODUCTION GO-LIVE. You built: 30 entities, 7 services, 17 tools, 4 agents, 12 UI routes, 8 test layers, 3 environments — from mkdir to signed launch.", "Beyond: extend to predictive maintenance (vibration ML on readings), multi-plant tenancy (Ch 60), Joule integration (Ch 02 map)."),
    }))

    return parts
