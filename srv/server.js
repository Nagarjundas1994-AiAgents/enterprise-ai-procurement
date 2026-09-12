import dotenv from 'dotenv';
dotenv.config(); // local .env (gitignored): PORT, CDS_ENV, JWT_SECRET, ALLOW_MOCK_AUTH

import cds from '@sap/cds';

// Enable TypeScript service handlers (.ts impl resolution in cds lib/srv/factory.js).
// Node 22.6+ strips erasable TS natively, so no transpiler is needed at runtime.
process.env.CDS_TYPESCRIPT ??= 'true';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

// Health / readiness / REST bootstrap. Business logic stays in CAP services.
cds.on('bootstrap', (app) => {
  app.use(helmet());
  // The @cap-js/agents preview chat (GET /a2a/<svc>/preview/) ships an inline
  // <script> that drives Send/message rendering. Helmet's default CSP
  // (script-src 'self') silently kills it: page skeleton renders but Send is
  // dead and no messages ever appear. Relax scripts ONLY under /a2a (dev-time
  // chat UI + JSON-RPC); the rest of the app keeps the strict default.
  // Must be registered AFTER helmet so it overwrites the header.
  app.use('/a2a', (_req, res, next) => {
    res.setHeader(
      'Content-Security-Policy',
      "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https:; img-src 'self' data:; font-src 'self' https: data:; connect-src 'self'; form-action 'self'; frame-ancestors 'self'; object-src 'none'",
    );
    next();
  });
  // Global safety net against runaway clients/agents (per-tool limits live in lib/security/rate-limit.ts).
  app.use(
    rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 600,
      standardHeaders: 'draft-7',
      legacyHeaders: false,
    }),
  );
  const checkDb = async () => {
    try { await cds.db?.run('SELECT 1'); return true; } catch { return false; }
  };
  app.get('/liveness', (_req, res) => res.json({ status: 'alive' }));
  app.get('/readiness', async (_req, res) => {
    const db = await checkDb();
    res.status(db ? 200 : 503).json({ ready: db, db, time: new Date().toISOString() });
  });
  // A2A discovery (JSON-RPC transport mounted by @cap-js/agents when configured;
  // this static card keeps Joule/A2A clients working even without AI Core keys).
  app.get('/.well-known/agent.json', (_req, res) => res.json({
    name: 'enterprise-ai-procurement-orchestrator',
    protocol: 'A2A/0.2', version: '1.0.0',
    skills: ['procurement', 'approval', 'supplier-risk', 'invoice-matching', 'budget-check', 'audit'],
    endpoints: { rpc: '/odata/v4/agents/orchestrate', mcp: '/mcp' },
  }));
});

export default cds.server;
