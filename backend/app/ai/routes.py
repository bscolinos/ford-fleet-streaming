"""
AI API routes for fleet insights and note summarization.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.auth.jwt import TokenData
from app.auth.middleware import get_current_user
from app.db import queries
from app.ai.llm import summarize_driver_notes, get_fleet_insights

router = APIRouter(prefix="/ai", tags=["AI Insights"])


class SummarizeRequest(BaseModel):
    """Request to summarize driver notes."""
    vehicle_id: Optional[str] = None
    customer_id: Optional[str] = None


class SummarizeResponse(BaseModel):
    """Summarization response."""
    summary: str
    notes_count: int


class InsightsRequest(BaseModel):
    """Request for fleet insights."""
    question: str


class InsightsResponse(BaseModel):
    """AI insights response."""
    answer: str
    context_used: dict


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_notes(
    request: SummarizeRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Summarize driver notes using AI.
    
    Fetches driver notes based on filters and user's RLS scope,
    then uses Claude to generate an executive summary.
    """
    
    # Get notes from database (RLS filtered)
    notes = queries.get_driver_notes(
        role=user.role,
        vehicle_id=request.vehicle_id,
        customer_id=request.customer_id,
        limit=50
    )
    
    # Get AI summary
    summary = summarize_driver_notes(notes)
    
    return SummarizeResponse(
        summary=summary,
        notes_count=len(notes)
    )


@router.post("/insights", response_model=InsightsResponse)
async def get_insights(
    request: InsightsRequest,
    user: TokenData = Depends(get_current_user)
):
    """
    Get AI-powered insights about the fleet.
    
    Fetches current fleet statistics and uses them as context
    for answering the user's question.
    """
    
    # Get fleet summary for context
    summary = queries.get_fleet_summary(role=user.role)
    
    # Get recent anomaly types
    anomalies = queries.get_anomalies(
        role=user.role,
        limit=20
    )
    anomaly_types = list(set(a.get("anomaly_type", "") for a in anomalies))
    
    # Build context
    context = {
        **summary,
        "anomaly_types": anomaly_types
    }
    
    # Get AI response
    answer = get_fleet_insights(request.question, context)
    
    return InsightsResponse(
        answer=answer,
        context_used=context
    )

