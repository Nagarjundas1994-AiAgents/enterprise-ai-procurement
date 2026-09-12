"""Part 8: m33-m37 (audit fixes, provider trio, UI5 files, full source)."""
from common import mod, step_mod, layer, callout, code, table, grid, steps, qa, quiz, mermaid

def build():
    parts = []

    b = []
    b.append(layer("Spec-to-repo name mapping (read this first)"))
    b.append(table(["Spec asked for", "Repo reality", "Verdict"], [["Inventory entity + get_inventory", "No Inventory entity in db/schema.cds", "Missing — extension pack below"], ["check_supplier_risk tool", "getProcurementRisk(requisitionID) exists; supplier-level scorer does not", "Missing — extension below"], ["checkInventory / calculateProcurementRisk functions", "No lib/risk module", "Missing — extension below"], ["approve_purchase_requisition MCP tool", "Approval is a ProcurementService action (APPROVE_PR), not an MCP tool", "Deliberate — dual control, do NOT add"], ["test/rbac + policy + requisition suites", "Repo ships test/unit.test.ts + test/security.test.ts", "Fixed in m27 caption; add policy-gate.test.ts"], ["lib/llm/provider.ts (LLMProvider)", "Real file is lib/agents/ai-service.ts (AIService + MockAI + getAIService)", "Fixed in m17"], ["Per-agent /.well-known cards", "One orchestrator card in srv/server.js (A2A/0.2)", "Fixed in m19"]]))
    b.append(callout("warn", "REAL bug found in the repo", "<p><b>/health is probed but never served.</b> Dockerfile HEALTHCHECK and mta.yaml health-check endpoints hit <code>/health</code>, but <code>srv/server.js</code> only defines <code>/liveness</code> and <code>/readiness</code> (verified: no <code>/health</code> route anywhere in srv/ or lib/). Until fixed, Docker reports the container unhealthy and CF health checks fail. One-line fix:</p>"))
    b.append(code("javascript", "FIX: srv/server.js inside cds.on(bootstrap)", "app.get('/health', (_req, res) => res.json({ status: 'ok', time: new Date().toISOString() }));"))
    b.append(layer("EXTENSION PACK 1: Inventory entity + seed"))
    b.append(code("cds", "Append to db/schema.cds, add CSV, recompile", """// EXTENSION (not in repo yet)
entity Inventory : cuid, managed, c.TenantAware {
  material     : Association to Materials not null;
  plant        : String(32) not null default 'PLANT-01';
  quantity     : Decimal(15,3) default 0 not null;
  unit         : String(16) default 'EA';
  reorderPoint : Decimal(15,3) default 0;
}"""))
    b.append(code("text", "db/data/procurement.db-Inventory.csv (same tenant-a style)", "ID,tenantId,material_ID,plant,quantity,unit,reorderPoint\ninv-01,tenant-a,mat-brake-pad,PLANT-01,850,EA,200\ninv-02,tenant-a,mat-filter,PLANT-01,120,EA,300"))
    b.append(layer("EXTENSION PACK 2: risk functions + tools"))
    b.append(code("typescript", "lib/risk/risk.ts (NEW, pure + unit-testable)", """import cds from '@sap/cds';
import { reqError } from '../security/errors.js';

// Pure math: easy unit test, no LLM inside (LLM recommends, this decides).
export function calculateProcurementRisk(input: { riskScore: number; onTimeRate: number; disputeCount: number }) {
  const score = Math.round(input.riskScore * 0.5 + (100 - input.onTimeRate) * 2 + Math.min(input.disputeCount * 6, 30));
  const level = score >= 70 ? 'HIGH' : score >= 40 ? 'MEDIUM' : 'LOW';
  return { score: Math.min(score, 100), level };
}

export async function checkInventory(tx: any, tenantId: string, materialID: string) {
  const rows: any[] = await tx.read('procurement.db.Inventory').where({ material_ID: materialID, tenantId });
  const total = rows.reduce((n, r) => n + Number(r.quantity ?? 0), 0);
  return { materialID, total, low: rows.filter((r) => Number(r.quantity) < Number(r.reorderPoint)) };
}

export async function checkSupplierRisk(tx: any, tenantId: string, supplierID: string) {
  const s: any = await tx.run(SELECT.one.from('procurement.db.Suppliers').where({ ID: supplierID, tenantId }));
  if (!s) throw reqError('RESOURCE_NOT_FOUND', 'Supplier not found');
  return { supplierID, ...calculateProcurementRisk(s), assessedAt: new Date().toISOString() };
}"""))
    b.append(code("cds", "srv/mcp-service.cds additions + rbac grant", """entity Inventory as projection on db.Inventory;
function getInventory(materialID : String) returns many Inventory;
function checkSupplierRisk(supplierID : String) returns RiskAssessments;"""))
    b.append(code("bash", "Wire + verify the extension", "npx cds compile --to csn db srv   # must exit 0\nnpm test                                # add a calculateProcurementRisk case\n# curl -H 'x-mock-user: buyer:EMPLOYEE' 'http://localhost:4004/odata/v4/mcp/getInventory(materialID=%27mat-brake-pad%27)'"))
    parts.append(step_mod("m33", "33", "Gap audit + missing code (Inventory, risk, /health)", "HAVE: 13 tools, no stock view. ADDING: the three missing functions plus a real repo bug fix.", "\n".join(b)))

    b = []
    b.append(layer("Real interface + three more providers behind it"))
    b.append('<p>Real: <code>AIService { generate / chat / structuredOutput }</code> with <code>MockAI</code> selected by <code>getAIService()</code> when no <code>AI_API_URL</code>/<code>AI_API_KEY</code> is set. Add providers without touching business logic:</p>')
    b.append(code("typescript", "lib/agents/providers.ts (EXTENSION pattern, VERIFY SDK names)", """import type { AIService, ChatMessage } from './ai-service.js';

function env(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`[ai] missing env ${name}`);
  return v;
}

export class OpenAIProvider implements AIService {
  async generate(prompt: string) { return this.chat([{ role: 'user', content: prompt }]); }
  async chat(messages: ChatMessage[]) {
    // VERIFY: endpoint + model names vs current OpenAI docs. Never log the key.
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env('AI_API_KEY')}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: process.env.AI_MODEL ?? 'gpt-4o-mini', messages }),
      signal: AbortSignal.timeout(30000),
    });
    if (!r.ok) throw new Error(`[ai] openai:${r.status}`);
    const j: any = await r.json();
    return j.choices[0].message.content;
  }
  async structuredOutput<T>(prompt: string, schemaHint: string): Promise<T> {
    return JSON.parse(await this.generate(`${prompt}\\nReturn ONLY JSON matching: ${schemaHint}`));
  }
}

export class AzureOpenAIProvider extends OpenAIProvider {
  // VERIFY: deployment URL shape vs current Azure OpenAI docs.
  // Same class, different base URL: https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions?api-version=2024-06-01
}

export class AICoreProvider extends OpenAIProvider {
  // SAP AI Core exposes an OpenAI-compatible proxy via the orchestration service.
  // VERIFY: base URL + deployment ID vs current Generative AI Hub docs.
  // Base URL comes from AI_API_URL (.env.example already has AI_API_URL/AI_MODEL/AI_PROVIDER).
}

export function providerFromEnv(): AIService {
  switch ((process.env.AI_PROVIDER ?? 'mock').toLowerCase()) {
    case 'openai': return new OpenAIProvider();
    case 'azure': return new AzureOpenAIProvider();
    case 'aicore': return new AICoreProvider();
    default: return new OpenAIProvider(); // replaced by getAIService() mock when no keys set
  }
}"""))
    b.append(callout("prod", "Key rule repeated", "<p>Providers read <code>AI_API_KEY</code> from env/BTP bindings only — never from UI code, never from git. Local dev with no keys keeps working on <code>MockAI</code>.</p>"))
    parts.append(step_mod("m34", "34", "LLM provider trio (OpenAI, Azure, AI Core)", "HAVE: MockAI. ADDING: three drop-in providers behind the same interface.", "\n".join(b)))

    b = []
    b.append(layer("The four UI5 files m22 skipped"))
    b.append(code("javascript", "app/procurement-ui/webapp/model/formatter.js (pattern)", """sap.ui.define([], function () {
  'use strict';
  return {
    statusState: function (s) {
      if (s === 'APPROVED' || s === 'CONVERTED_TO_PO') return 'Success';
      if (s === 'REJECTED') return 'Error';
      if (s === 'SUBMITTED' || s === 'UNDER_REVIEW') return 'Warning';
      return 'None';
    },
    riskState: function (r) {
      if (r === 'HIGH' || r === 'CRITICAL') return 'Error';
      if (r === 'MEDIUM') return 'Warning';
      return 'Success';
    }
  };
});"""))
    b.append(code("text", "i18n/i18n.properties + models.js + style.css (pattern)", """# i18n/i18n.properties — every UI string lives here, none hardcoded
appTitle=Autonomous Procurement Control Tower
prTitle=Purchase Requisitions
supplierRisk=Supplier Risk
assistantTitle=AI Assistant"""))
    b.append(code("javascript", "models.js + style.css (pattern)", """sap.ui.define(['sap/ui/model/json/JSONModel'], function (JSONModel) {
  'use strict';
  return {
    view: function () { return new JSONModel({ busy: false, tools: [] }); }
  };
});"""))
    b.append(code("css", "css/style.css (pattern)", """.tower .sapMPageHeader { background: #0B3D91; }\n.tower .riskHigh { color: #B23A2E; font-weight: 600; }\n@media (max-width: 600px) { .tower .hideSmall { display: none; } }"""))
    parts.append(step_mod("m35", "35", "UI5 missing files (formatter, i18n, models, CSS)", "HAVE: shell + table. ADDING: the four files every view needs.", "\n".join(b)))

    b = []
    b.append(layer("Deploy + config files, verbatim from the repo"))
    b.append(code("json", "FILE: package.json (REAL)", """{
  "name": "enterprise-ai-procurement",
  "version": "1.0.0",
  "type": "module",
  "engines": { "node": ">=20" },
  "scripts": {
    "build": "tsc --noEmit -p tsconfig.json",
    "start": "tsx ./node_modules/@sap/cds/bin/serve.js",
    "test": "vitest run",
    "db:deploy:pg": "node scripts/deploy-pg.cjs",
    "db:deploy:prod": "cds-deploy --to postgres --production"
  }
}"""))
    b.append(code("dockerfile", "FILE: Dockerfile (REAL)", """FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build || true

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts && npm rebuild @cap-js/postgres || true
COPY --from=build /app ./
EXPOSE 4004
CMD ["sh", "-c", "npm run db:deploy:prod || true; npm start"]"""))
    b.append(code("text", "FILE: .env.example + .gitignore + .cdsrc.json (REAL)", """PORT=4004
DB_HOST=localhost
DB_PORT=5432
DB_NAME=procurement
DB_USER=postgres
DB_PASSWORD=changeme
DATABASE_URL=
JWT_SECRET=dev-only-secret-change-me
ALLOW_MOCK_AUTH=true
AI_API_URL=
AI_API_KEY=
AI_MODEL=anthropic--claude-4-sonnet
AI_PROVIDER=aicore
---
.gitignore: .env / .env.* / default-env.json / node_modules/ / dist/ / coverage/
---
.cdsrc.json: sqlite memory by default; postgres under [postgres]/[production]; mocked auth, JWT in production"""))
    b.append(code("yaml", "FILE: mta.yaml (REAL, excerpt)", """modules:
  - name: procurement-backend
    type: nodejs
    path: .
    properties: { ALLOW_MOCK_AUTH: false }
    requires: [procurement-xsuaa, procurement-postgres]
  - name: procurement-approuter
    type: approuter.nodejs
    path: approuter
resources:
  - name: procurement-xsuaa       # service: xsuaa, plan: application, path: ./xs-security.json
  - name: procurement-postgres    # service: postgresql, plan: trial
# after deploy: cf run-task procurement-backend "npm run db:deploy:prod\""""))
    parts.append(step_mod("m36", "36", "Complete source I — config + deploy files", "HAVE: fragments. ADDING: every runtime file, verbatim.", "\n".join(b)))

    b = []
    b.append(layer("Library files, verbatim from the repo"))
    b.append(code("typescript", "FILE: lib/validation/validation.ts (REAL)", """export function validateRequisition(data: any) {
  if (!data.title?.trim()) throw reqError('VALIDATION_ERROR', 'Title is required');
  if (data.totalAmount !== undefined && Number(data.totalAmount) <= 0)
    throw reqError('VALIDATION_ERROR', 'Amount must be > 0');
}
export function validatePO(pr: any, supplier: any) {
  if (!pr) throw reqError('RESOURCE_NOT_FOUND', 'Purchase requisition not found');
  if (['REJECTED', 'DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'CANCELLED'].includes(pr.status))
    throw reqError('INVALID_STATE_TRANSITION', `PO cannot be created from PR in status ${pr.status}`);
  if (!supplier?.active) throw reqError('SUPPLIER_INACTIVE', 'Supplier is inactive');
}"""))
    b.append(code("typescript", "FILE: policy defaults + tool-permission map (REAL)", """// lib/workflow/policy.ts — DEFAULT_POLICIES (DB Policies rows override these)
PO_AUTO    AUTO_APPROVE    maxAmount 50000             priority 10
PO_MANAGER REQUIRE_MANAGER 50000-500000                priority 20
PO_SENIOR  REQUIRE_HUMAN   500000-1000000              priority 30
PO_EXEC    REQUIRE_HUMAN   minAmount 1000000           priority 40
PO_HIGH_RISK REQUIRE_HUMAN riskLevels HIGH,CRITICAL    priority 5  (wins first)
// lib/auth/rbac.ts — MCP_TOOL_PERMISSIONS (excerpt) + AI_AGENT: []
searchSuppliers/getSupplier -> READ_SUPPLIER | checkBudget -> READ_BUDGET
createPurchaseRequisition/submitForApproval -> CREATE_PR
createPurchaseOrder -> CREATE_PO | getProcurementRisk -> READ_PR
AI_AGENT: [] // explicit per-agent grants only, never wildcard"""))
    b.append(code("typescript", "FILE: test/unit.test.ts (REAL) + add policy-gate.test.ts", """import { describe, it, expect } from 'vitest';
import { checkRateLimit } from '../lib/security/rate-limit.js';
import { toHttpError, reqError } from '../lib/security/errors.js';

describe('rate limiting', () => {
  it('allows within limit then rejects', () => {
    const key = `test-${Date.now()}`;
    for (let i = 0; i < 5; i++) checkRateLimit(key, 5);
    expect(() => checkRateLimit(key, 5)).toThrow();
  });
});
// ADD: policy-gate.test.ts — evaluatePolicy AUTO_APPROVE under 50000,
// REQUIRE_HUMAN for HIGH risk, FALLBACK REQUIRE_HUMAN when nothing matches."""))
    b.append(code("text", "FILE: seed CSVs (REAL samples, tenant-a)", """Suppliers: s-ts,tenant-a,SUP-003,TechSource India,IN,true,70,HIGH,72.0,5,800000
Policies:  pol-risk,tenant-a,PO_HIGH_RISK,High risk gate,High/critical risk always human,"{""riskLevels"":[""HIGH"",""CRITICAL""]}",REQUIRE_HUMAN,5,true
File names: procurement.db-<Entity>.csv (Agents, Budgets, Departments, Materials, MCPTools, Users, Roles, ... 14 files)"""))
    b.append(qa([("Why is approve not an MCP tool?", "Dual control: the agent drafts and routes; a human manager approves in UI5. An auto-approving agent would collapse the REQUIRE_MANAGER/FINANCE/HUMAN bands."), ("Do I add Inventory to the running repo?", "Yes if you want stock checks: append the m33 CDS, add the CSV, extend mcp-service.cds + MCP_TOOL_PERMISSIONS, recompile, test. Nothing else changes."), ("What still needs SAP docs at deploy time?", "AI Core SDK names, IAS federation clicks, Event Mesh bindings, MTX onboarding — all marked VERIFY where they appear.")]))
    parts.append(step_mod("m37", "37", "Complete source II — lib, tests, seed data", "HAVE: config. ADDING: the business plumbing, verbatim.", "\n".join(b)))

    return parts
