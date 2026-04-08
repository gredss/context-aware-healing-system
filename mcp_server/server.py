"""
MCP Server for Context-Aware Healing System
Implements resources and tools for monitoring and healing applications.
"""
import asyncio
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent


# Initialize MCP server
app = Server("context-aware-healing-system")

# Base paths
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "examples" / "logs"
BACKUPS_DIR = BASE_DIR / "backups"
EXAMPLES_DIR = BASE_DIR / "examples"


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available monitoring resources."""
    return [
        Resource(
            uri="monitoring://app_logs",
            name="Application Logs",
            mimeType="text/plain",
            description="Real-time application logs for monitoring errors and events",
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read content from monitoring resources."""
    if uri == "monitoring://app_logs":
        log_file = LOGS_DIR / "app.log"
        
        if not log_file.exists():
            return "Log file not found. No logs available."
        
        try:
            with open(log_file, "r") as f:
                content = f.read()
            
            if not content.strip():
                return "Log file is empty. No logs available."
            
            return content
        except Exception as e:
            return f"Error reading log file: {str(e)}"
    
    return f"Unknown resource: {uri}"


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available healing tools."""
    return [
        Tool(
            name="apply_emergency_patch",
            description="Apply an emergency patch to a file. Creates a backup before modifying.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to patch (relative to project root)",
                    },
                    "new_content": {
                        "type": "string",
                        "description": "The new content to write to the file",
                    },
                },
                "required": ["file_path", "new_content"],
            },
        ),
        Tool(
            name="verify_health",
            description="Run pytest on the examples directory to verify application health",
            inputSchema={
                "type": "object",
                "properties": {
                    "verbose": {
                        "type": "boolean",
                        "description": "Enable verbose output",
                        "default": False,
                    }
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute healing tools."""
    
    if name == "apply_emergency_patch":
        return await apply_emergency_patch(
            arguments.get("file_path"),
            arguments.get("new_content")
        )
    
    elif name == "verify_health":
        return await verify_health(
            arguments.get("verbose", False)
        )
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def apply_emergency_patch(file_path: str, new_content: str) -> list[TextContent]:
    """
    Apply an emergency patch to a file.
    Creates a backup before modifying the file.
    """
    try:
        # Resolve the full path
        target_file = BASE_DIR / file_path
        
        if not target_file.exists():
            return [TextContent(
                type="text",
                text=f"Error: File not found: {file_path}"
            )]
        
        # Create backup directory if it doesn't exist
        BACKUPS_DIR.mkdir(exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{target_file.name}.{timestamp}.backup"
        backup_path = BACKUPS_DIR / backup_name
        
        # Create backup
        shutil.copy2(target_file, backup_path)
        
        # Apply patch
        with open(target_file, "w") as f:
            f.write(new_content)
        
        return [TextContent(
            type="text",
            text=f"✅ Emergency patch applied successfully!\n"
                 f"File: {file_path}\n"
                 f"Backup created: {backup_path.relative_to(BASE_DIR)}\n"
                 f"Timestamp: {timestamp}"
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error applying patch: {str(e)}"
        )]


async def verify_health(verbose: bool = False) -> list[TextContent]:
    """
    Run pytest on the examples directory to verify application health.
    Returns pass/fail status and test results.
    """
    try:
        # Build pytest command
        cmd = ["pytest", str(EXAMPLES_DIR)]
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add options for better output
        cmd.extend(["--tb=short", "--no-header"])
        
        # Run pytest
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        # Parse results
        output = result.stdout + result.stderr
        exit_code = result.returncode
        
        if exit_code == 0:
            status = "✅ PASSED"
            emoji = "🎉"
        else:
            status = "❌ FAILED"
            emoji = "⚠️"
        
        return [TextContent(
            type="text",
            text=f"{emoji} Health Check Results\n"
                 f"Status: {status}\n"
                 f"Exit Code: {exit_code}\n"
                 f"\n{'='*50}\n"
                 f"{output}\n"
                 f"{'='*50}"
        )]
    
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text="❌ Error: pytest not found. Please install dependencies:\n"
                 "pip install -e ."
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error running health check: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
