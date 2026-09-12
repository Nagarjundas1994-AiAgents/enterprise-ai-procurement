"""Part 2: CH04-CH09 (scaffold, folders, CDS, model, relations, seed)."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done

SCHEMA = """namespace maintenance.db;

using { cuid, managed } from '@sap/cds/common';

type AlertSeverity : String enum { LOW; MEDIUM; HIGH; CRITICAL; }
type AlertStatus : String enum { OPEN; ACKNOWLEDGED; IN_PROGRESS; RESOLVED; CLOSED; }
type OrderStatus : String enum { DRAFT; PLANNED; SCHEDULED; IN_PROGRESS; COMPLETED; CANCELLED; }
type OrderPriority : String enum { LOW; MEDIUM; HIGH; URGENT; }
type AssignmentStatus : String enum { ASSIGNED; ACCEPTED; IN_PROGRESS; DONE; CANCELLED; }
type MovementType : String enum { RECEIPT; ISSUE; RESERVE; RELEASE; ADJUST; }
type RiskLevel : String enum { LOW; MEDIUM; HIGH; CRITICAL; }
type ActorType : String enum { USER; AGENT; SYSTEM; }
type MessageRole : String enum { USER; ASSISTANT; TOOL; SYSTEM; }

entity Plants : cuid, managed {
  code    : String(32) @assert.unique not null;
  name    : String(256) not null;
  city    : String(128);
  country : String(64);
  active  : Boolean default true;
  lines   : Association to many ProductionLines on lines.plant = $self;
}

entity ProductionLines : cuid, managed {
  code      : String(32) @assert.unique not null;
  name      : String(256) not null;
  plant     : Association to Plants not null;
  status    : String(32) default 'RUNNING';
  equipment : Association to many Equipment on equipment.line = $self;
  schedules : Association to many ProductionSchedules on schedules.line = $self;
}

entity EquipmentTypes : cuid, managed {
  code        : String(32) @assert.unique not null;
  name        : String(256) not null;
  description : String(1024);
}

entity Equipment : cuid, managed {
  equipmentId : String(64) @assert.unique not null;
  name        : String(256) not null;
  type        : Association to EquipmentTypes;
  line        : Association to ProductionLines;
  plant       : Association to Plants;
  status      : String(32) default 'OPERATIONAL';
  installDate : Date;
  version     : Integer default 1 not null;
  sensors     : Composition of many Sensors on sensors.equipment = $self;
  alerts      : Association to many EquipmentAlerts on alerts.equipment = $self;
}

entity Sensors : cuid, managed {
  sensorId    : String(64) @assert.unique not null;
  equipment   : Association to Equipment not null;
  kind        : String(64) not null;
  unit        : String(16);
  warnAt      : Decimal(15,3);
  alarmAt     : Decimal(15,3);
  readings    : Composition of many SensorReadings on readings.sensor = $self;
}

entity SensorReadings : cuid {
  sensor      : Association to Sensors not null;
  equipment   : Association to Equipment not null;
  value       : Decimal(15,3) not null;
  unit        : String(16);
  measuredAt  : DateTime;
}

entity EquipmentAlerts : cuid, managed {
  alertNo     : String(32) @assert.unique not null;
  equipment   : Association to Equipment not null;
  severity    : AlertSeverity not null;
  status      : AlertStatus default #OPEN not null;
  title       : String(256) not null;
  description : String(2048);
  version     : Integer default 1 not null;
}

entity MaintenancePlans : cuid, managed {
  code          : String(64) @assert.unique not null;
  equipmentType : Association to EquipmentTypes;
  description   : String(2048);
  intervalDays  : Integer;
  operations    : Composition of many MaintenanceOperations on operations.plan = $self;
}

entity MaintenanceOperations : cuid {
  plan        : Association to MaintenancePlans;
  order       : Association to MaintenanceOrders;
  stepNo      : Integer not null;
  description : String(1024) not null;
  durationMin : Integer;
}

entity MaintenanceOrders : cuid, managed {
  orderNo     : String(32) @assert.unique not null;
  equipment   : Association to Equipment not null;
  alert       : Association to EquipmentAlerts;
  status      : OrderStatus default #DRAFT not null;
  priority    : OrderPriority default #MEDIUM not null;
  version     : Integer default 1 not null;
  idempotencyKey : String(64);
  plannedStart : DateTime;
  plannedEnd   : DateTime;
  assignments : Composition of many TechnicianAssignments on assignments.order = $self;
  operations  : Composition of many MaintenanceOperations on operations.order = $self;
}

entity MaintenanceHistory : cuid, managed {
  equipment   : Association to Equipment not null;
  order       : Association to MaintenanceOrders;
  summary     : String(2048) not null;
  failureCode : String(64);
  performedAt : DateTime;
}

entity Inspections : cuid, managed {
  equipment   : Association to Equipment not null;
  inspector   : Association to Technicians;
  result      : String(32);
  notes       : String(2048);
  inspectedAt : DateTime;
}

entity Technicians : cuid, managed {
  employeeId   : String(64) @assert.unique not null;
  name         : String(256) not null;
  email        : String(256);
  active       : Boolean default true not null;
  skills       : Composition of many TechnicianSkills on skills.technician = $self;
  availability : Composition of many TechnicianAvailability on availability.technician = $self;
}

entity TechnicianSkills : cuid {
  technician : Association to Technicians not null;
  skill      : String(64) not null;
  level      : String(16);
}

entity TechnicianAvailability : cuid {
  technician : Association to Technicians not null;
  date       : Date not null;
  shift      : String(16) not null;
  available  : Boolean default true;
}

entity TechnicianAssignments : cuid, managed {
  order          : Association to MaintenanceOrders not null;
  technician     : Association to Technicians not null;
  status         : AssignmentStatus default #ASSIGNED not null;
  idempotencyKey : String(64);
}

entity SpareParts : cuid, managed {
  partNo    : String(64) @assert.unique not null;
  name      : String(256) not null;
  unitPrice : Decimal(18,2);
  supplier  : Association to Suppliers;
}

entity Inventory : cuid, managed {
  part         : Association to SpareParts not null;
  plant        : Association to Plants not null;
  quantity     : Decimal(15,3) default 0 not null;
  reserved     : Decimal(15,3) default 0;
  reorderPoint : Decimal(15,3) default 0;
}

entity StockMovements : cuid, managed {
  part           : Association to SpareParts not null;
  plant          : Association to Plants;
  qty            : Decimal(15,3) not null;
  type           : MovementType not null;
  idempotencyKey : String(64);
  refOrder       : Association to MaintenanceOrders;
}

entity Suppliers : cuid, managed {
  supplierId : String(64) @assert.unique not null;
  name       : String(256) not null;
  country    : String(64);
  active     : Boolean default true not null;
}

entity ProductionSchedules : cuid, managed {
  line    : Association to ProductionLines not null;
  date    : Date not null;
  shift   : String(16) not null;
  product : String(128);
  status  : String(32) default 'PLANNED';
}

entity MaintenanceRecommendations : cuid, managed {
  alert     : Association to EquipmentAlerts not null;
  agentId   : String(128);
  summary   : LargeString not null;
  actions   : LargeString not null;
  status    : String(32) default 'PROPOSED';
  approvedBy : String(128);
  approvedAt : DateTime;
}

entity MaintenanceRisks : cuid, managed {
  entityType : String(64) not null;
  entityId   : String(64) not null;
  riskScore  : Integer not null;
  riskLevel  : RiskLevel not null;
  reasons    : LargeString;
}

entity Agents : cuid, managed {
  agentId      : String(128) @assert.unique not null;
  name         : String(256) not null;
  kind         : String(64) not null;
  active       : Boolean default true;
  allowedTools : LargeString;
  maxAutoApproveAmount : Decimal(18,2) default 0;
}

entity AgentTasks : cuid, managed {
  taskKey   : String(64) @assert.unique not null;
  fromAgent : String(128) not null;
  toAgent   : String(128) not null;
  intent    : String(128) not null;
  payload   : LargeString;
  status    : String(32) default 'PENDING';
  result    : LargeString;
  correlationId : String(64);
}

entity AgentMessages : cuid {
  task      : Association to AgentTasks not null;
  role      : MessageRole not null;
  content   : LargeString not null;
  createdAt : DateTime;
}

entity AgentExecutions : cuid, managed {
  agent     : Association to Agents;
  toolName  : String(128);
  input     : LargeString;
  output    : LargeString;
  status    : String(32) default 'PENDING';
  error     : LargeString;
  correlationId : String(64);
}

entity MCPToolExecutions : cuid, managed {
  toolName  : String(128) not null;
  actorType : ActorType not null;
  actorId   : String(128) not null;
  agentId   : String(128);
  input     : LargeString;
  output    : LargeString;
  status    : String(32) default 'PENDING';
  error     : LargeString;
  correlationId : String(64);
  durationMs : Integer;
}

entity AuditLogs : cuid, managed {
  timestamp : DateTime;
  actorType : ActorType not null;
  actorId   : String(128) not null;
  agentId   : String(128);
  action    : String(128) not null;
  entity    : String(128);
  entityId  : String(128);
  equipment : String(64);
  result    : String(32) default 'SUCCESS';
  error     : LargeString;
  correlationId : String(64);
  requestId : String(64);
}"""


def build():
    parts = []

    parts.append(ch("c04", "04", "Chapter 04 — Create the CAP Project", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> generate a working-but-empty CAP project from nothing. <b>Enterprise:</b> the standard Node.js CAP layout every SAP team scaffolds first. <b>Example:</b> pouring the foundation slab — flat, boring, everything stands on it.</p>",
        "Why is this important?": "<p>Every chapter 05-90 edits files created here. A broken scaffold multiplies into 86 chapters of confusion.</p>",
        "Where does this fit in the architecture?": "<p>Creates the CAP box of FIG. 0 plus its config shell (auth, DB profiles, router).</p>",
        "Prerequisites": "<p>Chapter 00 tools verified.</p>",
        "Folder/file changes": "<p>NEW directory <code>C:\\Projects\\autonomous-maintenance</code> with <code>db/</code>, <code>srv/</code>, <code>app/</code>, <code>test/</code>, <code>package.json</code>.</p>",
        "Exact commands": PWR + code("powershell", "Scaffold (project root: C:\\Projects)", "mkdir C:\\Projects\\autonomous-maintenance\ncd C:\\Projects\\autonomous-maintenance\ncds init --cap-js\nnpm install\ncds --version  # still healthy inside the project"),
        "Complete code": code("json", "FILE: package.json (created by cds init, then extended)", """{
  "name": "autonomous-maintenance-control-tower",
  "version": "1.0.0",
  "type": "module",
  "engines": { "node": ">=20" },
  "scripts": {
    "start": "cds-serve",
    "test": "vitest run",
    "build": "tsc --noEmit -p tsconfig.json"
  },
  "dependencies": {
    "@sap/cds": "^8",
    "@cap-js/postgres": "^1",
    "@sap/xssec": "^4",
    "express": "^4",
    "express-rate-limit": "^7",
    "helmet": "^8"
  },
  "devDependencies": { "@cap-js/sqlite": "^1", "vitest": "^2", "typescript": "^5" },
  "cds": {
    "requires": {
      "db": { "kind": "sqlite", "[production]": { "kind": "postgres" }, "[postgres]": { "kind": "postgres" } },
      "auth": { "kind": "mocked", "[production]": { "kind": "jwt" } }
    }
  }
}"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["type: module", "ES modules: import/export syntax everywhere"], ["cds-serve", "Starts CAP; swap to tsx wrapper in Chapter 10 if using TypeScript handlers"], ["db sqlite → postgres", "LEARNING-MOCK APPROACH local/tests; CURRENT SAP APPROACH in prod"], ["auth mocked → jwt", "Fake headers local; real JWT on BTP (Chapters 34-36)"]]),
        "Expected output": code("text", "npm install tail", "added 180 packages in 25s\nRun 'cds watch' to start developing."),
        "How to test it": std_test("<code>npm start</code>, open <code>http://localhost:4004</code> — CAP welcome page with no services yet."),
        "Negative test cases": neg([["Wrong folder", "Run cds init inside an existing repo", "Mixed files — start in an EMPTY directory"], ["Node 16", "npm install", "Engine warnings; upgrade Node"]]),
        "Common mistakes": "<p>Forgetting <code>cd</code> into the new folder — subsequent files land in <code>C:\\Projects</code>.</p>",
        "How to troubleshoot": "<p><code>npm cache clean --force</code> then reinstall. Proxy issues: <code>npm config get proxy</code>.</p>",
        "Production considerations": "<p><code>engines.node &gt;= 20</code> must match the BTP Node.js buildpack (Chapter 73) or deploys fail.</p>",
        "Security considerations": "<p>Run <code>npm audit</code> now; repeat in CI (Chapter 72). No secrets exist yet — keep it that way.</p>",
        "What we have completed": done("Empty runnable CAP project.", "Chapter 05: tour every folder and file."),
    }))

    parts.append(ch("c05", "05", "Chapter 05 — CAP Project Folder Structure", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> which folder owns what. <b>Enterprise:</b> separation of model (db), API (srv), UI (app), logic (lib), proof (test). <b>Example:</b> factory zones — stores, assembly, offices, lab; material flows one way.</p>",
        "Why is this important?": "<p>Chapters 06-90 say FILE: <code>db/schema.cds</code> — you must know where that lives and why.</p>",
        "Where does this fit in the architecture?": "<p>Maps folders to FIG. 0 boxes: <code>app</code>→UI5, <code>srv</code>→CAP, <code>db</code>→HANA, <code>srv/mcp</code>→tools, <code>srv/agents</code>→agents.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>CREATE the subfolders we will fill later. No logic yet.</p>",
        "Exact commands": PWR + code("powershell", "Create zones (project root)", "mkdir app, db\\data, srv\\services, srv\\mcp, srv\\agents, srv\\a2a, srv\\integrations, lib, test\\unit, test\\integration, test\\security, test\\mcp, test\\a2a, scripts, docker, .github\\workflows\nGet-ChildItem -Recurse -Depth 2 | Select-Object FullName"),
        "Complete code": code("text", "FILE: final tree (you build toward this)", """autonomous-maintenance-control-tower/
  app/maintenance-ui/          # UI5 (Ch 19-33)
  db/schema.cds                # domain (Ch 07)
  db/data/*.csv                # seed (Ch 09)
  srv/equipment-service.cds     # plant master data API (Ch 10)
  srv/maintenance-service.cds   # orders + approvals (Ch 10)
  srv/workforce-service.cds     # technicians (Ch 10)
  srv/inventory-service.cds     # spares (Ch 10)
  srv/production-service.cds    # schedules (Ch 10)
  srv/mcp-service.cds           # 17 MCP tools (Ch 43-44)
  srv/agent-service.cds         # 4 agents (Ch 41, 47-49)
  srv/server.js                 # helmet + limits + discovery (Ch 51)
  srv/integrations/             # sensor API client (Ch 38)
  lib/                          # validation, policy, audit, risk (Ch 13-14)
  test/                         # unit→agent suites (Ch 61-68)
  mta.yaml xs-security.json Dockerfile docker-compose.yml"""),
        "Explanation of every important line": "<p><code>srv/</code> holds one file per bounded context — never one giant service. <code>lib/</code> holds framework-free logic so tests run without CAP. <code>test/</code> mirrors the testing pyramid (Chapter 61).</p>",
        "Expected output": "<p><code>Get-ChildItem</code> lists all zones; <code>npm start</code> still serves the welcome page.</p>",
        "How to test it": std_test("create a scratch file in each zone, confirm the editor shows it, then delete it."),
        "Negative test cases": neg([["Business logic in srv/*.cds", "Review", "CDS is declaration only — logic goes in handlers + lib"]]),
        "Common mistakes": "<p>Putting UI5 code under <code>srv/</code> (it belongs in <code>app/</code>) or tests next to sources.</p>",
        "How to troubleshoot": "<p>Wrong nesting shows up as 404s in Chapters 10+ — compare against the tree above.</p>",
        "Production considerations": "<p>mta.yaml (Chapter 74) maps these folders to deployable modules one-to-one.</p>",
        "Security considerations": "<p>Public web content lives ONLY in <code>app/</code>; <code>srv/</code> is never statically served.</p>",
        "What we have completed": done("Empty zoned project.", "Chapter 06: CDS language from zero."),
    }))

    parts.append(ch("c06", "06", "Chapter 06 — CDS Fundamentals", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> CDS is the blueprint language: things, fields, links. <b>Enterprise:</b> one model compiles to OData APIs + SQL schema + Fiori annotations. <b>Example:</b> <code>entity Equipment { key ID: UUID; name: String(256); }</code> — a thing with an ID and a name.</p>",
        "Why is this important?": "<p>Chapter 07 writes 30 entities in this language. Misread one keyword and the whole model fails to compile.</p>",
        "Where does this fit in the architecture?": "<p>CDS feeds BOTH arrows out of CAP: the OData API (Chapter 12) and the DB schema (Chapters 17-18).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT <code>db/schema.cds</code> (create it): the learning playground for this chapter.</p>",
        "Exact commands": PWR + code("powershell", "Compile check (project root, after every CDS edit)", "npx cds compile --to csn db srv   # exit 0 = model valid"),
        "Complete code": code("cds", "FILE: db/schema.cds (this chapter: minimal example first)", """namespace maintenance.db;

using { cuid, managed } from '@sap/cds/common';

// MINIMAL EXAMPLE: one entity, then we grow it in Chapter 07.
entity Plants : cuid, managed {
  code    : String(32) @assert.unique not null;
  name    : String(256) not null;
  city    : String(128);
  active  : Boolean default true;
}"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["namespace", "Prefix for all entities: maintenance.db.Plants"], ["cuid", "Adds UUID key ID automatically"], ["managed", "Adds createdAt/modifiedAt/createdBy"], ["@assert.unique", "DB-level duplicate guard"], ["default true", "New plants are active unless stated"]]),
        "Expected output": code("text", "Compile", "CSN output, no errors. Plants table will exist on next deploy."),
        "How to test it": std_test("<code>npx cds compile --to csn db</code> exits 0; break one line (remove a semicolon) and watch it fail — then fix it."),
        "Negative test cases": neg([["Missing semicolon", "compile", "Syntax error with line number — the compiler tells you where"], ["Duplicate namespace", "compile", "Rename; namespaces must be unique per model"]]),
        "Common mistakes": "<p>Forgetting <code>key</code> (cuid supplies it — plain entities need one) and mixing <code>;</code> with <code>,</code>.</p>",
        "How to troubleshoot": "<p>Compiler errors name file + line. Fix top-down: the first error often causes the rest.</p>",
        "Production considerations": "<p>Keep CDS portable: no database-specific types — the same file targets SQLite, Postgres AND HANA.</p>",
        "Security considerations": "<p>No auth in CDS itself — access control lives in service definitions (Chapter 35).</p>",
        "What we have completed": done("One compiling entity.", "Chapter 07: the full 30-entity model."),
    }))

    parts.append(ch("c07", "07", "Chapter 07 — Build the Database Model", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> declare every table our factory needs. <b>Enterprise:</b> master data, documents, intelligence and governance entities with enums, versions and idempotency keys. <b>Example:</b> the full parts list before assembly.</p>",
        "Why is this important?": "<p>Services (10), UI (19-33), tools (44) and agents (47-49) all query THESE entities. Model mistakes echo for 80 chapters.</p>",
        "Where does this fit in the architecture?": "<p>The HANA box of FIG. 0 — plus the shape of every OData entity.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>REPLACE <code>db/schema.cds</code> with the full model below.</p>",
        "Exact commands": PWR + code("powershell", "Validate the full model", "npx cds compile --to csn db srv\n# expect: valid CSN, zero errors"),
        "Complete code": code("cds", "FILE: db/schema.cds (COMPLETE — keep for the whole course)", SCHEMA),
        "Explanation of every important line": table(["Construct", "Used for"], [["type X : String enum", "Closed value lists: severity, status, priority"], ["version : Integer", "Optimistic concurrency on Alerts + Orders (Chapter 14)"], ["idempotencyKey", "Safe retries on Orders, Assignments, Movements (Chapter 58)"], ["AgentTasks/AgentMessages", "A2A conversation persistence (Chapters 46-53)"], ["AuditLogs (no secrets)", "Every sensitive action, secret-free (Chapter 55)"]]),
        "Expected output": "<p>Compiler exits 0. You can count 30 <code>entity</code> keywords.</p>",
        "How to test it": std_test("count entities: <code>(Get-Content db/schema.cds | Select-String '^entity').Count</code> — expect 30."),
        "Negative test cases": neg([["Duplicate entity name", "compile", "Error — rename"], ["Missing referenced entity (e.g. Technicians used before defined)", "compile", "Order does not matter in CDS — the error means a typo, not ordering"]]),
        "Common mistakes": "<p>Typos in association targets — the compiler catches them; read the FIRST error only.</p>",
        "How to troubleshoot": "<p>Binary-search: comment half the file, compile, repeat until the error is isolated.</p>",
        "Production considerations": "<p>HANA: add indexes on hot foreign keys later (Chapter 76). Keep LargeString for unbounded text.</p>",
        "Security considerations": "<p>Tenant column arrives in Chapter 60 — note its absence now so the migration is explicit.</p>",
        "What we have completed": done("Full 30-entity compiling model.", "Chapter 08: why each link is association vs composition."),
    }))

    parts.append(ch("c08", "08", "Chapter 08 — Relationships, Associations and Compositions", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> association = points at someone (supplier); composition = owns children (order owns its lines). <b>Enterprise:</b> compositions cascade-delete and enable deep insert; associations stay independent. <b>Example:</b> delete an order → its assignments go too (composition); delete an order → the technician survives (association).</p>",
        "Why is this important?": "<p>Wrong choice deletes master data (catastrophic) or orphans children (audit nightmare).</p>",
        "Where does this fit in the architecture?": "<p>Decides OData $expand shapes (Chapter 12) and cascade behavior in transactions (Chapter 14).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>None — we classify Chapter 07 links. No edits unless you spot a mistake.</p>",
        "Exact commands": "<p>None. Classification exercise with the table below against <code>db/schema.cds</code>.</p>",
        "Complete code": table(["Link", "Kind in our model", "Why"], [["Plants.lines", "Association", "Lines outlive plant reorganizations"], ["Equipment.sensors", "Composition", "Sensors die with the machine"], ["MaintenanceOrders.assignments", "Composition", "Assignment meaningless without its order"], ["MaintenanceOrders.equipment", "Association", "Machine survives order completion"], ["TechnicianAssignments.technician", "Association", "Never delete people via orders"], ["Inventory.part / .plant", "Association", "Master data referenced, not owned"], ["AgentTasks (to AgentMessages)", "Composition via messages.task", "Messages are the task transcript"]]),
        "Explanation of every important line": "<p><code>on X = $self</code> is the backlink that makes compositions navigable both ways and powers deep create.</p>",
        "Expected output": "<p>You can justify every link in the table without notes.</p>",
        "How to test it": std_test("pick 3 links and state delete-consequence for each."),
        "Negative test cases": neg([["Composition to Suppliers", "Deletetester", "Would delete shared master data — must stay association"]]),
        "Common mistakes": "<p>Making everything a composition 'for convenience' — cascades become landmines.</p>",
        "How to troubleshoot": "<p>Orphan rows in tests (Chapter 63) trace back to a wrong-kind link here.</p>",
        "Production considerations": "<p>Deep inserts ($expand POST) only work through compositions — UI5 Chapter 23 relies on this.</p>",
        "Security considerations": "<p>Cascade paths must respect authorization: deleting a parent requires rights on children (Chapter 35).</p>",
        "What we have completed": done("Classified relationship model.", "Chapter 09: fill it with the Bangalore story data."),
    }))

    parts.append(ch("c09", "09", "Chapter 09 — Seed Realistic Business Data", "CAP", {
        "What are we learning?": "<p><b>Simple:</b> CSV files that auto-load demo rows. <b>Enterprise:</b> deterministic fixtures: same data on every machine, the basis of repeatable tests. <b>Example:</b> the cast list before the play — CNC-MACHINE-102 must exist or Chapter 89 has no patient.</p>",
        "Why is this important?": "<p>Agents, UI screens and tests all query this data. Hand-created rows differ per developer and break tests.</p>",
        "Where does this fit in the architecture?": "<p>Populates the HANA/Postgres box so every arrow has something to carry.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>db/data/maintenance.db-*.csv</code> (one per entity, header = field names).</p>",
        "Exact commands": PWR + code("powershell", "Deploy + verify seed (SQLite first, Postgres in Ch 17)", "npx cds deploy --to sqlite:db.sqlite\nnpx cds run --to sqlite:db.sqlite &\n# then query (see How to test it)"),
        "Complete code": code("text", "FILE: db/data/maintenance.db-Plants.csv", "ID,code,name,city,country,active\np-blr,BLR-01,Bangalore Manufacturing Plant,Bangalore,IN,true") + code("text", "FILE: db/data/maintenance.db-Equipment.csv", "ID,equipmentId,name,line_ID,plant_ID,status\n eq-cnc102,CNC-MACHINE-102,CNC Milling Center 102,line-03,p-blr,OPERATIONAL") + code("text", "FILE: db/data/maintenance.db-Sensors.csv + Readings + Alerts", "Sensors:\nID,sensorId,equipment_ID,kind,unit,warnAt,alarmAt\ns-vib,VIB-102,CNC-MACHINE-102-equipment,vibration,mm/s,4.5,7.1\nAlerts:\nID,alertNo,equipment_ID,severity,status,title\na-9001,ALT-9001,eq-cnc102,HIGH,OPEN,Abnormal Vibration") + code("text", "FILE: Technicians + Skills + SpareParts + Inventory + Schedules", "Technicians: t-ravi,EMP-201,Ravi Kumar,ravi@plant.in,true\nSkills: ts-1,t-ravi,bearing-replacement,expert\nSpareParts: sp-brg6205,BRG-6205,Deep-groove bearing 6205\nInventory: inv-1,sp-brg6205,p-blr,14,0,4\nSchedules: sch-1,line-03,2026-09-15,night,BRACKET-X,PLANNED"),
        "Explanation of every important line": "<p>CSV name = <code>&lt;namespace-with-dots&gt;-&lt;Entity&gt;.csv</code>. IDs are stable strings (eq-cnc102) so tests and chapters reference them forever. Vibration 7.1+ crosses alarmAt — the Chapter 89 trigger.</p>",
        "Expected output": "<p>Deployed DB contains the plant, line 3, CNC-MACHINE-102, its vibration sensor, one HIGH OPEN alert, Ravi Kumar (bearing expert), 14 bearings in stock.</p>",
        "How to test it": std_test("GET /odata/v4/equipment/Equipment?$filter=equipmentId eq 'CNC-MACHINE-102' returns one row (services exist from Chapter 10 — bookmark this test)."),
        "Negative test cases": neg([["Wrong CSV filename", "deploy", "Silently ignored — no rows, no error. Triple-check names"], ["Duplicate key in CSV", "deploy", "Constraint error — IDs must be unique"]]),
        "Common mistakes": "<p>Comma inside a field without quoting; referencing an ID that does not exist yet.</p>",
        "How to troubleshoot": "<p>Empty table = filename mismatch 90% of the time. Compare against an existing working CSV letter by letter.</p>",
        "Production considerations": "<p>Seed is DEV/TEST only. Production uses migration scripts + backups (Chapters 76, 87).</p>",
        "Security considerations": "<p>Fake people, fake mails, fake prices. Never seed real employee data or real supplier credentials.</p>",
        "What we have completed": done("Story data deployed.", "STOP MILESTONE 1: model + data stand. Chapter 10 exposes them as APIs."),
    }))

    return parts
