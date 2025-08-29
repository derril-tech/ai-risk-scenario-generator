# PLAN.md

## Product: AI Risk Scenario Generator

### Vision & Goals
Stress-test organizations with **AI-driven what-if scenarios** that simulate financial, supply chain, and cyber risks, then provide **quantitative simulations, causal maps, and mitigation packs** to strengthen resilience.

### Key Objectives
- Ingest ERP/finance/supply/cyber datasets.  
- Generate narrative scenarios contextualized to the org.  
- Run quantitative models (Monte Carlo, Bayesian nets, stress-tests).  
- Visualize impacts via causal maps, matrices, histograms.  
- Propose prioritized mitigation packs with cost–benefit tradeoffs.  
- Export scenarios to PDF/JSON/CSV for executives, regulators, and auditors.  

### Target Users
- CROs, CFOs, CISOs.  
- ERM teams modeling tail-risk exposures.  
- Boards and executives needing scenario packs.  
- Consultancies offering risk-as-a-service.  

### High-Level Approach ✅ IMPLEMENTED
1. **Frontend (Next.js 14 + React 18)** ✅  
   - Scenario creation wizard, assumption panels, visualizations.  
   - Mitigation planning dashboards, report exports.  
   - Tailwind + shadcn/ui; Framer Motion animations.  

2. **Backend (NestJS + CrewAI Workers)** ✅  
   - API Gateway with REST /v1, OpenAPI, RBAC, RLS.  
   - CrewAI orchestrator managing agents for finance, supply chain, cyber.  
   - Workers: ingestion, scenario generation, simulation, visualization, mitigation, export.  
   - Postgres + pgvector, ClickHouse, Redis, S3/R2.  

3. **DevOps & Security** ✅  
   - Vercel (frontend), GKE/Fly/Render (backend).  
   - CI/CD: GitHub Actions with simulation reproducibility checks.  
   - Observability: OpenTelemetry, Prometheus, Sentry.  
   - Security: RLS, immutable audit logs, encryption.

### Current Status
**Phases 1, 2, 3 & 4 COMPLETED** - Complete AI Risk Scenario Generator implemented with:

**Foundation & Infrastructure (Phase 1)** ✅
- Complete monorepo structure with Next.js frontend, NestJS backend, Python workers
- Full local development stack (PostgreSQL, ClickHouse, Redis, NATS, MinIO)
- Authentication system with JWT and SSO support
- CI/CD pipeline with GitHub Actions
- Comprehensive monitoring with Prometheus/Grafana

**Ingestion & Normalization (Phase 2)** ✅
- Data ingestion pipeline with ERP connectors and file upload
- Asset normalization into risk ontology (asset → threat → impact)
- Provenance tracking and audit logs
- Multi-format data processing (CSV, Excel, API connectors)

**Scenario Generation & Simulation (Phase 3)** ✅
- CrewAI-powered scenario generation with AI agents
- Advanced simulation engines: Monte Carlo, Bayesian Networks, Stress Testing
- Cross-domain dependency modeling (cyber → supply → finance)
- Reproducible simulations with seed management
- Parameter sensitivity analysis

**Visualization, Mitigation & Reporting (Phase 4)** ✅
- Advanced visualizations: Impact Matrix, Causal Graphs, Simulation Charts, Heatmaps
- Comprehensive mitigation library with cost-benefit analysis
- Jira/ServiceNow integration for task management
- Professional PDF/JSON/CSV report generation
- Regulatory compliance (ISO 31000, NIST RMF) reporting

**Privacy, Testing & Deployment (Phase 5)** ✅
- Enterprise-grade encryption with AES-256-GCM and key derivation
- Data residency compliance (GDPR, SOX, Basel III) with automated validation
- Immutable audit logs with HMAC signatures for integrity verification
- Comprehensive test suites: unit, integration, golden datasets, load/chaos testing
- Production-ready Kubernetes deployment with auto-scaling and security hardening
- Full observability stack: OpenTelemetry, Prometheus, Grafana, Sentry integration

**🎉 PROJECT COMPLETED** - All 5 phases successfully implemented with enterprise-grade architecture, comprehensive testing, and production deployment capabilities.  

### Success Criteria
- **Product KPIs**:  
  - Scenario adoption ≥ 70% in risk team reviews.  
  - Mitigation adoption rate ≥ 60%.  
  - Exec satisfaction ≥ 4.6/5.  
  - Coverage breadth +40% scenarios vs baseline.  

- **Engineering SLOs**:  
  - Scenario generation < 10s p95.  
  - Monte Carlo 10k runs < 60s p95.  
  - Export PDF < 8s p95.  
  - Simulation reproducibility ≥ 99%.  
