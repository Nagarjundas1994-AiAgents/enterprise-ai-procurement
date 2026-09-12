"""Part 7: CH34-CH39."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done


def build():
    parts = []

    parts.append(ch("c34", "34", "Chapter 34 — Authentication", "", {
        "What are we learning?": "<p><b>Simple:</b> proving who you are (badge scan). <b>Enterprise:</b> mock headers local → IAS/XSUAA JWT on BTP. <b>Example:</b> factory gate: temp pass today, biometric badge in production.</p>",
        "Why is this important?": "<p>Every write, tool call and agent task checks identity FIRST. No identity = no entry.</p>",
        "Where does this fit in the architecture?": "<p>The AUTHENTICATION box between approuter and CAP.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>lib/auth.js</code> (ctx builder); handlers call <code>ctxOf(req)</code>.</p>",
        "Exact commands": PWR + code("powershell", "Mock-auth drills (LEARNING-MOCK APPROACH)", "curl -H 'x-mock-user: operator:MaintenanceUser' http://localhost:4004/odata/v4/equipment/Equipment\ncurl -H 'x-mock-user: boss:MaintenanceManager' http://localhost:4004/odata/v4/equipment/Equipment"),
        "Complete code": code("javascript", "FILE: lib/auth.js (COMPLETE learning version)", """export async function ctxOf(req) {
  const raw = req.http?.req?.headers?.['x-mock-user'];
  if (process.env.ALLOW_MOCK_AUTH === 'true' && raw) {
    const [userId, role] = String(raw).split(':');
    return { userId, roles: role ? [role] : [], isAgent: !!req.http?.req?.headers?.['x-agent-id'],
             agentId: req.http?.req?.headers?.['x-agent-id'] ?? null,
             tenantId: 'blr-plant', correlationId: req.http?.req?.headers?.['x-correlation-id'] ?? ('corr-' + Date.now()) };
  }
  // CURRENT SAP APPROACH (Ch 36-37): JWT from approuter/XSUAA is validated here.
  throw Object.assign(new Error('Unauthorized'), { code: 'UNAUTHORIZED', status: 401 });
}"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["x-mock-user user:ROLE", "Local badge printer — format locked, parsed strictly"], ["x-agent-id", "Agent identity travels SEPARATELY from user (Chapter 51)"], ["ALLOW_MOCK_AUTH gate", "Mock path self-destructs in prod config (Chapter 77)"], ["throw 401", "No identity = immediate reject, before any logic"]]),
        "Expected output": "<p>Both drills return 200 with different role contexts (visible in audit, Chapter 55).</p>",
        "How to test it": std_test("call with no header → 401; malformed header → 401."),
        "Negative test cases": neg([["No header", "GET", "401 UNAUTHORIZED"], ["ALLOW_MOCK_AUTH=false + mock header", "GET", "401 — mock path dead (prod behavior)"]]),
        "Common mistakes": "<p>Reading roles from query params or body — identity comes ONLY from headers/token.</p>",
        "How to troubleshoot": "<p>401 with header set? Check ALLOW_MOCK_AUTH=true in .env and header spelling.</p>",
        "Production considerations": "<p>Mock code SHIPS but never ACTIVATES in prod — Chapter 82 gates on ALLOW_MOCK_AUTH=false.</p>",
        "Security considerations": "<p>Mock auth is clearly labelled LEARNING-MOCK in every chapter — never present it as real security.</p>",
        "What we have completed": done("Identity plumbing.", "Chapter 35: what each identity may do."),
    }))

    parts.append(ch("c35", "35", "Chapter 35 — Authorization", "", {
        "What are we learning?": "<p><b>Simple:</b> your badge opens SOME doors (roles). <b>Enterprise:</b> RBAC matrix enforced at every service boundary. <b>Example:</b> operator enters the shop floor; only managers open the parts vault.</p>",
        "Why is this important?": "<p>Agents are the least-trusted callers — authorization is what keeps them safe (Chapters 45, 52).</p>",
        "Where does this fit in the architecture?": "<p>Inside every CAP service + every MCP tool + every A2A call.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>xs-security.json</code> (scopes + roles) + <code>lib/rbac.js</code> (matrix).</p>",
        "Exact commands": PWR + code("powershell", "Matrix drills", "curl -H 'x-mock-user: op:MaintenanceUser' http://localhost:4004/odata/v4/equipment/Equipment\ncurl -X POST -H 'x-mock-user: op:MaintenanceUser' -d '{\"ID\":\"a-9001\"}' http://localhost:4004/odata/v4/equipment/acknowledgeAlert"),
        "Complete code": code("json", "FILE: xs-security.json (COMPLETE)", """{
  "xsappname": "assetops-maintenance",
  "tenant-mode": "dedicated",
  "scopes": [
    { "name": "$XSAPPNAME.READ", "description": "Read plant data" },
    { "name": "$XSAPPNAME.WRITE", "description": "Create/update orders, alerts" },
    { "name": "$XSAPPNAME.APPROVE", "description": "Approve recommendations" },
    { "name": "$XSAPPNAME.ASSIGN", "description": "Assign technicians, reserve stock" },
    { "name": "$XSAPPNAME.ADMIN", "description": "Master data admin" },
    { "name": "$XSAPPNAME.AGENT", "description": "Invoke agents and tools" }
  ],
  "role-templates": [
    { "name": "MaintenanceUser", "scope-references": ["$XSAPPNAME.READ", "$XSAPPNAME.WRITE"] },
    { "name": "MaintenanceManager", "scope-references": ["$XSAPPNAME.READ", "$XSAPPNAME.WRITE", "$XSAPPNAME.APPROVE", "$XSAPPNAME.ASSIGN"] },
    { "name": "MaintenanceAdmin", "scope-references": ["$XSAPPNAME.READ", "$XSAPPNAME.WRITE", "$XSAPPNAME.APPROVE", "$XSAPPNAME.ASSIGN", "$XSAPPNAME.ADMIN"] },
    { "name": "AgentOperator", "scope-references": ["$XSAPPNAME.READ", "$XSAPPNAME.AGENT"] },
    { "name": "AI_Agent", "scope-references": [] }
  ]
}""") + table(["Who", "READ", "CREATE/UPDATE", "DELETE", "Approve AI", "Invoke tools", "Talk A2A"], [["MaintenanceUser", "yes", "orders/alerts", "no", "no", "no", "no"], ["MaintenanceManager", "yes", "yes", "orders", "YES", "via agent", "via agent"], ["MaintenanceAdmin", "yes", "yes incl. master", "yes", "yes", "yes", "yes"], ["AgentOperator", "yes", "no", "no", "no", "YES supervised", "YES"], ["AI_Agent", "granted tools only", "granted only", "never", "never", "granted only", "granted only"]]),
        "Explanation of every important line": "<p><code>AI_Agent</code> scopes are EMPTY — agents act only through per-agent tool grants (Chapter 52). DELETE is rare by design; most entities retire via status.</p>",
        "Expected output": "<p>User drill: 200 read, 403 on approve. Manager drill: approve works.</p>",
        "How to test it": std_test("for each role × each action: assert allow/deny per the matrix (automated in Chapter 65)."),
        "Negative test cases": neg([["User approves", "approveRecommendation", "403 FORBIDDEN + audit DENIED row"], ["Agent deletes supplier", "DELETE", "403 — agents hold no delete grants"]]),
        "Common mistakes": "<p>Client-side button hiding WITHOUT server checks — Chapter 65 bypasses UI to prove the server holds.</p>",
        "How to troubleshoot": "<p>403 surprise? Log ctx.roles at the boundary — 90% are role-mapping mistakes, not code bugs.</p>",
        "Production considerations": "<p>Roles become BTP role COLLECTIONS assigned to user groups (Chapter 77) — same names, real IdP.</p>",
        "Security considerations": "<p>Least privilege + deny-by-default + every denial audited — the agent-safety triad.</p>",
        "What we have completed": done("RBAC matrix live.", "Chapter 36: how tokens carry it."),
    }))

    parts.append(ch("c36", "36", "Chapter 36 — OAuth2 and JWT", "", {
        "What are we learning?": "<p><b>Simple:</b> a stamped wristband (JWT) you show at every door. <b>Enterprise:</b> IAS login → approuter → XSUAA token with scopes → CAP validates signature + scopes. <b>Example:</b> concert wristband: gate checks stamp, color = your zone (role).</p>",
        "Why is this important?": "<p>Tokens replace mock headers in DEV/STAGE/PROD. Misunderstood expiry/scopes cause the most common prod auth outages.</p>",
        "Where does this fit in the architecture?": "<p>APPLICATION ROUTER → AUTHENTICATION arrows, token in hand.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT <code>lib/auth.js</code>: add JWT branch (below). Approuter wiring in Chapter 77.</p>",
        "Exact commands": "<p>Local simulation (LEARNING-MOCK): mint a fake structured token to see the shape — never accepted as real.</p>" + code("powershell", "Decode any JWT (read-only, safe)", "$t = '<paste-dev-token>'\n$payload = $t.Split('.')[1]\n[Text.Encoding]::Utf8.GetString([Convert]::FromBase64String($payload.PadRight(4 - $payload.Length % 4).Replace('-','+').Replace('_','/'))) | ConvertFrom-Json | Select-Object sub, scope, exp"),
        "Complete code": mermaid("FIG. 2 — TOKEN JOURNEY (CURRENT SAP APPROACH)", """flowchart TD
  IDP["Corporate IdP"] --> IAS["IAS login"]
  IAS --> AR["Approuter session"]
  AR --> JWT["XSUAA JWT (scopes)"]
  JWT --> CAP["CAP validates signature + expiry + audience"]
  CAP --> SC["Scopes to roles to permissions"]
  SC --> OK["Business operation"]""") + table(["JWT part", "Checked", "Failure"], [["Signature (JWKS)", "Signed by trusted XSUAA", "401 — key rotation or wrong instance"], ["exp", "Not expired", "401 — re-login; agents refresh (Ch 51)"], ["aud", "Our xsappname", "401 — token for another app"], ["scope", "Contains needed scope", "403 — Chapter 35 matrix"]]),
        "Explanation of every important line": "<p>LEGACY APPROACH (old tutorials): app validates tokens itself with hardcoded secrets. CURRENT SAP APPROACH: approuter + @sap/xssec validate against XSUAA JWKS; the app only maps scopes. Never implement the legacy path.</p>",
        "Expected output": "<p>You can decode a token and name which scope gates approveRecommendation.</p>",
        "How to test it": std_test("expired token → 401; valid token without APPROVE → 403 on approve."),
        "Negative test cases": neg([["Expired JWT", "approve", "401, re-login required"], ["Tampered payload", "any call", "401 signature invalid"], ["Wrong audience", "any call", "401"]]),
        "Common mistakes": "<p>Logging full tokens (they ARE credentials) — log sub + jti only.</p>",
        "How to troubleshoot": "<p>Clock skew breaks exp checks — sync server time (NTP) before blaming tokens.</p>",
        "Production considerations": "<p>Token validity window (default hours) balances re-login pain vs theft blast radius — set in xs-security (Chapter 74).</p>",
        "Security considerations": "<p>TLS everywhere; tokens in Authorization header, never URLs; short-lived + refresh.</p>",
        "What we have completed": done("Token literacy.", "Chapter 37: reaching outside via destinations."),
    }))

    parts.append(ch("c37", "37", "Chapter 37 — SAP BTP Destination Service", "", {
        "What are we learning?": "<p><b>Simple:</b> a phone book with locked numbers — code dials a NAME, BTP supplies URL + credentials. <b>Enterprise:</b> named destinations with auth types (Basic, OAuth2ClientCredentials, principal propagation). <b>Example:</b> speed-dial: mechanics dial 'SENSOR-API', the switchboard connects securely.</p>",
        "Why is this important?": "<p>Zero hardcoded URLs/secrets in code — the #1 deployment-surprise killer.</p>",
        "Where does this fit in the architecture?": "<p>CAP → DESTINATION SERVICE → EXTERNAL SYSTEMS arrow.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>Local: <code>.env SENSOR_API_URL</code>. BTP: destination instance (Chapter 78). Code reads the NAME only.</p>",
        "Exact commands": PWR + code("powershell", "Name the destination (local .env)", "Add-Content .env 'SENSOR_API_URL=http://localhost:5100'\nAdd-Content .env 'SENSOR_API_KEY=dev-mock-key'\n# BTP cockpit destination (Chapter 78): Name SENSOR_API, URL https://sensors.example.com, Auth OAuth2ClientCredentials"),
        "Complete code": code("javascript", "FILE: srv/integrations/sensorClient.js (COMPLETE)", """const TIMEOUT_MS = 8000;
export async function sensorGet(path) {
  const base = process.env.SENSOR_API_URL;              // NAME lookup: env local, binding on BTP
  if (!base) throw Object.assign(new Error('Destination SENSOR_API not configured'), { code: 'UPSTREAM_TIMEOUT', status: 504 });
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const r = await fetch(base + path, { headers: { Authorization: 'Bearer ' + (process.env.SENSOR_API_KEY ?? '') }, signal: ctrl.signal });
    if (r.status === 404) throw Object.assign(new Error('Sensor resource not found'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
    if (r.status === 429 || r.status >= 500) throw Object.assign(new Error('Sensor API unavailable'), { code: 'UPSTREAM_TIMEOUT', status: 504 });
    if (!r.ok) throw Object.assign(new Error('Sensor API error'), { code: 'UPSTREAM_TIMEOUT', status: 502 });
    return r.json();
  } catch (e) { if (e.name === 'AbortError') throw Object.assign(new Error('Sensor API timeout'), { code: 'UPSTREAM_TIMEOUT', status: 504 }); throw e; }
  finally { clearTimeout(t); }
}"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["env-only URL/key", "Destination NAME in code; VALUES in env/binding"], ["8s timeout + abort", "No hanging requests (Chapter 57)"], ["404 vs 429/5xx split", "Client errors fail fast; overload retries (Chapter 58)"], ["Chapter 15 codes", "Outward contract identical for local mock and real API"]]),
        "Expected output": "<p>Mock sensor API (Chapter 38) reachable via NAME; misconfigured env → clean 504, not a crash.</p>",
        "How to test it": std_test("unset SENSOR_API_URL → 504 configured-error; point at mock → 200 data."),
        "Negative test cases": neg([["Destination missing", "any sensor call", "504, clear message"], ["Slow API (>8s)", "call", "504 timeout, connection aborted"]]),
        "Common mistakes": "<p>Hardcoding the URL 'temporarily' — temporary becomes production. Use the NAME from day one.</p>",
        "How to troubleshoot": "<p>Port vs cockpit URL mismatch: print (redacted) base URL in debug logs only.</p>",
        "Production considerations": "<p>OAuth2ClientCredentials + principal propagation configured per-destination (Chapter 78); rotate via service, never code.</p>",
        "Security considerations": "<p>API keys live in bindings/vaults; responses validated before use (Chapter 38).</p>",
        "What we have completed": done("Clean outside line.", "Chapter 38: the mock sensor API."),
    }))

    parts.append(ch("c38", "38", "Chapter 38 — External API Integration", "", {
        "What are we learning?": "<p><b>Simple:</b> a fake sensor vendor we can break safely. <b>Enterprise:</b> mock server mirroring the real contract, integrated through Chapter 37's client. <b>Example:</b> crash-test dummy for integrations.</p>",
        "Why is this important?": "<p>Proves the integration layer BEFORE the vendor contract is final — and gives Chapters 63/67 something to break.</p>",
        "Where does this fit in the architecture?": "<p>EXTERNAL SYSTEMS box (mock) behind the destination arrow.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>docker/mock-sensor-api/server.js</code> (tiny Express app).</p>",
        "Exact commands": PWR + code("powershell", "Run mock + drill", "node docker/mock-sensor-api/server.js  # :5100\ncurl http://localhost:5100/equipment/eq-cnc102/sensors\ncurl http://localhost:5100/equipment/eq-cnc102/readings"),
        "Complete code": code("javascript", "FILE: docker/mock-sensor-api/server.js (COMPLETE)", """import express from 'express';
const app = express();
app.get('/equipment/:id/sensors', (req, res) => {
  if (req.params.id !== 'eq-cnc102') return res.status(404).json({ error: 'unknown equipment' });
  res.json([{ sensorId: 'VIB-102', kind: 'vibration', unit: 'mm/s', warnAt: 4.5, alarmAt: 7.1 }]);
});
app.get('/equipment/:id/readings', (req, res) => {
  const fail = req.query.fail;
  if (fail === 'timeout') return;                        // never responds: tests Chapter 37 timeout
  if (fail === 'flaky' && Math.random() < 0.5) return res.status(503).json({ error: 'overloaded' });
  const now = Date.now();
  res.json(Array.from({ length: 20 }, (_, i) => ({ value: +(6.4 + Math.random() * 1.6).toFixed(2), unit: 'mm/s', measuredAt: new Date(now - i * 60000).toISOString() })));
});
app.listen(5100, () => console.log('mock sensor API on :5100'));
"""),
        "Explanation of every important line": "<p><code>?fail=timeout|flaky</code> chaos switches: deterministic failure injection for retry/timeout tests (Chapters 58, 63).</p>",
        "Expected output": "<p>Readings hover 6.4-8.0 (alarm territory) — matching the story; <code>?fail=timeout</code> hangs (client aborts at 8s).</p>",
        "How to test it": std_test("normal drill → 20 rows; ?fail=flaky repeated → mix of 200/503 (retry logic proves itself)."),
        "Negative test cases": neg([["Unknown machine", "GET /equipment/nope/sensors", "404 passthrough"], ["fail=timeout", "client call", "504 after 8s, no hang"]]),
        "Common mistakes": "<p>Letting mock quirks (random data) leak into assertions — assert SHAPE + bands, not exact values.</p>",
        "How to troubleshoot": "<p>Port clash on 5100? Set PORT env (server reads it) and update .env to match.</p>",
        "Production considerations": "<p>Swap base URL to the real vendor via destination (Chapter 78) — client code UNCHANGED. That is the whole point.</p>",
        "Security considerations": "<p>Validate every vendor field (numbers in range, timestamps sane) — malformed responses are a test case (Chapter 64).</p>",
        "What we have completed": done("Breakable vendor double.", "Chapter 39: react to events."),
    }))

    parts.append(ch("c39", "39", "Chapter 39 — Event-Driven CAP", "", {
        "What are we learning?": "<p><b>Simple:</b> shout 'alert created!' so others react without being called. <b>Enterprise:</b> CAP emit/on locally; SAP Event Mesh in production. <b>Example:</b> fire alarm vs phone calls — one shout, many responders.</p>",
        "Why is this important?": "<p>Agents trigger on events (alert → investigate) instead of polling — cheaper, faster, auditable.</p>",
        "Where does this fit in the architecture?": "<p>EVENTS / EVENT MESH arrow out of CAP.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT handlers: emit after commits; NEW subscribers (below).</p>",
        "Exact commands": "<p>None — code + observe logs on alert acknowledge.</p>",
        "Complete code": code("javascript", "Events: emit + subscribe (COMPLETE pattern)", """// publisher (after successful commit in acknowledgeAlert):
await this.emit('EquipmentAlertCreated', { alertId: alert.ID, equipmentId: alert.equipment_ID, severity: alert.severity, correlationId: ctx.correlationId });

// subscriber (same service file; Event Mesh binding in prod):
this.on('EquipmentAlertCreated', async (msg) => {
  try {
    if (msg.data.severity === 'HIGH' || msg.data.severity === 'CRITICAL')
      await this.send('executeTask', { agentId: 'maintenance-agent', intent: 'investigate-alert', payload: JSON.stringify(msg.data) });
  } catch (e) { console.error('[event] subscriber failed', e.message); }  // subscribers never break publishers
});
// Event catalog: EquipmentAlertCreated, EquipmentHealthChanged, MaintenanceOrderCreated,
// MaintenanceOrderScheduled, SparePartReserved, TechnicianAssigned, MaintenanceCompleted"""),
        "Explanation of every important line": "<p>Emit AFTER commit (Chapter 14 pattern) — subscribers never see rolled-back ghosts. Subscriber try/catch protects the publisher. Cross-service calls use <code>.send()</code>, never <code>.run({action})</code>.</p>",
        "Expected output": "<p>Acknowledge ALT-9001 → log shows emit + agent task queued with the same correlationId.</p>",
        "How to test it": std_test("acknowledge alert; assert AgentTasks row appears with matching correlationId."),
        "Negative test cases": neg([["Subscriber throws", "acknowledge", "HTTP still 200 — failure isolated in logs"]]),
        "Common mistakes": "<p>Emitting BEFORE commit — subscribers act on data that never persists.</p>",
        "How to troubleshoot": "<p>No subscriber fire? Check event NAME spelling (case-sensitive) on both sides.</p>",
        "Production considerations": "<p>Same event names bind to SAP Event Mesh topics in prod (Chapter 75) — code unchanged, transport swapped.</p>",
        "Security considerations": "<p>Events carry IDs + severity, not PII or secrets — subscribers re-read what they are allowed to see.</p>",
        "What we have completed": done("STOP MILESTONE 5: connected backend.", "Chapter 40: the AI layer."),
    }))

    return parts
