# ARCH.md

## System Architecture — AI Risk Scenario Generator

### High-Level Diagram
```
Frontend (Next.js 14 + React 18)
   | REST / SSE
   v
API Gateway (NestJS)
   | NATS / gRPC
   v
CrewAI Orchestrator (Python + FastAPI)
   |-> ingest-worker (connectors, normalization)
   |-> scenario-worker (narratives, assumptions)
   |-> sim-worker (Monte Carlo, Bayesian, stress-tests)
   |-> viz-worker (graphs, matrices, histograms)
   |-> mitigation-worker (options, cost/benefit)
   |-> export-worker (PDF/JSON/CSV)
   |
   +-- Postgres (pgvector: assets/scenarios/sims/mitigations)
   +-- ClickHouse (financial/supply logs)
   +-- Redis (sessions, cache, jobs)
   +-- S3/R2 (exports)
```

### Frontend (Next.js + React)
- **ScenarioWizard**: assumptions entry + preview narrative.  
- **SimChart**: Monte Carlo curves.  
- **ImpactMatrix**: likelihood × severity.  
- **CausalGraph**: dependency chains.  
- **MitigationTable**: options, costs, benefits.  
- **ReportWizard**: PDF/CSV/JSON outputs.  
- **UI**: Tailwind + shadcn/ui, Framer Motion.  

### Backend (NestJS)
- REST /v1 with OpenAPI 3.1.  
- Casbin RBAC, RLS by org_id.  
- Idempotency-Key, Problem+JSON errors.  
- SSE for scenario runs and sims.  

### Workers (Python + FastAPI)
- **ingest-worker**: ERP/finance/supply/cyber connectors.  
- **scenario-worker**: narrative + assumptions with CrewAI agents.  
- **sim-worker**: Monte Carlo/Bayesian/stress tests.  
- **viz-worker**: diagrams and matrices.  
- **mitigation-worker**: mitigation planning + CBA.  
- **export-worker**: board-ready reports and exports.  

### Eventing
- **NATS Topics**: `data.ingest`, `scenario.gen`, `sim.run`, `viz.make`, `mitigation.plan`, `export.make`.  
- **Redis Streams**: progress updates, SSE.  

### Data Layer
- **Postgres 16 + pgvector**: assets, scenarios, sims, mitigations, exports.  
- **ClickHouse**: ERP/supply/finance/cyber logs.  
- **Redis**: caching, jobs, sessions.  
- **S3/R2**: scenario exports.  
- **Encryption**: Cloud KMS per tenant, immutable audit logs.  

### Observability & Security
- **Tracing**: OpenTelemetry.  
- **Metrics**: Prometheus + Grafana.  
- **Errors**: Sentry.  
- **Security**: MFA/SSO, SCIM, RLS, audit provenance.  

### DevOps & Deployment
- **Frontend**: Vercel.  
- **Backend**: GKE/Fly/Render with autoscaling pools.  
- **CI/CD**: GitHub Actions (lint, tests, reproducibility, deploy).  
- **Data**: PITR backups, retention policies.  
