"""Data models for ingestion"""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime


class DataSourceCreate(BaseModel):
    """Data source creation model"""
    name: str
    type: str
    connection_config: Dict[str, Any]


class DataSource(BaseModel):
    """Data source model"""
    id: str
    name: str
    type: str
    connection_config: Dict[str, Any]
    status: str
    last_sync: Optional[datetime] = None
    records_ingested: int = 0
    created_at: datetime
    updated_at: datetime


class IngestionJob(BaseModel):
    """Ingestion job model"""
    id: str
    filename: Optional[str] = None
    data_source_id: Optional[str] = None
    status: str  # pending, processing, completed, failed
    records_found: Optional[int] = None
    records_processed: Optional[int] = None
    assets_created: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class Asset(BaseModel):
    """Asset model for normalized data"""
    id: str
    name: str
    type: str
    category: str
    value: float
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    data_source_id: Optional[str] = None
    org_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ThreatEvent(BaseModel):
    """Threat event model"""
    id: str
    name: str
    type: str  # cyber, financial, operational, supply_chain
    severity: str  # low, medium, high, critical
    likelihood: float  # 0.0 to 1.0
    impact_categories: List[str]
    affected_assets: List[str]
    metadata: Dict[str, Any]
    created_at: datetime


class Impact(BaseModel):
    """Impact model linking threats to assets"""
    id: str
    threat_id: str
    asset_id: str
    impact_type: str  # financial, operational, reputational
    magnitude: float
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]
    created_at: datetime
