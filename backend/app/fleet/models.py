"""
Pydantic models for fleet API endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# =============================================================================
# Fleet Summary Models
# =============================================================================

class FleetSummary(BaseModel):
    """Aggregated fleet KPIs."""
    total_vehicles: int
    active_vehicles: int
    avg_speed: float
    avg_fuel_pct: float
    avg_engine_temp: float
    telemetry_count: int
    total_anomalies: int
    unacknowledged_anomalies: int
    critical_anomalies: int


class TimeSeriesPoint(BaseModel):
    """Single point in a time series."""
    period: str
    avg_speed: float
    avg_fuel: float
    avg_temp: float
    event_count: int
    vehicle_count: int


class FleetSummaryResponse(BaseModel):
    """Complete fleet summary with time series."""
    summary: FleetSummary
    timeseries: list[TimeSeriesPoint]


# =============================================================================
# Vehicle Models
# =============================================================================

class Vehicle(BaseModel):
    """Vehicle with current state."""
    vehicle_id: str
    customer_id: str
    region_id: str
    territory_id: str
    vin: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    license_plate: Optional[str] = None
    driver_name: Optional[str] = None
    last_seen_ts: Optional[str] = None
    status: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    speed: Optional[float] = None
    fuel_pct: Optional[float] = None
    engine_temp: Optional[float] = None
    battery_v: Optional[float] = None
    odometer: Optional[int] = None


class VehicleListResponse(BaseModel):
    """Paginated vehicle list."""
    vehicles: list[Vehicle]
    total: int
    limit: int
    offset: int


class TelemetryPoint(BaseModel):
    """Single telemetry data point."""
    ts: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    speed: Optional[float] = None
    engine_temp: Optional[float] = None
    fuel_pct: Optional[float] = None
    battery_v: Optional[float] = None
    odometer: Optional[int] = None
    dtc_code: Optional[str] = None
    heading: Optional[float] = None
    rpm: Optional[int] = None
    throttle_pct: Optional[float] = None


class VehicleTelemetryResponse(BaseModel):
    """Vehicle telemetry time series."""
    vehicle_id: str
    telemetry: list[TelemetryPoint]


# =============================================================================
# Anomaly Models
# =============================================================================

class Anomaly(BaseModel):
    """Detected anomaly with vehicle info."""
    anomaly_id: str
    vehicle_id: str
    customer_id: str
    region_id: str
    territory_id: str
    detected_at: str
    anomaly_type: str
    severity: str
    description: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    license_plate: Optional[str] = None
    driver_name: Optional[str] = None


class AnomalyListResponse(BaseModel):
    """Paginated anomaly list."""
    anomalies: list[Anomaly]
    total: int
    limit: int
    offset: int


class AcknowledgeRequest(BaseModel):
    """Request to acknowledge an anomaly."""
    pass  # No body needed, user comes from JWT


class AcknowledgeResponse(BaseModel):
    """Response after acknowledging an anomaly."""
    success: bool
    anomaly_id: str
    acknowledged_by: str


# =============================================================================
# Driver Notes Models
# =============================================================================

class DriverNote(BaseModel):
    """Driver note entry."""
    note_id: str
    vehicle_id: str
    customer_id: str
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    ts: str
    note_text: str
    category: Optional[str] = None
    region_id: str
    territory_id: str


class DriverNotesResponse(BaseModel):
    """List of driver notes."""
    notes: list[DriverNote]

