"""Part 8: CH40-CH45."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done

TOOLS_CDS = """service MCPService @(path:'/mcp') {
  // equipment + sensors + history (read-only)
  function get_equipment(ID : String) returns db.Equipment;
  function search_equipment(search : String) returns many db.Equipment;
  function get_equipment_history(equipmentID : String) returns many db.MaintenanceHistory;
  function get_sensor_readings(equipmentID : String, top : Integer) returns many db.SensorReadings;
  function get_equipment_alerts(status : String) returns many db.EquipmentAlerts;
  // maintenance writes (approval-gated, idempotent)
  action create_maintenance_order(equipmentID : String, alertID : String, priority : String) returns db.MaintenanceOrders;
  action update_maintenance_order(ID : String, patch : LargeString) returns db.MaintenanceOrders;
  action schedule_maintenance(orderID : String, start : DateTime, end : DateTime) returns String;
  // spares (reads free, reserve gated)
  function check_spare_part_stock(partNo : String) returns db.Inventory;
  action reserve_spare_part(partNo : String, qty : Decimal, orderID : String) returns db.StockMovements;
  function find_alternative_part(partNo : String) returns many db.SpareParts;
  // workforce (reads free, assign gated)
  function find_available_technician(skill : String, date : Date, shift : String) returns many db.Technicians;
  function check_technician_skill(technicianID : String, skill : String) returns Boolean;
  action assign_technician(orderID : String, technicianID : String) returns db.TechnicianAssignments;
  // production (reads)
  function get_production_schedule(lineID : String, from : Date, to : Date) returns many db.ProductionSchedules;
  function calculate_production_impact(lineID : String, start : DateTime, end : DateTime) returns LargeString;
  function find_maintenance_window(lineID : String, from : Date, to : Date) returns many db.ProductionSchedules;
}"""


def build():
    parts = []

    parts.append(ch("c40", "40", "Chapter 40 — AI Architecture", "", {
        "What are we learning?": "<p><b>Simple:</b> where the 'brain' sits: agent → tools → CAP, never agent → database. <b>Enterprise:</b> provider abstraction (mock local, AI Core prod), tool boundary, approval gate. <b>Example:</b> surgeon (agent) uses sterilized instruments (tools) — never bare hands in the wound (DB).</p>",
        "Why is this important?": "<p>Every Chapter 41-59 decision references this picture. Wrong picture = insecure agent.</p>",
        "Where does this fit in the architecture?": "<p>The AI / AGENT LAYER box and all arrows below it.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>lib/ai.js</code> (provider interface + mock).</p>",
        "Exact commands": "<p>None — interface chapter.</p>",
        "Complete code": mermaid("FIG. 3 — AI LAYER, ONE GOVERNED PATH", """flowchart TD
  U["User"] --> MA["Maintenance Agent"]
  MA --> MCP["MCP tools (17)"]
  MCP --> CAP["CAP services + RBAC + audit"]
  MA --> A2A["A2A tasks"]
  A2A --> IA["Inventory Agent"]
  A2A --> WA["Workforce Agent"]
  A2A --> PA["Production Agent"]
  IA --> MCP
  WA --> MCP
  PA --> MCP
  MA --> HU["Human approval gate"]
  HU --> EX["Execute writes"]""") + code("javascript", "FILE: lib/ai.js (COMPLETE)", """export async function generate(prompt, tools = []) {
  if (process.env.AI_API_KEY) { /* CURRENT SAP APPROACH: AI Core call here (Ch 75). VERIFY SDK names. */ throw new Error('AI Core wiring: see Chapter 75'); }
  return '[mock-ai] ' + String(prompt).slice(0, 200);   // LEARNING-MOCK APPROACH
}"""),
        "Explanation of every important line": "<p>Mock default keeps Chapters 41-54 runnable with ZERO keys or cost. The throw (not silent mock) when a key exists prevents accidentally demoing against production AI.</p>",
        "Expected output": "<p><code>generate('hi')</code> returns a mock string; with a key set it refuses until Chapter 75 wiring.</p>",
        "How to test it": std_test("call generate with/without AI_API_KEY; assert mock vs explicit error."),
        "Negative test cases": neg([["AI key in git", "scan", "CI secret-scan fails the build (Chapter 72)"]]),
        "Common mistakes": "<p>Hardcoding prompts with live IDs — prompts are templates; IDs arrive as parameters.</p>",
        "How to troubleshoot": "<p>Agent answers look canned? You are on mock — expected until Chapter 75.</p>",
        "Production considerations": "<p>Model choice (size/cost/latency) is deployment config, not code (Chapter 75).</p>",
        "Security considerations": "<p>Business text entering prompts is DATA — sanitized per Chapter 13 before use (Chapter 59).</p>",
        "What we have completed": done("AI layer contract.", "Chapter 41: the lead agent."),
    }))

    parts.append(ch("c41", "41", "Chapter 41 — Build the Maintenance Agent", "", {
        "What are we learning?": "<p><b>Simple:</b> a program that investigates: gather facts → analyze → ask specialists → recommend. <b>Enterprise:</b> the investigate-alert pipeline driving the Chapter 89 demo. <b>Example:</b> detective: collect evidence, consult experts, present the case — the judge (human) decides.</p>",
        "Why is this important?": "<p>The hero of the course. Everything after this chapter feeds or constrains it.</p>",
        "Where does this fit in the architecture?": "<p>MAINTENANCE AGENT box; calls MCP directly, specialists via A2A.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>srv/agents/maintenance-agent.js</code> (orchestrator logic).</p>",
        "Exact commands": PWR + code("powershell", "Investigate drill (alert must exist)", "curl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:AgentOperator' -H 'x-agent-id: maintenance-agent' -d '{\"agentId\":\"maintenance-agent\",\"intent\":\"investigate-alert\",\"payload\":\"{\\\"alertId\\\":\\\"a-9001\\\"}\"}' http://localhost:4004/odata/v4/agents/executeTask"),
        "Complete code": code("javascript", "FILE: srv/agents/maintenance-agent.js (COMPLETE pipeline)", """import { generate } from '../../lib/ai.js';

export async function investigateAlert(srv, ctx, alertId) {
  const tx = srv.tx(ctx);
  const alert = await tx.run(SELECT.one.from('maintenance.db.EquipmentAlerts').where({ ID: alertId }));
  const equipment = await tx.run(SELECT.one.from('maintenance.db.Equipment').where({ ID: alert.equipment_ID }));
  const readings = await tx.read('maintenance.db.SensorReadings').where({ equipment_ID: equipment.ID }).orderBy('measuredAt desc').limit(50);
  const history = await tx.read('maintenance.db.MaintenanceHistory').where({ equipment_ID: equipment.ID }).orderBy('performedAt desc').limit(10);
  const over = readings.filter((r) => Number(r.value) >= 7.1).length;
  const analysis = await generate(`Bearing analysis for ${equipment.equipmentId}: ${over}/50 readings over alarm, history: ${history.map((h) => h.failureCode).join(',') || 'none'}`);
  const recId = 'rec-' + Date.now().toString(36);
  await tx.run(INSERT.into('maintenance.db.MaintenanceRecommendations').entries({
    ID: recId, alert_ID: alertId, agentId: 'maintenance-agent',
    summary: 'Likely bearing failure (' + over + '/50 alarm readings). ' + analysis,
    actions: JSON.stringify({ orders: [{ orderNo: 'MO-' + Date.now().toString().slice(-6), priority: 'HIGH' }], reserve: [], assign: [] }),
    status: 'PROPOSED',
  }));
  await tx.run(INSERT.into('maintenance.db.AgentExecutions').entries({ agent_ID: 'maintenance-agent', toolName: 'investigate-alert', status: 'SUCCESS', correlationId: ctx.correlationId }));
  return recId;   // recommendation only — execution waits for Chapter 54 approval
}"""),
        "Explanation of every important line": table(["Step", "Maps to scenario step"], [["get equipment/alert", "Steps 1 + case file"], ["50 readings + 10 history", "Steps 2-4 (bounded pages)"], ["over-alarm count", "Steps 5-6, deterministic math — LLM words never decide alone"], ["PROPOSED recommendation", "Steps 12-13; writes wait for approval (Ch 54)"]]),
        "Expected output": "<p>Drill returns rec-ID; MaintenanceRecommendations row is PROPOSED with bearing summary.</p>",
        "How to test it": std_test("drill → rec row PROPOSED; re-drill same alert → second rec (investigation is repeatable, execution is not)."),
        "Negative test cases": neg([["Unknown alertId", "drill", "404, zero writes"], ["Agent without grant", "drill as stranger", "403 (Chapter 52)"]]),
        "Common mistakes": "<p>Letting the agent EXECUTE writes here — investigation proposes, approval disposes (Chapter 54).</p>",
        "How to troubleshoot": "<p>Empty readings? Seed + mock API (Chapters 09, 38) must both exist.</p>",
        "Production considerations": "<p>Reading caps (50/10) bound cost + latency — tune from Chapter 85 metrics.</p>",
        "Security considerations": "<p>Agent reads only what its grants allow; every read logged with agentId (Chapter 55).</p>",
        "What we have completed": done("Investigating lead agent.", "Chapter 42: the protocol it speaks."),
    }))

    parts.append(ch("c42", "42", "Chapter 42 — MCP Fundamentals", "", {
        "What are we learning?": "<p><b>Simple:</b> MCP = a waiter's notepad: structured orders (tools) between AI (guest) and kitchen (CAP). <b>Enterprise:</b> Host/Client/Server, Tools/Resources/Prompts, JSON-RPC transport. <b>Example:</b> REST is shouting into the kitchen; MCP is the ticket rail with dish numbers.</p>",
        "Why is this important?": "<p>Chapters 43-44 build a server in this image. Wrong mental model = wrong security assumptions.</p>",
        "Where does this fit in the architecture?": "<p>Every MCP arrow: agent → tools → CAP.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>None — vocabulary chapter with one tiny local experiment.</p>",
        "Exact commands": PWR + code("powershell", "See JSON-RPC shape (any MCP endpoint after Ch 43)", "curl -X POST -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' http://localhost:4004/mcp"),
        "Complete code": table(["Term", "Simple", "Ours"], [["MCP Host", "The app running the AI", "AgentService runtime"], ["MCP Client", "The pad session per request", "Per-request tool session"], ["MCP Server", "The ticket rail", "MCPService (Chapter 43)"], ["Tool", "One orderable dish", "17 tools (Chapter 44)"], ["Resource", "Read-only specials board", "Schedules and manuals"], ["Prompt", "House recipe card", "Investigation template (Ch 41)"], ["Transport", "How tickets travel", "HTTP JSON-RPC local, Streamable HTTP prod"], ["JSON-RPC", "Envelope format", "{jsonrpc, id, method, params}"]]) + grid([("REST vs MCP", "REST has human docs and bespoke auth. MCP has a machine menu, one session, per-tool grants.")], 1),
        "Explanation of every important line": "<p>MCP authorizes NOTHING itself — it carries identity to CAP, which decides (Chapter 45). Memorize this before building.</p>",
        "Expected output": "<p>You can label Host/Client/Server/Tool on FIG. 3 blindfolded.</p>",
        "How to test it": std_test("explain why check_spare_part_stock is safer as a tool than as raw SQL access."),
        "Negative test cases": neg([["'MCP handles auth'", "design review", "Rejected — transport ≠ authority (Chapter 45)"]]),
        "Common mistakes": "<p>Exposing a generic sql-query tool 'for flexibility' — Chapter 65 exploits exactly this.</p>",
        "How to troubleshoot": "<p>Confused by transports? Local HTTP JSON-RPC is all Chapters 43-44 need.</p>",
        "Production considerations": "<p>Tool schemas are versioned contracts — changing inputs breaks agents (Chapter 66 tests lock them).</p>",
        "Security considerations": "<p>Minimal output schemas: tools return need-to-know fields, never full rows with PII.</p>",
        "What we have completed": done("MCP literacy.", "Chapter 43: the server."),
    }))

    parts.append(ch("c43", "43", "Chapter 43 — Build an MCP Server", "", {
        "What are we learning?": "<p><b>Simple:</b> the ticket rail: one endpoint serving the 17-dish menu. <b>Enterprise:</b> MCPService CDS + handler wiring each tool to the SAME CAP logic UI uses. <b>Example:</b> one kitchen serving dine-in (UI) and room service (agents).</p>",
        "Why is this important?": "<p>Single implementation, two consumers — no logic drift between human and agent paths.</p>",
        "Where does this fit in the architecture?": "<p>The MCP box between agents and CAP.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>srv/mcp-service.cds</code> + <code>srv/mcp-service.js</code> (wiring; tool bodies in Chapter 44).</p>",
        "Exact commands": PWR + code("powershell", "List the menu", "npm start\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:AgentOperator' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' http://localhost:4004/mcp"),
        "Complete code": code("cds", "FILE: srv/mcp-service.cds (COMPLETE 17 tools)", "using { maintenance.db as db } from '../db/schema';\n\nservice MCPService @(path:'/mcp') {\n" + TOOLS_CDS + "\n}") + code("javascript", "FILE: srv/mcp-service.js (COMPLETE wiring pattern)", """import cds from '@sap/cds';
import { ctxOf } from '../lib/auth.js';
import * as tools from './mcp/tools.js';   // one function per tool (Chapter 44)

export default class MCPService extends cds.ApplicationService {
  async init() {
    for (const name of Object.keys(tools)) {
      this.on(name, async (req) => {
        const ctx = await ctxOf(req);                       // identity first
        const started = Date.now();
        try {
          const out = await tools[name](this, ctx, req.data);   // tool body
          await this.logExec(ctx, name, req.data, out, 'SUCCESS', Date.now() - started);
          return out;
        } catch (e) {
          await this.logExec(ctx, name, req.data, null, 'FAILED', Date.now() - started, e.message);
          throw e;
        }
      });
    }
    return super.init();
  }
  async logExec(ctx, tool, input, output, status, ms, err = '') {
    await cds.tx().run(INSERT.into('maintenance.db.MCPToolExecutions').entries({
      toolName: tool, actorType: ctx.isAgent ? 'AGENT' : 'USER', actorId: ctx.userId,
      agentId: ctx.agentId, input: JSON.stringify(input), output: JSON.stringify(output ?? '').slice(0, 4000),
      status, error: err, correlationId: ctx.correlationId, durationMs: ms,
    }));
  }
}"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["Object.keys(tools) loop", "Menu generated from code — adding a tool = exporting a function"], ["ctxOf first", "No anonymous tool calls, ever"], ["logExec both paths", "SUCCESS + FAILED both recorded — debugging needs failures too"], ["output sliced", "Audit stores excerpts, never secrets or megabytes"]]),
        "Expected output": "<p>tools/list returns 17 names; each call writes an MCPToolExecutions row.</p>",
        "How to test it": std_test("list → 17; call get_equipment → row with durationMs + correlationId."),
        "Negative test cases": neg([["No identity header", "tools/call", "401, nothing executed, FAILED row optional"]]),
        "Common mistakes": "<p>Tool bodies with inline SQL — they must call the SAME service logic as UI (Chapter 44).</p>",
        "How to troubleshoot": "<p>Tool missing from list = not exported from tools.js (check spelling + restart).</p>",
        "Production considerations": "<p>Gateway (Chapter 75) filters this menu per agent — server lists all, gateway narrows.</p>",
        "Security considerations": "<p>Execution log is append-only in practice — nobody edits audit rows (Chapter 55).</p>",
        "What we have completed": done("Tool rail with logging.", "Chapter 44: the 17 dishes."),
    }))

    parts.append(ch("c44", "44", "Chapter 44 — Build MCP Tools", "", {
        "What are we learning?": "<p><b>Simple:</b> cook each dish: schema in, validation, authorized CAP call, audited out. <b>Enterprise:</b> all 17 tools with timeout + idempotency where required. <b>Example:</b> recipes with hygiene rules printed on each card.</p>",
        "Why is this important?": "<p>Agents are only as safe as their tools. This chapter IS agent safety, concretely.</p>",
        "Where does this fit in the architecture?": "<p>Inside the MCP box: 17 implementations.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>srv/mcp/tools.js</code> (all 17, pattern below shows 4 fully + the rest follow it).</p>",
        "Exact commands": PWR + code("powershell", "Tool drills", "curl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:AgentOperator' -d '{\"ID\":\"eq-cnc102\"}' http://localhost:4004/mcp/get_equipment\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: op:AgentOperator' -d '{\"partNo\":\"BRG-6205\"}' http://localhost:4004/mcp/check_spare_part_stock"),
        "Complete code": code("javascript", "FILE: srv/mcp/tools.js (COMPLETE pattern — replicate per tool)", """import { validateReservation } from '../../lib/validation.js';

const TIMEOUT = (ms, p) => Promise.race([p, new Promise((_, rej) => setTimeout(() => rej(Object.assign(new Error('Tool timeout'), { code: 'UPSTREAM_TIMEOUT', status: 504 })), ms))]);

export async function get_equipment(srv, ctx, { ID }) {
  if (!ID) throw Object.assign(new Error('ID required'), { code: 'VALIDATION_ERROR', status: 400 });
  return TIMEOUT(5000, srv.tx(ctx).run(SELECT.one.from('maintenance.db.Equipment').where({ ID })));
}
export async function get_sensor_readings(srv, ctx, { equipmentID, top = 50 }) {
  const n = Math.min(Number(top) || 50, 200);
  return TIMEOUT(5000, srv.tx(ctx).read('maintenance.db.SensorReadings').where({ equipment_ID: equipmentID }).orderBy('measuredAt desc').limit(n));
}
export async function check_spare_part_stock(srv, ctx, { partNo }) {
  const inv = await srv.tx(ctx).run(SELECT.one.from('maintenance.db.Inventory').where({ part: { partNo } }));
  if (!inv) throw Object.assign(new Error('Part not stocked'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
  return { ...inv, available: Number(inv.quantity) - Number(inv.reserved) };
}
export async function reserve_spare_part(srv, ctx, { partNo, qty, orderID }) {
  validateReservation({ qty });                       // schema + validation
  const key = ctx.correlationId + ':' + partNo + ':' + orderID;   // idempotency
  const tx = srv.tx(ctx);
  const dup = await tx.run(SELECT.one.from('maintenance.db.StockMovements').where({ idempotencyKey: key }));
  if (dup) return dup;                                // retry returns previous result
  const inv = await check_spare_part_stock(srv, ctx, { partNo });
  if (Number(qty) > inv.available) throw Object.assign(new Error('Insufficient stock'), { code: 'BUDGET_EXCEEDED', status: 422 });
  await tx.run(UPDATE('maintenance.db.Inventory').set({ reserved: { '+=': Number(qty) } }).where({ ID: inv.ID }));
  const row = { part_ID: inv.part_ID, plant_ID: inv.plant_ID, qty: -Number(qty), type: 'RESERVE', idempotencyKey: key, refOrder_ID: orderID };
  await tx.run(INSERT.into('maintenance.db.StockMovements').entries(row));
  return row;
}
// Remaining 13 follow the same skeleton: validate -> authorize (Ch 45) -> TIMEOUT-wrapped CAP call -> audited return.
// create/update/schedule/assign/find_alternative/calculate_impact/find_window/get_history/get_alerts/search/check_skill/get_schedule
"""),
        "Explanation of every important line": table(["Rule", "Applies to"], [["TIMEOUT 5s", "ALL 17 — no hanging tools"], ["Idempotency key", "create/update/schedule/reserve/assign (Chapter 58)"], ["Duplicate-key pre-check", "Retries return the FIRST result, never a second row"], ["422 on short stock", "Business refusal, not a crash"]]),
        "Expected output": "<p>All drills 200 with correct payloads; reserve twice → identical single movement.</p>",
        "How to test it": std_test("each tool: happy path + missing-param 400 + timeout drill (Chapter 66 automates)."),
        "Negative test cases": neg([["qty -2", "reserve", "400, stock untouched"], ["partNo NOPE", "check", "404"], ["Double reserve retry", "same key", "same row returned"]]),
        "Common mistakes": "<p>New tools without the TIMEOUT wrapper — one slow tool stalls the whole agent (Chapter 57).</p>",
        "How to troubleshoot": "<p>Tool 500s? Read MCPToolExecutions.error for the tool — the log row IS the debugger.</p>",
        "Production considerations": "<p>Tool latency percentiles feed Chapter 85 dashboards — durationMs already captured.</p>",
        "Security considerations": "<p>Parameter allow-listing per tool (Chapter 45 adds the authorization layer on top).</p>",
        "What we have completed": done("STOP MILESTONE 6: 17 working tools.", "Chapter 45: who may call which."),
    }))

    parts.append(ch("c45", "45", "Chapter 45 — MCP Tool Security", "", {
        "What are we learning?": "<p><b>Simple:</b> the menu differs per guest: kids get no knives. <b>Enterprise:</b> per-tool scopes + per-agent grants + parameter guards. <b>Example:</b> valet key vs master key.</p>",
        "Why is this important?": "<p>A tool without authorization is a loaded gun on the ticket rail.</p>",
        "Where does this fit in the architecture?": "<p>The shield INSIDE the MCP box, before every tool body.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>lib/toolPolicy.js</code>; MCPService checks BEFORE calling tool bodies.</p>",
        "Exact commands": PWR + code("powershell", "Grant drills", "curl -X POST -H 'x-mock-user: op:AgentOperator' -H 'x-agent-id: inventory-agent' -H 'Content-Type: application/json' -d '{\"partNo\":\"BRG-6205\",\"qty\":2,\"orderID\":\"x\"}' http://localhost:4004/mcp/reserve_spare_part\ncurl -X POST -H 'x-mock-user: stranger:MaintenanceUser' -d '{\"partNo\":\"BRG-6205\",\"qty\":2,\"orderID\":\"x\"}' http://localhost:4004/mcp/reserve_spare_part"),
        "Complete code": code("javascript", "FILE: lib/toolPolicy.js (COMPLETE)", """const TOOL_SCOPE = {
  get_equipment: 'READ', search_equipment: 'READ', get_equipment_history: 'READ',
  get_sensor_readings: 'READ', get_equipment_alerts: 'READ', check_spare_part_stock: 'READ',
  find_alternative_part: 'READ', find_available_technician: 'READ', check_technician_skill: 'READ',
  get_production_schedule: 'READ', calculate_production_impact: 'READ', find_maintenance_window: 'READ',
  create_maintenance_order: 'WRITE', update_maintenance_order: 'WRITE', schedule_maintenance: 'ASSIGN',
  reserve_spare_part: 'ASSIGN', assign_technician: 'ASSIGN',
};
const AGENT_TOOLS = {
  'maintenance-agent': ['get_equipment', 'search_equipment', 'get_equipment_history', 'get_sensor_readings', 'get_equipment_alerts', 'find_maintenance_window', 'calculate_production_impact'],
  'inventory-agent': ['check_spare_part_stock', 'reserve_spare_part', 'find_alternative_part', 'get_equipment'],
  'workforce-agent': ['find_available_technician', 'check_technician_skill', 'assign_technician', 'get_equipment'],
  'production-agent': ['get_production_schedule', 'find_maintenance_window', 'calculate_production_impact', 'get_equipment'],
};
export function authorizeTool(ctx, tool) {
  const need = TOOL_SCOPE[tool];
  if (!need) throw Object.assign(new Error('Unknown tool'), { code: 'RESOURCE_NOT_FOUND', status: 404 });
  if (!ctx.roles.includes('MaintenanceAdmin') && !ctx.roles.includes('MaintenanceManager') && !ctx.roles.includes('AgentOperator') && !(need === 'READ' && ctx.roles.includes('MaintenanceUser')))
    throw Object.assign(new Error('Tool forbidden'), { code: 'FORBIDDEN', status: 403 });
  if (ctx.isAgent && !(AGENT_TOOLS[ctx.agentId] ?? []).includes(tool))
    throw Object.assign(new Error('Agent not granted for ' + tool), { code: 'FORBIDDEN', status: 403 });
}"""),
        "Explanation of every important line": "<p>Two gates: ROLE scope (humans) AND agent grant list (agents). Writes need ASSIGN/WRITE roles; agents NEVER hold create/update/schedule directly — the orchestrator executes post-approval (Chapter 54).</p>",
        "Expected output": "<p>Inventory-agent reserves OK; stranger gets 403 + DENIED audit row.</p>",
        "How to test it": std_test("4 agents × 17 tools matrix: assert allow/deny per table (Chapter 66 automates)."),
        "Negative test cases": neg([["workforce-agent calls reserve_spare_part", "tools/call", "403 — outside its menu"], ["User calls assign_technician", "tools/call", "403 — needs ASSIGN"]]),
        "Common mistakes": "<p>Granting by role only and forgetting the agent list — agents inherit human powers. Both gates, always.</p>",
        "How to troubleshoot": "<p>Unexpected 403? Print ctx.{roles,agentId} vs the two tables — the answer is always there.</p>",
        "Production considerations": "<p>Grant tables move to DB-backed config in prod (like procurement's AgentToolPermissions) — same checks, editable without deploy.</p>",
        "Security considerations": "<p>Unknown tool = 404 (not 403) — do not confirm the existence of hidden tools.</p>",
        "What we have completed": done("Governed tool rail.", "Chapter 46: agents talking to agents."),
    }))

    return parts
