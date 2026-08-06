import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

# Add app parent directory to Python path
sys.path.append(str(Path(__file__).parent))
from agents.supervisor import route_question

app = FastAPI(
    title="NovaTech AI Customer Support API",
    description="FastAPI Backend for LangGraph Multi-Agent Voice & Chat Support Hotline",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "NovaTech AI Customer Support"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message string cannot be empty.")
    
    try:
        reply = route_question(request.message, request.chat_history)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing agent workflow: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def serve_web_ui():
    
    
    return HTMLResponse()
