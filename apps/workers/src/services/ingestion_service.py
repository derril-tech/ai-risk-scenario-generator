"""Data ingestion service"""

import uuid
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime
import io

from ..models.ingestion import DataSourceCreate, IngestionJob, Asset
from ..core.database import db_manager
from ..core.messaging import messaging_manager

logger = structlog.get_logger()


class IngestionService:
    """Service for data ingestion and normalization"""
    
    async def connect_data_source(self, data_source: DataSourceCreate) -> Dict[str, Any]:
        """Connect to external data source"""
        try:
            # Generate unique ID
            source_id = str(uuid.uuid4())
            
            # Test connection based on type
            connection_status = await self._test_connection(data_source)
            
            # Store data source configuration
            query = """
                INSERT INTO data_sources (id, name, type, connection_config, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
            """
            
            now = datetime.utcnow()
            result = await db_manager.execute_one(
                query,
                source_id,
                data_source.name,
                data_source.type,
                json.dumps(data_source.connection_config),
                connection_status,
                now,
                now
            )
            
            # Publish connection event
            await messaging_manager.publish(
                "data.ingest",
                json.dumps({
                    "event": "source_connected",
                    "source_id": source_id,
                    "type": data_source.type
                }).encode()
            )
            
            return {
                "id": source_id,
                "name": data_source.name,
                "type": data_source.type,
                "status": connection_status,
                "created_at": now.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to connect data source", error=str(e))
            raise
    
    async def _test_connection(self, data_source: DataSourceCreate) -> str:
        """Test connection to data source"""
        # Mock connection testing - implement actual connectors
        connection_types = {
            'sap': self._test_sap_connection,
            'oracle': self._test_oracle_connection,
            'netsuite': self._test_netsuite_connection,
            'coupa': self._test_coupa_connection,
            'siem': self._test_siem_connection,
            'edr': self._test_edr_connection,
            'api': self._test_api_connection
        }
        
        if data_source.type in connection_types:
            return await connection_types[data_source.type](data_source.connection_config)
        
        return "connected"  # Default for unknown types
    
    async def _test_sap_connection(self, config: Dict[str, Any]) -> str:
        """Test SAP connection"""
        # TODO: Implement actual SAP RFC connection
        logger.info("Testing SAP connection", config=config)
        return "connected"
    
    async def _test_oracle_connection(self, config: Dict[str, Any]) -> str:
        """Test Oracle connection"""
        # TODO: Implement actual Oracle connection
        logger.info("Testing Oracle connection", config=config)
        return "connected"
    
    async def _test_netsuite_connection(self, config: Dict[str, Any]) -> str:
        """Test NetSuite connection"""
        # TODO: Implement actual NetSuite API connection
        logger.info("Testing NetSuite connection", config=config)
        return "connected"
    
    async def _test_coupa_connection(self, config: Dict[str, Any]) -> str:
        """Test Coupa connection"""
        # TODO: Implement actual Coupa API connection
        logger.info("Testing Coupa connection", config=config)
        return "connected"
    
    async def _test_siem_connection(self, config: Dict[str, Any]) -> str:
        """Test SIEM connection"""
        # TODO: Implement actual SIEM connection
        logger.info("Testing SIEM connection", config=config)
        return "connected"
    
    async def _test_edr_connection(self, config: Dict[str, Any]) -> str:
        """Test EDR connection"""
        # TODO: Implement actual EDR connection
        logger.info("Testing EDR connection", config=config)
        return "connected"
    
    async def _test_api_connection(self, config: Dict[str, Any]) -> str:
        """Test generic API connection"""
        # TODO: Implement actual API connection test
        logger.info("Testing API connection", config=config)
        return "connected"
    
    async def process_uploaded_file(self, filename: str, content: bytes, content_type: str) -> IngestionJob:
        """Process uploaded CSV/Excel file"""
        try:
            job_id = str(uuid.uuid4())
            
            # Parse file based on type
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(content))
            else:
                raise ValueError(f"Unsupported file type: {filename}")
            
            records_found = len(df)
            
            # Create ingestion job
            job = IngestionJob(
                id=job_id,
                filename=filename,
                status="processing",
                records_found=records_found,
                created_at=datetime.utcnow()
            )
            
            # Store raw data temporarily (in production, use proper storage)
            # For now, we'll just log the data structure
            logger.info(
                "Processing uploaded file",
                job_id=job_id,
                filename=filename,
                records=records_found,
                columns=list(df.columns)
            )
            
            # Publish processing event
            await messaging_manager.publish(
                "data.ingest",
                json.dumps({
                    "event": "file_uploaded",
                    "job_id": job_id,
                    "filename": filename,
                    "records": records_found
                }).encode()
            )
            
            # Start async processing
            await self._process_file_async(job_id, df)
            
            return job
            
        except Exception as e:
            logger.error("Failed to process uploaded file", error=str(e))
            raise
    
    async def _process_file_async(self, job_id: str, df: pd.DataFrame):
        """Process file data asynchronously"""
        try:
            # Normalize data into asset ontology
            assets = await self._normalize_to_assets(df)
            
            # Store assets in database
            for asset in assets:
                await self._store_asset(asset)
            
            # Update job status
            logger.info(f"Completed processing job {job_id}, created {len(assets)} assets")
            
        except Exception as e:
            logger.error("Failed to process file async", job_id=job_id, error=str(e))
    
    async def _normalize_to_assets(self, df: pd.DataFrame) -> List[Asset]:
        """Normalize DataFrame to Asset ontology"""
        assets = []
        
        for _, row in df.iterrows():
            # Basic asset normalization - customize based on data structure
            asset = Asset(
                id=str(uuid.uuid4()),
                name=str(row.get('name', row.get('asset_name', f'Asset_{len(assets)}'))),
                type=str(row.get('type', row.get('asset_type', 'unknown'))),
                category=str(row.get('category', 'general')),
                value=float(row.get('value', row.get('cost', 0))),
                metadata={
                    col: self._safe_convert(row[col]) 
                    for col in df.columns 
                    if col not in ['name', 'type', 'category', 'value']
                },
                created_at=datetime.utcnow()
            )
            assets.append(asset)
        
        return assets
    
    def _safe_convert(self, value):
        """Safely convert pandas values to JSON-serializable types"""
        if pd.isna(value):
            return None
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        return str(value)
    
    async def _store_asset(self, asset: Asset):
        """Store asset in database"""
        query = """
            INSERT INTO assets (id, name, type, category, value, metadata, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """
        
        await db_manager.execute_query(
            query,
            asset.id,
            asset.name,
            asset.type,
            asset.category,
            asset.value,
            json.dumps(asset.metadata),
            asset.created_at,
            asset.created_at
        )
    
    async def get_data_sources(self) -> List[Dict[str, Any]]:
        """Get all data sources"""
        query = "SELECT * FROM data_sources ORDER BY created_at DESC"
        results = await db_manager.execute_query(query)
        
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "status": row["status"],
                "last_sync": row["updated_at"].isoformat() if row["updated_at"] else None,
                "records_ingested": row.get("records_ingested", 0)
            }
            for row in results
        ]
    
    async def get_ingestion_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get ingestion job by ID"""
        # For now, return mock data - implement proper job tracking
        return {
            "id": job_id,
            "status": "completed",
            "records_processed": 150,
            "assets_created": 150,
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def normalize_data(self, job_id: str) -> Dict[str, Any]:
        """Normalize ingested data into ontology"""
        # Publish normalization event
        await messaging_manager.publish(
            "data.normalize",
            json.dumps({
                "event": "normalize_requested",
                "job_id": job_id
            }).encode()
        )
        
        return {
            "job_id": job_id,
            "status": "normalizing",
            "message": "Data normalization started"
        }
