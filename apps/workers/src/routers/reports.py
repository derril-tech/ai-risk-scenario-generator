"""Advanced reports router"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import structlog

from ..services.report_service import ReportService
from ..models.report import ReportRequest, ReportResponse

logger = structlog.get_logger()
router = APIRouter()
report_service = ReportService()


class GenerateReportRequest(BaseModel):
    scenario_id: str
    simulation_id: Optional[str] = None
    format: str = "pdf"  # pdf, json, csv
    sections: List[str]
    title: Optional[str] = None
    template: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=Dict[str, Any])
async def generate_report(request: GenerateReportRequest):
    """Generate comprehensive risk assessment report"""
    try:
        report_request = ReportRequest(
            scenario_id=request.scenario_id,
            simulation_id=request.simulation_id,
            format=request.format,
            sections=request.sections,
            title=request.title,
            template=request.template,
            custom_config=request.custom_config
        )
        
        response = await report_service.generate_report(report_request)
        
        return {
            "id": response.id,
            "scenario_id": response.scenario_id,
            "title": response.title,
            "format": response.format,
            "sections": response.sections,
            "status": response.status,
            "file_size": response.file_size,
            "download_url": response.download_url,
            "created_at": response.created_at.isoformat(),
            "completed_at": response.completed_at.isoformat() if response.completed_at else None
        }
        
    except Exception as e:
        logger.error("Failed to generate report", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_report_templates():
    """Get available report templates"""
    templates = [
        {
            "id": "executive_summary",
            "name": "Executive Summary",
            "description": "High-level risk assessment for C-suite and board",
            "target_audience": "executive",
            "sections": ["executive_summary", "key_findings", "recommendations", "risk_matrix"],
            "formats": ["pdf", "json"],
            "estimated_pages": 5
        },
        {
            "id": "detailed_analysis",
            "name": "Detailed Risk Analysis",
            "description": "Comprehensive technical risk analysis with full methodology",
            "target_audience": "technical",
            "sections": [
                "executive_summary",
                "scenario_details", 
                "simulation_results",
                "risk_matrix",
                "mitigation_strategies",
                "compliance_overview",
                "appendices"
            ],
            "formats": ["pdf", "json", "csv"],
            "estimated_pages": 25
        },
        {
            "id": "regulatory_compliance",
            "name": "Regulatory Compliance Report",
            "description": "Report formatted for regulatory submission (ISO 31000, NIST RMF)",
            "target_audience": "regulatory",
            "sections": [
                "compliance_overview",
                "risk_assessment",
                "control_effectiveness",
                "remediation_plan",
                "governance_framework"
            ],
            "formats": ["pdf", "json"],
            "estimated_pages": 15
        },
        {
            "id": "board_presentation",
            "name": "Board Risk Presentation",
            "description": "Executive presentation format for board meetings",
            "target_audience": "board",
            "sections": [
                "executive_summary",
                "key_risks",
                "financial_impact",
                "mitigation_priorities",
                "board_recommendations"
            ],
            "formats": ["pdf"],
            "estimated_pages": 10
        }
    ]
    
    return {"templates": templates}


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """Download generated report file"""
    try:
        # Get report file content
        file_content = await report_service.get_report_file(report_id)
        
        # Determine content type and filename
        # In production, get from database
        content_type = "application/pdf"
        filename = f"risk-report-{report_id}.pdf"
        
        return Response(
            content=file_content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error("Failed to download report", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}/status")
async def get_report_status(report_id: str):
    """Get report generation status"""
    try:
        # In production, query database for actual status
        return {
            "report_id": report_id,
            "status": "completed",
            "progress": 100,
            "estimated_completion": None,
            "file_size": 2048576,  # 2MB
            "pages": 15
        }
        
    except Exception as e:
        logger.error("Failed to get report status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{report_id}/share")
async def share_report(report_id: str, recipients: List[str]):
    """Share report with specified recipients"""
    try:
        # Mock sharing functionality
        return {
            "report_id": report_id,
            "shared_with": recipients,
            "share_links": [f"https://reports.ai-risk.com/shared/{report_id}?token=abc123"],
            "expiry": "2024-01-19T12:00:00Z",
            "status": "shared"
        }
        
    except Exception as e:
        logger.error("Failed to share report", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
