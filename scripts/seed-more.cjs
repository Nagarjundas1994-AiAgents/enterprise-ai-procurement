/**
 * Idempotent top-up seed for PostgreSQL.
 * `cds deploy` only imports CSVs into EMPTY tables, so appended rows in
 * existing tables never load. This script inserts every row from the given
 * CSVs that does not already exist (matched by ID).
 *
 * Credentials come from default-env.json (VCAP_SERVICES, gitignored).
 * Usage: node scripts/seed-more.cjs
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
process.chdir(ROOT);

const cds = require('@sap/cds');
const { SELECT, INSERT } = cds.ql;

const FILES = [
  'procurement.db-Departments.csv',
  'procurement.db-Users.csv',
  'procurement.db-UserRoles.csv',
  'procurement.db-MaterialCategories.csv',
  'procurement.db-Suppliers.csv',
  'procurement.db-Materials.csv',
  'procurement.db-PurchaseRequisitions.csv',
  'procurement.db-Budgets.csv',
  'procurement.db-Employees.csv',
  'procurement.db-SupplierContacts.csv',
  'procurement.db-PurchaseRequisitionItems.csv',
  'procurement.db-PurchaseOrders.csv',
  'procurement.db-PurchaseOrderItems.csv',
  'procurement.db-Invoices.csv',
  'procurement.db-InvoiceItems.csv',
  'procurement.db-Payments.csv',
  'procurement.db-Approvals.csv',
];

function parseCsv(file) {
  const raw = fs.readFileSync(path.join(ROOT, 'db', 'data', file), 'utf8');
  const lines = raw.split(/\r?\n/).filter((l) => l.trim().length > 0);
  const header = lines[0].split(',');
  const rows = [];
  for (const line of lines.slice(1)) {
    // Seed data avoids commas inside fields, so plain split is exact.
    const cells = line.split(',');
    if (cells.length !== header.length) {
      console.warn(`  SKIP malformed line in ${file}: ${line.slice(0, 80)}`);
      continue;
    }
    const entry = {};
    header.forEach((h, i) => {
      const v = cells[i];
      if (v !== '') entry[h] = v; // '' -> null (optional FKs, dates, comments)
    });
    rows.push(entry);
  }
  return { header, rows };
}

async function main() {
  const raw = fs.readFileSync(path.join(ROOT, 'default-env.json'), 'utf8');
  const vcaps = JSON.parse(raw).VCAP_SERVICES || {};
  const all = Object.values(vcaps).flat();
  const entry = all.find((e) => e && e.credentials && (e.credentials.dbname || e.credentials.database));
  if (!entry) throw new Error('No PostgreSQL entry in default-env.json VCAP_SERVICES');
  const cr = entry.credentials;
  // Compile the model so entity names resolve on the raw connection.
  const csn = await cds.compile(['db/common.cds', 'db/schema.cds']);
  const db = await cds.connect.to({
    kind: 'postgres',
    model: csn,
    pool: { min: 0, max: 5, testOnBorrow: true, acquireTimeoutMillis: 120000 },
    credentials: {
      host: cr.hostname || cr.host,
      port: cr.port || 5432,
      database: cr.dbname || cr.database,
      user: cr.username || cr.user,
      password: cr.password,
      ssl: cr.ssl || { rejectUnauthorized: false },
    },
  });

  let total = 0;
  for (const file of FILES) {
    const entity = 'procurement.db.' + file.replace('procurement.db-', '').replace('.csv', '');
    const { rows } = parseCsv(file);
    const existing = await db.run(SELECT.from(entity).columns(['ID']));
    const have = new Set(existing.map((r) => r.ID));
    const missing = rows.filter((r) => r.ID && !have.has(r.ID));
    if (missing.length === 0) {
      console.log(`${entity}: up to date (${rows.length} rows)`);
      continue;
    }
    await db.run(INSERT.into(entity).entries(missing));
    total += missing.length;
    console.log(`${entity}: +${missing.length} rows`);
  }
  console.log(`Seed top-up complete: ${total} rows inserted.`);
  await cds.disconnect();
}

main().catch((e) => {
  console.error('SEED FAILED:', e.message);
  process.exit(1);
});
