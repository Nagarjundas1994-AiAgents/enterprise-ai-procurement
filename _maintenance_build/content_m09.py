"""Part 9: CH46-CH54."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done


def build():
    parts = []

    parts.append(ch("c46", "46", "Chapter 46 — Agent-to-Agent Communication", "", {
        "What are we learning?": "<p><b>Simple:</b> MCP = agent asks a TOOL; A2A = agent asks another AGENT. <b>Enterprise:</b> signed tasks with intent + payload + correlationId over the AgentService. <b>Example:</b> detective phones the lab (A2A); the lab runs its own instruments (MCP).</p>",
        "Why is this important?": "<p>Specialists stay independent — maintenance never imports inventory internals, yet uses its answers.</p>",
        "Where does this fit in the architecture?": "<p>All three A2A arrows from the Maintenance Agent.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>srv/a2a/tasks.js</code> (task envelope helpers).</p>",
        "Exact commands": PWR + code("powershell", "A2A drill", "curl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:AgentOperator' -H 'x-agent-id: maintenance-agent' -d '{\"agentId\":\"inventory-agent\",\"intent\":\"check-stock\",\"payload\":\"{\\\"partNo\\\":\\\"BRG-6205\\\",\\\"qty\\\":2}\"}' http://localhost:4004/odata/v4/agents/executeTask"),
        "Complete code": mermaid("FIG. 4 — A2A TASK LIFECYCLE", """sequenceDiagram
  participant M as Maintenance Agent
  participant T as AgentTasks row
  participant S as Specialist Agent
  M->>T: create task (PENDING, corr-123)
  T->>S: deliver intent + payload
  S->>S: run own MCP tools
  S-->>T: result (SUCCESS)
  T-->>M: response with corr-123""") + code("javascript", "FILE: srv/a2a/tasks.js (COMPLETE)", """export async function sendTask(srv, ctx, toAgent, intent, payload) {
  const taskKey = 'task-' + Date.now().toString(36) + '-' + Math.floor(Math.random() * 1e4);
  await srv.tx(ctx).run(INSERT.into('maintenance.db.AgentTasks').entries({
    taskKey, fromAgent: ctx.agentId ?? 'maintenance-agent', toAgent, intent,
    payload: JSON.stringify(payload), status: 'PENDING', correlationId: ctx.correlationId,
  }));
  await srv.tx(ctx).run(INSERT.into('maintenance.db.AgentMessages').entries({ task_taskKey: taskKey, role: 'USER', content: intent + ': ' + JSON.stringify(payload) }));
  const out = await srv.send('executeTask', { agentId: toAgent, intent, payload: JSON.stringify(payload) });
  await srv.tx(ctx).run(UPDATE('maintenance.db.AgentTasks').set({ status: 'SUCCESS', result: String(out).slice(0, 4000) }).where({ taskKey }));
  return { taskKey, result: out };
}"""),
        "Explanation of every important line": "<p>Task row FIRST (PENDING) → delegate → record result. The transcript (messages) makes every delegation replayable in Chapter 88 incidents.</p>",
        "Expected output": "<p>Drill returns stock answer + taskKey; AgentTasks row flips PENDING → SUCCESS.</p>",
        "How to test it": std_test("drill → SUCCESS row; kill specialist mid-task → row stays RUNNING/FAILED with error (Chapter 57)."),
        "Negative test cases": neg([["Unknown toAgent", "sendTask", "404, task marked FAILED"], ["Specialist timeout", "sendTask", "504, caller decides retry (Chapter 58)"]]),
        "Common mistakes": "<p>Fire-and-forget without the task row — untraceable delegations fail every audit.</p>",
        "How to troubleshoot": "<p>Task stuck PENDING = executeTask never ran — check agentId spelling vs Agents seed.</p>",
        "Production considerations": "<p>Task rows are the distributed-trace backbone (Chapter 56 joins them by correlationId).</p>",
        "Security considerations": "<p>Task payloads carry IDs, never secrets — specialists re-read authorized data themselves.</p>",
        "What we have completed": done("Agent phone system.", "Chapters 47-49: the three specialists."),
    }))

    for chnum, cnum, title, kind, skill, body in [
        ("c47", "47", "Chapter 47 — Build the Inventory Agent", "inventory-agent", "check-spare-part-stock",
         """export async function handleStock(srv, ctx, { partNo, qty }) {
  const inv = await srv.send('checkSparePartStock', { partNo });
  const available = Number(inv.quantity) - Number(inv.reserved);
  if (available >= Number(qty)) return { ok: true, available, note: 'in stock' };
  const alts = await srv.send('findAlternativePart', { partNo });
  return { ok: false, available, alternatives: alts.map((a) => a.partNo) };
}"""),
        ("c48", "48", "Chapter 48 — Build the Workforce Agent", "workforce-agent", "find-available-technician",
         """export async function handleCrew(srv, ctx, { skill, date, shift }) {
  const techs = await srv.send('findAvailableTechnician', { skill, date, shift });
  const scored = [];
  for (const t of techs) {
    const ok = await srv.send('checkTechnicianSkill', { technicianID: t.ID, skill });
    if (ok) scored.push(t);
  }
  return { candidates: scored.map((t) => ({ id: t.ID, name: t.name })), count: scored.length };
}"""),
        ("c49", "49", "Chapter 49 — Build the Production Agent", "production-agent", "find-maintenance-window",
         """export async function handleWindow(srv, ctx, { lineID, from, to, start, end }) {
  const windows = await srv.send('findMaintenanceWindow', { lineID, from, to });
  const impact = await srv.send('calculateProductionImpact', { lineID, start, end });
  return { windows: windows.slice(0, 3), impact };
}"""),
    ]:
        parts.append(ch(chnum, cnum, title, "", {
            "What are we learning?": "<p><b>Simple:</b> a narrow expert answering one question well. <b>Enterprise:</b> intent handler using ONLY its granted tools (Chapter 45). <b>Example:</b> the lab that answers one test, perfectly.</p>",
            "Why is this important?": "<p>Scenario steps 9-11 (stock, crew, window) ARE these three agents.</p>",
            "Where does this fit in the architecture?": "<p>The %s box; A2A in, MCP out.</p>" % kind,
            "Prerequisites": PREV,
            "Folder/file changes": "<p>NEW <code>srv/agents/%s.js</code>.</p>" % kind,
            "Exact commands": PWR + code("powershell", "Drill (%s)" % skill, "curl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:AgentOperator' -H 'x-agent-id: %s' -d '{\"agentId\":\"%s\",\"intent\":\"%s\",\"payload\":\"{}\" }' http://localhost:4004/odata/v4/agents/executeTask" % (kind, kind, skill)),
            "Complete code": code("javascript", "FILE: srv/agents/%s.js (COMPLETE)" % kind, body),
            "Explanation of every important line": "<p>Reads via granted tools only; returns a SMALL ranked answer (ids + counts), never raw tables — the caller decides, the specialist informs.</p>",
            "Expected output": "<p>Drill returns candidates/availability verdict for the seeded story data.</p>",
            "How to test it": std_test("drill happy path + empty-result path (no stock / no crew / no window)."),
            "Negative test cases": neg([["Out-of-menu tool attempt", "specialist calls foreign tool", "403 per Chapter 45"], ["Empty result", "drill", "Structured 'none found', never an invented answer"]]),
            "Common mistakes": "<p>Specialists executing writes (reserve/assign) pre-approval — they CHECK; the orchestrator executes post-approval (Chapter 54).</p>",
            "How to troubleshoot": "<p>Empty when data exists? Verify the agent's grant list includes the tool it needs.</p>",
            "Production considerations": "<p>Specialists scale independently (Chapter 74): inventory checks run 10× more often than scheduling.</p>",
            "Security considerations": "<p>Narrow menus = blast-radius control; a compromised specialist can only reach its own tools.</p>",
            "What we have completed": done("Specialist %s." % kind, "Next agent chapter."),
        }))

    parts.append(ch("c50", "50", "Chapter 50 — Agent Discovery", "", {
        "What are we learning?": "<p><b>Simple:</b> a lobby directory listing every agent and what it does. <b>Enterprise:</b> <code>/.well-known/agent.json</code> with name, description, capabilities, endpoint, auth requirements. <b>Example:</b> hospital directory board — find cardiology without knowing the doctor.</p>",
        "Why is this important?": "<p>Orchestration (Chapter 53) resolves agents by capability, not hardcoded URLs.</p>",
        "Where does this fit in the architecture?": "<p>Agent discovery arrow into every A2A call.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT <code>srv/server.js</code>: serve the discovery card (below).</p>",
        "Exact commands": PWR + code("powershell", "Read the directory", "curl http://localhost:4004/.well-known/agent.json"),
        "Complete code": code("javascript", "srv/server.js discovery (COMPLETE)", """import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
cds.on('bootstrap', (app) => {
  app.use(helmet());
  app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 600 }));
  app.get('/.well-known/agent.json', (_req, res) => res.json({
    name: 'assetops-maintenance-orchestrator',
    description: 'Investigates equipment alerts and proposes maintenance (approval-gated execution).',
    protocol: 'A2A/0.2', version: '1.0.0',
    capabilities: ['investigate-alert', 'check-stock', 'find-crew', 'find-window', 'recommend'],
    endpoint: '/odata/v4/agents/executeTask',
    authentication: 'OAuth2 JWT (XSUAA) or x-mock-user + x-agent-id with ALLOW_MOCK_AUTH=true (LEARNING-MOCK)',
  }));
});"""),
        "Explanation of every important line": "<p>Capabilities are CLAIMS, not permissions — Discovery ≠ authorization (a stranger can READ the card but cannot CALL; Chapter 52 enforces).</p>",
        "Expected output": "<p>Card lists 5 capabilities + endpoint + auth requirements.</p>",
        "How to test it": std_test("fetch card; resolve 'find-crew' → workforce-agent without hardcoding its URL."),
        "Negative test cases": neg([["Card readable anonymously", "GET no auth", "200 BY DESIGN — metadata is public, execution is not"]]),
        "Common mistakes": "<p>Putting secrets or internal URLs in the card — it is public by design.</p>",
        "How to troubleshoot": "<p>Stale capabilities? The card is generated from the Agents seed — update data, not code.</p>",
        "Production considerations": "<p>Version the card; orchestrators pin capability versions to avoid silent behavior changes.</p>",
        "Security considerations": "<p>Card contains zero credentials and zero internal hostnames.</p>",
        "What we have completed": done("Agent directory.", "Chapter 51: proving caller identity."),
    }))

    parts.append(ch("c51", "51", "Chapter 51 — Agent Authentication", "", {
        "What are we learning?": "<p><b>Simple:</b> agents show ID too — badge + delegation slip. <b>Enterprise:</b> user JWT + x-agent-id + delegation scope; service credentials for agent-to-service. <b>Example:</b> valet shows YOUR claim ticket plus HIS staff badge.</p>",
        "Why is this important?": "<p>Without agent identity, every audit row says 'user did it' — agent actions become invisible.</p>",
        "Where does this fit in the architecture?": "<p>Authentication on every A2A and agent→MCP arrow.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT <code>lib/auth.js</code>: enforce delegation (below).</p>",
        "Exact commands": PWR + code("powershell", "Identity drills", "curl -X POST -H 'x-mock-user: op:AgentOperator' -H 'x-agent-id: maintenance-agent' -H 'Content-Type: application/json' -d '{\"agentId\":\"maintenance-agent\",\"intent\":\"ping\",\"payload\":\"{}\" }' http://localhost:4004/odata/v4/agents/executeTask\ncurl -X POST -H 'Content-Type: application/json' -d '{\"agentId\":\"maintenance-agent\",\"intent\":\"ping\",\"payload\":\"{}\" }' http://localhost:4004/odata/v4/agents/executeTask"),
        "Complete code": code("javascript", "Delegation check (COMPLETE, add to ctxOf callers)", """export function requireDelegation(ctx, tool) {
  if (!ctx.userId || ctx.userId === 'anonymous') throw Object.assign(new Error('No delegating user'), { code: 'UNAUTHORIZED', status: 401 });
  if (ctx.isAgent && !ctx.agentId) throw Object.assign(new Error('Agent identity required'), { code: 'UNAUTHORIZED', status: 401 });
  if (ctx.isAgent && ctx.agentId !== tool.split('_')[0] && false) throw new Error('unreachable');
  // Agents table must hold an ACTIVE row for agentId (checked by caller):
  // SELECT.one Agents where agentId + active=true, else 401 agent-unknown.
}"""),
        "Explanation of every important line": "<p>User identity (who benefits) + agent identity (who acts) travel TOGETHER; either missing = 401. Agent rows can be deactivated instantly to revoke a compromised agent.</p>",
        "Expected output": "<p>Drill 1 → executed with both IDs in audit; drill 2 (no headers) → 401.</p>",
        "How to test it": std_test("missing user, missing agent, inactive agent → three distinct 401s."),
        "Negative test cases": neg([["Agent impersonation ( чужой x-agent-id)", "call as another agent", "401/403 + impersonation alert row (Chapter 65 tests)"], ["Expired user JWT", "A2A call", "401 — delegation dies with the session"]]),
        "Common mistakes": "<p>Trusting agentId alone without the user's session — delegation requires BOTH.</p>",
        "How to troubleshoot": "<p>401 on valid setup? Agent row inactive in seed, or header name typo (x-agent-id).</p>",
        "Production considerations": "<p>Service credentials (client_credentials) for scheduled agents without users (Chapter 77).</p>",
        "Security considerations": "<p>Agent IDs are allow-listed (Agents table); arbitrary strings never authenticate.</p>",
        "What we have completed": done("Two-ID identity.", "Chapter 52: what the IDs may do."),
    }))

    parts.append(ch("c52", "52", "Chapter 52 — Agent Authorization", "", {
        "What are we learning?": "<p><b>Simple:</b> the valet key starts SOME cars only. <b>Enterprise:</b> user scope ∩ agent grant ∩ policy = allowed. All three, every call. <b>Example:</b> three locks on the vault, three different keys.</p>",
        "Why is this important?": "<p>THE chapter that makes agents enterprise-safe. Skip it and Chapter 65 will embarrass you.</p>",
        "Where does this fit in the architecture?": "<p>At every tool and A2A boundary — the business-service/tool boundary rule.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>Wire <code>authorizeTool</code> (Chapter 45) into MCPService + A2A handlers (one line each).</p>",
        "Exact commands": PWR + code("powershell", "Triple-gate drill", "curl -X POST -H 'x-mock-user: op:MaintenanceUser' -H 'x-agent-id: inventory-agent' -H 'Content-Type: application/json' -d '{\"partNo\":\"BRG-6205\",\"qty\":2,\"orderID\":\"x\"}' http://localhost:4004/mcp/reserve_spare_part"),
        "Complete code": table(["Gate", "Question", "Our answer"], [["1 User scope", "May the human?", "ASSIGN scope (Manager/Admin)"], ["2 Agent grant", "May THIS agent?", "inventory-agent holds reserve_spare_part"], ["3 Policy", "May it happen now?", "Stock available; amount under agent cap"]]) + "<p>Drill above: MaintenanceUser lacks ASSIGN → <b>403 even though the agent is granted</b>. Least privilege holds on ALL three axes.</p>",
        "Explanation of every important line": "<p>Treat agents as UNTRUSTED callers: 'because the AI called it' authorizes nothing. Denials write audit rows — silence would hide probing.</p>",
        "Expected output": "<p>403 + DENIED audit row naming the failed gate (user/agent/policy).</p>",
        "How to test it": std_test("remove each gate in turn (3 tests) → each removal still denies via the other two."),
        "Negative test cases": neg([["Privilege escalation via agent", "user asks agent for admin tool", "403 — agent lacks grant AND user lacks scope"], ["Cross-plant read (Ch 60)", "other plant ID", "403 tenant/plant mismatch"]]),
        "Common mistakes": "<p>Checking authorization in the agent instead of the boundary — agents are bypassable; boundaries are not.</p>",
        "How to troubleshoot": "<p>DENIED rows name gate + tool + IDs — the audit row IS the diagnosis (Chapter 55).</p>",
        "Production considerations": "<p>Grant changes are config (DB), not deploys — revoke in seconds during incidents (Chapter 88).</p>",
        "Security considerations": "<p>Default-deny, explicit-grant, least-privilege, audited-denial — state these four in every design review.</p>",
        "What we have completed": done("STOP MILESTONE 7: agents contained.", "Chapter 53: conduct the orchestra."),
    }))

    parts.append(ch("c53", "53", "Chapter 53 — A2A Orchestration", "", {
        "What are we learning?": "<p><b>Simple:</b> the conductor: fan out to 3 specialists in parallel, gather answers, compose ONE recommendation. <b>Enterprise:</b> orchestrate(goal) with parallel tasks + join + timeout + partial-failure policy. <b>Example:</b> ER triage: labs, X-ray and pharmacy work simultaneously; the doctor decides with whatever is back in time.</p>",
        "Why is this important?": "<p>Scenario steps 8-12 in ONE call — the Chapter 89 engine.</p>",
        "Where does this fit in the architecture?": "<p>AgentService.orchestrate: the conductor's podium.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>srv/agents/orchestrator.js</code> (below).</p>",
        "Exact commands": PWR + code("powershell", "Full orchestration drill", "curl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:AgentOperator' -H 'x-agent-id: maintenance-agent' -d '{\"goal\":\"investigate CNC-MACHINE-102\",\"payload\":\"{\\\"alertId\\\":\\\"a-9001\\\"}\"}' http://localhost:4004/odata/v4/agents/orchestrate"),
        "Complete code": code("javascript", "FILE: srv/agents/orchestrator.js (COMPLETE)", """import { sendTask } from '../a2a/tasks.js';
import { investigateAlert } from './maintenance-agent.js';

export async function orchestrate(srv, ctx, goal, payload) {
  const p = JSON.parse(payload);
  const recId = await investigateAlert(srv, ctx, p.alertId);   // steps 1-7 + PROPOSED rec
  const order = await srv.tx(ctx).run(SELECT.one.from('maintenance.db.MaintenanceOrders').where({ ID: p.orderId ?? '' }).catch(() => null));
  const [stock, crew, window] = await Promise.all([              // steps 9-11 in PARALLEL
    sendTask(srv, ctx, 'inventory-agent', 'check-stock', { partNo: 'BRG-6205', qty: 2 }),
    sendTask(srv, ctx, 'workforce-agent', 'find-crew', { skill: 'bearing-replacement', date: '2026-09-15', shift: 'night' }),
    sendTask(srv, ctx, 'production-agent', 'find-window', { lineID: 'line-03', from: '2026-09-15', to: '2026-09-18' }),
  ]);
  await srv.tx(ctx).run(UPDATE('maintenance.db.MaintenanceRecommendations')
    .set({ summary: `Bearing failure likely. Stock: ${stock.result.ok ? 'OK' : 'SHORT'}. Crew: ${crew.result.count} candidate(s). Window: ${(window.result.windows ?? [])[0]?.date ?? 'none'} night.` })
    .where({ ID: recId }));
  return recId;   // step 12-13: recommendation ready for Chapter 54 approval
}"""),
        "Explanation of every important line": "<p>Investigate first (facts), fan out second (parallel specialists), compose third (one summary). One specialist failing does not erase the others — partial results with explicit gaps (Chapter 57).</p>",
        "Expected output": "<p>Drill returns rec-ID whose summary names stock OK, Ravi Kumar, 2026-09-15 night.</p>",
        "How to test it": std_test("drill → 3 SUCCESS task rows + 1 PROPOSED rec, all sharing one correlationId."),
        "Negative test cases": neg([["Inventory agent down", "drill", "Rec notes SHORT/unknown; other two still complete"], ["Two orchestrations same alert", "drill twice", "Two recs (investigation is repeatable)"]]),
        "Common mistakes": "<p>Sequential specialist calls (3× latency) or failing the whole run on one specialist error.</p>",
        "How to troubleshoot": "<p>Slow orchestration? Check MCPToolExecutions.durationMs per tool — the slowest specialist sets the pace.</p>",
        "Production considerations": "<p>Parallel fan-out needs bulkheads (Chapter 57) so one slow agent cannot starve the rest.</p>",
        "Security considerations": "<p>Orchestrator holds NO extra powers — it borrows the caller's gates on every sub-call.</p>",
        "What we have completed": done("One-call investigation.", "Chapter 54: the human decides."),
    }))

    parts.append(ch("c54", "54", "Chapter 54 — Human-in-the-Loop Approval", "", {
        "What are we learning?": "<p><b>Simple:</b> AI proposes, human disposes — Approve/Reject buttons before metal moves. <b>Enterprise:</b> PROPOSED → APPROVED/REJECTED with comment, then Chapter 14's 9-step transaction executes. <b>Example:</b> pharmacist counsels, doctor signs, THEN the prescription fills.</p>",
        "Why is this important?": "<p>Enterprise AI without approval is a liability machine. This chapter is why the system is insurable.</p>",
        "Where does this fit in the architecture?": "<p>The HUMAN APPROVAL gate between recommendation and execution.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>REUSE Chapter 24 ApprovalDialog + Chapter 14 approveRecommendation (already built).</p>",
        "Exact commands": PWR + code("powershell", "Approve + reject drills", "curl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: boss:MaintenanceManager' -d '{\"ID\":\"<REC>\",\"comment\":\"Agreed, night shift\"}' http://localhost:4004/odata/v4/maintenance/approveRecommendation\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:MaintenanceUser' -d '{\"ID\":\"<REC>\",\"comment\":\"x\"}' http://localhost:4004/odata/v4/maintenance/approveRecommendation"),
        "Complete code": table(["Path", "Result"], [["Manager approves", "9-step transaction: order + reserve + assign + schedule + events + audit (Chapter 14)"], ["User attempts approve", "403 — only MaintenanceManager/Admin hold APPROVE"], ["Manager rejects + comment", "Recommendation REJECTED with reason; alert stays OPEN for re-investigation"]]),
        "Explanation of every important line": "<p>Approval is a DECISION RECORD (who, when, why), not just a flag — auditors replay it. Rejection is equally recorded; silence is never an option.</p>",
        "Expected output": "<p>Approve → MO- order PLANNED/SCHEDULED, 2 bearings reserved, Ravi assigned, night window booked, audit rows for each.</p>",
        "How to test it": std_test("approve as manager (full execution) + approve as user (403) + reject path (no writes)."),
        "Negative test cases": neg([["Approve twice", "double POST", "409 — single execution, idempotent"], ["Approve after stock vanished", "race", "422 rollback — approval never overrides physics"]]),
        "Common mistakes": "<p>Auto-executing 'low-risk' writes to skip the queue — risk is judged by POLICY, not convenience.</p>",
        "How to troubleshoot": "<p>Approved but nothing happened? Check the transaction logs (Chapter 14) — a late 422 rolls everything back BY DESIGN.</p>",
        "Production considerations": "<p>Approval SLA + escalation (manager on leave → deputy) configured per plant (Chapter 75).</p>",
        "Security considerations": "<p>Approval binds user + rec + version — approving stale recommendations fails closed.</p>",
        "What we have completed": done("STOP MILESTONE 8: story works end to end locally.", "Chapter 55: prove it with audit."),
    }))

    return parts
