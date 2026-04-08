"""
FastAPI Web Dashboard for the Context-Aware Healing System.
Provides real-time monitoring and manual approval interface.
"""
import asyncio
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from healer_agent.healer_agent import create_agent_from_env, HealerAgent


# Initialize FastAPI app
app = FastAPI(title="Context-Aware Healing System Dashboard")

# Setup templates and static files
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "ui" / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "ui" / "static")), name="static")

# Global agent instance
agent: Optional[HealerAgent] = None
agent_task: Optional[asyncio.Task] = None

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []


# Pydantic models for API
class ApprovalRequest(BaseModel):
    incident_id: int


class HealthCheckResponse(BaseModel):
    status: str
    incidents_count: int
    pending_approval: bool


# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Start the healer agent on application startup."""
    global agent, agent_task
    
    try:
        # Create agent from environment variables
        agent = create_agent_from_env(BASE_DIR)
        
        # Set up callbacks for real-time updates
        agent.set_callbacks(
            on_incident_detected=on_incident_detected,
            on_decision_made=on_decision_made,
            on_patch_applied=on_patch_applied,
        )
        
        # Start agent in background
        agent_task = asyncio.create_task(agent.start())
        
        print("✅ Dashboard and Healer Agent started successfully")
        
    except Exception as e:
        print(f"❌ Failed to start healer agent: {str(e)}")
        print("⚠️  Dashboard will run without agent. Check your .env file.")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the healer agent on application shutdown."""
    global agent, agent_task
    
    if agent:
        await agent.stop()
    
    if agent_task:
        agent_task.cancel()
        try:
            await agent_task
        except asyncio.CancelledError:
            pass
    
    print("🛑 Dashboard and Healer Agent stopped")


# Callback functions for agent events
async def on_incident_detected(incident: dict):
    """Called when a new incident is detected."""
    await manager.broadcast({
        "type": "incident_detected",
        "data": incident,
    })


async def on_decision_made(decision: dict):
    """Called when the agent makes a decision."""
    await manager.broadcast({
        "type": "decision_made",
        "data": decision,
    })


async def on_patch_applied(result: dict):
    """Called when a patch is applied."""
    await manager.broadcast({
        "type": "patch_applied",
        "data": result,
    })


# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the main dashboard."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Context-Aware Healing System",
        }
    )


@app.get("/api/health")
async def health_check() -> HealthCheckResponse:
    """Get system health status."""
    if not agent:
        return HealthCheckResponse(
            status="agent_not_running",
            incidents_count=0,
            pending_approval=False,
        )
    
    incidents = agent.get_all_incidents()
    pending = agent.get_pending_approval()
    
    return HealthCheckResponse(
        status="healthy" if agent.running else "stopped",
        incidents_count=len(incidents),
        pending_approval=pending is not None,
    )


@app.get("/api/incidents")
async def get_incidents():
    """Get all detected incidents."""
    if not agent:
        return {"incidents": []}
    
    return {"incidents": agent.get_all_incidents()}


@app.get("/api/incidents/current")
async def get_current_incident():
    """Get the current incident awaiting approval."""
    if not agent:
        return {"incident": None}
    
    return {"incident": agent.get_current_incident()}


@app.get("/api/pending")
async def get_pending_approval():
    """Get the decision pending approval."""
    if not agent:
        return {"pending": None}
    
    return {"pending": agent.get_pending_approval()}


@app.post("/api/approve")
async def approve_fix():
    """Approve and apply the pending fix."""
    if not agent:
        return {
            "success": False,
            "message": "Agent not running",
        }
    
    result = await agent.approve_current_fix()
    
    # Broadcast the result
    await manager.broadcast({
        "type": "approval_result",
        "data": result,
    })
    
    return result


@app.post("/api/force-check")
async def force_check():
    """Force an immediate error check."""
    if not agent:
        return {
            "success": False,
            "message": "Agent not running",
        }
    
    incident = await agent.force_check()
    
    return {
        "success": True,
        "incident": incident,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        if agent:
            await websocket.send_json({
                "type": "initial_state",
                "data": {
                    "incidents": agent.get_all_incidents(),
                    "pending": agent.get_pending_approval(),
                    "current": agent.get_current_incident(),
                }
            })
        
        # Keep connection alive
        while True:
            # Wait for messages from client (ping/pong)
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "ui.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

# Made with Bob
