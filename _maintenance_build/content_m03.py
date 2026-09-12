"""Part 3: CH10-CH16."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done

HANDLER = """import cds from '@sap/cds';
import { validateOrder, validateAssignment } from '../../lib/validation.js';
import { writeAudit } from '../../lib/audit.js';

async function ctxOf(req) {
  const user = req.user?.id ?? req.http?.req?.headers?.['x-mock-user'] ?? 'anonymous';
  return { userId: String(user).split(':')[0], roles: String(user).split(':')[1] ? [String(user).split(':')[1]] : [], correlationId: req.http?.req?.headers?.['x-correlation-id'] ?? ('corr-' + Date.now()) };
}

export default class MaintenanceService extends cds.ApplicationService {
  async init() {
    const { MaintenanceOrders } = this.entities;
    this.before('CREATE', MaintenanceOrders, async (req) => {
      req.data.status = 'DRAFT';
      req.data.orderNo ??= 'MO-' + Date.now().toString().slice(-6);
      validateOrder(req.data);
    });
    this.after('CREATE', MaintenanceOrders, async (data, req) => {
      try { if (data) await writeAudit(this, await ctxOf(req), { action: 'MAINTENANCE_ORDER_CREATED', entity: 'MaintenanceOrders', entityId: data.ID }); }
      catch (e) { console.error('[audit] failed', e.message); }
      return data;
    });
    return super.init();
  }
}"""


def build():
    parts = []

    parts.append(ch("c10", "10", "Chapter 10 — Create CAP Services", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> turn tables into web APIs with one declaration each. <b>Enterprise:</b> six bounded-context services with explicit actions for every state change. <b>Example:</b> menus per kitchen station — equipment desk, order desk, crew desk.</p>",
        "Why is this important?": "<p>UI (19-33), tools (44) and agents (47-49) all call THESE services. No service = nothing to call.</p>",
        "Where does this fit in the architecture?": "<p>The CAP box: six doors into the same database.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>srv/*-service.cds</code> (6 files). Handlers (<code>.js</code>) arrive in Chapter 11.</p>",
        "Exact commands": PWR + code("powershell", "Create + list routes", "New-Item srv/equipment-service.cds, srv/maintenance-service.cds, srv/workforce-service.cds, srv/inventory-service.cds, srv/production-service.cds, srv/agent-service.cds, srv/mcp-service.cds\nnpm start\n# open http://localhost:4004 -> six service links appear"),
        "Complete code": code("cds", "FILE: srv/equipment-service.cds + maintenance-service.cds", """using { maintenance.db as db } from '../db/schema';

service EquipmentService @(path:'/odata/v4/equipment') {
  entity Plants as projection on db.Plants;
  entity ProductionLines as projection on db.ProductionLines;
  entity EquipmentTypes as projection on db.EquipmentTypes;
  entity Equipment as projection on db.Equipment;
  entity Sensors as projection on db.Sensors;
  entity SensorReadings as projection on db.SensorReadings;
  entity EquipmentAlerts as projection on db.EquipmentAlerts;
  action acknowledgeAlert(ID : String) returns String;
  action resolveAlert(ID : String) returns String;
}

// srv/maintenance-service.cds
service MaintenanceService @(path:'/odata/v4/maintenance') {
  entity MaintenancePlans as projection on db.MaintenancePlans;
  entity MaintenanceOrders as projection on db.MaintenanceOrders;
  entity MaintenanceOperations as projection on db.MaintenanceOperations;
  entity MaintenanceHistory as projection on db.MaintenanceHistory;
  entity Inspections as projection on db.Inspections;
  entity MaintenanceRecommendations as projection on db.MaintenanceRecommendations;
  entity MaintenanceRisks as projection on db.MaintenanceRisks;
  action createMaintenanceOrder(equipmentID : String, alertID : String, priority : String) returns MaintenanceOrders;
  action approveRecommendation(ID : String, comment : String) returns String;
  action scheduleMaintenance(ID : String, start : DateTime, end : DateTime) returns String;
  action completeOrder(ID : String, summary : String) returns String;
}""") + code("cds", "FILE: workforce + inventory + production + agent service shells", """service WorkforceService @(path:'/odata/v4/workforce') {
  entity Technicians as projection on db.Technicians;
  entity TechnicianSkills as projection on db.TechnicianSkills;
  entity TechnicianAvailability as projection on db.TechnicianAvailability;
  entity TechnicianAssignments as projection on db.TechnicianAssignments;
  function findAvailableTechnician(skill : String, date : Date, shift : String) returns many Technicians;
  action assignTechnician(orderID : String, technicianID : String) returns TechnicianAssignments;
}
service InventoryService @(path:'/odata/v4/inventory') {
  entity SpareParts as projection on db.SpareParts;
  entity Inventory as projection on db.Inventory;
  entity StockMovements as projection on db.StockMovements;
  entity Suppliers as projection on db.Suppliers;
  function checkSparePartStock(partNo : String) returns Inventory;
  action reserveSparePart(partNo : String, qty : Decimal, orderID : String) returns StockMovements;
}
service ProductionService @(path:'/odata/v4/production') {
  entity ProductionSchedules as projection on db.ProductionSchedules;
  function findMaintenanceWindow(lineID : String, from : Date, to : Date) returns many ProductionSchedules;
}
service AgentService @(path:'/odata/v4/agents') {
  entity Agents as projection on db.Agents;
  entity AgentTasks as projection on db.AgentTasks;
  entity AgentMessages as projection on db.AgentMessages;
  entity AgentExecutions as projection on db.AgentExecutions;
  action executeTask(agentId : String, intent : String, payload : LargeString) returns LargeString;
  action chat(conversationId : String, message : String) returns LargeString;
  action orchestrate(goal : String, payload : LargeString) returns LargeString;
}"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["projection on", "Exposes DB entities without duplicating them"], ["action vs function", "Actions change state (POST); functions only read (GET)"], ["ID : String (not UUID)", "OData URL parsing nulls non-GUID UUID params — String avoids phantom 404s"], ["path", "The URL prefix UI and agents call"]]),
        "Expected output": "<p>Welcome page lists 6-7 services. Each <code>$metadata</code> URL returns XML.</p>",
        "How to test it": std_test("GET <code>/odata/v4/equipment/$metadata</code> shows Equipment + EquipmentAlerts."),
        "Negative test cases": neg([["UUID-typed ID param + readable seed ID", "call action", "404 — use String (stated above)"], ["Function called with ?p='v'", "GET", "400 — functions need (p='v') parenthesis syntax"]]),
        "Common mistakes": "<p>Forgetting the <code>using</code> import; two services with the same path.</p>",
        "How to troubleshoot": "<p>Service missing from welcome page = CDS syntax error — run the Chapter 06 compile command.</p>",
        "Production considerations": "<p>Paths are versioned contracts (<code>/v4/</code>). Never rename a path without a migration plan.</p>",
        "Security considerations": "<p>Projections expose fields — exclude internal columns here, not in UI (Chapter 35).</p>",
        "What we have completed": done("Six reading APIs + action signatures.", "Chapter 11: handlers that validate, default and audit."),
    }))

    parts.append(ch("c11", "11", "Chapter 11 — Implement CRUD", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> CAP already serves CRUD; you add smart edges (defaults, checks, audit). <b>Enterprise:</b> before/after hooks per entity; state changes ONLY via actions. <b>Example:</b> autopilot flies straight; pilots handle takeoff, landing, turbulence.</p>",
        "Why is this important?": "<p>Unvalidated CRUD corrupts the data every later chapter trusts.</p>",
        "Where does this fit in the architecture?": "<p>Inside each CAP service box: the request lifecycle.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>srv/maintenance-service.js</code> + <code>lib/validation.js</code> + <code>lib/audit.js</code> (minimal versions, extended later).</p>",
        "Exact commands": PWR + code("powershell", "Create handler + restart", "New-Item srv/maintenance-service.js, lib/validation.js, lib/audit.js\nnpm start"),
        "Complete code": code("javascript", "FILE: srv/maintenance-service.js (COMPLETE for this chapter)", HANDLER),
        "Explanation of every important line": table(["Line", "Meaning"], [["extends cds.ApplicationService", "REQUIRED base class — raw cds.Service has no CRUD executors"], ["before CREATE", "Stamp DRAFT + orderNo, validate — rejects bad writes"], ["after CREATE", "Audit in try/catch, ALWAYS return data (undefined wipes the response)"], ["ctxOf", "LEARNING-MOCK: parses x-mock-user; replaced by JWT ctx in Chapter 34"]]),
        "Expected output": "<p>POST an order without orderNo → created with generated MO- number and status DRAFT.</p>",
        "How to test it": std_test("POST <code>/odata/v4/maintenance/MaintenanceOrders</code> {equipment_ID, priority:'HIGH'} → 201 with orderNo."),
        "Negative test cases": neg([["Empty body", "POST {}", "400 validation error, no row created"], ["Handler extends cds.Service", "GET list", "Empty list — switch base class (classic trap)"]]),
        "Common mistakes": "<p>after-hook returning nothing (response body vanishes); audit throwing (breaks the happy path).</p>",
        "How to troubleshoot": "<p>Add <code>console.log(req.data)</code> in before-hook; check terminal, not just the HTTP response.</p>",
        "Production considerations": "<p>Handlers stay thin — heavy logic moves to lib/ for unit tests (Chapter 62).</p>",
        "Security considerations": "<p>Never trust client-sent status/version/tenant fields — server stamps them (Chapter 35 hardens this).</p>",
        "What we have completed": done("Validated audited CREATE.", "Chapter 12: read it back through OData."),
    }))

    parts.append(ch("c12", "12", "Chapter 12 — OData V4", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> the URL language for data: filter, expand, order, pages. <b>Enterprise:</b> typed contracts UI5 binds to directly. <b>Example:</b> <code>?$filter=severity eq 'HIGH'&$expand=equipment&$top=10</code> = 'high alerts with machines, ten please'.</p>",
        "Why is this important?": "<p>Chapters 22-33 bind UI controls to THESE URLs. Wrong URL = empty screen.</p>",
        "Where does this fit in the architecture?": "<p>The wire between UI5 and CAP in FIG. 0.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>None — query language over existing services.</p>",
        "Exact commands": PWR + code("powershell", "Drills (add -H 'x-mock-user: op:MaintenanceUser' when auth lands in Ch 34)", "curl 'http://localhost:4004/odata/v4/equipment/EquipmentAlerts?$filter=severity%20eq%20%27HIGH%27'\ncurl 'http://localhost:4004/odata/v4/equipment/Equipment?$expand=sensors,alerts'\ncurl 'http://localhost:4004/odata/v4/maintenance/MaintenanceOrders?$orderby=createdAt%20desc&$top=5&$skip=5'"),
        "Complete code": table(["URL pattern", "Returns"], [["/EquipmentAlerts", "All alerts"], ["?$filter=status eq 'OPEN'", "Open only"], ["?$expand=equipment($select=name)", "Alerts + machine names"], ["?$top=20&$skip=0", "Page 1 (Chapter 16)"], ["POST /acknowledgeAlert {ID}", "Action result string"]]),
        "Explanation of every important line": "<p><code>$expand</code> follows associations/compositions in ONE round trip. <code>$select</code> trims payload — mobile screens need it.</p>",
        "Expected output": "<p>ALT-9001 row with expanded CNC-MACHINE-102 equipment object.</p>",
        "How to test it": std_test("each drill URL returns 200 + JSON with @odata.context."),
        "Negative test cases": neg([["$filter=severity = 'HIGH' (single =)", "GET", "400 — OData uses eq, not ="], ["Expand non-existent nav", "GET", "400 — check association name spelling"]]),
        "Common mistakes": "<p>Unencoded spaces/quotes in curl (use %20 / %27) — browsers encode automatically, curl does not.</p>",
        "How to troubleshoot": "<p>Append <code>?$top=1</code> to isolate shape problems from data problems.</p>",
        "Production considerations": "<p>Cap $top server-side (Chapter 16) — unbounded expands are a DDoS vector.</p>",
        "Security considerations": "<p>URLs leak in logs — IDs in paths are fine, tokens/secrets never belong in URLs.</p>",
        "What we have completed": done("Fluent OData reads.", "Chapter 13: reject bad writes properly."),
    }))

    parts.append(ch("c13", "13", "Chapter 13 — CAP Validation", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> say NO to impossible data (empty names, negative quantities, unknown machines). <b>Enterprise:</b> central validators reused by handlers, tools AND agents. <b>Example:</b> bouncer with a written list, same list at every door.</p>",
        "Why is this important?": "<p>One validation hole lets agents create orders for phantom machines.</p>",
        "Where does this fit in the architecture?": "<p>First gate inside CAP, before any write.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EXTEND <code>lib/validation.js</code> (full version below).</p>",
        "Exact commands": PWR + code("powershell", "Run validation tests (Chapter 62 wires these)", "npm test -- validation  # after Chapter 62 exists; until then: npm start + manual POSTs"),
        "Complete code": code("javascript", "FILE: lib/validation.js (COMPLETE)", """export function fail(code, message, status = 400) {
  const e = new Error(message); e.code = code; e.status = status; throw e;
}
export function validateOrder(d) {
  if (!d.equipment_ID) fail('VALIDATION_ERROR', 'equipment_ID is required');
  if (d.priority && !['LOW','MEDIUM','HIGH','URGENT'].includes(d.priority))
    fail('VALIDATION_ERROR', 'Unknown priority ' + d.priority);
  if (d.plannedStart && d.plannedEnd && d.plannedStart > d.plannedEnd)
    fail('VALIDATION_ERROR', 'plannedStart must be before plannedEnd');
}
export function validateAssignment(d) {
  if (!d.order_ID || !d.technician_ID) fail('VALIDATION_ERROR', 'order_ID + technician_ID required');
}
export function validateReservation(d) {
  if (Number(d.qty) <= 0) fail('VALIDATION_ERROR', 'qty must be > 0');
}
export function sanitizeForLLM(input) {
  return String(input ?? '')
    .replace(/ignore\\s+(all\\s+)?previous\\s+instructions?/gi, '[redacted-instruction-like-text]')
    .replace(/system\\s*:\\s*/gi, 'system-data:').slice(0, 4000);
}"""),
        "Explanation of every important line": table(["Function", "Rule"], [["fail", "Stable {code,status} shape — Chapter 15 maps it to HTTP"], ["validateOrder", "Required refs + closed enums + date sanity"], ["sanitizeForLLM", "Instruction-like text redacted BEFORE any LLM sees it (Chapter 59)"]]),
        "Expected output": "<p>POST order with priority 'ASAP' → 400 <code>Unknown priority ASAP</code>, nothing written.</p>",
        "How to test it": std_test("POST each invalid body from the table; expect 400 + no row."),
        "Negative test cases": neg([["priority ASAP", "POST order", "400, no row"], ["qty -3 reservation", "reserveSparePart", "400, stock untouched"], ["end before start", "scheduleMaintenance", "400"]]),
        "Common mistakes": "<p>Validating in UI only — attackers skip UI. Server validation is the real gate.</p>",
        "How to troubleshoot": "<p>Validation passes but DB rejects? Add the missing rule here AND a matching DB constraint (Chapter 18).</p>",
        "Production considerations": "<p>Validators are pure functions — 100% unit-testable without booting CAP (Chapter 62).</p>",
        "Security considerations": "<p>Validate enums server-side: a forged 'ADMIN' priority must die here, not in the UI.</p>",
        "What we have completed": done("Central validation library.", "Chapter 14: all-or-nothing multi-step writes."),
    }))

    parts.append(ch("c14", "14", "Chapter 14 — CAP Transactions", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> 9 approval steps succeed together or fail together. <b>Enterprise:</b> <code>cds.tx(req)</code> + row locks + version checks. <b>Example:</b> wedding seating — all guests placed or nobody sits.</p>",
        "Why is this important?": "<p>Without transactions, a crash mid-approval leaves a reserved part with no order — phantom stock.</p>",
        "Where does this fit in the architecture?": "<p>Wraps the approve → reserve → assign → schedule chain (Chapter 54 executes it).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EXTEND <code>srv/maintenance-service.js</code>: approveRecommendation action (below).</p>",
        "Exact commands": PWR + code("powershell", "Exercise the transaction", "curl -X POST -H 'Content-Type: application/json' -d '{\"ID\":\"<REC-ID>\",\"comment\":\"ok\"}' http://localhost:4004/odata/v4/maintenance/approveRecommendation"),
        "Complete code": code("javascript", "approveRecommendation: 9 steps, 1 transaction (COMPLETE)", """this.on('approveRecommendation', async (req) => {
  const tx = cds.tx(req);                                  // 1 tx for all writes
  try {
    const rec = await tx.run(SELECT.one.from('maintenance.db.MaintenanceRecommendations').where({ ID: req.data.ID }));
    if (!rec) return req.reject(404, 'Recommendation not found');   // 2 validate
    if (rec.status !== 'PROPOSED') return req.reject(409, 'Already decided');
    const alert = await tx.run(SELECT.one.from('maintenance.db.EquipmentAlerts').where({ ID: rec.alert_ID }).forUpdate()); // 3 lock
    const actions = JSON.parse(rec.actions);               // 4 planned writes
    for (const a of actions.reserve || []) {               // 5 reserve parts
      await tx.run(UPDATE('maintenance.db.Inventory').set({ reserved: { '+=': a.qty } }).where({ ID: a.inventoryID }));
      await tx.run(INSERT.into('maintenance.db.StockMovements').entries({ part_ID: a.partID, qty: -a.qty, type: 'RESERVE', idempotencyKey: req.data.ID + ':' + a.partID, refOrder_ID: null }));
    }
    const orderIds = [];
    for (const a of actions.orders || []) {                // 6 create orders
      const id = cds.utils.uuid();
      await tx.run(INSERT.into('maintenance.db.MaintenanceOrders').entries({ ID: id, orderNo: a.orderNo, equipment_ID: alert.equipment_ID, alert_ID: alert.ID, status: 'PLANNED', priority: a.priority ?? 'HIGH', idempotencyKey: req.data.ID + ':' + a.orderNo }));
      orderIds.push(id);
    }
    for (const a of actions.assign || [])                  // 7 assign technicians
      await tx.run(INSERT.into('maintenance.db.TechnicianAssignments').entries({ order_ID: a.orderID, technician_ID: a.technicianID, status: 'ASSIGNED', idempotencyKey: req.data.ID + ':' + a.technicianID }));
    await tx.run(UPDATE('maintenance.db.MaintenanceRecommendations').set({ status: 'APPROVED' }).where({ ID: rec.ID })); // 8 decide
    await tx.run(UPDATE('maintenance.db.EquipmentAlerts').set({ status: 'IN_PROGRESS' }).where({ ID: alert.ID }));
    await this.emit('MaintenanceOrderCreated', { orderIds });  // 9 event (Chapter 39)
    return 'APPROVED';                                     // COMMIT happens here
  } catch (e) { throw e; }                                 // any throw = ROLLBACK
});"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["cds.tx(req)", "Request-scoped tx: all queries share it"], ["SELECT.one + forUpdate()", "Locks the alert row — two approvers cannot double-approve"], ["idempotencyKey", "Retry of the same approval hits unique keys, not duplicates (Chapter 58)"], ["emit inside tx", "Event fires only if commit succeeds"], ["throw = ROLLBACK", "Partial writes vanish — no phantom stock"]]),
        "Expected output": "<p>APPROVED + order rows + RESERVE movements + alert IN_PROGRESS. Kill the server mid-way (test!) → nothing persisted.</p>",
        "How to test it": std_test("approve twice with same ID → second returns 409, single order set."),
        "Negative test cases": neg([["Double approval", "POST twice", "409, exactly one order set"], ["Unknown rec ID", "POST bad ID", "404, zero writes"], ["DB dies mid-tx", "kill -9 during approve", "Rollback: counts unchanged after restart"]]),
        "Common mistakes": "<p>Reading with bare <code>tx.read().where()</code> (returns ARRAY) then accessing <code>.status</code> — always <code>SELECT.one</code> for single rows.</p>",
        "How to troubleshoot": "<p>Version errors (409) mean a concurrent writer won — re-read and retry with the new version.</p>",
        "Production considerations": "<p>Distributed transactions across systems do NOT exist — cross-service steps use outbox/saga patterns (Chapter 39).</p>",
        "Security considerations": "<p>Authorization checks (Chapter 35) run BEFORE tx starts — never open a transaction for an unauthorized caller.</p>",
        "What we have completed": done("Atomic approval chain.", "STOP MILESTONE 2: backend writes safely. Chapter 15 standardizes errors."),
    }))

    parts.append(ch("c15", "15", "Chapter 15 — Error Handling", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> every failure gets a clean code, never a stack trace. <b>Enterprise:</b> <code>{code,status}</code> contract mapped to HTTP 400-504. <b>Example:</b> hospital triage tags — every patient tagged, none left screaming in the hall.</p>",
        "Why is this important?": "<p>Agents and UI branch on codes. A leaked stack trace hands attackers your schema.</p>",
        "Where does this fit in the architecture?": "<p>Every layer translates inward errors to outward codes (UI5 Chapter 26 reuses them).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>lib/errors.js</code>; handlers call <code>req.reject(toHttp(e))</code>.</p>",
        "Exact commands": "<p>None — library chapter. Exercise via Chapter 13 negative POSTs.</p>",
        "Complete code": code("javascript", "FILE: lib/errors.js (COMPLETE)", """const MAP = { VALIDATION_ERROR: 400, UNAUTHORIZED: 401, FORBIDDEN: 403, RESOURCE_NOT_FOUND: 404, VERSION_CONFLICT: 409, BUDGET_EXCEEDED: 422, RATE_LIMITED: 429, UPSTREAM_TIMEOUT: 504 };
export function toHttp(e) {
  const status = e.status ?? MAP[e.code] ?? 500;
  const safe = status >= 500 ? 'Internal error' : (e.message ?? 'Request failed');
  return { code: e.code ?? 'INTERNAL_ERROR', status, message: safe };
}""") + table(["HTTP", "When in our app"], [["400", "Validation (Ch 13)"], ["401", "No/expired identity (Ch 34)"], ["403", "Missing scope or cross-tenant (Ch 35)"], ["404", "Bad ID or function-syntax error"], ["409", "Stale version / double decision"], ["422", "Business rule (no stock, no window)"], ["429", "Rate limit (Ch 58)"], ["500/502/503/504", "Bugs, bad gateway, down, timeout — message hidden"]]),
        "Explanation of every important line": "<p>5xx messages are REPLACED — <code>password=...</code> in a DB error never reaches the client (security test, Chapter 65).</p>",
        "Expected output": "<p>Every Chapter 13 negative test now returns <code>{code, message}</code> JSON with the right status.</p>",
        "How to test it": std_test("re-run Chapter 13 negatives; assert status + code + no stack field."),
        "Negative test cases": neg([["DB password in error", "force DB down, call API", "500 INTERNAL_ERROR, body contains no 'password'"]]),
        "Common mistakes": "<p><code>throw e</code> raw from handlers — always map through toHttp first.</p>",
        "How to troubleshoot": "<p>Wrong status? Check MAP first, then the throw site — the code travels untouched end to end.</p>",
        "Production considerations": "<p>Alert on 5xx rate (Chapter 85); 4xx rate means client bugs or abuse.</p>",
        "Security considerations": "<p>Error bodies are an attack surface — this single file is its firewall.</p>",
        "What we have completed": done("Stable error contract.", "Chapter 16: paging + filtering at scale."),
    }))

    parts.append(ch("c16", "16", "Chapter 16 — Pagination, Filtering and Sorting", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> never dump 100k readings at once — serve pages. <b>Enterprise:</b> server-capped <code>$top</code>, indexed sort columns, composite filters. <b>Example:</b> library loans 10 books at a time, not the building.</p>",
        "Why is this important?": "<p>Sensor readings explode (vibration every second). Unbounded queries kill the server — and look identical to a DDoS.</p>",
        "Where does this fit in the architecture?": "<p>Protects the CAP→DB arrow; UI5 tables consume pages (Chapter 29).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT service handlers: clamp <code>$top</code> (below). Indexes land in Chapter 18.</p>",
        "Exact commands": PWR + code("powershell", "Page drills", "curl 'http://localhost:4004/odata/v4/equipment/SensorReadings?$top=100&$skip=0&$orderby=measuredAt%20desc'\ncurl 'http://localhost:4004/odata/v4/equipment/SensorReadings?$filter=equipment_ID%20eq%20%27eq-cnc102%27&$top=50'"),
        "Complete code": code("javascript", "Clamp page size (add to each READ handler)", """this.before('READ', 'maintenance.db.SensorReadings', (req) => {
  const top = req.query?.top ?? req._query?.$top;
  if (top && Number(top) > 1000) return req.reject(400, 'Page size max is 1000');
});"""),
        "Explanation of every important line": "<p>Reject, do not silently clamp — silent clamping hides UI bugs where the pager thinks more data exists.</p>",
        "Expected output": "<p><code>?$top=5000</code> → 400. <code>?$top=100</code> → 100 rows + <code>@odata.nextLink</code>.</p>",
        "How to test it": std_test("request top=5000 (expect 400), then walk nextLink twice (expect no duplicate rows)."),
        "Negative test cases": neg([["top=0/negative", "GET", "400"], ["skip beyond end", "GET", "200 empty array, not an error"]]),
        "Common mistakes": "<p>Sorting by unindexed LargeString — slow and memory-heavy (Chapter 18 fixes with indexes).</p>",
        "How to troubleshoot": "<p>Duplicate rows across pages = unstable sort — always orderby a unique column second (ID).</p>",
        "Production considerations": "<p>HANA paging needs ORDER BY determinism; add <code>createdAt, ID</code> composite sort (Chapter 76).</p>",
        "Security considerations": "<p>Big pages amplify scraping — 1000 cap + rate limits (Chapter 58) compose the defense.</p>",
        "What we have completed": done("Scale-safe reads.", "STOP: services complete. Chapter 17 gives them a real database."),
    }))

    return parts
