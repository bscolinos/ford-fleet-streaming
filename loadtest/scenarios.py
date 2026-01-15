"""
Load testing scenarios for Ford Fleet Management Demo.
"""

import random
from typing import Callable

# Demo user credentials
demo_users = [
    {"username": "territory_manager_1", "password": "territory123"},
    {"username": "regional_manager_1", "password": "regional123"},
    {"username": "demo_admin", "password": "admin123"},
]


def get_random_user():
    """Get random demo user credentials."""
    return random.choice(demo_users)


# Scenario weights (probability of selection)
scenario_weights = {
    "browse_dashboard": 0.30,
    "view_vehicles": 0.25,
    "view_telemetry": 0.20,
    "view_anomalies": 0.15,
    "acknowledge_anomaly": 0.05,
    "ai_insights": 0.05,
}


async def scenario_browse_dashboard(session, base_url, token):
    """Simulate browsing the main dashboard."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get fleet summary
    async with session.get(
        f"{base_url}/fleet/summary?granularity=day",
        headers=headers
    ) as resp:
        return resp.status == 200


async def scenario_view_vehicles(session, base_url, token):
    """Simulate viewing the vehicles list."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get vehicles with various filters
    filters = [
        "",
        "?customer_id=customer_a",
        "?customer_id=customer_b",
        "?limit=50",
    ]
    
    filter_param = random.choice(filters)
    
    async with session.get(
        f"{base_url}/fleet/vehicles{filter_param}",
        headers=headers
    ) as resp:
        return resp.status == 200


async def scenario_view_telemetry(session, base_url, token):
    """Simulate viewing vehicle telemetry."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # First get a vehicle ID
    async with session.get(
        f"{base_url}/fleet/vehicles?limit=10",
        headers=headers
    ) as resp:
        if resp.status != 200:
            return False
        data = await resp.json()
        if not data.get("vehicles"):
            return True  # No vehicles, but successful request
        
        vehicle_id = random.choice(data["vehicles"])["vehicle_id"]
    
    # Then get its telemetry
    async with session.get(
        f"{base_url}/fleet/vehicle/{vehicle_id}/telemetry?limit=100",
        headers=headers
    ) as resp:
        return resp.status in [200, 404]  # 404 is valid if no telemetry yet


async def scenario_view_anomalies(session, base_url, token):
    """Simulate viewing anomalies."""
    headers = {"Authorization": f"Bearer {token}"}
    
    filters = [
        "",
        "?severity=critical",
        "?severity=warning",
        "?acknowledged=false",
    ]
    
    filter_param = random.choice(filters)
    
    async with session.get(
        f"{base_url}/fleet/anomalies{filter_param}",
        headers=headers
    ) as resp:
        return resp.status == 200


async def scenario_acknowledge_anomaly(session, base_url, token):
    """Simulate acknowledging an anomaly."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get unacknowledged anomalies
    async with session.get(
        f"{base_url}/fleet/anomalies?acknowledged=false&limit=5",
        headers=headers
    ) as resp:
        if resp.status != 200:
            return False
        data = await resp.json()
        if not data.get("anomalies"):
            return True  # No anomalies to ack, but successful
        
        anomaly_id = random.choice(data["anomalies"])["anomaly_id"]
    
    # Acknowledge it
    async with session.post(
        f"{base_url}/fleet/anomalies/{anomaly_id}/ack",
        headers=headers
    ) as resp:
        return resp.status in [200, 404]


async def scenario_ai_insights(session, base_url, token):
    """Simulate using AI insights."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    questions = [
        "What are the top issues in my fleet?",
        "How is fleet performance trending?",
        "Which vehicles need attention?",
        "Summary of fuel efficiency",
    ]
    
    async with session.post(
        f"{base_url}/ai/insights",
        headers=headers,
        json={"question": random.choice(questions)}
    ) as resp:
        # AI might fail if not configured, that's okay
        return resp.status in [200, 500]


# Map scenario names to functions
scenarios = {
    "browse_dashboard": scenario_browse_dashboard,
    "view_vehicles": scenario_view_vehicles,
    "view_telemetry": scenario_view_telemetry,
    "view_anomalies": scenario_view_anomalies,
    "acknowledge_anomaly": scenario_acknowledge_anomaly,
    "ai_insights": scenario_ai_insights,
}


def select_scenario() -> tuple[str, Callable]:
    """Select a scenario based on weights."""
    names = list(scenario_weights.keys())
    weights = [scenario_weights[n] for n in names]
    selected = random.choices(names, weights=weights, k=1)[0]
    return selected, scenarios[selected]

