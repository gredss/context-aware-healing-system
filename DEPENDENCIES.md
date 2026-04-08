# Dependencies Specification

## Core Dependencies

### 1. Model Context Protocol (MCP)
```
mcp>=0.9.0
```
- **Purpose**: Core MCP SDK for server and client implementation
- **Usage**: Expose resources and tools, communicate with MCP servers
- **Documentation**: https://modelcontextprotocol.io/

### 2. HTTP Client
```
httpx>=0.27.0
```
- **Purpose**: Async HTTP client for API communication
- **Usage**: Call Granite 3.0 API, make external requests
- **Features**: Async/await support, connection pooling, timeout handling

### 3. Data Validation
```
pydantic>=2.0.0
pydantic-settings>=2.0.0
```
- **Purpose**: Data validation and settings management
- **Usage**: Validate MCP tool inputs, configuration schemas
- **Features**: Type hints, automatic validation, JSON schema generation

### 4. LLM Integration
```
openai>=1.0.0
```
- **Purpose**: OpenAI-compatible API client for Granite 3.0
- **Usage**: Generate fixes using Granite 3.0 model
- **Note**: Granite 3.0 supports OpenAI-compatible API endpoints

### 5. Async Runtime
```
anyio>=4.0.0
```
- **Purpose**: Async I/O abstraction layer
- **Usage**: MCP server async operations, concurrent task handling
- **Features**: Works with asyncio and trio

### 6. Logging
```
structlog>=24.0.0
```
- **Purpose**: Structured logging with JSON output
- **Usage**: System logs, audit trails, debugging
- **Features**: Context binding, processors, formatters

### 7. Configuration Management
```
pyyaml>=6.0
python-dotenv>=1.0.0
```
- **Purpose**: Configuration file parsing and environment variables
- **Usage**: Load YAML configs, manage secrets
- **Features**: Safe YAML loading, .env file support

### 8. Web Framework
```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
```
- **Purpose**: Web dashboard backend with REST API and WebSocket
- **Usage**: Real-time OODA loop visualization, human-in-the-loop approval
- **Features**: Async support, automatic API docs, WebSocket support

### 9. WebSocket Communication
```
websockets>=12.0
python-multipart>=0.0.9
```
- **Purpose**: Real-time bidirectional communication
- **Usage**: Live updates to dashboard, instant approval notifications
- **Features**: Async WebSocket, connection management

### 10. File Watching (Optional)
```
watchdog>=4.0.0
```
- **Purpose**: Monitor file system changes
- **Usage**: Real-time log file monitoring
- **Features**: Cross-platform, efficient event handling

## Development Dependencies

### Testing
```
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
```
- **Purpose**: Testing framework with async support
- **Usage**: Unit tests, integration tests, coverage reports
- **Features**: Fixtures, parametrization, async test support

### Code Quality
```
black>=24.0.0
ruff>=0.3.0
mypy>=1.8.0
```
- **Purpose**: Code formatting, linting, type checking
- **Usage**: Maintain code quality and consistency
- **Features**: Auto-formatting, fast linting, static type analysis

### Pre-commit Hooks
```
pre-commit>=3.6.0
```
- **Purpose**: Git hooks for code quality checks
- **Usage**: Run checks before commits
- **Features**: Multiple hook support, automatic installation

## Optional Dependencies

### Monitoring & Metrics
```
prometheus-client>=0.20.0
```
- **Purpose**: Expose metrics for monitoring
- **Usage**: Track healing success rate, error counts
- **Features**: Counter, Gauge, Histogram metrics

### Database (for persistent state)
```
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
```
- **Purpose**: Store healing history and state
- **Usage**: Track past fixes, learn from history
- **Features**: Async support, ORM capabilities

## Python Version Requirement

```
python>=3.11
```

**Rationale**:
- Modern async/await syntax improvements
- Better type hints support
- Performance improvements
- Exception groups (PEP 654)
- TOML support in standard library

## Installation Methods

### Using pip with requirements.txt
```bash
pip install -r requirements.txt
```

### Using Poetry (recommended)
```bash
poetry install
```

### Using pip with pyproject.toml
```bash
pip install -e .
```

## Dependency Groups

### Production
- mcp
- httpx
- pydantic
- pydantic-settings
- openai
- anyio
- structlog
- pyyaml
- python-dotenv
- fastapi
- uvicorn[standard]
- websockets
- python-multipart

### Development
- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock
- black
- ruff
- mypy
- pre-commit

### Optional
- watchdog
- prometheus-client
- sqlalchemy
- aiosqlite

## Security Considerations

1. **Pin Major Versions**: Use `>=` for flexibility but test thoroughly
2. **Regular Updates**: Check for security advisories monthly
3. **Vulnerability Scanning**: Use `pip-audit` or `safety` tools
4. **Lock Files**: Generate `requirements.lock` or use Poetry's lock file

## Compatibility Matrix

| Dependency | Python 3.11 | Python 3.12 | Python 3.13 |
|------------|-------------|-------------|-------------|
| mcp        | ✅          | ✅          | ✅          |
| httpx      | ✅          | ✅          | ✅          |
| pydantic   | ✅          | ✅          | ✅          |
| openai     | ✅          | ✅          | ✅          |
| pytest     | ✅          | ✅          | ✅          |

## Known Issues & Workarounds

### Issue 1: MCP SDK Version Compatibility
- **Problem**: MCP SDK is rapidly evolving
- **Solution**: Pin to tested version, monitor releases
- **Workaround**: Use version constraints in pyproject.toml

### Issue 2: OpenAI Client Rate Limiting
- **Problem**: API rate limits may affect healing speed
- **Solution**: Implement exponential backoff
- **Workaround**: Use local Granite 3.0 deployment if available

## Future Dependencies

Potential additions for enhanced functionality:

1. **LangChain** - For advanced prompt engineering
2. **Redis** - For distributed state management
3. **Celery** - For task queue management
4. **FastAPI** - For REST API interface
5. **Grafana/Prometheus** - For advanced monitoring

## Dependency Update Strategy

1. **Monthly**: Check for security updates
2. **Quarterly**: Review and update minor versions
3. **Annually**: Consider major version upgrades
4. **Always**: Test in staging before production

## License Compatibility

All dependencies use permissive licenses compatible with production use:
- MIT License: mcp, httpx, pydantic, pytest
- Apache 2.0: openai
- BSD License: pyyaml

No GPL or copyleft licenses that would restrict commercial use.