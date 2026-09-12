// Remote agents — tiny standalone Express + A2A (JSON-RPC) server hosting TWO agents.
// Each agent owns its OWN data that the main CAP app does NOT have.
// Main app calls them via the standard A2A protocol:
//
//   Supplier agent:
//     GET  /.well-known/agent-card.json   -> discovery card
//     POST /                              -> JSON-RPC 2.0 { method: "message/send", ... }
//   Logistics agent (NEW, same server):
//     GET  /logistics/.well-known/agent-card.json (also /.well-known/logistics-agent-card.json)
//     POST /logistics/                    -> JSON-RPC 2.0 { method: "message/send", ... }
//
// Run:  npm run remote-agent   (serves http://localhost:4007)
// Env:  REMOTE_AGENT_PORT (default 4007)

import express from 'express';

// ---------------------------------------------------------------------------
// The remote server's OWN data. Deliberately richer than the CAP seed data:
// live availability + lead times + MOQs live here, not in PostgreSQL.
// supplierCode maps to the main app's Suppliers.supplierId (SUP-001..004).
// ---------------------------------------------------------------------------
const SUPPLIER_NETWORK = [
  { supplierCode: 'SUP-001', name: 'ABC Industrial Supplies', country: 'IN', active: true, availability: 'IN_STOCK', leadTimeDays: 3, moq: 5, currency: 'INR', unitPriceHint: 85000, rating: 4.8 },
  { supplierCode: 'SUP-002', name: 'Global Components', country: 'IN', active: true, availability: 'LIMITED', leadTimeDays: 12, moq: 10, currency: 'INR', unitPriceHint: 62000, rating: 4.1 },
  { supplierCode: 'SUP-003', name: 'TechSource India', country: 'IN', active: true, availability: 'BACKORDER', leadTimeDays: 30, moq: 2, currency: 'INR', unitPriceHint: 54000, rating: 3.2 },
  { supplierCode: 'SUP-004', name: 'Prime Logistics', country: 'IN', active: true, availability: 'IN_STOCK', leadTimeDays: 5, moq: 1, currency: 'INR', unitPriceHint: 41000, rating: 4.9 },
];

const tasks = new Map(); // taskId -> task (for tasks/get)
const randomId = () => `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;

function answerQuery(rawText) {
  const text = String(rawText ?? '').toLowerCase();
  // "quote SUP-002 qty 15" -> line total hint (check before plain code lookup)
  const quote = text.match(/quote\s+(sup-00[1-4])\s+qty\s+(\d+)/);
  if (quote) {
    const s = SUPPLIER_NETWORK.find((x) => x.supplierCode === quote[1].toUpperCase());
    const qty = Number(quote[2]);
    const bulkDiscount = qty >= s.moq * 5 ? 0.95 : 1;
    return {
      query: `quote ${s.supplierCode} x${qty}`, count: 1,
      suppliers: [{ ...s, quotedQty: qty, lineTotalHint: Math.round(s.unitPriceHint * qty * bulkDiscount) }],
      source: 'remote-supplier-network',
    };
  }
  // Direct code lookup: "SUP-001"
  const codeHit = (text.match(/sup-00[1-4]/) || [])[0]?.toUpperCase();
  if (codeHit) {
    const s = SUPPLIER_NETWORK.find((x) => x.supplierCode === codeHit);
    return { query: codeHit, count: 1, suppliers: [s], source: 'remote-supplier-network' };
  }
  // Name fragment search, or "list"/"all" -> everything
  const hits = SUPPLIER_NETWORK.filter((s) => text.includes('list') || text.includes('all') || s.name.toLowerCase().includes(text) || text.split(/\s+/).some((w) => w.length > 3 && s.name.toLowerCase().includes(w)));
  return { query: String(rawText ?? '').slice(0, 120), count: hits.length, suppliers: hits, source: 'remote-supplier-network' };
}

// ---------------------------------------------------------------------------
// SECOND agent: remote logistics network (shipment tracking + freight hints).
// Completely different data domain from the supplier network above.
// shipmentId is the lookup key (SHP-101..104).
// ---------------------------------------------------------------------------
const LOGISTICS_NETWORK = [
  { shipmentId: 'SHP-101', lane: 'Mumbai -> Bangalore', carrier: 'Prime Logistics', mode: 'ROAD', status: 'IN_TRANSIT', etaDays: 2, freightHint: 18000, currency: 'INR' },
  { shipmentId: 'SHP-102', lane: 'Chennai -> Delhi', carrier: 'Global Freightways', mode: 'RAIL', status: 'CUSTOMS_HOLD', etaDays: 7, freightHint: 42000, currency: 'INR' },
  { shipmentId: 'SHP-103', lane: 'Mumbai -> Pune', carrier: 'ABC Industrial', mode: 'ROAD', status: 'DELIVERED', etaDays: 0, freightHint: 9000, currency: 'INR' },
  { shipmentId: 'SHP-104', lane: 'Kolkata -> Mumbai', carrier: 'TechSource Lines', mode: 'SEA', status: 'BOOKED', etaDays: 5, freightHint: 31000, currency: 'INR' },
];

function answerLogisticsQuery(rawText) {
  const text = String(rawText ?? '').toLowerCase();
  // "quote SHP-102 weight 500" -> freight estimate (check before plain id lookup)
  const quote = text.match(/quote\s+(shp-10[1-4])\s+weight\s+(\d+)/);
  if (quote) {
    const s = LOGISTICS_NETWORK.find((x) => x.shipmentId === quote[1].toUpperCase());
    const weightKg = Number(quote[2]);
    return {
      query: `quote ${s.shipmentId} ${weightKg}kg`, count: 1,
      shipments: [{ ...s, quotedWeightKg: weightKg, freightTotalHint: Math.round(s.freightHint * Math.max(1, weightKg / 100)) }],
      source: 'remote-logistics-network',
    };
  }
  // Direct id lookup: "SHP-101" or "track SHP-101"
  const idHit = (text.match(/shp-10[1-4]/) || [])[0]?.toUpperCase();
  if (idHit) {
    const s = LOGISTICS_NETWORK.find((x) => x.shipmentId === idHit);
    return { query: idHit, count: 1, shipments: [s], source: 'remote-logistics-network' };
  }
  // Status / lane / carrier fragment search, or "list"/"all" -> everything
  const hits = LOGISTICS_NETWORK.filter((s) =>
    text.includes('list') || text.includes('all') || text.includes('shipment')
    || s.status.toLowerCase().includes(text) || s.lane.toLowerCase().includes(text) || s.carrier.toLowerCase().includes(text)
    || text.split(/\s+/).some((w) => w.length > 3 && (s.lane.toLowerCase().includes(w) || s.carrier.toLowerCase().includes(w))));
  return { query: String(rawText ?? '').slice(0, 120), count: hits.length, shipments: hits, source: 'remote-logistics-network' };
}

function extractText(params) {
  // Official A2A shape: params.message.parts[].{kind:"text",text}
  // Accept legacy {message:{content}} / {text} / raw string too.
  const m = params?.message ?? params;
  if (typeof m === 'string') return m;
  if (typeof params?.text === 'string') return params.text;
  if (typeof m?.content === 'string') return m.content;
  if (Array.isArray(m?.parts)) return m.parts.filter((p) => p?.kind === 'text' && typeof p.text === 'string').map((p) => p.text).join('\n');
  return '';
}

function taskResult(id, data, artifactName = 'supplier-network-result') {
  const task = {
    kind: 'task', id: randomId(), contextId: randomId(),
    status: { state: 'completed' },
    artifacts: [{ artifactId: randomId(), name: artifactName, parts: [{ kind: 'text', text: JSON.stringify(data) }] }],
  };
  tasks.set(task.id, task);
  return { jsonrpc: '2.0', id, result: task };
}

function handleRpc(answerFn, artifactName) {
  return (req, res) => {
    const { method, params, id } = req.body ?? {};
    try {
      if (method === 'message/send') {
        const data = answerFn(extractText(params));
        return res.json(taskResult(id ?? 1, data, artifactName));
      }
      if (method === 'tasks/get') {
        const task = tasks.get(params?.id);
        if (!task) return res.json({ jsonrpc: '2.0', id: id ?? 1, error: { code: -32002, message: 'Task not found' } });
        return res.json({ jsonrpc: '2.0', id: id ?? 1, result: task });
      }
      return res.json({ jsonrpc: '2.0', id: id ?? 1, error: { code: -32601, message: `Method not found: ${method}` } });
    } catch (e) {
      return res.json({ jsonrpc: '2.0', id: id ?? 1, error: { code: -32603, message: String(e?.message || e) } });
    }
  };
}

const PORT = Number(process.env.REMOTE_AGENT_PORT || 4007);
const app = express();
app.use(express.json({ limit: '256kb' }));

const agentCard = {
  name: 'remote-supplier-agent',
  description: 'External supplier-network agent: live availability, lead times, MOQs and quote hints for SUP-001..SUP-004.',
  version: '1.0.0',
  protocolVersion: '0.3',
  url: `http://localhost:${PORT}/`,
  capabilities: { streaming: false, pushNotifications: false },
  defaultInputModes: ['text'],
  defaultOutputModes: ['text'],
  skills: [
    { id: 'supplier-lookup', name: 'Supplier lookup', description: 'Get live availability/lead-time/MOQ for a supplier code (e.g. "supplier SUP-001").', tags: ['supplier', 'availability'], examples: ['supplier SUP-001', 'quote SUP-002 qty 15'] },
    { id: 'supplier-search', name: 'Supplier search', description: 'Search the network by name fragment, or "list suppliers" for all.', tags: ['supplier', 'search'], examples: ['list suppliers', 'TechSource'] },
  ],
};

const logisticsCard = {
  name: 'remote-logistics-agent',
  description: 'External logistics agent: live shipment tracking, ETAs and freight hints for SHP-101..SHP-104.',
  version: '1.0.0',
  protocolVersion: '0.3',
  url: `http://localhost:${PORT}/logistics/`,
  capabilities: { streaming: false, pushNotifications: false },
  defaultInputModes: ['text'],
  defaultOutputModes: ['text'],
  skills: [
    { id: 'shipment-track', name: 'Shipment tracking', description: 'Get live status/ETA for a shipment id (e.g. "track SHP-102").', tags: ['shipment', 'tracking'], examples: ['track SHP-102', 'list shipments'] },
    { id: 'freight-quote', name: 'Freight quote', description: 'Estimate freight for a shipment + weight in kg (e.g. "quote SHP-101 weight 500").', tags: ['freight', 'quote'], examples: ['quote SHP-101 weight 500', 'quote SHP-104 weight 1200'] },
  ],
};

app.get('/health', (_req, res) => res.json({ status: 'UP', agents: [agentCard.name, logisticsCard.name] }));
app.get('/.well-known/agent-card.json', (_req, res) => res.json(agentCard));
app.get('/.well-known/agent.json', (_req, res) => res.json(agentCard)); // alias for older clients
// Logistics discovery: path-scoped card (for base http://host:PORT/logistics)
// plus a global alias so both agents are discoverable from root.
app.get('/logistics/.well-known/agent-card.json', (_req, res) => res.json(logisticsCard));
app.get('/logistics/agent-card.json', (_req, res) => res.json(logisticsCard));
app.get('/.well-known/logistics-agent-card.json', (_req, res) => res.json(logisticsCard));

// A2A JSON-RPC endpoints: root = supplier agent, /logistics = logistics agent.
app.post('/', handleRpc(answerQuery, 'supplier-network-result'));
app.post(['/logistics', '/logistics/'], handleRpc(answerLogisticsQuery, 'logistics-network-result'));

const server = app.listen(PORT, () => console.log(`[remote-agents] A2A serving supplier http://localhost:${PORT} + logistics http://localhost:${PORT}/logistics/`));
server.on('error', (err) => {
  if (err?.code === 'EADDRINUSE') {
    console.error(`[remote-supplier-agent] Port ${PORT} already in use. Another instance is already running (http://localhost:${PORT}/health), or kill it: Get-NetTCPConnection -LocalPort ${PORT} | Select-Object OwningProcess; Stop-Process -Id <pid> -Force. Or use another port: REMOTE_AGENT_PORT=4008 npm run remote-agent`);
    process.exit(1);
  }
  throw err;
});
