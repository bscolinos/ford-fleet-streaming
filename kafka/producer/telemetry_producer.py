"""
Ford Fleet Management Demo - Kafka Telemetry Producer

Generates simulated telematics events for each customer topic.
Events include vehicle location, speed, engine metrics, and occasional anomalies.
"""

import json
import os
import random
import time
import uuid
from datetime import datetime
from typing import Any

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# Configuration from environment
kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
events_per_second = float(os.getenv("EVENTS_PER_SECOND", "10"))
anomaly_probability = float(os.getenv("ANOMALY_PROBABILITY", "0.02"))

# Customer configuration - each customer has their own topic
customers = [
    {
        "customer_id": "customer_a",
        "topic": "customer_a_telemetry",
        "name": "Acme Logistics"
    },
    {
        "customer_id": "customer_b", 
        "topic": "customer_b_telemetry",
        "name": "BlueStar Transport"
    }
]

# Vehicle configuration by region/territory
# Format: (vehicle_id_prefix, region_id, territory_id, base_lat, base_lon, count)
vehicle_configs = {
    "customer_a": [
        ("v_a_w1_", "WEST", "WEST_1", 47.6062, -122.3321, 20),
        ("v_a_w2_", "WEST", "WEST_2", 33.4484, -112.0740, 20),
        ("v_a_e1_", "EAST", "EAST_1", 40.7128, -74.0060, 15),
        ("v_a_e2_", "EAST", "EAST_2", 28.5383, -81.3792, 20),
        ("v_a_c1_", "CENTRAL", "CENTRAL_1", 41.8781, -87.6298, 12),
        ("v_a_c2_", "CENTRAL", "CENTRAL_2", 39.0997, -94.5786, 13),
    ],
    "customer_b": [
        ("v_b_w1_", "WEST", "WEST_1", 47.6062, -122.3321, 15),
        ("v_b_w2_", "WEST", "WEST_2", 33.4484, -112.0740, 15),
        ("v_b_e1_", "EAST", "EAST_1", 40.7128, -74.0060, 15),
        ("v_b_e2_", "EAST", "EAST_2", 28.5383, -81.3792, 15),
        ("v_b_c1_", "CENTRAL", "CENTRAL_1", 41.8781, -87.6298, 10),
        ("v_b_c2_", "CENTRAL", "CENTRAL_2", 39.0997, -94.5786, 10),
    ]
}

# DTC codes for anomaly simulation
dtc_codes = [
    "P0171",  # System too lean
    "P0300",  # Random misfire
    "P0420",  # Catalyst efficiency
    "P0442",  # EVAP leak
    "P0500",  # Vehicle speed sensor
    "P0700",  # Transmission control
    "P0562",  # System voltage low
    "P0128",  # Coolant thermostat
]


class VehicleSimulator:
    """Simulates a single vehicle's telemetry data."""
    
    def __init__(self, vehicle_id: str, customer_id: str, region_id: str, 
                 territory_id: str, base_lat: float, base_lon: float):
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.region_id = region_id
        self.territory_id = territory_id
        
        # Initial position with some randomness
        self.lat = base_lat + random.uniform(-0.5, 0.5)
        self.lon = base_lon + random.uniform(-0.5, 0.5)
        
        # Vehicle state
        self.heading = random.uniform(0, 360)
        self.speed = random.uniform(0, 45)
        self.engine_temp = random.uniform(180, 210)
        self.fuel_pct = random.uniform(40, 100)
        self.battery_v = random.uniform(12.4, 14.4)
        self.odometer = random.randint(10000, 100000)
        self.rpm = random.randint(800, 2500)
        self.throttle_pct = random.uniform(0, 50)
        
        # Access roles for RLS - format: ,TERRITORY_X,REGION_Y,ADMIN_ALL,
        self.access_roles = f",territory_{territory_id.lower()},region_{region_id.lower()},admin_all,"
        
    def generate_event(self) -> dict[str, Any]:
        """Generate a telemetry event with realistic changes."""
        # Update position based on heading and speed
        speed_factor = self.speed / 3600 / 69  # Approximate degrees per second
        self.lat += speed_factor * random.uniform(-0.5, 1.5) * (1 if random.random() > 0.5 else -1)
        self.lon += speed_factor * random.uniform(-0.5, 1.5) * (1 if random.random() > 0.5 else -1)
        
        # Constrain to reasonable bounds
        self.lat = max(min(self.lat, 49.0), 25.0)
        self.lon = max(min(self.lon, -70.0), -125.0)
        
        # Update heading
        self.heading = (self.heading + random.uniform(-15, 15)) % 360
        
        # Update speed with some momentum
        speed_change = random.uniform(-5, 5)
        self.speed = max(0, min(85, self.speed + speed_change))
        
        # Engine temp varies slowly
        if random.random() < anomaly_probability:
            # Potential overheating anomaly
            self.engine_temp = random.uniform(220, 250)
        else:
            self.engine_temp = max(170, min(220, self.engine_temp + random.uniform(-2, 2)))
        
        # Fuel decreases over time
        self.fuel_pct = max(5, self.fuel_pct - random.uniform(0, 0.1))
        if self.fuel_pct < 15 and random.random() > 0.8:
            # Refuel occasionally when low
            self.fuel_pct = random.uniform(80, 100)
        
        # Battery voltage
        if random.random() < anomaly_probability:
            # Low battery anomaly
            self.battery_v = random.uniform(10.5, 11.5)
        else:
            self.battery_v = max(11.5, min(14.8, self.battery_v + random.uniform(-0.1, 0.1)))
        
        # Odometer always increases
        self.odometer += random.randint(0, 2)
        
        # RPM correlates with speed
        self.rpm = int(800 + (self.speed / 85) * 4000 + random.uniform(-200, 200))
        self.rpm = max(600, min(6000, self.rpm))
        
        # Throttle
        self.throttle_pct = max(0, min(100, self.speed / 85 * 100 + random.uniform(-10, 10)))
        
        # DTC code (anomaly)
        dtc_code = None
        if random.random() < anomaly_probability:
            dtc_code = random.choice(dtc_codes)
        
        return {
            "customer_id": self.customer_id,
            "vehicle_id": self.vehicle_id,
            "ts": datetime.utcnow().isoformat(timespec='microseconds') + "Z",
            "region_id": self.region_id,
            "territory_id": self.territory_id,
            "lat": round(self.lat, 7),
            "lon": round(self.lon, 7),
            "speed": round(self.speed, 2),
            "engine_temp": round(self.engine_temp, 2),
            "fuel_pct": round(self.fuel_pct, 2),
            "battery_v": round(self.battery_v, 2),
            "odometer": self.odometer,
            "dtc_code": dtc_code,
            "heading": round(self.heading, 2),
            "rpm": self.rpm,
            "throttle_pct": round(self.throttle_pct, 2),
            "access_roles": self.access_roles
        }


def create_producer() -> KafkaProducer:
    """Create Kafka producer with retry logic."""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_bootstrap,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                linger_ms=10,
                batch_size=16384
            )
            print(f"Connected to Kafka at {kafka_bootstrap}")
            return producer
        except NoBrokersAvailable:
            print(f"Waiting for Kafka... attempt {attempt + 1}/{max_retries}")
            time.sleep(retry_delay)
    
    raise RuntimeError(f"Could not connect to Kafka at {kafka_bootstrap}")


def create_vehicles() -> dict[str, list[VehicleSimulator]]:
    """Create vehicle simulators for all customers."""
    vehicles_by_customer = {}
    
    for customer in customers:
        customer_id = customer["customer_id"]
        configs = vehicle_configs.get(customer_id, [])
        vehicles = []
        
        for prefix, region_id, territory_id, base_lat, base_lon, count in configs:
            for i in range(1, count + 1):
                vehicle_id = f"{prefix}{i:03d}"
                vehicle = VehicleSimulator(
                    vehicle_id=vehicle_id,
                    customer_id=customer_id,
                    region_id=region_id,
                    territory_id=territory_id,
                    base_lat=base_lat,
                    base_lon=base_lon
                )
                vehicles.append(vehicle)
        
        vehicles_by_customer[customer_id] = vehicles
        print(f"Created {len(vehicles)} vehicle simulators for {customer['name']}")
    
    return vehicles_by_customer


def main():
    """Main producer loop."""
    print("=" * 60)
    print("Ford Fleet Management - Telemetry Producer")
    print("=" * 60)
    print(f"Kafka Bootstrap: {kafka_bootstrap}")
    print(f"Events per second: {events_per_second}")
    print(f"Anomaly probability: {anomaly_probability}")
    print()
    
    # Create producer
    producer = create_producer()
    
    # Create vehicle simulators
    vehicles_by_customer = create_vehicles()
    
    # Calculate timing
    total_vehicles = sum(len(v) for v in vehicles_by_customer.values())
    delay_between_events = 1.0 / events_per_second
    
    print(f"\nTotal vehicles: {total_vehicles}")
    print(f"Delay between events: {delay_between_events:.4f}s")
    print("\nStarting telemetry generation...\n")
    
    # Round-robin through all vehicles
    all_vehicles = []
    for customer in customers:
        customer_id = customer["customer_id"]
        topic = customer["topic"]
        for vehicle in vehicles_by_customer[customer_id]:
            all_vehicles.append((topic, vehicle))
    
    event_count = 0
    start_time = time.time()
    
    try:
        while True:
            for topic, vehicle in all_vehicles:
                event = vehicle.generate_event()
                
                # Use vehicle_id as key for partition consistency
                producer.send(
                    topic,
                    key=vehicle.vehicle_id,
                    value=event
                )
                
                event_count += 1
                
                if event_count % 1000 == 0:
                    elapsed = time.time() - start_time
                    rate = event_count / elapsed
                    print(f"Sent {event_count:,} events | Rate: {rate:.1f}/s | "
                          f"Topic: {topic} | Vehicle: {vehicle.vehicle_id}")
                
                time.sleep(delay_between_events / len(all_vehicles))
            
            # Flush periodically
            producer.flush()
            
    except KeyboardInterrupt:
        print("\n\nShutting down producer...")
        producer.flush()
        producer.close()
        print(f"Total events sent: {event_count:,}")


if __name__ == "__main__":
    main()

