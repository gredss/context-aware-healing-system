# Context-Aware Healing System - MCP Server

This is the Model Context Protocol (MCP) server implementation for the Context-Aware Healing System. It provides monitoring resources and healing tools that can be accessed by MCP clients.

## Features

### Resources
- **monitoring://app_logs** - Real-time access to application logs for error detection and monitoring

### Tools
- **apply_emergency_patch** - Apply emergency code patches with automatic backup creation
- **verify_health** - Run pytest to verify application health and test status

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using the project setup:
```bash
pip install -e .
```

## Running the Server

Start the MCP server using stdio transport:

```bash
python mcp_server/server.py
```

The server will run in stdio mode, communicating via standard input/output streams.

## Testing the Server

### 1. Read Application Logs
Access the monitoring resource to view application logs:
- Resource URI: `monitoring://app_logs`
- Returns: Contents of `examples/logs/app.log`

### 2. Apply Emergency Patch
Use the tool to patch a file with automatic backup:
```json
{
  "name": "apply_emergency_patch",
  "arguments": {
    "file_path": "examples/broken_app.py",
    "new_content": "# Fixed code here..."
  }
}
```

### 3. Verify Health
Run pytest to check application health:
```json
{
  "name": "verify_health",
  "arguments": {
    "verbose": true
  }
}
```

## Architecture

```
mcp_server/
├── __init__.py
├── server.py          # Main MCP server implementation
└── README.md          # This file

examples/
├── broken_app.py      # Sample app with deliberate errors
├── test_broken_app.py # Test suite for health verification
└── logs/
    └── app.log        # Application logs

backups/               # Automatic backups created by apply_emergency_patch
```

## Development

The server uses:
- **mcp** - Model Context Protocol SDK
- **asyncio** - Asynchronous I/O
- **pathlib** - Path operations
- **subprocess** - Running pytest for health checks

## Next Steps

Phase 2 will add:
- LLM integration for intelligent error analysis
- Automated patch generation
- Advanced monitoring capabilities