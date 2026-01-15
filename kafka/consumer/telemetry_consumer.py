"""
Ford Fleet Management Demo - Kafka Telemetry Consumer

Consumes telematics events from customer topics and:
1. Batch inserts into telemetry_raw table
2. Updates vehicle_state with latest position/status
3. Runs anomaly detection and inserts detected anomalies
"""

import json
import os
import socket
import time
import uuid
from datetime import datetime
from typing import Any

import singlestoredb as s2
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

# Configuration from environment
kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
db_host = os.getenv("SINGLESTORE_HOST", "localhost")
db_port = int(os.getenv("SINGLESTORE_PORT", "3306"))
db_user = os.getenv("SINGLESTORE_USER", "admin")
db_password = os.getenv("SINGLESTORE_PASSWORD", "")
db_name = os.getenv("SINGLESTORE_DATABASE", "ford_fleet")


def resolve_hostname(hostname: str) -> str:
    """Resolve hostname with fallback to public DNS for macOS compatibility."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        pass

    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        answers = resolver.resolve(hostname, 'A')
        return str(answers[0])
    except Exception:
        return hostname

batch_size = int(os.getenv("BATCH_SIZE", "100"))
batch_timeout = float(os.getenv("BATCH_TIMEOUT", "1.0"))

# Topics to consume
topics = [
    "customer_a_telemetry",
    "customer_b_telemetry"
]

# Anomaly detection thresholds
anomaly_thresholds = {
    "high_engine_temp": {"field": "engine_temp", "threshold": 220, "severity": "critical"},
    "low_battery": {"field": "battery_v", "threshold": 11.5, "severity": "warning", "below": True},
    "speeding": {"field": "speed", "threshold": 80, "severity": "info"},
    "low_fuel": {"field": "fuel_pct", "threshold": 10, "severity": "warning", "below": True},
}


def create_consumer() -> KafkaConsumer:
    """Create Kafka consumer with retry logic."""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=kafka_bootstrap,
                group_id="fleet-telemetry-consumer",
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                max_poll_records=500,
                session_timeout_ms=30000
            )
            print(f"Connected to Kafka at {kafka_bootstrap}")
            print(f"Subscribed to topics: {topics}")
            return consumer
        except NoBrokersAvailable:
            print(f"Waiting for Kafka... attempt {attempt + 1}/{max_retries}")
            time.sleep(retry_delay)
    
    raise RuntimeError(f"Could not connect to Kafka at {kafka_bootstrap}")


def create_db_connection():
    """Create SingleStore database connection with retry logic."""
    max_retries = 30
    retry_delay = 2
    resolved_host = resolve_hostname(db_host)

    for attempt in range(max_retries):
        try:
            conn = s2.connect(
                host=resolved_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name
            )
            print(f"Connected to SingleStore at {db_host} ({resolved_host}):{db_port}")
            return conn
        except Exception as e:
            print(f"Waiting for SingleStore... attempt {attempt + 1}/{max_retries}: {e}")
            time.sleep(retry_delay)

    raise RuntimeError(f"Could not connect to SingleStore at {db_host}:{db_port}")


def detect_anomalies(event: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect anomalies in a telemetry event."""
    anomalies = []
    
    for anomaly_type, config in anomaly_thresholds.items():
        field = config["field"]
        threshold = config["threshold"]
        severity = config["severity"]
        is_below = config.get("below", False)
        
        value = event.get(field)
        if value is None:
            continue
        
        triggered = value < threshold if is_below else value > threshold
        
        if triggered:
            anomaly = {
                "anomaly_id": str(uuid.uuid4()),
                "vehicle_id": event["vehicle_id"],
                "customer_id": event["customer_id"],
                "region_id": event["region_id"],
                "territory_id": event["territory_id"],
                "detected_at": event["ts"],
                "anomaly_type": anomaly_type.upper(),
                "severity": severity,
                "description": f"{field} {'below' if is_below else 'above'} threshold: {value:.2f} vs {threshold}",
                "metric_value": value,
                "threshold_value": threshold,
                "access_roles": event["access_roles"]
            }
            anomalies.append(anomaly)
    
    # Check for DTC codes
    if event.get("dtc_code"):
        anomaly = {
            "anomaly_id": str(uuid.uuid4()),
            "vehicle_id": event["vehicle_id"],
            "customer_id": event["customer_id"],
            "region_id": event["region_id"],
            "territory_id": event["territory_id"],
            "detected_at": event["ts"],
            "anomaly_type": "DTC_PRESENT",
            "severity": "warning",
            "description": f"Diagnostic trouble code detected: {event['dtc_code']}",
            "metric_value": None,
            "threshold_value": None,
            "access_roles": event["access_roles"]
        }
        anomalies.append(anomaly)
    
    return anomalies


def batch_insert_telemetry(conn, events: list[dict[str, Any]]):
    """Batch insert telemetry events into telemetry_raw table."""
    if not events:
        return
    
    sql = """
        INSERT INTO telemetry_raw 
        (customer_id, vehicle_id, ts, region_id, territory_id, lat, lon, 
         speed, engine_temp, fuel_pct, battery_v, odometer, dtc_code, 
         heading, rpm, throttle_pct, access_roles)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = []
    for e in events:
        values.append((
            e["customer_id"],
            e["vehicle_id"],
            e["ts"],
            e["region_id"],
            e["territory_id"],
            e.get("lat"),
            e.get("lon"),
            e.get("speed"),
            e.get("engine_temp"),
            e.get("fuel_pct"),
            e.get("battery_v"),
            e.get("odometer"),
            e.get("dtc_code"),
            e.get("heading"),
            e.get("rpm"),
            e.get("throttle_pct"),
            e["access_roles"]
        ))
    
    with conn.cursor() as cursor:
        cursor.executemany(sql, values)
    conn.commit()


def batch_update_vehicle_state(conn, events: list[dict[str, Any]]):
    """Update vehicle_state with latest telemetry for each vehicle."""
    if not events:
        return
    
    # Get latest event per vehicle
    latest_by_vehicle = {}
    for e in events:
        vid = e["vehicle_id"]
        if vid not in latest_by_vehicle or e["ts"] > latest_by_vehicle[vid]["ts"]:
            latest_by_vehicle[vid] = e
    
    # Use INSERT ... ON DUPLICATE KEY UPDATE pattern
    # Since we don't have unique keys, we'll use REPLACE or a more complex upsert
    sql = """
        REPLACE INTO vehicle_state 
        (vehicle_id, last_seen_ts, status, lat, lon, speed, heading, 
         fuel_pct, engine_temp, battery_v, odometer)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = []
    for e in latest_by_vehicle.values():
        values.append((
            e["vehicle_id"],
            e["ts"],
            "active",
            e.get("lat"),
            e.get("lon"),
            e.get("speed"),
            e.get("heading"),
            e.get("fuel_pct"),
            e.get("engine_temp"),
            e.get("battery_v"),
            e.get("odometer")
        ))
    
    with conn.cursor() as cursor:
        cursor.executemany(sql, values)
    conn.commit()


def batch_insert_anomalies(conn, anomalies: list[dict[str, Any]]):
    """Batch insert detected anomalies."""
    if not anomalies:
        return
    
    sql = """
        INSERT INTO anomalies 
        (anomaly_id, vehicle_id, customer_id, region_id, territory_id,
         detected_at, anomaly_type, severity, description, 
         metric_value, threshold_value, access_roles)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = []
    for a in anomalies:
        values.append((
            a["anomaly_id"],
            a["vehicle_id"],
            a["customer_id"],
            a["region_id"],
            a["territory_id"],
            a["detected_at"],
            a["anomaly_type"],
            a["severity"],
            a["description"],
            a.get("metric_value"),
            a.get("threshold_value"),
            a["access_roles"]
        ))
    
    with conn.cursor() as cursor:
        cursor.executemany(sql, values)
    conn.commit()


def main():
    """Main consumer loop."""
    print("=" * 60)
    print("Ford Fleet Management - Telemetry Consumer")
    print("=" * 60)
    print(f"Kafka Bootstrap: {kafka_bootstrap}")
    print(f"SingleStore: {db_host}:{db_port}/{db_name}")
    print(f"Batch size: {batch_size}")
    print(f"Batch timeout: {batch_timeout}s")
    print()
    
    # Create connections
    consumer = create_consumer()
    conn = create_db_connection()
    
    print("\nStarting consumption...\n")
    
    event_batch = []
    anomaly_batch = []
    last_flush = time.time()
    total_events = 0
    total_anomalies = 0
    
    try:
        while True:
            # Poll for messages
            messages = consumer.poll(timeout_ms=100)
            
            for topic_partition, records in messages.items():
                for record in records:
                    event = record.value
                    event_batch.append(event)
                    
                    # Detect anomalies
                    anomalies = detect_anomalies(event)
                    anomaly_batch.extend(anomalies)
            
            # Check if we should flush
            should_flush = (
                len(event_batch) >= batch_size or
                (time.time() - last_flush) >= batch_timeout and event_batch
            )
            
            if should_flush:
                try:
                    # Batch insert telemetry
                    batch_insert_telemetry(conn, event_batch)
                    
                    # Update vehicle states
                    batch_update_vehicle_state(conn, event_batch)
                    
                    # Insert anomalies
                    batch_insert_anomalies(conn, anomaly_batch)
                    
                    total_events += len(event_batch)
                    total_anomalies += len(anomaly_batch)
                    
                    if total_events % 1000 == 0 or anomaly_batch:
                        print(f"Processed {total_events:,} events | "
                              f"Anomalies: {total_anomalies:,} | "
                              f"Batch: {len(event_batch)} events, {len(anomaly_batch)} anomalies")
                    
                    event_batch = []
                    anomaly_batch = []
                    last_flush = time.time()
                    
                except Exception as e:
                    print(f"Error during batch processing: {e}")
                    # Try to reconnect
                    try:
                        conn.close()
                    except:
                        pass
                    conn = create_db_connection()
                    
    except KeyboardInterrupt:
        print("\n\nShutting down consumer...")
        consumer.close()
        conn.close()
        print(f"Total events processed: {total_events:,}")
        print(f"Total anomalies detected: {total_anomalies:,}")


if __name__ == "__main__":
    main()

