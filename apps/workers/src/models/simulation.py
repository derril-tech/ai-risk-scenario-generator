"""Simulation models"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class MonteCarloConfig(BaseModel):
    """Monte Carlo simulation configuration"""
    scenario_type: str
    parameters: Dict[str, Any]  # Parameter distributions
    correlations: Optional[Dict[str, float]] = None


class BayesianNetworkConfig(BaseModel):
    """Bayesian network configuration"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    evidence: Dict[str, float]


class StressTestConfig(BaseModel):
    """Stress test configuration"""
    scenarios: Dict[str, Any]  # Stress scenarios
    stress_levels: List[str] = ["mild", "moderate", "severe", "extreme"]


class SimulationRequest(BaseModel):
    """Simulation request model"""
    scenario_id: str
    method: str  # monte_carlo, bayesian_network, stress_test
    runs: int = 10000
    seed: Optional[int] = None
    monte_carlo_config: Optional[MonteCarloConfig] = None
    bayesian_config: Optional[BayesianNetworkConfig] = None
    stress_test_config: Optional[StressTestConfig] = None


class SimulationResults(BaseModel):
    """Simulation results model"""
    statistics: Dict[str, float]
    distribution: List[float]
    percentiles: Dict[str, float]
    detailed_results: Optional[List[Dict[str, Any]]] = None


class SimulationResponse(BaseModel):
    """Simulation response model"""
    id: str
    scenario_id: str
    method: str
    runs: int
    status: str
    results: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None


class DependencyModel(BaseModel):
    """Cross-domain dependency model"""
    source_event: str
    target_events: List[str]
    propagation_delay: int  # hours
    impact_multiplier: float
    probability: float
