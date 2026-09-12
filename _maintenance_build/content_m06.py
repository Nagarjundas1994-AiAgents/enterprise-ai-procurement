"""Part 6: CH27-CH33 (plant screens)."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done


def build():
    parts = []

    parts.append(ch("c27", "27", "Chapter 27 — Equipment Dashboard", "", {
        "What are we learning?": "<p><b>Simple:</b> the control-room wall: counts, open alerts, line status. <b>Enterprise:</b> card layout + aggregation bindings + drill-down navigation. <b>Example:</b> shift-start glance: anything red?</p>",
        "Why is this important?": "<p>The entry point of the Chapter 89 demo: user OPENS the dashboard and SEES the alert.</p>",
        "Where does this fit in the architecture?": "<p>UI5 dashboard route (#/); read-only over equipment + alerts services.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>view/Dashboard.view.xml</code> + <code>controller/Dashboard.controller.js</code>.</p>",
        "Exact commands": "<p>None — markup + reload.</p>",
        "Complete code": code("xml", "FILE: view/Dashboard.view.xml (COMPLETE)", """<mvc:View xmlns:mvc="sap.ui.core.mvc" xmlns="sap.m" xmlns:card="sap.f.cards" controllerName="assetops.maintenance.ui.controller.Dashboard">
  <Page title="{i18n>appTitle}">
    <VBox class="sapUiMediumMargin">
      <NumericHeader number="{dashboard>/openAlerts}" title="Open alerts" press=".navAlerts"/>
      <NumericHeader number="{dashboard>/operational}" title="Operational machines" press=".navEquipment"/>
      <Table id="alertTable" items="{equipment>/EquipmentAlerts}" growing="true" growingThreshold="10">
        <columns><Column><Text text="Alert"/></Column><Column><Text text="Severity"/></Column><Column><Text text="Machine"/></Column></columns>
        <items><ColumnListItem type="Navigation" press=".onAlert">
          <ObjectIdentifier title="{equipment>alertNo}"/>
          <ObjectStatus text="{equipment>severity}" state="{path:'equipment>severity',formatter:'.formatter.severityState'}"/>
          <Text text="{equipment>equipment/name}"/>
        </ColumnListItem></items>
      </Table>
    </VBox>
  </Page>
</mvc:View>"""),
        "Explanation of every important line": table(["Markup", "Meaning"], [["{dashboard&gt;...}", "JSONModel counts loaded by the controller on init"], ["items={equipment&gt;/EquipmentAlerts}", "Live alert feed, paged"], ["{equipment&gt;equipment/name}", "Navigation-property binding through the association"], ["press=.onAlert", "Drill to Chapter 28 details with the alert ID"]]),
        "Expected output": "<p>ALT-9001 HIGH row visible with CNC-MACHINE-102; tap navigates to details.</p>",
        "How to test it": std_test("dashboard shows seed alert; tap drills to #/equipment/eq-cnc102."),
        "Negative test cases": neg([["No alerts in DB", "empty table", "Friendly 'all clear' text, not a blank wall"]]),
        "Common mistakes": "<p>Binding <code>equipment/name</code> without $expand — add <code>parameters: {$expand:'equipment'}</code> on the binding.</p>",
        "How to troubleshoot": "<p>Machine column empty = association not expanded. Check network $expand param.</p>",
        "Production considerations": "<p>Dashboard queries are the hottest path — cache counts server-side if monitoring (Ch 85) shows strain.</p>",
        "Security considerations": "<p>Dashboard shows all plants — plant scoping arrives with tenancy (Chapter 60).</p>",
        "What we have completed": done("Control-room wall.", "Chapter 28: machine details."),
    }))

    parts.append(ch("c28", "28", "Chapter 28 — Equipment Details", "", {
        "What are we learning?": "<p><b>Simple:</b> one machine's full file: specs, sensors, alerts, history. <b>Enterprise:</b> object page with sections bound to one key + related lists. <b>Example:</b> patient chart at the bedside.</p>",
        "Why is this important?": "<p>Chapter 89: user opens THIS page for CNC-MACHINE-102 before asking the assistant.</p>",
        "Where does this fit in the architecture?": "<p>Route #/equipment/{id}; reads equipment + sensors + alerts + history.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>view/EquipmentDetails.view.xml</code> + controller with route-matched binding.</p>",
        "Exact commands": "<p>None — code + reload.</p>",
        "Complete code": code("javascript", "EquipmentDetails.controller.js onRouteMatched (COMPLETE)", """onInit: function () {
  this.getRouter().getRoute('equipmentDetails').attachPatternMatched(this.onMatched, this);
},
onMatched: function (oEvent) {
  var sId = oEvent.getParameter('arguments').equipmentId;
  var oView = this.getView();
  oView.bindElement({ path: \"/Equipment('\" + sId + \"')\", model: 'equipment',
    parameters: { $expand: 'sensors,alerts,type,line' } });
}"""),
        "Explanation of every important line": "<p>Route param → element binding with one $expand fetching sensors, alerts, type and line in a single round trip.</p>",
        "Expected output": "<p>CNC-MACHINE-102 header + VIB-102 sensor row + ALT-9001 alert + empty history (filled in Chapter 30).</p>",
        "How to test it": std_test("open #/equipment/eq-cnc102; all four sections render; unknown ID shows not-found text."),
        "Negative test cases": neg([["Bad ID in URL", "open #/equipment/nope", "Not-found message, no console exception"]]),
        "Common mistakes": "<p>Binding before the view exists — always bind inside the pattern-matched handler.</p>",
        "How to troubleshoot": "<p>Sections empty but header filled = $expand missing or misspelled nav name.</p>",
        "Production considerations": "<p>Details pages are deep-linked from alerts, mails and agent answers — URLs must be stable forever.</p>",
        "Security considerations": "<p>ID in URL is untrusted — Chapter 35 verifies the user may read THIS plant's machines.</p>",
        "What we have completed": done("Machine file view.", "Chapter 29: live sensor charts."),
    }))

    parts.append(ch("c29", "29", "Chapter 29 — Sensor Monitoring", "", {
        "What are we learning?": "<p><b>Simple:</b> vibration-over-time list with warn/alarm coloring. <b>Enterprise:</b> time-ordered paging, threshold bands, refresh handling. <b>Example:</b> heart monitor strip for the machine.</p>",
        "Why is this important?": "<p>The EVIDENCE behind every agent recommendation (Chapter 41 reads the same endpoint).</p>",
        "Where does this fit in the architecture?": "<p>SensorReadings entity set, newest-first, capped pages (Chapter 16).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW sensor section in details view + refresh timer in controller.</p>",
        "Exact commands": PWR + code("powershell", "Reading drill", "curl 'http://localhost:4004/odata/v4/equipment/SensorReadings?$filter=equipment_ID%20eq%20%27eq-cnc102%27&$orderby=measuredAt%20desc&$top=20'"),
        "Complete code": code("xml", "Sensor table section (COMPLETE)", """<Table id="readTable" items="{equipment>/SensorReadings}" growing="true" growingThreshold="20">
  <headerToolbar><Toolbar><Title text="Vibration (mm/s)"/><ToolbarSpacer/><Button text="Refresh" press=".onRefreshReadings"/></Toolbar></headerToolbar>
  <columns><Column><Text text="Time"/></Column><Column><Text text="Value"/></Column><Column><Text text="Band"/></Column></columns>
  <items><ColumnListItem>
    <Text text="{equipment>measuredAt}"/><ObjectNumber number="{equipment>value}" unit="{equipment>unit}"/>
    <ObjectStatus text="{= ${equipment>value} >= 7.1 ? 'ALARM' : ${equipment>value} >= 4.5 ? 'WARN' : 'OK'}" state="{= ${equipment>value} >= 7.1 ? 'Error' : ${equipment>value} >= 4.5 ? 'Warning' : 'Success'}"/>
  </ColumnListItem></items>
</Table>"""),
        "Explanation of every important line": "<p>Expression binding compares live value against sensor warnAt/alarmAt thresholds (4.5/7.1 for VIB-102) — no controller code needed.</p>",
        "Expected output": "<p>Readings above 7.1 glow red ALARM — the visual proof of the story.</p>",
        "How to test it": std_test("seed an 8.2 reading; row renders ALARM; refresh re-queries."),
        "Negative test cases": neg([["Sensor gap (no rows)", "empty set", "'No readings yet' text — sensors can be offline"]]),
        "Common mistakes": "<p>Auto-refresh faster than the API ( hammering ) — 30s minimum, manual refresh primary.</p>",
        "How to troubleshoot": "<p>Stale values = cached binding — call refresh on the list binding, not the whole model.</p>",
        "Production considerations": "<p>High-frequency sensors aggregate server-side (Chapter 38 external API) — UI never pages raw 1Hz streams.</p>",
        "Security considerations": "<p>Readings reveal production tempo — treat as sensitive operational data (Chapter 35).</p>",
        "What we have completed": done("Machine vitals monitor.", "Chapter 30: orders."),
    }))

    parts.append(ch("c30", "30", "Chapter 30 — Maintenance Orders", "", {
        "What are we learning?": "<p><b>Simple:</b> the work ticket list + lifecycle buttons (plan → schedule → complete). <b>Enterprise:</b> status state machine in UI mirroring Chapter 14 transitions. <b>Example:</b> job cards on the foreman's board.</p>",
        "Why is this important?": "<p>Orders are the unit the agent creates (Chapter 54) and production validates (Chapter 84).</p>",
        "Where does this fit in the architecture?": "<p>MaintenanceOrders entity set + four lifecycle actions.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>view/Orders.view.xml</code> + controller calling the Chapter 23 dialog.</p>",
        "Exact commands": PWR + code("powershell", "Lifecycle drill (replace IDs)", "curl -X POST -H 'Content-Type: application/json' -d '{\"equipmentID\":\"eq-cnc102\",\"priority\":\"HIGH\"}' http://localhost:4004/odata/v4/maintenance/createMaintenanceOrder\ncurl -X POST -H 'Content-Type: application/json' -d '{\"ID\":\"<MO>\",\"start\":\"2026-09-15T22:00:00Z\",\"end\":\"2026-09-16T02:00:00Z\"}' http://localhost:4004/odata/v4/maintenance/scheduleMaintenance"),
        "Complete code": code("javascript", "Orders.controller.js status guard (COMPLETE)", """canSchedule: function (sStatus) { return sStatus === 'PLANNED' || sStatus === 'DRAFT'; },
canComplete: function (sStatus) { return sStatus === 'IN_PROGRESS' || sStatus === 'SCHEDULED'; },
onSchedule: async function (sId, sStart, sEnd) {
  await this.postAction('scheduleMaintenance', { ID: sId, start: sStart, end: sEnd });
}"""),
        "Explanation of every important line": "<p>Buttons enable ONLY for legal transitions — the UI mirrors the server state machine so users cannot even attempt illegal jumps (server still re-checks).</p>",
        "Expected output": "<p>Order moves DRAFT → PLANNED → SCHEDULED → IN_PROGRESS → COMPLETED with buttons enabling/disabling correctly.</p>",
        "How to test it": std_test("walk one order through all five states via UI; verify each transition in DB."),
        "Negative test cases": neg([["Schedule a COMPLETED order", "action", "409 — UI hid the button; curl proves the server agrees"]]),
        "Common mistakes": "<p>Driving status via PATCH instead of actions — transitions bypass audit and version checks.</p>",
        "How to troubleshoot": "<p>Button enabled but 409 = stale list — refresh bindings after every action.</p>",
        "Production considerations": "<p>Order list is the auditor's favorite page — every row links to its audit trail (Chapter 55).</p>",
        "Security considerations": "<p>Lifecycle buttons hide by role (Chapter 35): users see create; managers see approve/schedule.</p>",
        "What we have completed": done("Ticket lifecycle UI.", "Chapter 31: crew."),
    }))

    parts.append(ch("c31", "31", "Chapter 31 — Technician Management", "", {
        "What are we learning?": "<p><b>Simple:</b> crew directory with skills + availability + assignments. <b>Enterprise:</b> skill matching (who CAN) × availability (who is FREE) = assignable. <b>Example:</b> team sheet before the match.</p>",
        "Why is this important?": "<p>The Workforce Agent (Chapter 48) automates THIS screen's logic — build the manual version first.</p>",
        "Where does this fit in the architecture?": "<p>WorkforceService entities + findAvailableTechnician + assignTechnician.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>view/Technicians.view.xml</code> + assign dialog reuse (Chapter 24 pattern).</p>",
        "Exact commands": PWR + code("powershell", "Skill drill", "curl 'http://localhost:4004/odata/v4/workforce/findAvailableTechnician(skill=%27bearing-replacement%27,date=%272026-09-15%27,shift=%27night%27)'"),
        "Complete code": code("xml", "Technician row with skills (COMPLETE)", """<Table items="{workforce>/Technicians}">
  <columns><Column><Text text="Name"/></Column><Column><Text text="Skills"/></Column><Column><Text text="Assign"/></Column></columns>
  <items><ColumnListItem>
    <Text text="{workforce>name}"/>
    <Text text="{= ${workforce>skills}.map(function(s){return s.skill}).join(', ') }"/>
    <Button text="Assign" press=".onAssign"/>
  </ColumnListItem></items>
</Table>"""),
        "Explanation of every important line": "<p>Skills render from the composition; assign opens the order picker then calls assignTechnician (idempotent, Chapter 58).</p>",
        "Expected output": "<p>Ravi Kumar shows bearing-replacement (expert); drill returns him for night shift 2026-09-15.</p>",
        "How to test it": std_test("drill returns Ravi; assign him; double-assign returns the SAME assignment (idempotent)."),
        "Negative test cases": neg([["No skilled tech free", "drill", "Empty list + 'escalate' hint — never auto-assign unqualified"]]),
        "Common mistakes": "<p>Assigning by name instead of ID — names duplicate, IDs do not.</p>",
        "How to troubleshoot": "<p>Drill empty but tech exists? Check date format (YYYY-MM-DD) and shift spelling.</p>",
        "Production considerations": "<p>Availability is shift-planned data — sync it from HR systems via Destination (Chapter 38), not hand edits.</p>",
        "Security considerations": "<p>Technician PII (email) visible only to workforce roles (Chapter 35).</p>",
        "What we have completed": done("Crew management.", "Chapter 32: spares."),
    }))

    parts.append(ch("c32", "32", "Chapter 32 — Spare Parts and Inventory", "", {
        "What are we learning?": "<p><b>Simple:</b> parts catalog + stock per plant + reserve/release. <b>Enterprise:</b> quantity vs reserved math, reorder points, movement ledger. <b>Example:</b> parts crib with a ledger book.</p>",
        "Why is this important?": "<p>The Inventory Agent (Chapter 47) automates THIS ledger — and stock-outs stop the whole story.</p>",
        "Where does this fit in the architecture?": "<p>InventoryService entities + checkSparePartStock + reserveSparePart.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>view/Spares.view.xml</code> showing available = quantity − reserved.</p>",
        "Exact commands": PWR + code("powershell", "Stock drills", "curl 'http://localhost:4004/odata/v4/inventory/checkSparePartStock(partNo=%27BRG-6205%27)'\ncurl -X POST -H 'Content-Type: application/json' -d '{\"partNo\":\"BRG-6205\",\"qty\":2,\"orderID\":\"<MO>\"}' http://localhost:4004/odata/v4/inventory/reserveSparePart"),
        "Complete code": code("xml", "Stock row with availability math (COMPLETE)", """<Table items="{inventory>/Inventory}">
  <columns><Column><Text text="Part"/></Column><Column><Text text="On hand"/></Column><Column><Text text="Available"/></Column></columns>
  <items><ColumnListItem>
    <Text text="{inventory>part/partNo}"/>
    <ObjectNumber number="{inventory>quantity}"/>
    <ObjectNumber number="{= ${inventory>quantity} - ${inventory>reserved} }" state="{= ${inventory>quantity} - ${inventory>reserved} <= ${inventory>reorderPoint} ? 'Warning' : 'Success' }"/>
  </ColumnListItem></items>
</Table>"""),
        "Explanation of every important line": "<p>Available = on-hand MINUS reserved (never sell the same bearing twice). Reorder-point breach colors the row — the visual reorder alarm.</p>",
        "Expected output": "<p>BRG-6205: 14 on hand, 14 available; after reserve of 2 → 12 available + RESERVE movement row.</p>",
        "How to test it": std_test("reserve twice with same idempotency key → one movement, quantity moved once."),
        "Negative test cases": neg([["Reserve more than available", "action", "422 — no negative stock, ever"], ["Unknown partNo", "check", "404"]]),
        "Common mistakes": "<p>Showing quantity as available (ignoring reserved) — double-booking parts across orders.</p>",
        "How to troubleshoot": "<p>Counts drift? Reconcile: sum(StockMovements) must equal quantity delta since last count.</p>",
        "Production considerations": "<p>Stock ledger is financial-adjacent — every movement needs the audit row (Chapter 55).</p>",
        "Security considerations": "<p>Reserve is a write with money impact — AgentOperator+ roles only (Chapter 35).</p>",
        "What we have completed": done("Parts crib.", "Chapter 33: production windows."),
    }))

    parts.append(ch("c33", "33", "Chapter 33 — Production Scheduling", "", {
        "What are we learning?": "<p><b>Simple:</b> when is Line 3 free for a 4-hour fix? <b>Enterprise:</b> schedule grid + window finder honoring shifts and planned runs. <b>Example:</b> booking the operating theater between surgeries.</p>",
        "Why is this important?": "<p>The Production Agent (Chapter 49) answers THIS question — the last input to the recommendation.</p>",
        "Where does this fit in the architecture?": "<p>ProductionSchedules + findMaintenanceWindow(line, from, to, durationH).</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>view/Schedule.view.xml</code> (week grid bound to schedules).</p>",
        "Exact commands": PWR + code("powershell", "Window drill", "curl 'http://localhost:4004/odata/v4/production/findMaintenanceWindow(lineID=%27line-03%27,from=%272026-09-15%27,to=%272026-09-18%27)'"),
        "Complete code": code("javascript", "findMaintenanceWindow logic (COMPLETE, service handler)", """this.on('findMaintenanceWindow', async (req) => {
  const { lineID, from, to } = req.data;
  const tx = cds.tx(req);
  const runs = await tx.read('maintenance.db.ProductionSchedules')
    .where({ line_ID: lineID, date: { between: [from, to] } }).orderBy('date');
  const free = [];
  for (const r of runs) if (r.status === 'PLANNED' && r.shift === 'night') free.push(r);
  return free;   // night shifts with no firm run = candidate windows
});"""),
        "Explanation of every important line": "<p>Only PLANNED night shifts qualify — firm runs and day shifts are never offered as windows. Ordering by date gives the earliest window first.</p>",
        "Expected output": "<p>Drill returns 2026-09-15 night on Line 3 (22:00-02:00 maintenance slot).</p>",
        "How to test it": std_test("drill returns the seeded night shift; book it via scheduleMaintenance (Chapter 30)."),
        "Negative test cases": neg([["No free window in range", "drill", "Empty list + 'extend range' hint — never invent a window"]]),
        "Common mistakes": "<p>Offering windows during firm production runs — the impact calculator (Chapter 44) exists to price that mistake.</p>",
        "How to troubleshoot": "<p>Empty when shifts exist? Status must be PLANNED exactly — check seed spelling.</p>",
        "Production considerations": "<p>Schedules sync from MES/ERP via Destination (Chapter 38) — manual edits are stopgaps.</p>",
        "Security considerations": "<p>Schedules reveal production tempo — same sensitivity as sensor data (Chapter 35).</p>",
        "What we have completed": done("STOP MILESTONE 4: full UI + plant logic.", "Chapter 34: lock it all down with auth."),
    }))

    return parts
