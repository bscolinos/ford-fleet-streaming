"""
SQL query functions for fleet management operations.
All reads use RLS views to ensure proper access control.
"""

from datetime import datetime
from typing import Optional

from app.db.connection import execute_query, execute_write


# =============================================================================
# Fleet Summary Queries
# =============================================================================

def get_fleet_summary(
    role: str,
    customer_id: Optional[str] = None,
    start_ts: Optional[datetime] = None,
    end_ts: Optional[datetime] = None,
    granularity: str = "day"
) -> dict:
    """Get aggregated KPIs for the fleet."""
    
    # Base query for vehicle counts (uses RLS view)
    vehicle_sql = """
        SELECT 
            COUNT(*) as total_vehicles,
            COUNT(DISTINCT vs.vehicle_id) as active_vehicles
        FROM vehicles v
        LEFT JOIN vehicle_state vs ON v.vehicle_id = vs.vehicle_id
            AND vs.last_seen_ts > DATE_SUB(NOW(), INTERVAL 5 MINUTE)
    """
    
    params = []
    where_clauses = []
    
    if customer_id:
        where_clauses.append("v.customer_id = %s")
        params.append(customer_id)
    
    if where_clauses:
        vehicle_sql += " WHERE " + " AND ".join(where_clauses)
    
    vehicle_result = execute_query(vehicle_sql, tuple(params), role)
    
    # Telemetry aggregations
    telemetry_sql = """
        SELECT 
            AVG(speed) as avg_speed,
            AVG(fuel_pct) as avg_fuel_pct,
            AVG(engine_temp) as avg_engine_temp,
            COUNT(*) as telemetry_count
        FROM telemetry_raw
        WHERE 1=1
    """
    
    telem_params = []
    if customer_id:
        telemetry_sql += " AND customer_id = %s"
        telem_params.append(customer_id)
    if start_ts:
        telemetry_sql += " AND ts >= %s"
        telem_params.append(start_ts)
    if end_ts:
        telemetry_sql += " AND ts <= %s"
        telem_params.append(end_ts)
    
    telemetry_result = execute_query(telemetry_sql, tuple(telem_params), role)
    
    # Anomaly count
    anomaly_sql = """
        SELECT 
            COUNT(*) as total_anomalies,
            SUM(CASE WHEN acknowledged = 0 THEN 1 ELSE 0 END) as unacknowledged,
            SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_count
        FROM anomalies
        WHERE 1=1
    """
    
    anom_params = []
    if customer_id:
        anomaly_sql += " AND customer_id = %s"
        anom_params.append(customer_id)
    if start_ts:
        anomaly_sql += " AND detected_at >= %s"
        anom_params.append(start_ts)
    if end_ts:
        anomaly_sql += " AND detected_at <= %s"
        anom_params.append(end_ts)
    
    anomaly_result = execute_query(anomaly_sql, tuple(anom_params), role)
    
    return {
        "total_vehicles": vehicle_result[0]["total_vehicles"] if vehicle_result else 0,
        "active_vehicles": vehicle_result[0]["active_vehicles"] if vehicle_result else 0,
        "avg_speed": float(telemetry_result[0]["avg_speed"] or 0) if telemetry_result else 0,
        "avg_fuel_pct": float(telemetry_result[0]["avg_fuel_pct"] or 0) if telemetry_result else 0,
        "avg_engine_temp": float(telemetry_result[0]["avg_engine_temp"] or 0) if telemetry_result else 0,
        "telemetry_count": telemetry_result[0]["telemetry_count"] if telemetry_result else 0,
        "total_anomalies": anomaly_result[0]["total_anomalies"] if anomaly_result else 0,
        "unacknowledged_anomalies": anomaly_result[0]["unacknowledged"] if anomaly_result else 0,
        "critical_anomalies": anomaly_result[0]["critical_count"] if anomaly_result else 0,
    }


def get_fleet_timeseries(
    role: str,
    customer_id: Optional[str] = None,
    start_ts: Optional[datetime] = None,
    end_ts: Optional[datetime] = None,
    granularity: str = "day"
) -> list:
    """Get time-series data for dashboard charts."""
    
    # Determine date truncation based on granularity
    if granularity == "year":
        date_trunc = "DATE_FORMAT(ts, '%Y-01-01')"
    elif granularity == "month":
        date_trunc = "DATE_FORMAT(ts, '%Y-%m-01')"
    else:  # day
        date_trunc = "DATE(ts)"
    
    sql = f"""
        SELECT 
            {date_trunc} as period,
            AVG(speed) as avg_speed,
            AVG(fuel_pct) as avg_fuel,
            AVG(engine_temp) as avg_temp,
            COUNT(*) as event_count,
            COUNT(DISTINCT vehicle_id) as vehicle_count
        FROM telemetry_raw
        WHERE 1=1
    """
    
    params = []
    if customer_id:
        sql += " AND customer_id = %s"
        params.append(customer_id)
    if start_ts:
        sql += " AND ts >= %s"
        params.append(start_ts)
    if end_ts:
        sql += " AND ts <= %s"
        params.append(end_ts)
    
    sql += f" GROUP BY {date_trunc} ORDER BY period"
    
    results = execute_query(sql, tuple(params), role)
    
    # Convert decimals to floats
    for row in results:
        row["period"] = str(row["period"])
        row["avg_speed"] = float(row["avg_speed"] or 0)
        row["avg_fuel"] = float(row["avg_fuel"] or 0)
        row["avg_temp"] = float(row["avg_temp"] or 0)
    
    return results


# =============================================================================
# Vehicle Queries
# =============================================================================

def get_vehicles(
    role: str,
    customer_id: Optional[str] = None,
    region_id: Optional[str] = None,
    territory_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> list:
    """Get vehicles visible to the user with filters."""
    
    sql = """
        SELECT 
            v.vehicle_id,
            v.customer_id,
            v.region_id,
            v.territory_id,
            v.vin,
            v.make,
            v.model,
            v.year,
            v.color,
            v.license_plate,
            v.driver_name,
            vs.last_seen_ts,
            vs.status,
            vs.lat,
            vs.lon,
            vs.speed,
            vs.fuel_pct,
            vs.engine_temp,
            vs.battery_v,
            vs.odometer
        FROM vehicles v
        LEFT JOIN vehicle_state vs ON v.vehicle_id = vs.vehicle_id
        WHERE 1=1
    """
    
    params = []
    if customer_id:
        sql += " AND v.customer_id = %s"
        params.append(customer_id)
    if region_id:
        sql += " AND v.region_id = %s"
        params.append(region_id)
    if territory_id:
        sql += " AND v.territory_id = %s"
        params.append(territory_id)
    
    sql += " ORDER BY v.vehicle_id LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    results = execute_query(sql, tuple(params), role)
    
    # Convert types
    for row in results:
        if row.get("last_seen_ts"):
            row["last_seen_ts"] = row["last_seen_ts"].isoformat() if hasattr(row["last_seen_ts"], 'isoformat') else str(row["last_seen_ts"])
        for field in ["lat", "lon", "speed", "fuel_pct", "engine_temp", "battery_v"]:
            if row.get(field) is not None:
                row[field] = float(row[field])
    
    return results


def get_vehicle_telemetry(
    role: str,
    vehicle_id: str,
    start_ts: Optional[datetime] = None,
    end_ts: Optional[datetime] = None,
    limit: int = 1000
) -> list:
    """Get telemetry time series for a specific vehicle."""
    
    sql = """
        SELECT 
            ts,
            lat,
            lon,
            speed,
            engine_temp,
            fuel_pct,
            battery_v,
            odometer,
            dtc_code,
            heading,
            rpm,
            throttle_pct
        FROM telemetry_raw
        WHERE vehicle_id = %s
    """
    
    params = [vehicle_id]
    if start_ts:
        sql += " AND ts >= %s"
        params.append(start_ts)
    if end_ts:
        sql += " AND ts <= %s"
        params.append(end_ts)
    
    sql += " ORDER BY ts DESC LIMIT %s"
    params.append(limit)
    
    results = execute_query(sql, tuple(params), role)
    
    # Convert types
    for row in results:
        row["ts"] = row["ts"].isoformat() if hasattr(row["ts"], 'isoformat') else str(row["ts"])
        for field in ["lat", "lon", "speed", "engine_temp", "fuel_pct", "battery_v", "throttle_pct"]:
            if row.get(field) is not None:
                row[field] = float(row[field])
    
    return results


# =============================================================================
# Anomaly Queries
# =============================================================================

def get_anomalies(
    role: str,
    customer_id: Optional[str] = None,
    region_id: Optional[str] = None,
    territory_id: Optional[str] = None,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    start_ts: Optional[datetime] = None,
    end_ts: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> list:
    """Get anomalies with filters."""
    
    sql = """
        SELECT 
            a.anomaly_id,
            a.vehicle_id,
            a.customer_id,
            a.region_id,
            a.territory_id,
            a.detected_at,
            a.anomaly_type,
            a.severity,
            a.description,
            a.metric_value,
            a.threshold_value,
            a.acknowledged,
            a.acknowledged_by,
            a.acknowledged_at,
            v.make,
            v.model,
            v.license_plate,
            v.driver_name
        FROM anomalies a
        LEFT JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        WHERE 1=1
    """
    
    params = []
    if customer_id:
        sql += " AND a.customer_id = %s"
        params.append(customer_id)
    if region_id:
        sql += " AND a.region_id = %s"
        params.append(region_id)
    if territory_id:
        sql += " AND a.territory_id = %s"
        params.append(territory_id)
    if severity:
        sql += " AND a.severity = %s"
        params.append(severity)
    if acknowledged is not None:
        sql += " AND a.acknowledged = %s"
        params.append(1 if acknowledged else 0)
    if start_ts:
        sql += " AND a.detected_at >= %s"
        params.append(start_ts)
    if end_ts:
        sql += " AND a.detected_at <= %s"
        params.append(end_ts)
    
    sql += " ORDER BY a.detected_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    results = execute_query(sql, tuple(params), role)
    
    # Convert types
    for row in results:
        row["detected_at"] = row["detected_at"].isoformat() if hasattr(row["detected_at"], 'isoformat') else str(row["detected_at"])
        if row.get("acknowledged_at"):
            row["acknowledged_at"] = row["acknowledged_at"].isoformat() if hasattr(row["acknowledged_at"], 'isoformat') else str(row["acknowledged_at"])
        for field in ["metric_value", "threshold_value"]:
            if row.get(field) is not None:
                row[field] = float(row[field])
        row["acknowledged"] = bool(row.get("acknowledged"))
    
    return results


def acknowledge_anomaly(anomaly_id: str, user_id: str, role: str) -> bool:
    """Acknowledge an anomaly (transactional write)."""
    
    sql = """
        UPDATE anomalies 
        SET acknowledged = 1, 
            acknowledged_by = %s, 
            acknowledged_at = NOW()
        WHERE anomaly_id = %s
    """
    
    # Note: We use base table for writes, not RLS view
    # The app layer controls write access via role checks
    rows_affected = execute_write(sql, (user_id, anomaly_id), role)
    return rows_affected > 0


# =============================================================================
# Driver Notes Queries
# =============================================================================

def get_driver_notes(
    role: str,
    vehicle_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    start_ts: Optional[datetime] = None,
    end_ts: Optional[datetime] = None,
    limit: int = 50
) -> list:
    """Get driver notes for AI summarization."""
    
    sql = """
        SELECT 
            note_id,
            vehicle_id,
            customer_id,
            driver_id,
            driver_name,
            ts,
            note_text,
            category,
            region_id,
            territory_id
        FROM driver_notes
        WHERE 1=1
    """
    
    params = []
    if vehicle_id:
        sql += " AND vehicle_id = %s"
        params.append(vehicle_id)
    if customer_id:
        sql += " AND customer_id = %s"
        params.append(customer_id)
    if start_ts:
        sql += " AND ts >= %s"
        params.append(start_ts)
    if end_ts:
        sql += " AND ts <= %s"
        params.append(end_ts)
    
    sql += " ORDER BY ts DESC LIMIT %s"
    params.append(limit)
    
    results = execute_query(sql, tuple(params), role)
    
    for row in results:
        row["ts"] = row["ts"].isoformat() if hasattr(row["ts"], 'isoformat') else str(row["ts"])
    
    return results


# =============================================================================
# Real-time Dashboard Queries
# =============================================================================

def get_realtime_stats(role: str) -> dict:
    """Get real-time statistics for WebSocket updates."""
    
    # Recent telemetry (last 5 seconds)
    recent_sql = """
        SELECT 
            COUNT(*) as events_5s,
            AVG(speed) as avg_speed,
            MAX(speed) as max_speed,
            AVG(engine_temp) as avg_temp,
            MAX(engine_temp) as max_temp
        FROM telemetry_raw
        WHERE ts > DATE_SUB(NOW(), INTERVAL 5 SECOND)
    """
    
    recent = execute_query(recent_sql, (), role)
    
    # Active vehicles (seen in last minute)
    active_sql = """
        SELECT COUNT(*) as active_count
        FROM vehicle_state
        WHERE last_seen_ts > DATE_SUB(NOW(), INTERVAL 1 MINUTE)
    """
    
    active = execute_query(active_sql, (), role)
    
    # Recent anomalies (last minute, unacknowledged)
    anomaly_sql = """
        SELECT 
            anomaly_id,
            vehicle_id,
            anomaly_type,
            severity,
            detected_at
        FROM anomalies
        WHERE detected_at > DATE_SUB(NOW(), INTERVAL 1 MINUTE)
            AND acknowledged = 0
        ORDER BY detected_at DESC
        LIMIT 10
    """
    
    anomalies = execute_query(anomaly_sql, (), role)
    
    for a in anomalies:
        a["detected_at"] = a["detected_at"].isoformat() if hasattr(a["detected_at"], 'isoformat') else str(a["detected_at"])
    
    return {
        "events_per_5s": recent[0]["events_5s"] if recent else 0,
        "avg_speed": float(recent[0]["avg_speed"] or 0) if recent else 0,
        "max_speed": float(recent[0]["max_speed"] or 0) if recent else 0,
        "avg_temp": float(recent[0]["avg_temp"] or 0) if recent else 0,
        "max_temp": float(recent[0]["max_temp"] or 0) if recent else 0,
        "active_vehicles": active[0]["active_count"] if active else 0,
        "recent_anomalies": anomalies
    }

