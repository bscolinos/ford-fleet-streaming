"""
Ford Fleet Management Demo - FastAPI Application

Main entry point for the backend API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.auth.routes import router as auth_router
from app.fleet.routes import router as fleet_router
from app.realtime.websocket import router as realtime_router
from app.ai.routes import router as ai_router

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    Ford Fleet Management Demo API
    
    This API demonstrates SingleStore's capabilities for:
    - Transaction processing (rowstore tables)
    - Fast analytical queries (columnstore tables)
    - Real-time streaming ingestion from Kafka
    - Row-Level Security (RLS) with RBAC
    
    ## Authentication
    
    Use the `/auth/login` endpoint to authenticate and receive a JWT token.
    Include the token in the `Authorization: Bearer <token>` header for protected endpoints.
    
    ## Demo Credentials
    
    - `territory_manager_1` / `territory123` - Territory manager (WEST_1)
    - `regional_manager_1` / `regional123` - Regional manager (WEST region)
    - `demo_admin` / `admin123` - Admin (full access)
    
    ## RLS Demonstration
    
    Each role sees different data based on their security scope:
    - Territory managers see only their territory's vehicles and telemetry
    - Regional managers see all territories in their region
    - Admins see everything
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(fleet_router)
app.include_router(realtime_router)
app.include_router(ai_router)


@app.get("/", tags=["Health"])
async def root():
    """API root - health check."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

