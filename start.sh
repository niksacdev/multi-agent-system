#!/bin/bash
# Interactive startup script for Multi-Agent Loan Processing System

set -e

echo "🏦 Multi-Agent Loan Processing System"
echo "====================================="
echo "   Intelligent loan processing with AI agents"
echo

# Check requirements
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' package manager is required"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ Environment check passed"
echo

# Cleanup function
cleanup() {
    echo
    echo "🧹 Shutting down system..."
    pkill -f "loan_processing.tools.mcp_servers" || true
    echo "✅ All servers stopped cleanly"
    echo "👋 Thanks for using Multi-Agent Loan Processing!"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "🚀 Phase 1: Starting MCP Data Services"
echo "--------------------------------------"
python scripts/start_mcp_servers.py

# Check if servers started successfully
if [ $? -ne 0 ]; then
    echo "❌ Failed to start MCP servers. Please check the error messages above."
    exit 1
fi

echo
echo "🎉 System Ready!"
echo "==============="
echo "✅ All MCP data services are running"
echo "✅ AI agents are configured and ready"
echo "✅ Loan processing system is operational"
echo

# Scenario Selection
echo "🎯 Choose Test Scenario:"
echo "========================"
echo "1) Random      - Randomly selected scenario"
echo "2) Approval    - High-quality applicant (likely approved)"
echo "3) Conditional - Borderline applicant (conditional approval)"
echo "4) Manual      - High-risk applicant (manual review)"
echo "5) Denial      - Low Income applicant (likely denied)"
echo

while true; do
    read -p "Select scenario (1-5): " choice
    case $choice in
        1) scenario="random"; break;;
        2) scenario="approval"; break;;
        3) scenario="conditional"; break;;
        4) scenario="manual_review"; break;;
        5) scenario="denial"; break;;
        *) echo "❌ Invalid choice. Please select 1-5.";;
    esac
done

echo
echo "✅ Selected scenario: $scenario"
echo

echo "🚀 Phase 2: Starting Console Application"
echo "---------------------------------------"
echo "💡 Tip: Use Ctrl+C anytime to stop the entire system"
echo

uv run python scripts/run_console_app.py $scenario