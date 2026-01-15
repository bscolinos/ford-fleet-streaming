"""
AI integration using SingleStore AI endpoint with boto3 Bedrock client.
"""

import os
from typing import Any, Optional

import boto3
from botocore.config import Config
from botocore import UNSIGNED

from app.config import get_settings

settings = get_settings()

# Model configuration
model_api_auth = settings.model_api_auth
model_name = settings.model_name
model_api_endpoint = settings.model_api_endpoint

# boto3 client (lazy initialized)
_llm_client = None


def get_llm_client():
    """Get or create the LLM client."""
    global _llm_client
    
    if _llm_client is not None:
        return _llm_client
    
    if not model_api_auth:
        return None
    
    # Create client with unsigned config (we inject auth manually)
    cfg = Config(signature_version=UNSIGNED)
    
    _llm_client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        endpoint_url=model_api_endpoint,
        aws_access_key_id="placeholder",
        aws_secret_access_key="placeholder",
        config=cfg
    )
    
    # Inject API_AUTH key for all request types
    def _inject_headers(request: Any, **_ignored: Any) -> None:
        request.headers['Authorization'] = f'Bearer {model_api_auth}'
        request.headers.pop('X-Amz-Date', None)
        request.headers.pop('X-Amz-Security-Token', None)
    
    emitter = _llm_client._endpoint._event_emitter
    emitter.register_first('before-send.bedrock-runtime.Converse', _inject_headers)
    emitter.register_first('before-send.bedrock-runtime.ConverseStream', _inject_headers)
    emitter.register_first('before-send.bedrock-runtime.InvokeModel', _inject_headers)
    emitter.register_first('before-send.bedrock-runtime.InvokeModelWithResponseStream', _inject_headers)
    
    return _llm_client


def get_chat_response(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Get a chat response from the LLM.
    
    Args:
        prompt: The user's message
        system_prompt: Optional system prompt for context
    
    Returns:
        The model's response text
    """
    client = get_llm_client()
    
    if client is None:
        return "AI integration not configured. Please set MODEL_API_AUTH in environment."
    
    try:
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        
        kwargs = {
            "modelId": model_name,
            "messages": messages
        }
        
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]
        
        response = client.converse(**kwargs)
        
        return response["output"]["message"]["content"][0]["text"]
    
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"


def summarize_driver_notes(notes: list[dict]) -> str:
    """
    Summarize a list of driver notes using the LLM.
    
    Args:
        notes: List of driver note dictionaries
    
    Returns:
        Summary text
    """
    if not notes:
        return "No driver notes available to summarize."
    
    # Format notes for the prompt
    notes_text = "\n\n".join([
        f"[{note.get('ts', 'Unknown date')}] {note.get('driver_name', 'Unknown driver')} "
        f"({note.get('category', 'general')}): {note.get('note_text', '')}"
        for note in notes
    ])
    
    system_prompt = """You are a fleet management analyst. Your job is to analyze driver notes 
and provide actionable insights for fleet managers. Focus on:
1. Maintenance concerns that need attention
2. Operational patterns or issues
3. Positive feedback or improvements
4. Safety concerns

Be concise and prioritize the most important findings."""
    
    prompt = f"""Please summarize the following driver notes from our fleet:

{notes_text}

Provide:
1. A brief executive summary (2-3 sentences)
2. Key maintenance issues to address
3. Operational recommendations
4. Any urgent items requiring immediate attention"""
    
    return get_chat_response(prompt, system_prompt)


def get_fleet_insights(question: str, context: dict) -> str:
    """
    Answer a fleet-related question using LLM with context.
    
    Args:
        question: User's question about the fleet
        context: Dictionary with fleet statistics and data
    
    Returns:
        AI-generated answer
    """
    system_prompt = """You are an AI assistant for a fleet management platform. You help 
fleet managers understand their data and make better decisions. You have access to 
real-time fleet statistics and can provide insights on:
- Vehicle performance and health
- Fuel efficiency
- Driver behavior
- Maintenance needs
- Anomaly patterns

Be helpful, concise, and data-driven in your responses."""
    
    context_text = f"""Current Fleet Status:
- Total Vehicles: {context.get('total_vehicles', 'N/A')}
- Active Vehicles: {context.get('active_vehicles', 'N/A')}
- Average Speed: {context.get('avg_speed', 'N/A'):.1f} mph
- Average Fuel Level: {context.get('avg_fuel_pct', 'N/A'):.1f}%
- Average Engine Temp: {context.get('avg_engine_temp', 'N/A'):.1f}F
- Total Anomalies: {context.get('total_anomalies', 'N/A')}
- Unacknowledged Anomalies: {context.get('unacknowledged_anomalies', 'N/A')}
- Critical Anomalies: {context.get('critical_anomalies', 'N/A')}

Recent Anomaly Types: {', '.join(context.get('anomaly_types', [])) or 'None'}
"""
    
    prompt = f"""{context_text}

User Question: {question}

Please provide a helpful and actionable response based on the fleet data above."""
    
    return get_chat_response(prompt, system_prompt)

