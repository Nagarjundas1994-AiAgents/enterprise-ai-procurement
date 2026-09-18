# ProcureChat Frontend (Next.js)

Beautiful dark + gold UI for the enterprise-ai-procurement CAP backend:
command center with KPIs, requisition/order/supplier worklist with row
actions (budget check, submit, Ask AI), and a live DeepSeek chat assistant.

## Run

Terminal 1 — backend (from repo root):

```bash
npm start          # CAP on http://localhost:4004
```

Terminal 2 — frontend (from `frontend/`):

```bash
npm install
npm run dev        # Next.js on http://localhost:3000
```

Open http://localhost:3000. Pick a demo user (Admin has full access);
Employee/Approver/Auditor demonstrate RBAC denials.

## How it connects

`next.config.js` rewrites `/backend/:path*` to the CAP backend
(`CAP_BACKEND_URL`, default `http://localhost:4004`). Same-origin for the
browser (no CORS); the `x-mock-user` header is forwarded as-is for local
mock auth. In BTP the approuter injects the real user instead.
