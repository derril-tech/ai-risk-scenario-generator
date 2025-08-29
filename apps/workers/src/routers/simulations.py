"""Advanced simulation router"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog

from ..services.simulation_service import SimulationService
from ..models.simulation import (
    SimulationRequest, SimulationResponse, MonteCarloConfig,
    BayesianNetworkConfig, StressTestConfig
)

logger = structlog.get_logger()
router = APIRouter()
simulation_service = SimulationService()


class RunSimulationRequest(BaseModel):
    scenario_id: str
    method: str = "monte_carlo"  # monte_carlo, bayesian_network, stress_test
    runs: int = 10000
    seed: Optional[int] = None
    monte_carlo_config: Optional[Dict[str, Any]] = None
    bayesian_config: Optional[Dict[str, Any]] = None
    stress_test_config: Optional[Dict[str, Any]] = None


@router.post("/run", response_model=Dict[str, Any])
async def run_simulation(request: RunSimulationRequest):
    """Run advanced simulation (Monte Carlo, Bayesian, Stress Test)"""
    try:
        # Build simulation request
        sim_request = SimulationRequest(
            scenario_id=request.scenario_id,
            method=request.method,
            runs=request.runs,
            seed=request.seed
        )
        
        # Add method-specific configuration
        if request.method == "monte_carlo" and request.monte_carlo_config:
            sim_request.monte_carlo_config = MonteCarloConfig(**request.monte_carlo_config)
        elif request.method == "bayesian_network" and request.bayesian_config:
            sim_request.bayesian_config = BayesianNetworkConfig(**request.bayesian_config)
        elif request.method == "stress_test" and request.stress_test_config:
            sim_request.stress_test_config = StressTestConfig(**request.stress_test_config)
        
        # Run simulation
        response = await simulation_service.run_simulation(sim_request)
        
        return {
            "id": response.id,
            "scenario_id": response.scenario_id,
            "method": response.method,
            "runs": response.runs,
            "status": response.status,
            "results": response.results,
            "created_at": response.created_at.isoformat(),
            "completed_at": response.completed_at.isoformat() if response.completed_at else None
        }
        
    except Exception as e:
        logger.error("Failed to run simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methods")
async def get_simulation_methods():
    """Get available simulation methods"""
    methods = [
        {
            "id": "monte_carlo",
            "name": "Monte Carlo Simulation",
            "description": "Random sampling simulation for uncertainty quantification with multiple probability distributions",
            "parameters": {
                "runs": {"type": "integer", "min": 1000, "max": 100000, "default": 10000},
                "seed": {"type": "integer", "optional": True},
                "scenario_type": {"type": "string", "required": True},
                "parameters": {"type": "object", "description": "Parameter distributions"}
            },
            "distributions": ["normal", "lognormal", "uniform", "triangular", "beta"]
        },
        {
            "id": "bayesian_network",
            "name": "Bayesian Network Analysis",
            "description": "Probabilistic graphical model for complex dependency modeling",
            "parameters": {
                "nodes": {"type": "array", "description": "Network nodes with properties"},
                "edges": {"type": "array", "description": "Dependency relationships"},
                "evidence": {"type": "object", "description": "Known evidence values"}
            },
            "features": ["dependency_modeling", "inference", "sensitivity_analysis"]
        },
        {
            "id": "stress_test",
            "name": "Stress Testing",
            "description": "Extreme scenario testing with multiple stress levels and recovery analysis",
            "parameters": {
                "scenarios": {"type": "object", "description": "Stress test scenarios"},
                "stress_levels": {"type": "array", "default": ["mild", "moderate", "severe", "extreme"]}
            },
            "metrics": ["stressed_impact", "recovery_time", "resilience_score"]
        }
    ]
    
    return {"methods": methods}


@router.get("/{simulation_id}/results")
async def get_simulation_results(simulation_id: str):
    """Get detailed simulation results"""
    try:
        # In production, retrieve from database
        # For now, return mock detailed results
        return {
            "simulation_id": simulation_id,
            "detailed_results": {
                "parameter_sensitivity": {
                    "market_volatility": 0.8,
                    "recovery_time": 0.6,
                    "system_redundancy": -0.4
                },
                "scenario_breakdown": {
                    "best_case": {"probability": 0.1, "impact": 500000},
                    "expected_case": {"probability": 0.7, "impact": 2500000},
                    "worst_case": {"probability": 0.2, "impact": 8000000}
                },
                "confidence_intervals": {
                    "90%": {"lower": 800000, "upper": 4200000},
                    "95%": {"lower": 600000, "upper": 5100000},
                    "99%": {"lower": 300000, "upper": 7800000}
                }
            }
        }
        
    except Exception as e:
        logger.error("Failed to get simulation results", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
