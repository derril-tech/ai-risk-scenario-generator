"""Scenario generation router"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog

from ..services.scenario_service import ScenarioService
from ..models.scenario import ScenarioRequest, ScenarioResponse

logger = structlog.get_logger()
router = APIRouter()
scenario_service = ScenarioService()


class GenerateScenarioRequest(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    assumptions: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    template_id: Optional[str] = None


@router.post("/generate", response_model=Dict[str, Any])
async def generate_scenario(request: GenerateScenarioRequest):
    """Generate AI-driven scenario narrative using CrewAI"""
    try:
        scenario_request = ScenarioRequest(
            name=request.name,
            type=request.type,
            description=request.description,
            assumptions=request.assumptions,
            context=request.context,
            template_id=request.template_id
        )
        
        response = await scenario_service.generate_scenario(scenario_request)
        
        return {
            "id": response.id,
            "name": response.name,
            "type": response.type,
            "narrative": response.narrative,
            "assumptions": response.assumptions,
            "status": response.status,
            "created_at": response.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to generate scenario", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_scenario_templates():
    """Get available scenario templates"""
    try:
        templates = await scenario_service.get_scenario_templates()
        return {"templates": templates}
        
    except Exception as e:
        logger.error("Failed to get scenario templates", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scenario_id}/dependencies")
async def get_scenario_dependencies(scenario_id: str):
    """Get cross-domain dependencies for a scenario"""
    try:
        # Mock dependencies - in production, analyze scenario and return actual dependencies
        dependencies = [
            {
                "source": "Cyber Attack",
                "target": "System Downtime", 
                "strength": 0.9,
                "delay": 1,
                "type": "causal"
            },
            {
                "source": "System Downtime",
                "target": "Revenue Loss",
                "strength": 0.8,
                "delay": 2,
                "type": "financial"
            },
            {
                "source": "Revenue Loss",
                "target": "Customer Impact",
                "strength": 0.6,
                "delay": 24,
                "type": "operational"
            }
        ]
        
        return {
            "scenario_id": scenario_id,
            "dependencies": dependencies,
            "dependency_count": len(dependencies)
        }
        
    except Exception as e:
        logger.error("Failed to get scenario dependencies", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
