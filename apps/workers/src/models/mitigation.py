"""Mitigation models"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class MitigationRequest(BaseModel):
    """Mitigation request model"""
    scenario_id: str
    risk_type: str
    risk_data: Dict[str, Any]
    budget_limit: Optional[float] = None
    priority: str = "medium"  # high, medium, low
    max_strategies: int = 10
    ranking_criteria: Optional[Dict[str, float]] = None


class CostBenefitAnalysis(BaseModel):
    """Cost-benefit analysis model"""
    implementation_cost: float
    annual_operating_cost: float
    annual_benefit: float
    total_cost: float
    total_benefit: float
    net_benefit: float
    roi_percent: float
    payback_period_years: float
    npv: float
    break_even_point: Optional[float] = None


class RiskReduction(BaseModel):
    """Risk reduction assessment"""
    risk_type: str
    current_risk_level: float
    residual_risk_level: float
    reduction_percentage: float
    confidence_level: float


class ImplementationPlan(BaseModel):
    """Implementation plan model"""
    strategy_id: str
    total_duration_days: int
    phases: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    required_resources: List[Dict[str, Any]]
    dependencies: List[str]
    success_criteria: List[str]
    implementation_risks: List[Dict[str, Any]]
    estimated_start_date: datetime
    estimated_completion_date: datetime


class MitigationStrategy(BaseModel):
    """Mitigation strategy model"""
    id: str
    name: str
    category: str
    description: str
    effectiveness: float
    cost_benefit_analysis: CostBenefitAnalysis
    implementation_plan: ImplementationPlan
    risk_reduction: RiskReduction
    prerequisites: List[str]
    kpis: List[str]
    rank: Optional[int] = None
    total_score: Optional[float] = None


class MitigationResponse(BaseModel):
    """Mitigation response model"""
    id: str
    scenario_id: str
    strategies: List[Dict[str, Any]]
    total_strategies: int
    recommended_strategy: Optional[Dict[str, Any]] = None
    analysis_summary: Dict[str, Any]
    status: str
    created_at: datetime


class JiraIntegration(BaseModel):
    """Jira integration configuration"""
    server_url: str
    username: str
    api_token: str
    project_key: str
    issue_type: str = "Task"


class ServiceNowIntegration(BaseModel):
    """ServiceNow integration configuration"""
    instance_url: str
    username: str
    password: str
    table: str = "incident"
