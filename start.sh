#!/bin/bash
# Simple startup script for Multi-Agent Loan Processing System

set -e

echo "🚀 Multi-Agent Loan Processing System"
echo "======================================"
echo

# Check requirements
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' is required"
    echo "   Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Cleanup function
cleanup() {
    echo
    echo "🧹 Stopping servers..."
    pkill -f "loan_processing.tools.mcp_servers" || true
    echo "✅ Cleanup completed"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "📋 Starting MCP servers..."
python start_mcp_servers.py

echo
echo "📋 Starting console application..."
echo "💡 Use Ctrl+C to stop everything"
echo

uv run python run_console_app.py