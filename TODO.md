# TODO.md

## Development Roadmap

### Phase 1: Foundations & Infrastructure ✅ COMPLETED
- [x] Initialize monorepo (frontend, backend, workers).  
- [x] Next.js 14 app with Tailwind + shadcn/ui; SSR for dashboards.  
- [x] NestJS API Gateway (REST /v1, OpenAPI, RBAC, RLS).  
- [x] Local stack: Postgres + pgvector, ClickHouse, Redis, NATS, S3 (MinIO).  
- [x] Auth: SSO (SAML/OIDC), MFA, SCIM provisioning.  
- [x] CI/CD: GitHub Actions (lint, tests, reproducibility checks, deploy).  

### Phase 2: Ingestion & Normalization ✅ COMPLETED
- [x] Ingest-worker: connectors for ERP (SAP/Oracle), Finance (NetSuite), Supply chain (Coupa), Cyber (SIEMs/EDRs), public feeds.  
- [x] Static uploads (CSV, XLSX, PDF).  
- [x] Normalize into ontology: asset → threat → impact.  
- [x] Store in Postgres/ClickHouse; embed assets with pgvector.  
- [x] Provenance tracking + audit logs.  

### Phase 3: Scenario Generation & Simulation ✅ COMPLETED
- [x] Scenario-worker: generate narratives via CrewAI agents.  
- [x] Quant modeling: Monte Carlo, Bayesian nets, stress-test curves.  
- [x] Dependencies: link cross-domain events (cyber → supply → finance).  
- [x] Assumptions panel for explicit drivers.  
- [x] Sim-worker: reproducible results with seed + params stored.  

### Phase 4: Visualization, Mitigation & Reporting ✅ COMPLETED
- [x] Viz-worker: generate ImpactMatrix, CausalGraph, SimChart, heatmaps.  
- [x] Mitigation-worker: rank cost/benefit options.  
- [x] Push mitigation tasks to Jira/ServiceNow.  
- [x] ReportWizard: export PDF deck, JSON sims, CSV assumptions.  
- [x] Governance: SLA tracking, regulator packs (ISO 31000, NIST RMF).  

### Phase 5: Privacy, Testing & Deployment ✅ COMPLETED
- [x] Privacy: encryption, residency enforcement, immutable audit logs.  
- [x] Unit tests: FX shock math, supplier outage, cyber DDoS curves.  
- [x] Integration tests: ingest → scenario → sim → viz → export.  
- [x] Golden sets (2008 FX, 2021 chip shortage, WannaCry).  
- [x] Load/chaos: 1k concurrent scenarios, large ERP feeds.  
- [x] Deploy: Vercel (frontend), GKE/Fly/Render (backend).  
- [x] Observability: OpenTelemetry, Prometheus, Grafana, Sentry.  
