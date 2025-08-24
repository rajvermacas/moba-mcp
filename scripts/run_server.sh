#!/bin/bash
# Run the MCP server with SSE transport

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Parse port from MCP_SERVER_URL if set, otherwise use default
if [ -n "$MCP_SERVER_URL" ]; then
    PORT=$(echo $MCP_SERVER_URL | sed -n 's/.*:\([0-9]*\).*/\1/p')
    if [ -z "$PORT" ]; then
        PORT=8000
    fi
else
    PORT=${PORT:-8000}
fi

echo "Starting MCP Server with SSE Transport..."
echo "========================================"
echo "Server will be accessible at: http://0.0.0.0:$PORT"
echo "SSE endpoint: http://0.0.0.0:$PORT/sse"
echo "========================================"
echo ""

# Run without specifying port/host to let environment variables take effect
poetry run python -m moba_mcp.server \
    --transport sse \
    --database test_data/sample.db \
    --metadata resources/metadata.json \
    --log-level INFO