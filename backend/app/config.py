"""
Application configuration from environment variables.
"""

import os
from dotenv import load_dotenv
load_dotenv()
from functools import lru_cache

from pydantic_settings import BaseSettings


def get_env(key: str, default: str | None = None) -> str | None:
    """Fetch an environment variable with an optional default."""
    return os.getenv(key, default)


class Settings(BaseSettings):
    """Application settings loaded from environment."""
    
    # Application
    app_name: str = "Ford Fleet Management Demo"
    debug: bool = False
    
    # JWT Configuration
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # SingleStore Connection
    singlestore_host: str = os.getenv("SINGLESTORE_HOST")
    singlestore_port: int = 3306
    singlestore_database: str = "ford_fleet"
    singlestore_user: str = "admin"
    singlestore_password: str = os.getenv("SINGLESTORE_PASSWORD")

    # Database credentials per persona (for RLS - created in security.sql)
    db_admin_user: str = "demo_admin"
    db_admin_password: str = "AdminPass123!"
    
    db_territory_manager_user: str = "territory_manager_1"
    db_territory_manager_password: str = "TerritoryPass123!"
    
    db_regional_manager_user: str = "regional_manager_1"
    db_regional_manager_password: str = "RegionalPass123!"
    
    db_ingest_user: str = "ingest_user"
    db_ingest_password: str = "IngestPass123!"
    
    # AI Configuration (SingleStore AI Endpoint)
    model_api_auth: str = ""
    model_name: str = "claude-sonnet-4-5-79066"
    model_api_endpoint: str = "https://ai.us-east-1.cloud.singlestore.com/5cc87edb-3e18-48f8-bef9-6097eb8fcab6/v1"
    
    # Demo user credentials (for login endpoint)
    demo_users: dict = {
        "territory_manager_1": {
            "password": "territory123",
            "role": "territory_manager",
            "region_id": "WEST",
            "territory_id": "WEST_1",
            "db_user": "territory_manager_1"
        },
        "territory_manager_2": {
            "password": "territory123",
            "role": "territory_manager",
            "region_id": "EAST",
            "territory_id": "EAST_1",
            "db_user": "territory_manager_1"  # Use same DB user for demo
        },
        "regional_manager_1": {
            "password": "regional123",
            "role": "regional_manager",
            "region_id": "WEST",
            "territory_id": None,
            "db_user": "regional_manager_1"
        },
        "regional_manager_2": {
            "password": "regional123",
            "role": "regional_manager",
            "region_id": "EAST",
            "territory_id": None,
            "db_user": "regional_manager_1"  # Use same DB user for demo
        },
        "demo_admin": {
            "password": "admin123",
            "role": "admin",
            "region_id": None,
            "territory_id": None,
            "db_user": "demo_admin"
        }
    }
    
    class Config:
        env_file = "../.env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
