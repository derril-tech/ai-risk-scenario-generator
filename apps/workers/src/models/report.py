"""Report generation models"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class ReportRequest(BaseModel):
    """Report generation request"""
    scenario_id: str
    simulation_id: Optional[str] = None
    format: str  # pdf, json, csv
    sections: List[str]
    title: Optional[str] = None
    template: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class ReportResponse(BaseModel):
    """Report generation response"""
    id: str
    scenario_id: str
    title: str
    format: str
    sections: List[str]
    status: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class ReportSection(BaseModel):
    """Report section configuration"""
    name: str
    title: str
    content_type: str  # text, table, chart, image
    data_source: str
    template: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ExecutiveSummary(BaseModel):
    """Executive summary section"""
    risk_overview: str
    key_findings: List[str]
    recommendations: List[str]
    risk_score: float
    confidence_level: float


class RiskAssessment(BaseModel):
    """Risk assessment section"""
    methodology: str
    risk_categories: List[Dict[str, Any]]
    risk_matrix: Dict[str, Any]
    top_risks: List[Dict[str, Any]]
    overall_score: float


class SimulationSummary(BaseModel):
    """Simulation results summary"""
    method: str
    runs: int
    statistics: Dict[str, float]
    percentiles: Dict[str, float]
    distribution_chart: Optional[str] = None


class MitigationSummary(BaseModel):
    """Mitigation strategies summary"""
    total_strategies: int
    recommended_strategies: List[Dict[str, Any]]
    total_investment: float
    expected_risk_reduction: float
    implementation_timeline: int


class ComplianceReport(BaseModel):
    """Compliance reporting section"""
    frameworks: List[str]
    requirements: List[Dict[str, Any]]
    compliance_status: str
    gaps: List[str]
    remediation_plan: Optional[Dict[str, Any]] = None


class ReportTemplate(BaseModel):
    """Report template configuration"""
    id: str
    name: str
    description: str
    sections: List[ReportSection]
    target_audience: str  # executive, technical, regulatory
    format_options: List[str]
    default_config: Dict[str, Any]
