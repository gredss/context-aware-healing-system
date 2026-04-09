# Setup Guide - Context-Aware Healing System

This guide will help you set up and run the Context-Aware Healing System MCP Server.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git (for version control)

## Quick Start

### Option 1: Using the Startup Script (Recommended)

The easiest way to get started:

```bash
./start_mcp_server.sh
```

This script will:
1. Create a virtual environment if it doesn't exist
2. Install all required dependencies
3. Start the MCP server

### Option 2: Manual Setup

If you prefer manual setup:

1. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Or using pyproject.toml:
```bash
pip install -e .
```

3. **Start the MCP server:**
```bash
python mcp_server/server.py
```

## Project Structure

```
context-aware-healing-system/
├── mcp_server/              # MCP server implementation
│   ├── __init__.py
│   ├── server.py           # Main server code
│   └── README.md           # Server documentation
├── examples/                # Example applications and tests
│   ├── __init__.py
│   ├── broken_app.py       # Sample app with errors
│   ├── test_broken_app.py  # Test suite
│   └── logs/
│       └── app.log         # Application logs
├── backups/                 # Automatic backups (created by server)
│   └── .gitkeep
├── ui/                      # Future: Web dashboard
│   └── __init__.py
├── pyproject.toml          # Project configuration
├── requirements.txt        # Python dependencies
├── start_mcp_server.sh     # Startup script
└── README.md               # Project overview
```

## Testing the Installation

### 1. Test the Broken App

Run the example application to see the errors:

```bash
python examples/broken_app.py
```

Expected output will show ZeroDivisionError and KeyError.

### 2. Run Tests

Verify the test suite works:

```bash
pytest examples/ -v
```

### 3. Test MCP Server

The MCP server runs in stdio mode and communicates via standard input/output. To test it properly, you'll need an MCP client (like Claude Desktop or another MCP-compatible tool).

## MCP Server Capabilities

### Resources

**monitoring://app_logs**
- Provides real-time access to application logs
- Location: `examples/logs/app.log`
- Use this to monitor errors and events

### Tools

**apply_emergency_patch**
- Applies code patches with automatic backup
- Parameters:
  - `file_path`: Path to file (relative to project root)
  - `new_content`: New code content
- Creates timestamped backups in `backups/` directory

**verify_health**
- Runs pytest on the examples directory
- Parameters:
  - `verbose`: Enable verbose output (optional)
- Returns pass/fail status and test results

## Configuration

### Environment Variables

Create a `.env` file in the project root for configuration (optional):

```env
# Future configuration options
LOG_LEVEL=INFO
BACKUP_DIR=backups
```

## Troubleshooting

### Import Errors

If you see import errors for `mcp`, `pytest`, etc.:
```bash
pip install -r requirements.txt
```

### Permission Denied on Startup Script

Make the script executable:
```bash
chmod +x start_mcp_server.sh
```

### Python Version Issues

Ensure you're using Python 3.10+:
```bash
python --version
```

### Virtual Environment Not Activating

On Windows, you may need to enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

1. **Phase 2**: LLM Integration
   - Add OpenAI/Anthropic API integration
   - Implement intelligent error analysis
   - Automated patch generation

2. **Phase 3**: Web Dashboard
   - Real-time monitoring UI
   - Patch history visualization
   - System health metrics

3. **Phase 4**: Advanced Features
   - Multi-application monitoring
   - Predictive error detection
   - Custom healing strategies

## Support

For issues or questions:
1. Check the documentation in each module's README
2. Review the TECHNICAL_SPEC.md for architecture details
3. See IMPLEMENTATION_PLAN.md for development roadmap

## Development

To contribute or modify the system:

1. **Code Style**: Use Black for formatting
```bash
black mcp_server/ examples/
```

2. **Linting**: Use Ruff
```bash
ruff check mcp_server/ examples/
```

3. **Type Checking**: Use mypy
```bash
mypy mcp_server/
```
