"""Scenario generation models"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime


class ScenarioRequest(BaseModel):
    """Request model for scenario generation"""
    name: str
    type: str  # financial, supply_chain, cyber, operational
    description: Optional[str] = None
    assumptions: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    template_id: Optional[str] = None


class TimelineEvent(BaseModel):
    """Timeline event in scenario narrative"""
    day: int
    event: str
    impact: str  # low, medium, high, critical
    details: Optional[str] = None


class AffectedAsset(BaseModel):
    """Asset affected by scenario"""
    name: str
    type: str
    impact_level: str  # low, medium, high, critical
    financial_impact: Optional[float] = None


class BusinessImpact(BaseModel):
    """Business impact assessment"""
    financial: Dict[str, Any]
    operational: Dict[str, Any]
    reputational: Dict[str, Any]
    regulatory: Optional[Dict[str, Any]] = None


class NarrativeSection(BaseModel):
    """Narrative section of scenario"""
    executive_summary: str
    timeline: List[TimelineEvent]
    key_events: List[str]
    affected_assets: List[AffectedAsset]
    business_impact: BusinessImpact
    stakeholders: List[str]
    generated_content: Optional[str] = None


class ScenarioResponse(BaseModel):
    """Response model for generated scenario"""
    id: str
    name: str
    type: str
    narrative: Dict[str, Any]
    assumptions: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class ScenarioTemplate(BaseModel):
    """Scenario template model"""
    id: str
    name: str
    type: str
    description: str
    default_assumptions: Dict[str, Any]
    key_drivers: List[str]
    industry_focus: Optional[List[str]] = None


class DependencyLink(BaseModel):
    """Cross-domain dependency link"""
    source_domain: str
    target_domain: str
    trigger_event: str
    impact_type: str
    delay_hours: int
    amplification_factor: float
    confidence: float  # 0.0 to 1.0
