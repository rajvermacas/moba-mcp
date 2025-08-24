
# moba-mcp

MCP (Model Context Protocol) implementation for moba.

## Overview

This project implements the Model Context Protocol (MCP) to provide contextual information and tools for AI models.

## Features

- MCP server implementation
- Tool definitions and handlers
- Resource management
- Context handling

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry package manager
- SQLite3 (included with Python)

### Environment Setup

#### Method 1: Using Poetry (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/moba-mcp.git
cd moba-mcp
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies in development mode:
```bash
poetry install
```
This automatically installs the package in editable/development mode within Poetry's virtual environment.

4. Activate the virtual environment:
```bash
poetry shell
```

#### Method 2: Using pip with Poetry-built package

If you prefer using pip but still want to leverage Poetry's build system:

1. Build the package with Poetry:
```bash
poetry build
```

2. Install with pip in editable mode:
```bash
# First, ensure you have a virtual environment active
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .
```

**Note:** When using `pip install -e .` with a Poetry-based project, pip will read the `pyproject.toml` and use Poetry's build backend automatically. However, this approach bypasses Poetry's dependency resolution and lock file, so it's generally better to use `poetry install` for development.

### Configuration

Set up environment variables (optional):
```bash
# Create .env file for configuration
cat > .env << EOF
DATABASE_PATH=./data/database.db
METADATA_PATH=./data/metadata.json
LOG_LEVEL=INFO
HOST=localhost
PORT=8000
TRANSPORT=stdio
EOF
```

### Running the Server

#### Option 1: Run with stdio transport (default)
```bash
python -m moba_mcp.server
```

#### Option 2: Run with SSE transport for remote access
```bash
python -m moba_mcp.server --transport sse --host 0.0.0.0 --port 8000
```

#### Option 3: Run with streamable HTTP transport
```bash
python -m moba_mcp.server --transport streamable-http --host 0.0.0.0 --port 8000
```

#### Option 4: Run in stateless mode for scalability
```bash
python -m moba_mcp.server --transport streamable-http --stateless --port 8000
```

#### Option 5: Use JSON responses instead of SSE
```bash
python -m moba_mcp.server --transport streamable-http --json-response --port 8000
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--database, --db` | Path to SQLite database file | From config/env |
| `--metadata` | Path to metadata JSON file | From config/env |
| `--host` | Host address to bind | localhost |
| `--port, -p` | Port number for the server | 8000 |
| `--transport, -t` | Transport type (stdio/sse/streamable-http) | stdio |
| `--stateless` | Enable stateless HTTP mode | False |
| `--json-response` | Use JSON responses instead of SSE | False |
| `--no-cors` | Disable CORS headers | False |
| `--log-level` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| `--server-name` | Server name identifier | talk2tables-mcp |

### Quick Start with tmux (for background execution)

To run the server in the background using tmux:
```bash
tmux new-session -d -s mcp -c "$(pwd)" "poetry run python -m moba_mcp.server --transport sse --port 8000"
```

To attach to the tmux session:
```bash
tmux attach -t mcp
```

To stop the server:
```bash
tmux kill-session -t mcp
```

## Project Structure

```
moba-mcp/
├── src/
│   └── moba_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── tools/
│       ├── resources/
│       └── handlers/
├── tests/
│   └── test_*.py
├── test_data/
│   └── # Test data files
├── scripts/
│   └── # Utility and debug scripts
├── resources/
│   └── reports/
│       └── # Generated reports
├── pyproject.toml
├── README.md
├── .gitignore
└── CLAUDE.md
```

## Usage

### Starting the MCP Server

```python
from moba_mcp import MCPServer

# Initialize the server
server = MCPServer()

# Start the server
server.start()
```

### Defining Tools

Tools can be defined in the `src/moba_mcp/tools/` directory:

```python
from moba_mcp.tools import Tool

class MyTool(Tool):
    def execute(self, params):
        # Tool implementation
        pass
```

### Adding Resources

Resources can be managed through the resource handler:

```python
from moba_mcp.resources import ResourceManager

manager = ResourceManager()
manager.add_resource("name", resource_data)
```

## Development

### Running Tests

Run all tests with coverage:
```bash
poetry run pytest
```

Run specific test file:
```bash
poetry run pytest tests/test_server.py
```

### Test Coverage

Generate coverage report:
```bash
poetry run pytest --cov=src/moba_mcp --cov-report=html
```

View the HTML coverage report at `htmlcov/index.html`.

### Code Quality

This project follows the coding guidelines defined in CLAUDE.md:
- Test-driven development approach
- Extensive logging and exception handling
- Modular architecture with files under 800 lines
- Clean project structure

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Implement your changes
5. Run tests to ensure everything passes
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/yourusername/moba-mcp/issues).

## Acknowledgments

- MCP (Model Context Protocol) specification
- Contributors and maintainers