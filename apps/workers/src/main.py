"""
AI Risk Scenario Generator Workers
FastAPI application for orchestrating CrewAI workers
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from prometheus_client import make_asgi_app

from .config import settings
from .routers import ingestion, scenarios, simulations, reports, visualizations, mitigations
from .core.database import init_db
from .core.messaging import init_messaging


logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Risk Workers...")
    await init_db()
    await init_messaging()
    logger.info("Workers started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Risk Workers...")


app = FastAPI(
    title="AI Risk Workers",
    description="CrewAI workers for AI Risk Scenario Generator",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion.router, prefix="/api/v1/ingestion", tags=["Ingestion"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["Scenarios"])
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["Simulations"])
app.include_router(visualizations.router, prefix="/api/v1/visualizations", tags=["Visualizations"])
app.include_router(mitigations.router, prefix="/api/v1/mitigations", tags=["Mitigations"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-risk-workers"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Risk Scenario Generator Workers",
        "version": "0.1.0",
        "docs": "/docs"
    }
