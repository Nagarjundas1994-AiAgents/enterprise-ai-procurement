"""Part 4: CH17-CH18."""
from common import code, table, grid, steps, qa, quiz, mermaid, callout
from mx import ch, PWR, PREV, neg, std_test, done


def build():
    parts = []

    parts.append(ch("c17", "17", "Chapter 17 — PostgreSQL Local Database", "", {
        "What are we learning?": "<p><b>Simple:</b> swap the toy database for real Postgres in Docker. <b>Enterprise:</b> production-like semantics (types, constraints, concurrency) on your laptop. <b>Example:</b> rehearsing in the actual theater, not your garage.</p>",
        "Why is this important?": "<p>SQLite hides locking and type bugs that explode on HANA. Postgres surfaces them early and cheaply.</p>",
        "Where does this fit in the architecture?": "<p>Replaces the DB box locally; CDS and handlers stay byte-identical.</p>",
        "Prerequisites": "<p>Docker from Chapter 00. Previous chapters done (SQLite).</p>",
        "Folder/file changes": "<p>NEW <code>docker-compose.yml</code> + <code>.env</code> (gitignored) + <code>.env.example</code> (committed).</p>",
        "Exact commands": PWR + code("powershell", "Up + deploy + run (project root)", "docker compose up -d db\nCopy-Item .env.example .env\n# edit .env: DB_PASSWORD=changeme (dev only)\nnpm run db:deploy:pg   # deploys schema + seed CSVs\nnpm start"),
        "Complete code": code("yaml", "FILE: docker-compose.yml (COMPLETE)", """services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: assetops
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: changeme
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10
  app:
    build: .
    depends_on: { db: { condition: service_healthy } }
    environment:
      PORT: 4004
      DATABASE_URL: postgresql://postgres:changeme@db:5432/assetops
      ALLOW_MOCK_AUTH: "true"
    ports: ["4004:4004"]
volumes: { pgdata: {} }""") + code("text", "FILE: .env.example (COMPLETE, commit this — never .env)", """PORT=4004
DB_HOST=localhost
DB_PORT=5432
DB_NAME=assetops
DB_USER=postgres
DB_PASSWORD=changeme
DATABASE_URL=
JWT_SECRET=dev-only-secret-change-me
ALLOW_MOCK_AUTH=true
AI_API_URL=
AI_API_KEY=
AI_MODEL=claude-sonnet
AI_PROVIDER=mock"""),
        "Explanation of every important line": table(["Line", "Meaning"], [["healthcheck pg_isready", "App starts only after DB accepts connections"], ["DATABASE_URL", "Single connection string; individual DB_* vars are the fallback"], ["ALLOW_MOCK_AUTH", "LEARNING-MOCK APPROACH — forced false on BTP (Chapter 77)"], [".env gitignored", "Secrets never committed (Chapter 71 enforces in CI)"]]),
        "Expected output": "<p><code>docker compose ps</code> shows db healthy; OData alerts query returns ALT-9001 from Postgres.</p>",
        "How to test it": std_test("stop Docker, restart, re-query — data persists via pgdata volume."),
        "Negative test cases": neg([["DB container stopped", "npm start + GET", "503 readiness — start db first"], [".env committed", "git status", "Must never appear — check .gitignore (Chapter 71)"]]),
        "Common mistakes": "<p>Port 5432 already used by a local Postgres — change the host port mapping.</p>",
        "How to troubleshoot": "<p><code>docker logs &lt;db-container&gt;</code> for auth errors; <code>pg_isready -h localhost</code> for connectivity.</p>",
        "Production considerations": "<p>Same major Postgres version locally as the managed hyperscaler Postgres (Chapter 75) — types behave identically.</p>",
        "Security considerations": "<p><code>changeme</code> is DEV-ONLY. CI fails the build if <code>changeme</code> appears in prod config (Chapter 72).</p>",
        "What we have completed": done("Real local database." + mermaid('FIG. 8 - SAME CDS, THREE ENGINES', 'flowchart LR; CDS[CDS model]-->SQLITE[SQLite tests]; CDS-->PG[Postgres local]; CDS-->HANA[HANA Cloud prod]'), "Chapter 18: HANA Cloud for DEV/STAGING/PROD."),
    }))

    parts.append(ch("c18", "18", "Chapter 18 — SAP HANA Cloud", "", {
        "What are we learning?": "<p><b>Simple:</b> SAP's cloud database where production data lives. <b>Enterprise:</b> HANA Cloud instance + service binding + schema deploy + indexes. <b>Example:</b> moving from rehearsal theater to the opera house — same play, stricter stage.</p>",
        "Why is this important?": "<p>LOCAL Postgres, DEV/STAGING/PROD HANA must be tested carefully — type, locking and pooling differences bite at 2am.</p>",
        "Where does this fit in the architecture?": "<p>The HANA CLOUD box: CAP connects via service binding, never hardcoded credentials.</p>",
        "Prerequisites": PREV + "<p>BTP subaccount with HANA Cloud entitlement (Chapters 73-75 create it).</p>",
        "Folder/file changes": "<p>EDIT <code>mta.yaml</code> (HANA module — full file in Chapter 74). No CDS changes.</p>",
        "Exact commands": "<p>BTP CLI (Chapters 73-76 run these):</p>" + code("powershell", "HANA wiring (BTP, after Chapter 75)", "cf create-service hana hdi-shared assetops-hana   # plan names vary: VERIFY vs current catalog\ncf bind-service maintenance-backend assetops-hana\ncf restage maintenance-backend\ncf run-task maintenance-backend \"npm run db:deploy:prod\"  # schema only, data untouched"),
        "Complete code": table(["Concern", "CURRENT SAP APPROACH"], [["Schema", "HDI deployer via mta hdb module — migrations, never drops"], ["Indexes", "Composite (equipment_ID, measuredAt desc) on readings; (status, severity) on alerts"], ["Constraints", "@assert.unique becomes real unique constraints — duplicates fail loudly"], ["Pooling", "CAP pool min 0 max 5 local; BTP-sized pool via binding (Chapter 76)"], ["Concurrency", "forUpdate row locks + version checks behave identically to Postgres (Chapter 14)"]]),
        "Explanation of every important line": "<p>Service binding injects credentials into <code>VCAP_SERVICES</code> — the app reads them, never stores them. <code>run-task</code> deploys schema without touching production rows.</p>",
        "Expected output": "<p>BTP app binds to HANA; <code>/readiness</code> reports db true; seed absent in prod (correct).</p>",
        "How to test it": std_test("Stage the Chapter 89 scenario against DEV HANA with fixture data loaded by script, not seed."),
        "Negative test cases": neg([["Deploy to prod with seed CSVs", "review", "Rejected — seed is DEV/TEST only (Chapter 09)"], ["Destructive column drop", "migration review", "Rejected without backup + rollback plan (Chapter 87)"]]),
        "Common mistakes": "<p>Assuming SQLite-tested locking works on HANA — re-run Chapter 63 integration tests against HANA.</p>",
        "How to troubleshoot": "<p>HDI deploy errors name the failed object — fix CDS, rebuild MTA, redeploy (Chapter 86 matrix).</p>",
        "Production considerations": "<p>Backup/recovery plan reviewed BEFORE first prod deploy (Chapter 82 gate). Connection pool sized from load tests.</p>",
        "Security considerations": "<p>HANA users follow least privilege: the app schema user cannot drop schemas or read other tenants (Chapter 60).</p>",
        "What we have completed": done("Prod-grade persistence story.", "STOP: backend complete. Chapter 19 builds the human face."),
    }))

    return parts
