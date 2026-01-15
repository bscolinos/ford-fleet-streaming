"""
WebSocket endpoint for real-time dashboard updates.
Queries the database periodically and pushes updates to connected clients.
"""

import asyncio
import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.auth.jwt import decode_token
from app.db import queries

router = APIRouter(tags=["Realtime"])


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: list[tuple[WebSocket, str]] = []
    
    async def connect(self, websocket: WebSocket, role: str):
        await websocket.accept()
        self.active_connections.append((websocket, role))
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections = [
            (ws, role) for ws, role in self.active_connections 
            if ws != websocket
        ]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for websocket, role in self.active_connections:
            try:
                await websocket.send_json(message)
            except:
                pass


manager = ConnectionManager()


async def get_updates(role: str) -> dict:
    """Fetch real-time stats from database."""
    try:
        stats = queries.get_realtime_stats(role)
        return {
            "type": "stats_update",
            "data": stats
        }
    except Exception as e:
        return {
            "type": "error",
            "message": str(e)
        }


@router.websocket("/realtime/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time dashboard updates.
    
    Connect with: ws://host/realtime/stream?token=<jwt_token>
    
    Sends updates every 2 seconds with:
    - Active vehicle count
    - Recent telemetry stats
    - New anomalies
    """
    
    # Authenticate via token query param
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return
    
    token_data = decode_token(token)
    if not token_data:
        await websocket.close(code=4002, reason="Invalid token")
        return
    
    role = token_data.role
    
    await manager.connect(websocket, role)
    
    try:
        # Send initial update
        initial_data = await get_updates(role)
        await manager.send_personal_message(initial_data, websocket)
        
        # Create background task for periodic updates
        async def send_periodic_updates():
            while True:
                await asyncio.sleep(2)
                try:
                    update = await get_updates(role)
                    await manager.send_personal_message(update, websocket)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    error_msg = {"type": "error", "message": str(e)}
                    try:
                        await manager.send_personal_message(error_msg, websocket)
                    except:
                        break
        
        # Start periodic updates
        update_task = asyncio.create_task(send_periodic_updates())
        
        # Wait for client messages (mainly for keepalive)
        while True:
            try:
                data = await websocket.receive_text()
                # Handle client messages if needed
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
        
        update_task.cancel()
        
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

