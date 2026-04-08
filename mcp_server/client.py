"""
MCP Client wrapper for the healing agent.
Provides a simple interface to interact with the MCP server.
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

import httpx


class MCPClient:
    """Client for interacting with the MCP server via stdio."""
    
    def __init__(self, server_script: str = "mcp_server/server.py"):
        self.server_script = Path(server_script)
        self.process: Optional[asyncio.subprocess.Process] = None
        
    async def start(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            "python",
            str(self.server_script),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
    async def stop(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            
    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP server not started")
            
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        if self.process.stdout:
            response_line = await self.process.stdout.readline()
            response = json.loads(response_line.decode())
            return response
        
        raise RuntimeError("No response from MCP server")
    
    async def read_logs(self) -> str:
        """Read application logs from the monitoring resource."""
        try:
            response = await self._send_request(
                "resources/read",
                {"uri": "monitoring://app_logs"}
            )
            
            if "result" in response:
                return response["result"].get("contents", [{}])[0].get("text", "")
            
            return ""
        except Exception as e:
            return f"Error reading logs: {str(e)}"
    
    async def apply_patch(self, file_path: str, new_content: str) -> Dict[str, Any]:
        """Apply an emergency patch to a file."""
        try:
            response = await self._send_request(
                "tools/call",
                {
                    "name": "apply_emergency_patch",
                    "arguments": {
                        "file_path": file_path,
                        "new_content": new_content,
                    }
                }
            )
            
            if "result" in response:
                return {
                    "success": True,
                    "message": response["result"].get("content", [{}])[0].get("text", ""),
                }
            
            return {
                "success": False,
                "message": response.get("error", {}).get("message", "Unknown error"),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error applying patch: {str(e)}",
            }
    
    async def verify_health(self, verbose: bool = False) -> Dict[str, Any]:
        """Run health verification tests."""
        try:
            response = await self._send_request(
                "tools/call",
                {
                    "name": "verify_health",
                    "arguments": {"verbose": verbose}
                }
            )
            
            if "result" in response:
                result_text = response["result"].get("content", [{}])[0].get("text", "")
                return {
                    "success": "PASSED" in result_text,
                    "output": result_text,
                }
            
            return {
                "success": False,
                "output": response.get("error", {}).get("message", "Unknown error"),
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Error verifying health: {str(e)}",
            }


class SimpleMCPClient:
    """
    Simplified MCP client that directly calls the server functions.
    Used when running in the same process as the server.
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logs_dir = base_dir / "examples" / "logs"
        
    async def read_logs(self) -> str:
        """Read application logs directly from file."""
        log_file = self.logs_dir / "app.log"
        
        if not log_file.exists():
            return "Log file not found."
        
        try:
            with open(log_file, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading logs: {str(e)}"
    
    async def apply_patch(self, file_path: str, new_content: str) -> Dict[str, Any]:
        """Apply patch by directly calling the server function."""
        # Import here to avoid circular imports
        from mcp_server.server import apply_emergency_patch
        
        result = await apply_emergency_patch(file_path, new_content)
        
        return {
            "success": True,
            "message": result[0].text if result else "Patch applied",
        }
    
    async def verify_health(self, verbose: bool = False) -> Dict[str, Any]:
        """Verify health by directly calling the server function."""
        # Import here to avoid circular imports
        from mcp_server.server import verify_health
        
        result = await verify_health(verbose)
        result_text = result[0].text if result else ""
        
        return {
            "success": "PASSED" in result_text,
            "output": result_text,
        }

# Made with Bob
