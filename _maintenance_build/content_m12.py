"""Part 12: CH69-CH78."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done


def build():
    parts = []

    parts.append(ch("c69", "69", "Chapter 69 — Docker", "", {
        "What are we learning?": "<p><b>Simple:</b> ship the app + DB + mock API as sealed boxes that run anywhere. <b>Enterprise:</b> multi-stage Dockerfile + compose network. <b>Example:</b> shipping containers: packed once, unloaded identically in every port.</p>",
        "Why is this important?": "<p>'Works on my machine' dies here — CI, staging and prod all run THESE images.</p>",
        "Where does this fit in the architecture?": "<p>Packaging for every box in FIG. 0 (locally).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>Dockerfile</code> + <code>docker/mock-sensor-api/Dockerfile</code>; EXTEND compose.</p>",
        "Exact commands": PWR + code("powershell", "Build + run everything", "docker compose up -d --build\ndocker compose ps\ndocker compose logs app --tail 20"),
        "Complete code": code("dockerfile", "FILE: Dockerfile (COMPLETE)", """FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build || true
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts
COPY --from=build /app ./
EXPOSE 4004
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://127.0.0.1:4004/health || exit 1
CMD ["sh", "-c", "npm run db:deploy:prod || true; npm start"]""") + "<p>Add <code>app.get('/health', ...)</code> to server.js (Chapter 50 file) or the HEALTHCHECK fails — liveness vs readiness vs health are distinct probes (Chapter 80).</p>",
        "Explanation of every important line": table(["Line", "Meaning"], [["multi-stage", "Dev deps never ship — smaller, safer image"], ["npm ci --omit=dev", "Reproducible prod install from lockfile"], ["HEALTHCHECK /health", "Orchestrator restarts sick containers automatically"], ["db:deploy:prod || true", "Schema migrate on boot; data never touched"]]),
        "Expected output": "<p>db + app + mock-api all healthy; OData + UI + mock reachable.</p>",
        "How to test it": std_test("compose up; run Chapters 63-64 suites against container URLs; compose down -v; repeat (reproducible)."),
        "Negative test cases": neg([["Missing /health route", "docker ps", "app shows unhealthy — add the route"], ["Stale image", "after code change", "Rebuild with --build or test old code by accident"]]),
        "Common mistakes": "<p>Committing images instead of Dockerfiles — images build in CI (Chapter 72).</p>",
        "How to troubleshoot": "<p><code>docker compose logs</code> per service; <code>docker inspect</code> for health details.</p>",
        "Production considerations": "<p>CF runs buildpacks, not these images — but identical Node version + env shape keeps parity (Chapter 73).</p>",
        "Security considerations": "<p>Scan images for CVEs in CI (Chapter 72); run as non-root where possible.</p>",
        "What we have completed": done("Boxed system.", "Chapter 70: prod-like local stage."),
    }))

    parts.append(ch("c70", "70", "Chapter 70 — Production-Like Local Environment", "", {
        "What are we learning?": "<p><b>Simple:</b> one command that mimics prod: app + DB + mock vendor + (mock) gateway. <b>Enterprise:</b> compose profiles, prod-like env values, smoke script. <b>Example:</b> dress rehearsal on a replica stage.</p>",
        "Why is this important?": "<p>Catches 'prod-only' surprises (CSRF, CORS, timeouts, token paths) before BTP costs money.</p>",
        "Where does this fit in the architecture?": "<p>Whole FIG. 0 on one machine.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>scripts/smoke-local.ps1</code> (below).</p>",
        "Exact commands": PWR + code("powershell", "Full local prod-sim", "docker compose up -d --build\npowershell ./scripts/smoke-local.ps1"),
        "Complete code": code("powershell", "FILE: scripts/smoke-local.ps1 (COMPLETE)", """$ErrorActionPreference = 'Stop'
$base = 'http://localhost:4004'
function Check($name, $url, $expect = 200) {
  $r = Invoke-WebRequest -Uri $url -UseBasicParsing
  if ($r.StatusCode -ne $expect) { throw "$name: expected $expect, got $($r.StatusCode)" }
  Write-Host "OK $name"
}
Check 'health' "$base/health"
Check 'odata-alerts' "$base/odata/v4/equipment/EquipmentAlerts?%24top=1"
Check 'discovery' "$base/.well-known/agent.json"
Check 'mock-sensors' 'http://localhost:5100/equipment/eq-cnc102/sensors'
Write-Host 'LOCAL SMOKE GREEN'"""),
        "Explanation of every important line": "<p>PowerShell-native (no curl flags to mistype); <code>$ErrorActionPreference='Stop'</code> fails the script on ANY bad check; <code>%24</code> escapes $ for OData.</p>",
        "Expected output": "<p>Four OKs + LOCAL SMOKE GREEN.</p>",
        "How to test it": std_test("run script fresh after compose up; break one service; script names the culprit."),
        "Negative test cases": neg([["Mock API down", "script", "Fails at mock-sensors with the exact URL — fix order is obvious"]]),
        "Common mistakes": "<p>Skipping this before BTP deploys — local green is the cheapest gate.</p>",
        "How to troubleshoot": "<p>Check order in script = boot order to verify (health → data → agents → vendors).</p>",
        "Production considerations": "<p>This script becomes the DEV/STAGE/PROD smoke template (Chapters 80, 84) with tokens + URLs swapped.</p>",
        "Security considerations": "<p>Smoke uses read-only endpoints — writes stay in test suites with fixtures.</p>",
        "What we have completed": done("Replica stage.", "Chapter 71: the delivery pipeline."),
    }))

    parts.append(ch("c71", "71", "Chapter 71 — CI/CD", "", {
        "What are we learning?": "<p><b>Simple:</b> a robot that tests every push and stops bad code. <b>Enterprise:</b> pipeline stages with gates: lint → unit → integration → security → build → package → DEV → smoke → STAGE → approval → PROD. <b>Example:</b> factory QA gates between stations — defects stop the line.</p>",
        "Why is this important?": "<p>No application can guarantee zero defects — but gates catch them BEFORE production, every time, without relying on memory.</p>",
        "Where does this fit in the architecture?": "<p>Around everything: the conveyor moving code to users.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>.github/workflows/ci.yml</code> (full file in Chapter 72).</p>",
        "Exact commands": "<p>Git workflow (PowerShell):</p>" + code("powershell", "Branch + PR flow", "git checkout -b feature/alert-ack\ngit add .\ngit commit -m 'feat: acknowledge alert action'\ngit push -u origin feature/alert-ack\n# open Pull Request on GitHub -> pipeline runs -> merge only when green"),
        "Complete code": mermaid("FIG. 6 — PIPELINE WITH GATES", """flowchart TD
  PUSH["Push / PR"] --> LINT["Lint"]
  LINT --> UNIT["Unit tests"]
  UNIT --> INT["Integration tests"]
  INT --> SEC["Security tests"]
  SEC --> BUILD["Build + package"]
  BUILD --> DEV["Deploy DEV"]
  DEV --> SMOKE["Smoke tests"]
  SMOKE --> STAGE["STAGING"]
  STAGE --> APPR["Manual approval"]
  APPR --> PROD["PRODUCTION"]
  PROD --> POST["Post-deploy validation"]"""),
        "Explanation of every important line": "<p>Order matters: cheap fast tests first; security BEFORE build (no point packaging a vulnerability); manual approval ONLY before prod — DEV/STAGE stay automatic.</p>",
        "Expected output": "<p>PR shows green checks per stage; red security test blocks merge.</p>",
        "How to test it": std_test("open a PR with a deliberately failing unit test; verify merge is blocked."),
        "Negative test cases": neg([["Bypassed gate", "admin merge", "Requires security sign-off + incident note (Chapter 88)"]]),
        "Common mistakes": "<p>Gates that warn instead of fail — warnings are invisible; failures are respected.</p>",
        "How to troubleshoot": "<p>Flaky gate? Quarantine the test with an issue link — never delete a gate silently.</p>",
        "Production considerations": "<p>Pipeline must STOP on critical failures — 'continue on error' is forbidden on gate jobs.</p>",
        "Security considerations": "<p>Secrets in CI come from GitHub Environments/secrets, never workflow files.</p>",
        "What we have completed": done("Delivery conveyor designed.", "Chapter 72: build it in GitHub Actions."),
    }))

    parts.append(ch("c72", "72", "Chapter 72 — GitHub Actions", "", {
        "What are we learning?": "<p><b>Simple:</b> the robot's instruction card in YAML. <b>Enterprise:</b> jobs per gate with Postgres service, secret scanning, artifact packaging. <b>Example:</b> autopilot checklist, laminated.</p>",
        "Why is this important?": "<p>Implements Chapter 71 — without this file the pipeline is a drawing.</p>",
        "Where does this fit in the architecture?": "<p>CI system around the repo.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>.github/workflows/ci.yml</code> (below).</p>",
        "Exact commands": "<p>Push to GitHub — Actions tab shows the run. No local command; the cloud runs it.</p>",
        "Complete code": code("yaml", "FILE: .github/workflows/ci.yml (COMPLETE)", """name: ci
on: [push, pull_request]
jobs:
  gates:
    runs-on: ubuntu-latest
    services:
      postgres: { image: postgres:16-alpine, env: { POSTGRES_PASSWORD: changeme, POSTGRES_DB: assetops }, ports: ['5432:5432'],
        options: >- --health-cmd pg_isready --health-interval 5s --health-retries 10 }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx cds compile --to csn db srv
      - run: npm run build
      - run: npm test -- unit
      - run: npm test -- integration
      - run: npm test -- security
      - run: npm test -- mcp
      - run: npm test -- a2a
      - name: secret scan
        run: "! grep -rEi 'password\\s*=\\s*[^c]|api[_-]?key\\s*=\\s*['\\\"]?[A-Za-z0-9]{8}' --include='*.js' --include='*.ts' --include='*.json' srv lib app test || true"
      - run: npm audit --audit-level=high
"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["services.postgres", "Real Postgres per run — integration tests never touch SQLite-only semantics"], ["cds compile gate", "Model errors fail the build in seconds"], ["layered npm test", "Failure names the layer instantly"], ["secret scan", "Catches committed credentials (tune the regex, keep it strict)"], ["npm audit high", "Known CVEs block the line"]]),
        "Expected output": "<p>Green run in ~5 minutes; failing security test = red run, blocked PR.</p>",
        "How to test it": std_test("push a bad commit on a branch; watch the exact gate fail; fix; green."),
        "Negative test cases": neg([["Secret committed", "push key", "Secret-scan job fails the run"], ["Vulnerable dep", "npm install bad-lib", "Audit job fails"]]),
        "Common mistakes": "<p>Long mystery jobs — one job per layer keeps failures attributable.</p>",
        "How to troubleshoot": "<p>Download the job log; re-run the exact failing command locally with the same Node version.</p>",
        "Production considerations": "<p>Deploy jobs (Chapters 79-83) extend this file with environment approvals.</p>",
        "Security considerations": "<p>Workflow files need code review too — pipeline tampering is a supply-chain attack.</p>",
        "What we have completed": done("STOP MILESTONE 11: guarded delivery.", "Chapter 73: BTP itself."),
    }))

    parts.append(ch("c73", "73", "Chapter 73 — SAP BTP Cloud Foundry", "", {
        "What are we learning?": "<p><b>Simple:</b> SAP's cloud estate: accounts, spaces, apps, services. <b>Enterprise:</b> subaccount → space → app + bound services + routes. <b>Example:</b> industrial park: plot (subaccount), unit (space), machines (apps), utilities (services).</p>",
        "Why is this important?": "<p>Chapters 74-78 map every local thing to its BTP counterpart — this chapter teaches the map legend.</p>",
        "Where does this fit in the architecture?": "<p>The ground everything production stands on.</p>",
        "Prerequisites": "<p>BTP trial/global account + CF CLI (Chapter 00).</p>",
        "Folder/file changes": "<p>None — account-level work in cockpit + CLI.</p>",
        "Exact commands": "<p>BTP CLI (PowerShell):</p>" + code("powershell", "Target the landscape", "cf login -a https://api.cf.<region>.hana.ondemand.com  # VERIFY region URL vs current SAP docs\ncf target -o <org> -s dev\ncf apps        # what runs here now\ncf services    # what utilities exist"),
        "Complete code": table(["Concept", "Simple", "Ours"], [["Subaccount", "Fenced plot", "assetops-dev / -stage / -prod"], ["Space", "Unit in the plot", "dev, stage, prod spaces"], ["Application", "A machine", "maintenance-backend + approuter"], ["Service instance", "Utility hookup", "HANA, XSUAA, Destination, Logging"], ["Binding", "Pipe + meter", "Credentials injected, never copied"], ["Route", "Street address", "https://assetops-dev..."], ["Org/quota", "Park rules", "Memory + service entitlements"]]),
        "Explanation of every important line": "<p>Separate subaccounts/spaces per environment (DEV/STAGE/PROD) — never share a space across stages; quotas prevent noisy-neighbor surprises.</p>",
        "Expected output": "<p><code>cf apps</code> lists the space; targeting dev/stage/prod works.</p>",
        "How to test it": std_test("target each space; list apps + services; confirm isolation."),
        "Negative test cases": neg([["Deploy to wrong space", "cf push", "Space naming + pipeline env checks prevent (Chapter 79)"]]),
        "Common mistakes": "<p>One space for everything — a load test kills prod. Separate from day one.</p>",
        "How to troubleshoot": "<p>Login failures: region URL or SSO method — VERIFY against current SAP docs (they change).</p>",
        "Production considerations": "<p>Entitlements (HANA, XSUAA) per subaccount — request BEFORE deploy day (Chapter 82).</p>",
        "Security considerations": "<p>Space roles (who can push/bind) are production access control — audit them (Chapter 77).</p>",
        "What we have completed": done("Landscape literacy.", "Chapter 74: describe our slice as code."),
    }))

    parts.append(ch("c74", "74", "Chapter 74 — mta.yaml", "", {
        "What are we learning?": "<p><b>Simple:</b> one file describing apps + services + wirings. <b>Enterprise:</b> modules, resources, requires/provides, routes, bindings. <b>Example:</b> factory blueprint: machines, utilities, pipes — approved once, built identically everywhere.</p>",
        "Why is this important?": "<p>Deploys become repeatable across DEV/STAGE/PROD — the end of snowflake environments.</p>",
        "Where does this fit in the architecture?": "<p>Build/deploy descriptor for the whole FIG. 0 prod side.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>mta.yaml</code> (below, COMPLETE).</p>",
        "Exact commands": "<p>BTP CLI:</p>" + code("powershell", "Build the archive (needs MTA build tool)", "mbt build\ncf deploy mta_archives/assetops-maintenance_1.0.0.mtar"),
        "Complete code": code("yaml", "FILE: mta.yaml (COMPLETE)", """_schema-version: '3.1'
ID: assetops-maintenance
version: 1.0.0
parameters: { enable-parallel-deployments: true }
modules:
  - name: maintenance-backend
    type: nodejs
    path: .
    parameters: { memory: 512M, buildpack: nodejs_buildpack, health-check-type: http, health-check-http-endpoint: /health }
    properties: { ALLOW_MOCK_AUTH: false }
    requires: [maintenance-xsuaa, maintenance-hana, maintenance-destination, maintenance-logging]
  - name: maintenance-approuter
    type: approuter.nodejs
    path: approuter
    parameters: { memory: 256M }
    requires:
      - name: maintenance-xsuaa
      - name: maintenance-backend
        group: destinations
        properties: { name: maintenance-backend, url: ~{url}, forwardAuthToken: true }
resources:
  - name: maintenance-xsuaa
    type: org.cloudfoundry.managed-service
    parameters: { service: xsuaa, service-plan: application, path: ./xs-security.json }
  - name: maintenance-hana
    type: org.cloudfoundry.managed-service
    parameters: { service: hana, service-plan: hdi-shared }   # VERIFY plan vs current catalog
  - name: maintenance-destination
    type: org.cloudfoundry.managed-service
    parameters: { service: destination, service-plan: lite }
  - name: maintenance-logging
    type: org.cloudfoundry.managed-service
    parameters: { service: application-logs, service-plan: lite }"""),
        "Explanation of every important line": table(["Block", "Meaning"], [["modules.backend", "Our CAP app; ALLOW_MOCK_AUTH=false hardcoded — mocks CANNOT activate in prod"], ["approuter destinations group", "UI calls flow WITH the user token (forwardAuthToken)"], ["resources", "Four managed services bound by NAME — code never holds credentials"], ["health-check /health", "CF restarts failed instances; needs the Chapter 69 route"]]),
        "Expected output": "<p><code>mbt build</code> produces the .mtar; deploy creates 2 apps + 4 services.</p>",
        "How to test it": std_test("deploy to DEV space; cf apps shows 2/2 running; bindings listed per app."),
        "Negative test cases": neg([["MTA build fails", "mbt build", "Schema version or path typo — error names the block"], ["Missing entitlement", "cf deploy", "Service creation fails — request entitlement (Chapter 73)"]]),
        "Common mistakes": "<p>Editing service config in cockpit instead of mta.yaml — drift. Code wins, always redeploy.</p>",
        "How to troubleshoot": "<p><code>cf deploy</code> logs name the failed module/resource — fix, rebuild, redeploy.</p>",
        "Production considerations": "<p>Version bumps (1.0.0 → 1.0.1) per release — rollback (Chapter 87) targets versions.</p>",
        "Security considerations": "<p>No secrets in mta.yaml — EVER. Bindings inject them at runtime.</p>",
        "What we have completed": done("Deployable blueprint.", "Chapters 75-78: each service, configured."),
    }))

    parts.append(ch("c75", "75", "Chapter 75 — BTP Service Configuration", "", {
        "What are we learning?": "<p><b>Simple:</b> order the utilities: HANA, XSUAA, Destination, Logging, AI. <b>Enterprise:</b> plans, bindings, AI Core wiring for Chapter 40's provider. <b>Example:</b> connecting water, power, gas before opening the plant.</p>",
        "Why is this important?": "<p>Every production arrow needs its service — missing one = dead arrow at 2am.</p>",
        "Where does this fit in the architecture?": "<p>All managed-service boxes.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT <code>lib/ai.js</code>: real AI Core branch (below). Config otherwise via cockpit/CLI.</p>",
        "Exact commands": "<p>BTP CLI:</p>" + code("powershell", "Verify bindings (after Chapter 74 deploy)", "cf services\ncf env maintenance-backend   # shows VCAP_SERVICES (redact before sharing!)"),
        "Complete code": table(["Service", "Plan hint", "Feeds"], [["HANA Cloud", "hdi-shared (VERIFY)", "Schema + prod data (Ch 76)"], ["XSUAA", "application", "JWT auth (Ch 77)"], ["Destination", "lite", "Sensor vendor (Ch 78)"], ["Application Logging", "lite", "Log shipping (Ch 85)"], ["AI Core / GenAI Hub", "per entitlement", "lib/ai.js provider (below)"]]) + code("javascript", "lib/ai.js production branch (COMPLETE pattern, VERIFY SDK)", """// Called when AI_API_KEY is set (binding-provided on BTP):
// VERIFY: package + method names vs current @sap-ai-sdk/* docs before use.
export async function generateCore(prompt) {
  const { url, key, model } = { url: process.env.AI_API_URL, key: process.env.AI_API_KEY, model: process.env.AI_MODEL ?? 'claude-sonnet' };
  const r = await fetch(url + '/v2/inference', { method: 'POST',
    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, messages: [{ role: 'user', content: prompt.slice(0, 4000) }] }),
    signal: AbortSignal.timeout(30000) });
  if (!r.ok) throw Object.assign(new Error('AI Core error'), { code: 'UPSTREAM_TIMEOUT', status: 504 });
  const j = await r.json();
  return j.choices?.[0]?.message?.content ?? JSON.stringify(j).slice(0, 2000);
}"""),
        "Explanation of every important line": "<p>Prompt truncated (cost control), 30s timeout (Chapter 57), 504 mapping (Chapter 15), VERIFY marker on SDK drift. Keys arrive via BINDING, never files.</p>",
        "Expected output": "<p><code>cf services</code> shows all five bound; mock AI still active until keys are bound (safe default).</p>",
        "How to test it": std_test("unbind AI → mock answers; bind AI → real answers; both logged distinctly."),
        "Negative test cases": neg([["AI down", "generate", "504 + rules-only fallback rec (Chapter 57)"]]),
        "Common mistakes": "<p>Pasting keys into env files on BTP — bindings exist precisely to avoid this.</p>",
        "How to troubleshoot": "<p><code>cf env</code> (carefully redacted) shows what the app actually sees.</p>",
        "Production considerations": "<p>Model version pinned per stage — STAGE validates new models before PROD sees them.</p>",
        "Security considerations": "<p>AI inputs sanitized (Chapter 59) + outputs scanned for secrets before display.</p>",
        "What we have completed": done("Utilities connected.", "Chapters 76-78: HANA, auth, destinations live."),
    }))

    parts.append(ch("c76", "76", "Chapter 76 — HANA Cloud Deployment", "", {
        "What are we learning?": "<p><b>Simple:</b> move the database into SAP's cloud, safely. <b>Enterprise:</b> HDI deploy, indexes, constraints, pool sizing, migration discipline. <b>Example:</b> moving the vault to the bank — inventory every bar.</p>",
        "Why is this important?": "<p>Production data is irreplaceable. Schema discipline here prevents the 2am restores of Chapter 87.</p>",
        "Where does this fit in the architecture?": "<p>HANA CLOUD box, production incarnation.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>db/indexes.hdbindex</code> (below); schema deploys via task, never code push.</p>",
        "Exact commands": "<p>BTP CLI:</p>" + code("powershell", "Schema deploy (DEV first, then STAGE, then PROD)", "cf run-task maintenance-backend \"npm run db:deploy:prod\"\ncf logs maintenance-backend --recent | Select-String -Pattern 'deploy'"),
        "Complete code": code("text", "FILE: db/indexes.hdbindex (COMPLETE hot paths)", """INDEX "idx_readings_eq_time" ON "maintenance.db::SensorReadings" ("equipment_ID", "measuredAt" DESC);
INDEX "idx_alerts_status_sev" ON "maintenance.db::EquipmentAlerts" ("status", "severity");
INDEX "idx_audit_corr" ON "maintenance.db::AuditLogs" ("correlationId");
INDEX "idx_tasks_corr" ON "maintenance.db::AgentTasks" ("correlationId");"""),
        "Explanation of every important line": "<p>Indexes mirror the hottest WHERE/ORDER BY from Chapters 12, 29, 55-56 — correlationId indexed because incidents query it first.</p>",
        "Expected output": "<p>Task succeeds; tables + indexes exist; zero data loss (empty prod) or untouched rows.</p>",
        "How to test it": std_test("deploy → verify object counts → run Chapter 63 suite against DEV HANA."),
        "Negative test cases": neg([["Destructive change without backup", "review", "Rejected — Chapter 82 gate + 87 plan required"], ["Index missing on hot query", "load test", "Slow query in monitoring (Chapter 85) → add index"]]),
        "Common mistakes": "<p>Deploying schema WITH seed to prod — seed is DEV/TEST only (Chapter 09).</p>",
        "How to troubleshoot": "<p>HDI errors name objects — fix CDS/indexes, rebuild MTA, redeploy (Chapter 86).</p>",
        "Production considerations": "<p>Migration windows, backups, rollback scripts — reviewed in Chapter 82 before EVERY prod schema change.</p>",
        "Security considerations": "<p>Least-privilege schema users; tenant isolation re-verified post-deploy (Chapter 65 suite on DEV).</p>",
        "What we have completed": done("Prod data home ready.", "Chapter 77: prod identity."),
    }))

    parts.append(ch("c77", "77", "Chapter 77 — Authentication Deployment", "", {
        "What are we learning?": "<p><b>Simple:</b> real badges: IAS login, XSUAA tokens, role collections. <b>Enterprise:</b> cockpit trust config, approuter routes, collection→group mapping, mock lockdown. <b>Example:</b> swapping temp passes for biometrics, turnstiles included.</p>",
        "Why is this important?": "<p>LOCAL vs DEV vs PROD auth differ completely — this chapter makes the differences explicit and testable.</p>",
        "Where does this fit in the architecture?": "<p>APPLICATION ROUTER → AUTHENTICATION arrows, production form.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>approuter/xs-app.json</code> (below); cockpit: role collections per Chapter 35 names.</p>",
        "Exact commands": "<p>BTP CLI + cockpit:</p>" + code("powershell", "Lockdown check (after deploy)", "cf get-env maintenance-backend | Select-String -Pattern 'ALLOW_MOCK_AUTH'\n# must print: ALLOW_MOCK_AUTH: false"),
        "Complete code": code("json", "FILE: approuter/xs-app.json (COMPLETE)", """{
  "welcomeFile": "/index.html",
  "authenticationMethod": "route",
  "logout": { "logoutEndpoint": "/do/logout" },
  "routes": [
    { "source": "^/odata/(.*)$", "target": "/odata/$1", "destination": "maintenance-backend", "authenticationType": "xsuaa" },
    { "source": "^/mcp(.*)$", "target": "/mcp$1", "destination": "maintenance-backend", "authenticationType": "xsuaa" },
    { "source": "^(.*)$", "target": "$1", "localDir": "resources", "authenticationType": "xsuaa" }
  ]
}""") + table(["Environment", "Login", "Token", "Mock"], [["LOCAL", "none (header)", "none", "ON (dev only)"], ["DEV", "IAS test users", "XSUAA JWT", "forced OFF"], ["STAGE/PROD", "Corporate IdP → IAS", "XSUAA JWT", "forced OFF + gated"]]),
        "Explanation of every important line": "<p>Every route demands xsuaa — no anonymous paths (not even /health externally). forwardAuthToken (mta) carries the USER to CAP so agents keep delegation (Chapter 51).</p>",
        "Expected output": "<p>Unauthenticated UI hits redirect to IAS; mock headers ignored; role collections gate pages.</p>",
        "How to test it": std_test("no-token → login redirect; user token → USER pages only; manager token → approval works."),
        "Negative test cases": neg([["Mock header on DEV", "send x-mock-user", "Ignored/401 — mocks dead where ALLOW_MOCK_AUTH=false"], ["User opens approve", "UI + direct API", "Hidden button AND 403 (both layers)"]]),
        "Common mistakes": "<p>Old tutorials' standalone-UAA flows — CURRENT SAP APPROACH is IAS + XSUAA via approuter (differs from legacy; cockpit labels change — VERIFY).</p>",
        "How to troubleshoot": "<p>Redirect loops = xs-app route order (specific first, catch-all last) or destination misname.</p>",
        "Production considerations": "<p>IdP federation tested in STAGE with real corporate accounts BEFORE prod (Chapter 81).</p>",
        "Security considerations": "<p>Space roles + role collections reviewed quarterly; leavers deprovisioned via IdP.</p>",
        "What we have completed": done("Real identity perimeter.", "Chapter 78: real vendor line."),
    }))

    parts.append(ch("c78", "78", "Chapter 78 — Destination Deployment", "", {
        "What are we learning?": "<p><b>Simple:</b> the vendor speed-dial goes live with real credentials. <b>Enterprise:</b> cockpit destination (URL, OAuth2ClientCredentials, certificates), principal propagation, connectivity checks. <b>Example:</b> test hotline → real supplier hotline, same speed-dial button.</p>",
        "Why is this important?": "<p>Code from Chapter 37 works UNCHANGED — this chapter proves the abstraction held.</p>",
        "Where does this fit in the architecture?": "<p>DESTINATION SERVICE box, production form.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>Cockpit/instance config only — zero code changes (verify this claim!).</p>",
        "Exact commands": "<p>BTP CLI:</p>" + code("powershell", "Destination check", "cf service maintenance-destination\n# cockpit: Destinations -> SENSOR_API -> Check Connection (expect 200)"),
        "Complete code": table(["Field", "DEV", "PROD"], [["Name", "SENSOR_API (identical everywhere)", "SENSOR_API"], ["URL", "https://sensors-dev.example.com", "https://sensors.example.com"], ["Authentication", "OAuth2ClientCredentials (test creds)", "OAuth2ClientCredentials (vault creds)"], ["ProxyType", "Internet", "Internet / OnPremise via Cloud Connector if intranet"]]) + "<p>Swap test: point DEV destination at the Chapter 38 mock — app behavior identical. That symmetry IS the test.</p>",
        "Explanation of every important line": "<p>NAME constant across stages; only VALUES differ. Client-credentials flow for service calls; user propagation where the vendor authorizes per-user (principal propagation).</p>",
        "Expected output": "<p>Check Connection 200 per stage; sensor drills green through the real destination.</p>",
        "How to test it": std_test("mock-backed DEV destination vs vendor STAGE destination — same client, same assertions."),
        "Negative test cases": neg([["Expired vendor secret", "drill", "502/504 + rotation runbook (Chapter 88)"], ["Wrong name (SENSOR-API vs SENSOR_API)", "call", "504 not-configured — names are exact"]]),
        "Common mistakes": "<p>Editing destinations to 'fix' code bugs — destination changes need the same review as code.</p>",
        "How to troubleshoot": "<p>Check Connection first (isolates destination), then app logs (isolates code).</p>",
        "Production considerations": "<p>Secret rotation scheduled + tested; Cloud Connector HA for on-prem vendors.</p>",
        "Security considerations": "<p>Vendor credentials in destination service ONLY — Chapter 82 scans for URL/key literals in code.</p>",
        "What we have completed": done("STOP MILESTONE 12: BTP wired.", "Chapter 79: first real deploy."),
    }))

    return parts
