"""NATS messaging setup"""

import nats
import structlog
from .config import settings

logger = structlog.get_logger()


class MessagingManager:
    """NATS messaging manager"""
    
    def __init__(self):
        self.nc = None
        self.js = None
    
    async def connect(self):
        """Connect to NATS"""
        try:
            self.nc = await nats.connect(settings.NATS_URL)
            self.js = self.nc.jetstream()
            
            # Create streams
            await self._create_streams()
            
            logger.info("Connected to NATS")
        except Exception as e:
            logger.error("Failed to connect to NATS", error=str(e))
            raise
    
    async def _create_streams(self):
        """Create NATS JetStream streams"""
        streams = [
            {
                "name": "DATA_INGESTION",
                "subjects": ["data.ingest", "data.normalize", "data.embed"]
            },
            {
                "name": "SCENARIO_GENERATION", 
                "subjects": ["scenario.gen", "scenario.narrative", "scenario.assumptions"]
            },
            {
                "name": "SIMULATIONS",
                "subjects": ["sim.run", "sim.monte_carlo", "sim.bayesian"]
            },
            {
                "name": "VISUALIZATIONS",
                "subjects": ["viz.make", "viz.matrix", "viz.graph", "viz.chart"]
            },
            {
                "name": "REPORTS",
                "subjects": ["export.make", "export.pdf", "export.json", "export.csv"]
            }
        ]
        
        for stream_config in streams:
            try:
                await self.js.add_stream(
                    name=stream_config["name"],
                    subjects=stream_config["subjects"]
                )
                logger.info(f"Created stream: {stream_config['name']}")
            except Exception as e:
                if "stream name already in use" not in str(e):
                    logger.error(f"Failed to create stream {stream_config['name']}", error=str(e))
    
    async def publish(self, subject: str, data: bytes):
        """Publish message to NATS"""
        if self.js:
            await self.js.publish(subject, data)
    
    async def subscribe(self, subject: str, callback):
        """Subscribe to NATS subject"""
        if self.nc:
            await self.nc.subscribe(subject, cb=callback)
    
    async def close(self):
        """Close NATS connection"""
        if self.nc:
            await self.nc.close()
            logger.info("NATS connection closed")


messaging_manager = MessagingManager()


async def init_messaging():
    """Initialize messaging connections"""
    await messaging_manager.connect()
