"""Part 5: CH19-CH26 (UI5 core)."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done


def build():
    parts = []

    parts.append(ch("c19", "19", "Chapter 19 — Build the SAPUI5 Application", "", {
        "What are we learning?": "<p><b>Simple:</b> a Fiori-style web app shell with pages and navigation. <b>Enterprise:</b> UI5 MVC + Component + manifest-first configuration. <b>Example:</b> the factory control room: one wall, many screens.</p>",
        "Why is this important?": "<p>Every Chapter 27-33 screen plugs into THIS shell. Wrong bootstrap = 14 broken pages.</p>",
        "Where does this fit in the architecture?": "<p>The SAPUI5 APPLICATION box users actually touch.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>app/maintenance-ui/</code>: manifest.json, Component.js, views/, controllers/, fragments/, model/, i18n/, css/.</p>",
        "Exact commands": PWR + code("powershell", "Scaffold UI (project root)", "mkdir app\\maintenance-ui\\webapp\\view, app\\maintenance-ui\\webapp\\controller, app\\maintenance-ui\\webapp\\fragment, app\\maintenance-ui\\webapp\\model, app\\maintenance-ui\\webapp\\i18n, app\\maintenance-ui\\webapp\\css\nnpm start  # UI served alongside CAP in dev"),
        "Complete code": code("json", "FILE: manifest.json (COMPLETE skeleton, routes grow in Ch 20)", """{
  "sap.app": { "id": "assetops.maintenance.ui", "type": "application", "title": "{{appTitle}}" },
  "sap.ui5": {
    "rootView": { "viewName": "assetops.maintenance.ui.view.App", "type": "XML" },
    "routing": { "config": { "routerClass": "sap.m.routing.Router", "viewType": "XML" }, "routes": [], "targets": {} }
  },
  "sap.cloud": { "public": true }
}""") + code("javascript", "FILE: Component.js (COMPLETE)", """sap.ui.define(['sap/ui/core/UIComponent', 'sap/ui/model/odata/v4/ODataModel', './model/models'],
  function (UIComponent, ODataModel, models) {
    'use strict';
    return UIComponent.extend('assetops.maintenance.ui.Component', {
      init: function () {
        UIComponent.prototype.init.apply(this, arguments);
        this.setModel(new ODataModel({ serviceUrl: '/odata/v4/equipment/', synchronizationMode: 'None' }), 'equipment');
        this.setModel(new ODataModel({ serviceUrl: '/odata/v4/maintenance/', synchronizationMode: 'None' }), 'maintenance');
        this.setModel(models.view(), 'view');
        this.getRouter().initialize();
      }
    });
  });"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["Two ODataModels", "Named models per service — equipment vs maintenance stay separate"], ["synchronizationMode None", "Async binding; UI stays responsive (busy indicators Ch 26)"], ["models.view()", "Local JSONModel for busy flags + UI state (Chapter 21)"], ["getRouter().initialize()", "Activates Chapter 20 routes"]]),
        "Expected output": "<p>App loads (blank shell, no errors in browser console).</p>",
        "How to test it": std_test("open the UI URL; console shows zero 404s for Component/manifest."),
        "Negative test cases": neg([["Wrong serviceUrl", "load", "All lists empty — compare URL against Chapter 10 paths"]]),
        "Common mistakes": "<p>One default (unnamed) model for everything — named models prevent cross-service binding bugs.</p>",
        "How to troubleshoot": "<p>UI5 404s name the missing file exactly — create it, hard-refresh (Ctrl+F5).</p>",
        "Production considerations": "<p>UI5 ships via approuter (Chapter 77) — serviceUrls stay RELATIVE so DEV/STAGE/PROD all work.</p>",
        "Security considerations": "<p>No secrets, tokens or keys in ANY frontend file — ever (CI scans for this, Chapter 72).</p>",
        "What we have completed": done("Running UI shell." + mermaid('FIG. 9 - UI5 MVC WIRING', 'flowchart LR; V[XML view]-->C[Controller]; C-->M1[ODataModel equipment]; C-->M2[ODataModel maintenance]; C-->VM[JSON view model]; M1-->CAP[CAP services]; M2-->CAP'), "Chapter 20: pages + deep links."),
    }))

    parts.append(ch("c20", "20", "Chapter 20 — UI5 Routing", "", {
        "What are we learning?": "<p><b>Simple:</b> URLs for every screen (#/equipment/eq-cnc102). <b>Enterprise:</b> router + targets + deep linking + back navigation. <b>Example:</b> room numbers in the factory — every screen addressable.</p>",
        "Why is this important?": "<p>Agents link users to exact records; bookmarks and alerts need stable URLs (Chapter 29).</p>",
        "Where does this fit in the architecture?": "<p>Inside the UI5 box: screen-to-screen flow.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT <code>manifest.json</code> routing; NEW view/controller stubs per route.</p>",
        "Exact commands": "<p>No CLI — edit + reload. Routes below cover Chapters 27-33 screens.</p>",
        "Complete code": code("json", "manifest.json routing (COMPLETE route table)", """{ "routes": [
  { "name": "dashboard", "pattern": "", "target": "Dashboard" },
  { "name": "equipment", "pattern": "equipment", "target": "Equipment" },
  { "name": "equipmentDetails", "pattern": "equipment/{equipmentId}", "target": "EquipmentDetails" },
  { "name": "orders", "pattern": "orders", "target": "Orders" },
  { "name": "technicians", "pattern": "technicians", "target": "Technicians" },
  { "name": "spares", "pattern": "spares", "target": "Spares" },
  { "name": "schedule", "pattern": "schedule", "target": "Schedule" },
  { "name": "assistant", "pattern": "assistant", "target": "Assistant" },
  { "name": "agents", "pattern": "agents", "target": "AgentMonitoring" },
  { "name": "audit", "pattern": "audit", "target": "Audit" }
] }"""),
        "Explanation of every important line": "<p><code>pattern</code> is the hash URL; <code>{equipmentId}</code> passes the record key to the details controller (<code>onRouteMatched</code> binds it).</p>",
        "Expected output": "<p>#/equipment/eq-cnc102 opens the (stub) details page with the ID in the controller.</p>",
        "How to test it": std_test("visit every pattern; each renders its target without console errors."),
        "Negative test cases": neg([["Unknown hash", "open #/nope", "NotFound target (add one) instead of blank page"]]),
        "Common mistakes": "<p>Two routes matching '' — exactly one default route.</p>",
        "How to troubleshoot": "<p>Blank page = target view name typo. Router logs the attempted view in the console.</p>",
        "Production considerations": "<p>Deep links are the incident-playbook currency (Chapter 88 links alerts to records).</p>",
        "Security considerations": "<p>Route params are user input — validate IDs before binding (Chapter 26).</p>",
        "What we have completed": done("Navigable screen map.", "Chapter 21: the models behind the screens."),
    }))

    parts.append(ch("c21", "21", "Chapter 21 — UI5 Models", "", {
        "What are we learning?": "<p><b>Simple:</b> ODataModel = live server data; JSONModel = local UI state. <b>Enterprise:</b> named models per service + a view model for busy/error flags. <b>Example:</b> live scoreboard (OData) vs coach's notepad (JSON).</p>",
        "Why is this important?": "<p>Mixing them causes phantom edits (local changes that never save) or frozen screens.</p>",
        "Where does this fit in the architecture?": "<p>UI5-side data layer feeding every binding in Chapters 22-33.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>model/models.js</code> (view model factory).</p>",
        "Exact commands": "<p>None — code + reload.</p>",
        "Complete code": code("javascript", "FILE: model/models.js (COMPLETE)", """sap.ui.define(['sap/ui/model/json/JSONModel'], function (JSONModel) {
  'use strict';
  return { view: function () { return new JSONModel({ busy: false, tools: [], error: '' }); } };
});"""),
        "Explanation of every important line": "<p>Single factory keeps initial flags consistent on EVERY page — busy, tool trace, error string.</p>",
        "Expected output": "<p><code>{view&gt;/busy}</code> bindings resolve on all pages.</p>",
        "How to test it": std_test("toggle busy in console via the view model; spinner appears."),
        "Negative test cases": neg([["Binding to unnamed model", "use {/x}", "Empty — OData lives on NAMED models (equipment&gt;, maintenance&gt;)"]]),
        "Common mistakes": "<p>Storing server data in JSONModel copies — they go stale; bind OData directly.</p>",
        "How to troubleshoot": "<p>Binding errors name the model + path — check the name prefix first.</p>",
        "Production considerations": "<p>View-model shape is a UI contract — changing flag names breaks all pages at once.</p>",
        "Security considerations": "<p>Never place tokens or user secrets in any model — Chapter 72 scans for this.</p>",
        "What we have completed": done("Two-model discipline.", "Chapter 22: OData V4 binding in views."),
    }))

    parts.append(ch("c22", "22", "Chapter 22 — OData V4 from UI5", "", {
        "What are we learning?": "<p><b>Simple:</b> bind controls directly to Chapter 12 URLs. <b>Enterprise:</b> list bindings, $expand, deferred groups for batched saves. <b>Example:</b> plug the scoreboard cable into the live feed.</p>",
        "Why is this important?": "<p>This is how EVERY list, form and chart in Chapters 27-33 gets data.</p>",
        "Where does this fit in the architecture?": "<p>The UI5→CAP arrow, realized.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT views: add bindings (example: Equipment list below).</p>",
        "Exact commands": "<p>None — markup + reload.</p>",
        "Complete code": code("xml", "FILE: view/Equipment.view.xml (COMPLETE list binding)", """<mvc:View xmlns:mvc="sap.ui.core.mvc" xmlns="sap.m" controllerName="assetops.maintenance.ui.controller.Equipment">
  <Page title="{i18n>equipmentTitle}">
    <Table id="eqTable" items="{equipment>/Equipment}" busy="{view>/busy}" growing="true" growingThreshold="20">
      <headerToolbar><Toolbar><SearchField search=".onSearch" width="20rem"/></Toolbar></headerToolbar>
      <columns><Column><Text text="ID"/></Column><Column><Text text="Name"/></Column><Column><Text text="Status"/></Column></columns>
      <items><ColumnListItem type="Navigation" press=".onNav">
        <ObjectIdentifier title="{equipment>equipmentId}"/><Text text="{equipment>name}"/><ObjectStatus text="{equipment>status}"/>
      </ColumnListItem></items>
    </Table>
  </Page>
</mvc:View>"""),
        "Explanation of every important line": table(["Markup", "Meaning"], [["items={equipment>/Equipment}", "Named-model list binding to the entity set"], ["growing=true Threshold=20", "Client pager over Chapter 16 server pages"], ["{i18n>...}", "No hardcoded strings (Chapter 25)"], ["type=Navigation", "Row tap → details route (Chapter 20)"]]),
        "Expected output": "<p>CNC-MACHINE-102 appears in the table; search filters server-side.</p>",
        "How to test it": std_test("table shows seed rows; network tab shows one OData call with $skip/$top."),
        "Negative test cases": neg([["Service down", "stop CAP, reload", "Table shows error state, not infinite spinner (Chapter 26)"]]),
        "Common mistakes": "<p>Binding <code>{/Equipment}</code> (default model) instead of <code>{equipment&gt;/Equipment}</code>.</p>",
        "How to troubleshoot": "<p>Empty table + 200 response = wrong entity-set name. Compare with $metadata.</p>",
        "Production considerations": "<p>growingThreshold aligns with server page caps — tune from monitoring (Chapter 85).</p>",
        "Security considerations": "<p>Bindings render data — formatter-escaped text only, no raw HTML (XSS, Chapter 65).</p>",
        "What we have completed": done("Live data binding.", "Chapter 23: write back through CRUD."),
    }))

    parts.append(ch("c23", "23", "Chapter 23 — UI5 CRUD", "", {
        "What are we learning?": "<p><b>Simple:</b> create/edit dialogs that save through OData. <b>Enterprise:</b> create-then-bind pattern, draft-free direct save with validation, message handling. <b>Example:</b> fill a work-permit form, clerk stamps it.</p>",
        "Why is this important?": "<p>Orders, assignments and schedules are BORN in these dialogs (Chapter 30-33).</p>",
        "Where does this fit in the architecture?": "<p>UI5→CAP write arrow with Chapter 13 validation on the far side.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>fragment/OrderDialog.fragment.xml</code>; EDIT Orders controller.</p>",
        "Exact commands": "<p>None — markup + controller + reload.</p>",
        "Complete code": code("javascript", "Orders.controller.js onCreate/onSave (COMPLETE)", """onCreate: function () {
  var oModel = this.getView().getModel('maintenance');
  this._ctx = oModel.bindContext('/MaintenanceOrders', undefined, { $$updateGroupId: 'orderCreate' });
  this.byId('orderDialog').open();
},
onSave: async function () {
  var oView = this.getView();
  oView.getModel('view').setProperty('/busy', true);
  try {
    var oCtx = this._ctx;
    oCtx.setProperty('equipment_ID', this.byId('eqInput').getValue());
    oCtx.setProperty('priority', this.byId('prioSelect').getSelectedKey());
    await oCtx.created();
    await oView.getModel('maintenance').submitBatch('orderCreate');
    sap.m.MessageToast.show('Order created');
  } catch (e) { sap.m.MessageBox.error(e.message); }
  finally { oView.getModel('view').setProperty('/busy', false); }
}"""),
        "Explanation of every important line": "<p>Bind-then-set Defers the POST until submitBatch — validation (Chapter 26) runs BEFORE anything travels. Busy flag + try/catch/finally = no stuck spinners.</p>",
        "Expected output": "<p>New MO- order appears in the list with status DRAFT.</p>",
        "How to test it": std_test("create with valid + invalid input; list refreshes; error box shows server message."),
        "Negative test cases": neg([["Save with empty machine", "onSave", "Server 400 surfaces in MessageBox; dialog stays open"], ["Double-click save", "click twice fast", "Disable button while busy — single POST"]]),
        "Common mistakes": "<p>Forgetting submitBatch — context created locally, never sent, user thinks it saved.</p>",
        "How to troubleshoot": "<p>400 in network tab but generic box? Read error response body — Chapter 15 codes are there.</p>",
        "Production considerations": "<p>CSRF handshake required via approuter (Chapter 77) — test creates through the real route before go-live.</p>",
        "Security considerations": "<p>Client validation is UX only; Chapter 13 server validation is the gate (test by bypassing UI with curl).</p>",
        "What we have completed": done("Working write path.", "Chapter 24: reusable dialogs."),
    }))

    parts.append(ch("c24", "24", "Chapter 24 — Fragments and Dialogs", "", {
        "What are we learning?": "<p><b>Simple:</b> reusable popups: one approval dialog used everywhere. <b>Enterprise:</b> fragment cache, depended-on-view lifecycle, shared approval + assign + reserve dialogs. <b>Example:</b> one stamp, many desks.</p>",
        "Why is this important?": "<p>Chapters 30-33 and the Chapter 54 approval share ONE dialog — fix once, fixed everywhere.</p>",
        "Where does this fit in the architecture?": "<p>UI5 component reuse layer.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>fragment/ApprovalDialog.fragment.xml</code> + helper <code>controller/dialogs.js</code>.</p>",
        "Exact commands": "<p>None — markup + reload.</p>",
        "Complete code": code("xml", "FILE: fragment/ApprovalDialog.fragment.xml (COMPLETE)", """<core:FragmentDefinition xmlns:core="sap.ui.core" xmlns="sap.m">
  <Dialog id="approvalDialog" title="{i18n>approveTitle}">
    <Text text="{view>/recommendation/summary}"/>
    <List items="{view>/recommendation/actions}"><StandardListItem title="{view>label}" description="{view>detail}"/></List>
    <buttons>
      <Button text="{i18n>approve}" type="Emphasized" press=".onApprove"/>
      <Button text="{i18n>reject}" press=".onReject"/>
    </buttons>
  </Dialog>
</core:FragmentDefinition>"""),
        "Explanation of every important line": "<p>Fragment binds the SAME view model the assistant page fills (Chapter 54) — zero duplication between AI flow and manual flow.</p>",
        "Expected output": "<p>Approval dialog opens from orders AND assistant with identical content.</p>",
        "How to test it": std_test("open dialog from two pages; approve on one; both lists refresh."),
        "Negative test cases": neg([["Dialog opened twice", "double open", "Singleton helper reuses instance — no duplicates"]]),
        "Common mistakes": "<p>Loading fragments without addDependent — models do not propagate and bindings stay empty.</p>",
        "How to troubleshoot": "<p>Empty dialog = missing addDependent(oView) in dialogs.js helper.</p>",
        "Production considerations": "<p>Shared fragments are versioned with the app — MTA rollback (Chapter 87) reverts UI + API together.</p>",
        "Security considerations": "<p>Approval buttons require MaintenanceManager role client-side AND server-side (Chapter 35).</p>",
        "What we have completed": done("Reusable approval UX.", "Chapter 25: formatters + types."),
    }))

    parts.append(ch("c25", "25", "Chapter 25 — Formatters and Type Handling", "", {
        "What are we learning?": "<p><b>Simple:</b> turn codes into colors (HIGH → red). <b>Enterprise:</b> formatter module + UI5 types for dates/numbers + i18n. <b>Example:</b> control-room lamps: same signal, instant meaning.</p>",
        "Why is this important?": "<p>Operators triage in seconds from color + text — Chapters 27-29 depend on instant readability.</p>",
        "Where does this fit in the architecture?": "<p>UI5 presentation layer; zero backend impact.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>NEW <code>model/formatter.js</code> + <code>i18n/i18n.properties</code>.</p>",
        "Exact commands": "<p>None — code + reload.</p>",
        "Complete code": code("javascript", "FILE: model/formatter.js (COMPLETE)", """sap.ui.define([], function () {
  'use strict';
  return {
    severityState: function (s) {
      if (s === 'CRITICAL' || s === 'HIGH') return 'Error';
      if (s === 'MEDIUM') return 'Warning';
      return 'Success';
    },
    orderState: function (s) {
      if (s === 'COMPLETED') return 'Success';
      if (s === 'CANCELLED') return 'Error';
      if (s === 'IN_PROGRESS' || s === 'SCHEDULED') return 'Information';
      return 'None';
    }
  };
});""") + code("text", "FILE: i18n/i18n.properties (COMPLETE core keys)", """appTitle=Asset Maintenance Control Tower
equipmentTitle=Equipment
alertsTitle=Alerts
approveTitle=Approve AI recommendation
approve=Approve
reject=Reject"""),
        "Explanation of every important line": "<p>Pure functions: input code → output state. i18n keys replace every hardcoded string.</p>",
        "Expected output": "<p>HIGH alerts render red; COMPLETED orders green.</p>",
        "How to test it": std_test("formatter unit checks in console for each code; screenshot review with operators."),
        "Negative test cases": neg([["Unknown code 'ASAP'", "format", "Falls through to neutral — never throws"]]),
        "Common mistakes": "<p>Formatting in controllers (untestable) instead of the formatter module.</p>",
        "How to troubleshoot": "<p>Wrong color = wrong binding path — check the property name against $metadata.</p>",
        "Production considerations": "<p>Formatter changes are UI-only deploys — no backend regression needed.</p>",
        "Security considerations": "<p>Formatters output text, never HTML — XSS-safe by construction.</p>",
        "What we have completed": done("Readable UI language.", "Chapter 26: validation + errors."),
    }))

    parts.append(ch("c26", "26", "Chapter 26 — UI5 Validation and Error Handling", "", {
        "What are we learning?": "<p><b>Simple:</b> red borders on bad fields + friendly error boxes. <b>Enterprise:</b> MessageManager, value states, busy handling, offline states. <b>Example:</b> spellcheck before sending the permit to the clerk.</p>",
        "Why is this important?": "<p>Last UX chapter before the plant screens — every Chapter 27-33 form uses these patterns.</p>",
        "Where does this fit in the architecture?": "<p>UI5 error edge; server codes from Chapter 15 surface here.</p>",
        "Prerequisites": PREV,
        "Folder/file changes": "<p>EDIT controllers: wire MessageManager + value states (pattern below).</p>",
        "Exact commands": "<p>None — code + reload.</p>",
        "Complete code": code("javascript", "Validation pattern (COMPLETE, paste into any controller)", """onFieldChange: function (oEvent) {
  var oInput = oEvent.getSource();
  var ok = oInput.getValue().trim().length > 0;
  oInput.setValueState(ok ? 'None' : 'Error');
  oInput.setValueStateText(ok ? '' : this.getResourceBundle().getText('fieldRequired'));
  this.byId('saveBtn').setEnabled(ok);
},
showError: function (message) {
  this.getView().getModel('view').setProperty('/busy', false);
  sap.m.MessageBox.error(message);
}"""),
        "Explanation of every important line": "<p>Validate on change (instant), gate the save button (prevention), always clear busy on error (no stuck spinners).</p>",
        "Expected output": "<p>Empty required field → red border + disabled save; server 400 → MessageBox with the Chapter 15 message.</p>",
        "How to test it": std_test("submit empty, invalid, then valid — three states, three correct behaviors."),
        "Negative test cases": neg([["Server 500", "force failure", "Generic friendly text — internals stay hidden"], ["Offline backend", "stop CAP", "Error state page, retry button"]]),
        "Common mistakes": "<p>Leaving busy=true on error paths — the #1 'frozen app' complaint.</p>",
        "How to troubleshoot": "<p>MessageBox shows [object Object]? Pass e.message, not the error object.</p>",
        "Production considerations": "<p>Client errors logged with correlationId (Chapter 56) — support can trace user reports.</p>",
        "Security considerations": "<p>Client validation is UX sugar — Chapter 65 proves bypassing it still fails server-side.</p>",
        "What we have completed": done("STOP MILESTONE 3: UI foundation complete.", "Chapter 27: the dashboard."),
    }))

    return parts
