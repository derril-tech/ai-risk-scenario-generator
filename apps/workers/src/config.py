"""Configuration settings for AI Risk Workers"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ai_risk_db"
    CLICKHOUSE_URL: str = "http://localhost:8123"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Messaging
    NATS_URL: str = "nats://localhost:4222"
    
    # AI/ML APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin123"
    S3_BUCKET: str = "ai-risk-exports"
    
    # Security
    JWT_SECRET: str = "your-jwt-secret-key"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Worker Configuration
    WORKER_CONCURRENCY: int = 4
    MAX_SIMULATION_RUNS: int = 100000
    
    # Monitoring
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
