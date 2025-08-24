#!/bin/bash
# Run the MCP server with SSE transport

echo "Starting MCP Server with SSE Transport..."
echo "========================================"
echo "Server will be accessible at: http://0.0.0.0:8000"
echo "SSE endpoint: http://0.0.0.0:8000/sse"
echo "========================================"
echo ""

poetry run python -m moba_mcp.server \
    --transport sse \
    --host 0.0.0.0 \
    --port 8000 \
    --database test_data/sample.db \
    --metadata resources/metadata.json \
    --log-level INFO