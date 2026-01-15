"""
Fleet management API routes.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.jwt import TokenData
from app.auth.middleware import get_current_user
from app.db import queries
from app.fleet.models import (
    FleetSummary,
    FleetSummaryResponse,
    TimeSeriesPoint,
    Vehicle,
    VehicleListResponse,
    VehicleTelemetryResponse,
    TelemetryPoint,
    Anomaly,
    AnomalyListResponse,
    AcknowledgeResponse,
    DriverNote,
    DriverNotesResponse,
)

router = APIRouter(prefix="/fleet", tags=["Fleet Management"])


@router.get("/summary", response_model=FleetSummaryResponse)
async def get_fleet_summary(
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    start_ts: Optional[datetime] = Query(None, description="Start timestamp"),
    end_ts: Optional[datetime] = Query(None, description="End timestamp"),
    granularity: str = Query("day", description="Time granularity: day, month, year"),
    user: TokenData = Depends(get_current_user)
):
    """
    Get aggregated fleet KPIs and time series data.
    
    Data is filtered by the user's role:
    - Territory managers see only their territory
    - Regional managers see their entire region
    - Admins see everything
    """
    
    # Get summary stats
    summary_data = queries.get_fleet_summary(
        role=user.role,
        customer_id=customer_id,
        start_ts=start_ts,
        end_ts=end_ts,
        granularity=granularity
    )
    
    # Get time series
    timeseries_data = queries.get_fleet_timeseries(
        role=user.role,
        customer_id=customer_id,
        start_ts=start_ts,
        end_ts=end_ts,
        granularity=granularity
    )
    
    return FleetSummaryResponse(
        summary=FleetSummary(**summary_data),
        timeseries=[TimeSeriesPoint(**ts) for ts in timeseries_data]
    )


@router.get("/vehicles", response_model=VehicleListResponse)
async def get_vehicles(
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    region_id: Optional[str] = Query(None, description="Filter by region"),
    territory_id: Optional[str] = Query(None, description="Filter by territory"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user: TokenData = Depends(get_current_user)
):
    """
    Get list of vehicles with current state.
    
    Results are filtered by the user's role through RLS.
    """
    
    vehicles_data = queries.get_vehicles(
        role=user.role,
        customer_id=customer_id,
        region_id=region_id,
        territory_id=territory_id,
        limit=limit,
        offset=offset
    )
    
    return VehicleListResponse(
        vehicles=[Vehicle(**v) for v in vehicles_data],
        total=len(vehicles_data),  # In production, get actual count
        limit=limit,
        offset=offset
    )


@router.get("/vehicle/{vehicle_id}/telemetry", response_model=VehicleTelemetryResponse)
async def get_vehicle_telemetry(
    vehicle_id: str,
    start_ts: Optional[datetime] = Query(None, description="Start timestamp"),
    end_ts: Optional[datetime] = Query(None, description="End timestamp"),
    limit: int = Query(1000, ge=1, le=10000, description="Max data points"),
    user: TokenData = Depends(get_current_user)
):
    """
    Get telemetry time series for a specific vehicle.
    
    Access is controlled by RLS - users can only see vehicles in their scope.
    """
    
    telemetry_data = queries.get_vehicle_telemetry(
        role=user.role,
        vehicle_id=vehicle_id,
        start_ts=start_ts,
        end_ts=end_ts,
        limit=limit
    )
    
    if not telemetry_data:
        # Could be unauthorized or vehicle not found
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle {vehicle_id} not found or not accessible"
        )
    
    return VehicleTelemetryResponse(
        vehicle_id=vehicle_id,
        telemetry=[TelemetryPoint(**t) for t in telemetry_data]
    )


@router.get("/anomalies", response_model=AnomalyListResponse)
async def get_anomalies(
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    region_id: Optional[str] = Query(None, description="Filter by region"),
    territory_id: Optional[str] = Query(None, description="Filter by territory"),
    severity: Optional[str] = Query(None, description="Filter by severity: critical, warning, info"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgement status"),
    start_ts: Optional[datetime] = Query(None, description="Start timestamp"),
    end_ts: Optional[datetime] = Query(None, description="End timestamp"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user: TokenData = Depends(get_current_user)
):
    """
    Get list of anomalies with filters.
    
    Results are filtered by the user's role through RLS.
    """
    
    anomalies_data = queries.get_anomalies(
        role=user.role,
        customer_id=customer_id,
        region_id=region_id,
        territory_id=territory_id,
        severity=severity,
        acknowledged=acknowledged,
        start_ts=start_ts,
        end_ts=end_ts,
        limit=limit,
        offset=offset
    )
    
    return AnomalyListResponse(
        anomalies=[Anomaly(**a) for a in anomalies_data],
        total=len(anomalies_data),
        limit=limit,
        offset=offset
    )


@router.post("/anomalies/{anomaly_id}/ack", response_model=AcknowledgeResponse)
async def acknowledge_anomaly(
    anomaly_id: str,
    user: TokenData = Depends(get_current_user)
):
    """
    Acknowledge an anomaly.
    
    This is a transactional write operation demonstrating
    SingleStore's rowstore transaction capabilities.
    """
    
    success = queries.acknowledge_anomaly(
        anomaly_id=anomaly_id,
        user_id=user.username,
        role=user.role
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Anomaly {anomaly_id} not found"
        )
    
    return AcknowledgeResponse(
        success=True,
        anomaly_id=anomaly_id,
        acknowledged_by=user.username
    )


@router.get("/notes", response_model=DriverNotesResponse)
async def get_driver_notes(
    vehicle_id: Optional[str] = Query(None, description="Filter by vehicle"),
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    start_ts: Optional[datetime] = Query(None, description="Start timestamp"),
    end_ts: Optional[datetime] = Query(None, description="End timestamp"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    user: TokenData = Depends(get_current_user)
):
    """
    Get driver notes for AI summarization.
    
    Results are filtered by the user's role through RLS.
    """
    
    notes_data = queries.get_driver_notes(
        role=user.role,
        vehicle_id=vehicle_id,
        customer_id=customer_id,
        start_ts=start_ts,
        end_ts=end_ts,
        limit=limit
    )
    
    return DriverNotesResponse(
        notes=[DriverNote(**n) for n in notes_data]
    )

