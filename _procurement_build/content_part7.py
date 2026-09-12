"""Part 7: m27-m41 (testing→finish)."""
from common import mod, step_mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid, depth

def build():
    parts = []

    b = []
    b.append(layer("Pyramid: unit → service → agent → E2E + security"))
    b.append(code("typescript", "test/policy-gate.test.ts -- ADD this file (repo ships unit.test.ts + security.test.ts)", "import { describe, it, expect } from 'vitest';\nimport { evaluatePolicy } from '../lib/workflow/policy.js';\n\ndescribe('policy decides, LLM recommends', () => {\n  it('REQUIRE_HUMAN above agent cap', () => {\n    const d = evaluatePolicy({ amount: 200000, riskLevel: 'HIGH' },\n      [{ code: 'BIG_SPEND', conditions: { minAmount: 100000 }, action: 'REQUIRE_HUMAN' }]);\n    expect(d.action).toBe('REQUIRE_HUMAN');\n  });\n});"))
    b.append(code("bash", "Run it", "npm test                # vitest run\nnpm run build         # tsc --noEmit\nnpx cds compile --to csn db srv   # CDS gate after every model change"))
    b.append(table(["Layer", "Tests"], [["Unit", "validation, policy, lifecycle transitions, formatter"], ["Service", "OData CRUD + actions under mocked roles (EMPLOYEE vs MANAGER)"], ["Agent/MCP", "Tool grants enforced; DENIED paths; A2A delegation payload"], ["Security", "Cross-tenant read blocked; client tenantId rejected; injection prompt ignored"], ["E2E", "PR→approve→convert→PO→receipt→invoice→payment with audit rows"]]))
    parts.append(step_mod("m27", "27", "Phase 26 — Testing", "HAVE: code. ADDING: proof it works + stays working.", "\n".join(b)))

    b = []
    b.append(code("bash", "REST drills (x-mock-user locally; Bearer JWT in prod)", "# create supplier (SUPPLIER_MANAGER)\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: sm:SUPPLIER_MANAGER' \\\n  -d '{\"supplierId\":\"SUP-1001\",\"name\":\"Acme Bearings\",\"country\":\"IN\"}' \\\n  http://localhost:4004/odata/v4/supplier/Suppliers\n# create PR → submit → approve → convert\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: buyer:EMPLOYEE' \\\n  -d '{\"title\":\"Brake pads x200\",\"totalAmount\":45000}' http://localhost:4004/odata/v4/procurement/PurchaseRequisitions\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: buyer:EMPLOYEE' -d '{\"ID\":\"<PR>\"}' http://localhost:4004/odata/v4/procurement/submitRequisition\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: mgr:PROCUREMENT_MANAGER' -d '{\"ID\":\"<PR>\",\"comment\":\"ok\"}' http://localhost:4004/odata/v4/procurement/approveRequisition\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: mgr:PROCUREMENT_MANAGER' -d '{\"requisitionID\":\"<PR>\",\"supplierID\":\"<SUP>\"}' http://localhost:4004/odata/v4/procurement/convertToPurchaseOrder\n# MCP tool + agent task\ncurl -H 'x-mock-user: buyer:EMPLOYEE' 'http://localhost:4004/odata/v4/mcp/searchSuppliers(search=%27acme%27)'\ncurl -X POST -H 'Content-Type: application/json' -H 'x-mock-user: buyer:EMPLOYEE' -H 'x-agent-id: procurement-agent' -d '{\"agentId\":\"procurement-agent\",\"intent\":\"find-risky-suppliers\",\"payload\":\"{}\"}' http://localhost:4004/odata/v4/agents/executeTask"))
    parts.append(step_mod("m28", "28", "Phase 27 — Postman / REST client", "HAVE: endpoints. ADDING: repeatable request library for every actor.", "\n".join(b)))

    b = []
    b.append(table(["Stage", "Command", "Safety"], [["Dev data", "seed CSVs in db/data/", "Fake suppliers only"], ["Postgres local", "npm run db:deploy:pg", "Drops/recreates dev DB — never prod"], ["HANA prod", "mbt build + cf deploy (mta.yaml hdb module)", "Schema migrate only; data untouched; backup first"]]))
    b.append(code("bash", "Docker + git + CI essentials", "docker compose up -d --build   # postgres + cap + mock supplier\n# branches: main (protected) ← develop ← feature/* ; PR + review to merge\n# secrets: .env locally, BTP service bindings in prod — never committed"))
    b.append(code("yaml", ".github/workflows/ci.yml (pattern)", "name: ci\non: [push, pull_request]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n        with: { node-version: 20 }\n      - run: npm ci\n      - run: npx cds compile --to csn db srv\n      - run: npm run build\n      - run: npm test"))
    parts.append(step_mod("m29", "29", "Phases 28-31 — Migrations, Docker, Git, CI/CD", "HAVE: app. ADDING: reproducible environments + gated pipeline.", "\n".join(b)))

    b = []
    b.append(code("bash", "CF deploy from zero (VERIFY flags vs current cf CLI + MTA plugin)", "cf login -a https://api.cf.<region>.hana.ondemand.com\ncf target -o <org> -s <space>\nmbt build\ncf deploy mta_archives/enterprise-ai-procurement_1.0.0.mtar\n# then in cockpit: HANA Cloud instance → service binding → Destination SUPPLIER_API →\n# role collections (xs-security.json) assigned to users/groups → approuter route"))
    b.append(table(["Checklist item", "Done when"], [["Secrets", "No key in code/UI/git; bindings + vault only"], ["OAuth/JWT", "Approuter validates; CAP maps scopes 1:1 to PERMISSIONS"], ["Least privilege", "AI_AGENT empty; per-tool grants + maxAmount"], ["Network", "TLS everywhere; CORS allow-list; CSRF tokens on mutations"], ["AI abuse", "Injection tests green; exfiltration capped by schemas + audit"], ["Tenancy", "tenantId server-stamped; cross-tenant tests red→blocked"]]))
    b.append('<p><b>Multi-tenancy:</b> dedicated tenant-mode; every row carries <code>tenantId</code> from ctx; provider/subscriber model via MTX in full SaaS (deployment descriptor + tenant onboarding). This repo ships the tenant-isolation half; MTX onboarding is the documented next step, not a hidden claim.</p>')
    parts.append(step_mod("m30", "30", "Phases 32-35 — BTP deploy, security, tenancy", "HAVE: local prod-like. ADDING: Cloud Foundry reality + hardening.", "\n".join(b)))

    b = []
    b.append(mermaid("FIG. 12 — FINAL PRODUCTION POSTER", """flowchart TD
  U["User"] --> F["UI5 / Fiori"]
  F --> AR["Approuter"]
  AR --> IAS["IAS + XSUAA"]
  IAS --> CAP["CAP app"]
  CAP --> HANA["HANA Cloud"]
  CAP --> DST["Destination"]
  DST --> XAPI["External APIs"]
  CAP --> EM["Event Mesh"]
  CAP --> GW["MCP Gateway"]
  GW --> TOOLS["MCP tools"]
  CAP --> AG["Agents (orchestrator + 7)"]
  AG --> GW
  AG --> XA["External agents (A2A)"]
  CAP --> LOG["Logging + Monitoring"]"""))
    b.append(table(["Feature", "Local", "BTP production"], [["Database", "Postgres Docker / SQLite tests", "HANA Cloud via mta binding"], ["Auth", "x-mock-user + x-agent-id", "IAS → approuter → XSUAA JWT"], ["MCP/A2A/LLM", "13 tools, A2A tasks, MockLLM", "Same interfaces; gateway + AI Core/HUB"], ["Destinations/messaging", "Mock server + EventEmitter", "Destination + Event Mesh"], ["Logs/monitor", "Console JSON", "Application Logging + alerts"], ["Deploy", "docker compose", "mbt build + cf deploy + CI/CD"]]))
    b.append(qa([("cds command not found", "Reinstall @sap/cds-dk globally; reopen shell."),("DB connection failed","docker compose ps; check DATABASE_URL; pg_isready."),("401/403","Wrong mock role or missing scope; compare JWT scopes vs PERMISSIONS."),("404 OData","Check service path + parenthesis fn syntax + String ID params."),("CAP reads return empty","Handler must extend cds.ApplicationService; check srv/server.js."),("Agent cannot call tool","Missing AgentToolPermissions grant or scope; inspect DENIED execution row."),("A2A timeout","Check discovery URL, agent active flag, downstream MCP latency; retry with idempotency key."),("MTA/CF deploy fails","Rebuild with mbt; verify org/space, HANA binding, xs-security upload.")]))
    parts.append(step_mod("m31", "31", "Phases 36-37 — Production map + troubleshooting", "HAVE: everything built. ADDING: where each piece lives in prod + how to fix it.", "\n".join(b)))

    b = []
    b.append(layer("Complete, internally consistent file set (matches this repo)"))
    b.append(code("text", "Final tree", "db/schema.cds db/common.cds db/data/*.csv\nsrv/procurement-service.cds|.ts srv/catalog-service.cds|.ts srv/supplier-service.cds|.ts\nsrv/invoice-service.cds|.ts srv/approval-service.cds|.ts srv/audit-service.cds\nsrv/mcp-service.cds|.ts srv/agent-service.cds|.ts srv/server.js\nlib/auth/authentication.ts lib/auth/rbac.ts lib/authorization/authorization.ts\nlib/workflow/policy.ts lib/workflow/lifecycle.ts lib/validation/validation.ts\nlib/audit/audit.ts lib/security/errors.ts lib/security/observability.ts\napp/procurement-ui/ (manifest, Component, controllers, views, fragments, i18n)\npackage.json .cdsrc.json mta.yaml xs-security.json Dockerfile docker-compose.yml .env.example"))
    b.append(code("cds", "FILE: srv/catalog-service.cds + supplier + invoice + approval (shapes)", "service CatalogService @(path:'/odata/v4/catalog') { entity Materials as projection on db.Materials; entity MaterialCategories as projection on db.MaterialCategories; }\nservice SupplierService @(path:'/odata/v4/supplier') { entity Suppliers as projection on db.Suppliers; entity SupplierContacts as projection on db.SupplierContacts; }\nservice InvoiceService @(path:'/odata/v4/invoice') { entity Invoices as projection on db.Invoices; entity Payments as projection on db.Payments; }\nservice ApprovalService @(path:'/odata/v4/approval') { entity Approvals as projection on db.Approvals; entity WorkflowTasks as projection on db.WorkflowTasks; }"))
    b.append(code("bash", "FILE: execution checklist (24 steps, abridged commands)", "1 node -v && cds --version   2 cds init && npm i   3 docker compose up -d db\n4 write db/*.cds   5 npm run db:deploy:pg   6 npm start   7 curl OData with x-mock-user\n8 add lib/auth + xs-security   9 Postgres profile   10 UI5 scaffold   11 mock supplier API\n12 annotate @mcp + 13 tools   13 MockLLM agent   14 A2A executeTask   15 audit rows\n16 npm test   17 docker compose up --build   18 git push + PR   19 mbt build && cf deploy\n20 bind HANA   21 Destination SUPPLIER_API   22 IAS/XSUAA roles   23 hardening checklist   24 E2E drill"))
    b.append(table(["Capability", "Implemented", "Local", "BTP"], [["CAP/CDS/OData/CRUD", "Yes", "Yes", "Yes"], ["Postgres → HANA", "Yes", "PG", "HANA"], ["UI5 + chat UI", "Yes", "Yes", "Via approuter"], ["OAuth/IAS/Destination", "Yes", "Mocked", "Managed"], ["MCP 13 tools + gateway", "Yes", "Learning gw", "Managed gw"], ["7 agents + A2A", "Yes", "Yes", "Yes + AI Core"], ["Events/jobs/audit/observe", "Yes", "Emitter/jobs", "Event Mesh/scheduler"], ["CI/CD/Docker/tenancy", "Yes", "Compose/GHA", "MTA/CF/MTX path"]]))
    b.append(layer("What next"))
    b.append(table(["Level", "Learn"], [["Beginner", "CAP docs end-to-end (cds model→service→deploy), OData $filter/$expand"], ["Intermediate", "XSUAA scopes, destinations, HANA deployment, UI5 routing"], ["Advanced", "MCP transports, tool governance, A2A delegation, Event Mesh"], ["Expert", "Joule extensions, AI Core orchestration, MTX SaaS, ARC assessment"]]))
    parts.append(step_mod("m32", "32", "Phases 38-41 — Source, checklist, matrix, roadmap", "HAVE: full system. ADDING: the wrap-up that proves consistency.", "\n".join(b)))

    return parts
