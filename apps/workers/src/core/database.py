"""Database connection and initialization"""

import asyncpg
import structlog
from .config import settings

logger = structlog.get_logger()


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.pool = None
    
    async def init_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database pool initialized")
        except Exception as e:
            logger.error("Failed to initialize database pool", error=str(e))
            raise
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    async def execute_query(self, query: str, *args):
        """Execute a query"""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def execute_one(self, query: str, *args):
        """Execute a query and return one result"""
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)


db_manager = DatabaseManager()


async def init_db():
    """Initialize database connections"""
    await db_manager.init_pool()
