"""Visualization generation router"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog

from ..services.visualization_service import VisualizationService
from ..models.visualization import VisualizationRequest, VisualizationResponse

logger = structlog.get_logger()
router = APIRouter()
visualization_service = VisualizationService()


class GenerateVisualizationRequest(BaseModel):
    scenario_id: str
    viz_type: str  # impact_matrix, causal_graph, simulation_chart, heatmap
    data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=Dict[str, Any])
async def generate_visualization(request: GenerateVisualizationRequest):
    """Generate visualization (impact matrix, causal graph, charts, heatmaps)"""
    try:
        viz_request = VisualizationRequest(
            scenario_id=request.scenario_id,
            viz_type=request.viz_type,
            data=request.data,
            config=request.config
        )
        
        response = await visualization_service.generate_visualization(viz_request)
        
        return {
            "id": response.id,
            "scenario_id": response.scenario_id,
            "viz_type": response.viz_type,
            "chart_data": response.chart_data,
            "metadata": response.metadata,
            "status": response.status,
            "created_at": response.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to generate visualization", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_visualization_types():
    """Get available visualization types"""
    viz_types = [
        {
            "id": "impact_matrix",
            "name": "Risk Impact Matrix",
            "description": "Likelihood vs Impact matrix with risk zones",
            "data_requirements": ["risks", "likelihood", "impact"],
            "output_format": "interactive_chart",
            "use_cases": ["risk_assessment", "executive_summary"]
        },
        {
            "id": "causal_graph",
            "name": "Causal Dependency Graph",
            "description": "Network graph showing risk dependencies and cascading effects",
            "data_requirements": ["dependencies", "events", "relationships"],
            "output_format": "network_diagram",
            "use_cases": ["scenario_analysis", "dependency_modeling"]
        },
        {
            "id": "simulation_chart",
            "name": "Simulation Results Charts",
            "description": "Distribution, timeline, sensitivity, and comparison charts",
            "data_requirements": ["simulation_results", "statistics"],
            "output_format": "interactive_chart",
            "chart_types": ["distribution", "timeline", "sensitivity", "comparison"],
            "use_cases": ["monte_carlo_results", "stress_testing"]
        },
        {
            "id": "heatmap",
            "name": "Risk Correlation Heatmap",
            "description": "Correlation matrix showing risk factor relationships",
            "data_requirements": ["correlation_matrix", "risk_factors"],
            "output_format": "heatmap",
            "use_cases": ["correlation_analysis", "portfolio_risk"]
        }
    ]
    
    return {"visualization_types": viz_types}


@router.get("/{viz_id}")
async def get_visualization(viz_id: str):
    """Get visualization by ID"""
    try:
        # In production, retrieve from database
        return {
            "id": viz_id,
            "scenario_id": "scenario-123",
            "viz_type": "impact_matrix",
            "status": "completed",
            "created_at": "2024-01-01T12:00:00Z",
            "chart_data": "{\"chart\": \"data\"}",
            "metadata": {
                "risk_count": 6,
                "high_risk_count": 2,
                "chart_type": "impact_matrix"
            }
        }
        
    except Exception as e:
        logger.error("Failed to get visualization", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def generate_batch_visualizations(requests: List[GenerateVisualizationRequest]):
    """Generate multiple visualizations in batch"""
    try:
        results = []
        
        for request in requests:
            viz_request = VisualizationRequest(
                scenario_id=request.scenario_id,
                viz_type=request.viz_type,
                data=request.data,
                config=request.config
            )
            
            response = await visualization_service.generate_visualization(viz_request)
            
            results.append({
                "id": response.id,
                "viz_type": response.viz_type,
                "status": response.status
            })
        
        return {
            "batch_id": f"batch-{len(results)}",
            "total_visualizations": len(results),
            "results": results,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error("Failed to generate batch visualizations", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
