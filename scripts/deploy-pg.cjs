/**
 * Deploy schema + seed data to PostgreSQL.
 * Credentials come from default-env.json (VCAP_SERVICES, gitignored — never committed).
 * Usage: npm run db:deploy:pg
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
process.chdir(ROOT);

const cds = require('@sap/cds');

async function main() {
  const raw = fs.readFileSync(path.join(ROOT, 'default-env.json'), 'utf8');
  const vcaps = JSON.parse(raw).VCAP_SERVICES || {};
  const all = Object.values(vcaps).flat();
  const entry = all.find((e) => e && e.credentials && (e.credentials.dbname || e.credentials.database));
  if (!entry) throw new Error('No PostgreSQL entry with credentials found in default-env.json VCAP_SERVICES');
  const cr = entry.credentials;
  const credentials = {
    host: cr.hostname || cr.host,
    port: cr.port || 5432,
    database: cr.dbname || cr.database,
    user: cr.username || cr.user,
    password: cr.password,
    ssl: cr.ssl || { rejectUnauthorized: false },
  };
  for (const k of ['host', 'database', 'user', 'password']) {
    if (!credentials[k]) throw new Error(`PostgreSQL credential missing: ${k}`);
  }
  console.log(`Deploying to postgres://${credentials.host}:${credentials.port}/${credentials.database} as ${credentials.user}`);
  const db = await cds.connect.to({
    kind: 'postgres',
    credentials,
    pool: { min: 0, max: 5, testOnBorrow: true, acquireTimeoutMillis: 120000 },
  });
  await cds.deploy('./db', './srv').to(db);
  console.log('PostgreSQL deployment complete.');
  await cds.disconnect();
}

main().catch((e) => { console.error('DEPLOY FAILED:', e.message); process.exit(1); });
