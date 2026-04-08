"""
Main Healer Agent that runs the OODA loop continuously.
This agent monitors the application, detects errors, and proposes fixes.
"""
import asyncio
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from healer_agent.ooda_loop import OODALoop
from mcp_server.client import SimpleMCPClient


class HealerAgent:
    """
    The main healing agent that orchestrates the OODA loop.
    Runs as a background task alongside the web dashboard.
    """
    
    def __init__(
        self,
        base_dir: Path,
        watsonx_api_key: str,
        watsonx_project_id: str,
        watsonx_url: str = "https://us-south.ml.cloud.ibm.com",
        check_interval: int = 30,
    ):
        self.base_dir = base_dir
        self.check_interval = check_interval
        self.running = False
        self.current_incident: Optional[dict] = None
        
        # Initialize MCP client
        self.mcp_client = SimpleMCPClient(base_dir)
        
        # Initialize OODA loop
        self.ooda_loop = OODALoop(
            mcp_client=self.mcp_client,
            base_dir=base_dir,
            watsonx_api_key=watsonx_api_key,
            watsonx_project_id=watsonx_project_id,
            watsonx_url=watsonx_url,
        )
        
        # Callbacks for UI integration
        self.on_incident_detected = None
        self.on_decision_made = None
        self.on_patch_applied = None
    
    def set_callbacks(
        self,
        on_incident_detected=None,
        on_decision_made=None,
        on_patch_applied=None,
    ):
        """Set callback functions for UI integration."""
        self.on_incident_detected = on_incident_detected
        self.on_decision_made = on_decision_made
        self.on_patch_applied = on_patch_applied
    
    async def start(self):
        """Start the healing agent."""
        self.running = True
        print("🤖 Healer Agent started - monitoring for errors...")
        
        while self.running:
            try:
                # Run one OODA cycle
                incident = await self.ooda_loop.run_cycle()
                
                if incident:
                    print(f"🚨 Incident detected: {incident['error_context']['error_type']}")
                    self.current_incident = incident
                    
                    # Notify UI
                    if self.on_incident_detected:
                        await self.on_incident_detected(incident)
                    
                    # Notify about decision
                    if self.on_decision_made:
                        await self.on_decision_made(incident['decision'])
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Error in healing agent: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Stop the healing agent."""
        self.running = False
        print("🛑 Healer Agent stopped")
    
    async def approve_current_fix(self) -> dict:
        """Approve and apply the current pending fix."""
        if not self.current_incident:
            return {
                "success": False,
                "message": "No current incident to approve",
            }
        
        try:
            result = await self.ooda_loop.approve_and_act()
            
            # Notify UI
            if self.on_patch_applied:
                await self.on_patch_applied(result)
            
            print(f"✅ Patch applied: {result.get('status', 'unknown')}")
            
            return {
                "success": True,
                "result": result,
            }
            
        except Exception as e:
            error_msg = f"Error applying patch: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                "success": False,
                "message": error_msg,
            }
    
    def get_current_incident(self) -> Optional[dict]:
        """Get the current incident awaiting approval."""
        return self.current_incident
    
    def get_all_incidents(self) -> list:
        """Get all detected incidents."""
        return self.ooda_loop.incidents
    
    def get_pending_approval(self) -> Optional[dict]:
        """Get the decision pending approval."""
        return self.ooda_loop.pending_approval
    
    async def force_check(self) -> Optional[dict]:
        """Force an immediate check for errors."""
        print("🔍 Forcing immediate error check...")
        incident = await self.ooda_loop.run_cycle()
        
        if incident:
            self.current_incident = incident
            
            # Notify UI
            if self.on_incident_detected:
                await self.on_incident_detected(incident)
            
            if self.on_decision_made:
                await self.on_decision_made(incident['decision'])
        
        return incident


def create_agent_from_env(base_dir: Path) -> HealerAgent:
    """Create a healer agent using environment variables."""
    load_dotenv()
    
    # Get required environment variables
    watsonx_api_key = os.getenv("WATSONX_API_KEY")
    watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")
    watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    check_interval = int(os.getenv("CHECK_INTERVAL", "30"))
    
    if not watsonx_api_key or not watsonx_project_id:
        raise ValueError(
            "Missing required environment variables: WATSONX_API_KEY, WATSONX_PROJECT_ID"
        )
    
    return HealerAgent(
        base_dir=base_dir,
        watsonx_api_key=watsonx_api_key,
        watsonx_project_id=watsonx_project_id,
        watsonx_url=watsonx_url,
        check_interval=check_interval,
    )


async def main():
    """Run the healer agent standalone."""
    base_dir = Path(__file__).parent.parent
    
    try:
        agent = create_agent_from_env(base_dir)
        await agent.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down healer agent...")
    except Exception as e:
        print(f"❌ Failed to start healer agent: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
