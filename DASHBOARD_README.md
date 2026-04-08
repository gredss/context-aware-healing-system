# Context-Aware Healing System - Dashboard & Agent Guide

This guide covers the complete system including the Healer Agent (OODA Loop) and Web Dashboard.

## 🎯 Overview

The system consists of three main components:

1. **MCP Server** - Provides monitoring resources and healing tools
2. **Healer Agent** - Autonomous OODA loop that detects and proposes fixes
3. **Web Dashboard** - Real-time UI for monitoring and manual approval

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- IBM Watsonx AI account with API key
- Git

### 2. Setup

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd context-aware-healing-system

# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
CHECK_INTERVAL=30
```

Get your IBM Watsonx credentials:
- API Key: https://cloud.ibm.com/iam/apikeys
- Project ID: https://dataplatform.cloud.ibm.com/projects

### 3. Launch the System

```bash
./start_system.sh
```

This single command will:
- Create a virtual environment (if needed)
- Install all dependencies
- Start the healer agent
- Launch the web dashboard

The dashboard will be available at: **http://localhost:8000**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Dashboard (FastAPI)                  │
│  - Real-time monitoring via WebSocket                       │
│  - Manual approval interface                                │
│  - Health status visualization                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Healer Agent (OODA Loop)                  │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ OBSERVE  │→ │  ORIENT  │→ │  DECIDE  │→ │   ACT    │   │
│  │ Read logs│  │ Analyze  │  │ Generate │  │  Apply   │   │
│  │          │  │ context  │  │ fix (LLM)│  │  patch   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                    ▲                         │
│                                    │                         │
│                            IBM Granite 3.0                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP Server                              │
│  - monitoring://app_logs (Resource)                         │
│  - apply_emergency_patch (Tool)                             │
│  - verify_health (Tool)                                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 OODA Loop Explained

The Healer Agent implements the OODA (Observe, Orient, Decide, Act) loop:

### 1. **Observe** 🔍
- Continuously monitors application logs via MCP
- Runs every 30 seconds (configurable)
- Detects error patterns in real-time

### 2. **Orient** 🧭
- Analyzes detected errors
- Extracts file paths and line numbers from stack traces
- Reads the relevant source code
- Builds context for decision-making

### 3. **Decide** 🤔
- Sends error context and code to IBM Granite 3.0
- LLM analyzes the error and generates a fix
- Returns:
  - Reasoning (why this fix works)
  - Fixed code (complete file content)
  - Risk level (low/medium/high)
  - Confidence score (0-100%)

### 4. **Act** ⚡
- **Waits for manual approval** via dashboard
- Creates automatic backup before patching
- Applies the fix via MCP
- Runs health verification tests
- Reports results to dashboard

## 🎨 Dashboard Features

### Main Interface

1. **Incidents List** (Left Panel)
   - Shows all detected errors
   - Real-time updates
   - Status indicators

2. **Agent's Analysis** (Right Panel)
   - Live OODA loop status
   - Reasoning from Granite 3.0
   - Step-by-step progress

3. **Proposed Fix** (Right Panel)
   - Complete fixed code
   - Syntax highlighting
   - Risk assessment
   - Confidence score

4. **Approval Interface**
   - Big "Approve & Heal" button
   - Manual review before applying
   - Safety mechanism

5. **Health Status**
   - System metrics
   - Incident count
   - Pending approvals
   - Test results after patching

### Real-Time Updates

The dashboard uses WebSocket for instant updates:
- New incidents appear immediately
- Agent thoughts stream in real-time
- Patch results shown instantly
- No page refresh needed

## 🛠️ API Endpoints

### REST API

```
GET  /                      - Dashboard UI
GET  /api/health           - System health status
GET  /api/incidents        - List all incidents
GET  /api/incidents/current - Current incident
GET  /api/pending          - Pending approval
POST /api/approve          - Approve and apply fix
POST /api/force-check      - Force immediate check
```

### WebSocket

```
WS   /ws                   - Real-time updates
```

## 📝 Usage Examples

### Example 1: Automatic Error Detection

1. The broken app runs and generates errors
2. Agent detects error in logs (Observe)
3. Agent reads the source code (Orient)
4. Granite 3.0 generates a fix (Decide)
5. Dashboard shows proposed fix
6. You click "Approve & Heal" (Act)
7. System applies patch and runs tests
8. Dashboard shows results

### Example 2: Manual Check

Click "Force Check" button to:
- Immediately scan logs
- Detect any errors
- Generate fixes
- Display in dashboard

### Example 3: Monitoring Multiple Incidents

- Dashboard tracks all incidents
- Each has a unique ID
- Status updates in real-time
- History preserved for analysis

## 🔧 Configuration

### Agent Settings

Edit `.env` to configure:

```env
# How often to check for errors (seconds)
CHECK_INTERVAL=30

# Watsonx model settings (in code)
# - model_id: ibm/granite-3-8b-instruct
# - temperature: 0.3 (conservative)
# - max_tokens: 2000
```

### Dashboard Settings

```env
DASHBOARD_HOST=0.0.0.0  # Listen on all interfaces
DASHBOARD_PORT=8000     # Default port
```

## 🧪 Testing the System

### 1. Test with Broken App

```bash
# In one terminal, start the system
./start_system.sh

# In another terminal, run the broken app
python examples/broken_app.py

# Watch the dashboard detect and propose fixes
```

### 2. Test Health Verification

After applying a fix, the system automatically runs:
```bash
pytest examples/ -v
```

Results appear in the dashboard.

### 3. Test Manual Approval Flow

1. Force a check via dashboard
2. Review the proposed fix
3. Check risk level and confidence
4. Approve or reject
5. Monitor health check results

## 🚨 Troubleshooting

### Agent Not Starting

**Error:** `Missing required environment variables`

**Solution:** 
```bash
cp .env.example .env
# Edit .env and add your Watsonx credentials
```

### WebSocket Connection Failed

**Error:** Dashboard shows "Disconnected"

**Solution:**
- Check if the server is running
- Verify no firewall blocking port 8000
- Check browser console for errors

### LLM Errors

**Error:** `Error calling LLM`

**Solution:**
- Verify Watsonx API key is valid
- Check project ID is correct
- Ensure you have Granite 3.0 access
- Check internet connection

### Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Monitoring Best Practices

1. **Keep Dashboard Open** - Real-time monitoring is most effective
2. **Review Reasoning** - Always read the LLM's reasoning before approving
3. **Check Risk Level** - Be cautious with "high" risk fixes
4. **Verify Tests** - Ensure health checks pass after patching
5. **Monitor Logs** - Keep an eye on the agent's console output

## 🔐 Security Considerations

1. **Manual Approval Required** - No automatic patching without approval
2. **Automatic Backups** - Every patch creates a timestamped backup
3. **Risk Assessment** - LLM evaluates risk before proposing fixes
4. **Health Verification** - Tests run after every patch
5. **Audit Trail** - All incidents and actions are logged

## 🎓 Advanced Usage

### Custom Check Intervals

For faster detection in development:
```env
CHECK_INTERVAL=10  # Check every 10 seconds
```

For production (less aggressive):
```env
CHECK_INTERVAL=60  # Check every minute
```

### Running Components Separately

**Agent only:**
```bash
python healer_agent/healer_agent.py
```

**Dashboard only:**
```bash
python -m uvicorn ui.app:app --host 0.0.0.0 --port 8000
```

**MCP Server only:**
```bash
python mcp_server/server.py
```

## 📚 Next Steps

1. **Phase 4**: Multi-application monitoring
2. **Phase 5**: Predictive error detection
3. **Phase 6**: Custom healing strategies
4. **Phase 7**: Integration with CI/CD pipelines

## 🤝 Support

For issues or questions:
1. Check the logs in the terminal
2. Review the SETUP_GUIDE.md
3. Check the TECHNICAL_SPEC.md for architecture details
4. Review the IMPLEMENTATION_PLAN.md for roadmap

## 📄 License

[Add your license information here]