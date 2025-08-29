"""Mitigation strategies router"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog

from ..services.mitigation_service import MitigationService
from ..models.mitigation import MitigationRequest, MitigationResponse

logger = structlog.get_logger()
router = APIRouter()
mitigation_service = MitigationService()


class GenerateMitigationsRequest(BaseModel):
    scenario_id: str
    risk_type: str
    risk_data: Dict[str, Any]
    budget_limit: Optional[float] = None
    priority: str = "medium"  # high, medium, low
    max_strategies: int = 10
    ranking_criteria: Optional[Dict[str, float]] = None


@router.post("/generate", response_model=Dict[str, Any])
async def generate_mitigations(request: GenerateMitigationsRequest):
    """Generate ranked mitigation strategies with cost-benefit analysis"""
    try:
        mitigation_request = MitigationRequest(
            scenario_id=request.scenario_id,
            risk_type=request.risk_type,
            risk_data=request.risk_data,
            budget_limit=request.budget_limit,
            priority=request.priority,
            max_strategies=request.max_strategies,
            ranking_criteria=request.ranking_criteria
        )
        
        response = await mitigation_service.generate_mitigations(mitigation_request)
        
        return {
            "id": response.id,
            "scenario_id": response.scenario_id,
            "strategies": response.strategies,
            "total_strategies": response.total_strategies,
            "recommended_strategy": response.recommended_strategy,
            "analysis_summary": response.analysis_summary,
            "status": response.status,
            "created_at": response.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to generate mitigations", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_mitigation_templates():
    """Get available mitigation strategy templates"""
    try:
        templates = mitigation_service.library.templates
        
        template_data = []
        for template in templates:
            template_data.append({
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "description": template.description,
                "risk_types": template.risk_types,
                "implementation_time": template.implementation_time,
                "cost_range": template.cost_range,
                "effectiveness": template.effectiveness,
                "prerequisites": template.prerequisites,
                "kpis": template.kpis
            })
        
        return {"templates": template_data}
        
    except Exception as e:
        logger.error("Failed to get mitigation templates", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{mitigation_id}/implement")
async def create_implementation_tasks(mitigation_id: str, selected_strategies: List[str]):
    """Create implementation tasks in Jira/ServiceNow"""
    try:
        result = await mitigation_service.create_jira_tasks(mitigation_id, selected_strategies)
        
        return {
            "mitigation_id": mitigation_id,
            "tasks_created": result["tasks_created"],
            "tasks": result["tasks"],
            "integration": "jira",
            "project": result["jira_project"],
            "status": result["status"]
        }
        
    except Exception as e:
        logger.error("Failed to create implementation tasks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_mitigation_categories():
    """Get mitigation categories and their characteristics"""
    categories = [
        {
            "id": "cyber",
            "name": "Cybersecurity",
            "description": "Technical and procedural controls for cyber risk mitigation",
            "common_strategies": [
                "Enhanced backup systems",
                "Multi-factor authentication",
                "Security awareness training",
                "Incident response planning"
            ],
            "typical_cost_range": [10000, 500000],
            "implementation_time_range": [30, 180]
        },
        {
            "id": "financial",
            "name": "Financial Risk Management",
            "description": "Financial instruments and strategies for market risk mitigation",
            "common_strategies": [
                "Hedging strategies",
                "Portfolio diversification",
                "Liquidity management",
                "Credit risk controls"
            ],
            "typical_cost_range": [50000, 1000000],
            "implementation_time_range": [30, 120]
        },
        {
            "id": "supply_chain",
            "name": "Supply Chain Resilience",
            "description": "Strategies to reduce supply chain disruption risks",
            "common_strategies": [
                "Supplier diversification",
                "Strategic inventory buffers",
                "Supply chain monitoring",
                "Alternative sourcing"
            ],
            "typical_cost_range": [75000, 1000000],
            "implementation_time_range": [60, 180]
        },
        {
            "id": "operational",
            "name": "Operational Continuity",
            "description": "Business continuity and operational resilience measures",
            "common_strategies": [
                "Business continuity planning",
                "Cross-training programs",
                "Process automation",
                "Redundancy systems"
            ],
            "typical_cost_range": [25000, 800000],
            "implementation_time_range": [90, 180]
        }
    ]
    
    return {"categories": categories}


@router.get("/{mitigation_id}/cost-benefit")
async def get_cost_benefit_analysis(mitigation_id: str):
    """Get detailed cost-benefit analysis for mitigation strategies"""
    try:
        # In production, retrieve from database
        return {
            "mitigation_id": mitigation_id,
            "analysis": {
                "total_investment": 450000,
                "annual_savings": 1200000,
                "roi_percent": 167,
                "payback_period_months": 4.5,
                "npv_5_year": 3200000,
                "risk_reduction": 0.75,
                "confidence_level": 0.85
            },
            "breakdown": {
                "implementation_cost": 300000,
                "annual_operating_cost": 30000,
                "training_cost": 50000,
                "technology_cost": 100000
            },
            "benefits": {
                "avoided_losses": 1000000,
                "efficiency_gains": 150000,
                "compliance_benefits": 50000
            }
        }
        
    except Exception as e:
        logger.error("Failed to get cost-benefit analysis", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
