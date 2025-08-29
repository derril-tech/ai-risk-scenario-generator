"""Data ingestion router"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import pandas as pd
import structlog

from ..services.ingestion_service import IngestionService
from ..models.ingestion import DataSourceCreate, IngestionJob

logger = structlog.get_logger()
router = APIRouter()
ingestion_service = IngestionService()


class ConnectDataSourceRequest(BaseModel):
    name: str
    type: str
    connection_config: Dict[str, Any]


class UploadResponse(BaseModel):
    job_id: str
    filename: str
    size: int
    status: str
    records_found: int


@router.post("/connect", response_model=Dict[str, Any])
async def connect_data_source(request: ConnectDataSourceRequest):
    """Connect to external data source"""
    try:
        data_source = DataSourceCreate(
            name=request.name,
            type=request.type,
            connection_config=request.connection_config
        )
        
        result = await ingestion_service.connect_data_source(data_source)
        return result
        
    except Exception as e:
        logger.error("Failed to connect data source", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process CSV/Excel file"""
    try:
        # Validate file type
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Only CSV and Excel files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Process file
        job = await ingestion_service.process_uploaded_file(
            filename=file.filename,
            content=content,
            content_type=file.content_type
        )
        
        return UploadResponse(
            job_id=job.id,
            filename=file.filename,
            size=len(content),
            status=job.status,
            records_found=job.records_found or 0
        )
        
    except Exception as e:
        logger.error("Failed to upload file", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def get_data_sources():
    """Get all connected data sources"""
    try:
        sources = await ingestion_service.get_data_sources()
        return {"sources": sources}
        
    except Exception as e:
        logger.error("Failed to get data sources", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_ingestion_job(job_id: str):
    """Get ingestion job status"""
    try:
        job = await ingestion_service.get_ingestion_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
        
    except Exception as e:
        logger.error("Failed to get ingestion job", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/normalize/{job_id}")
async def normalize_data(job_id: str):
    """Normalize ingested data into ontology"""
    try:
        result = await ingestion_service.normalize_data(job_id)
        return result
        
    except Exception as e:
        logger.error("Failed to normalize data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
