#!/usr/bin/env python3
"""Simple MCP server starter."""

import subprocess
import sys
import time

servers = [
    {"module": "loan_processing.tools.mcp_servers.application_verification.server", "port": 8010},
    {"module": "loan_processing.tools.mcp_servers.document_processing.server", "port": 8011},
    {"module": "loan_processing.tools.mcp_servers.financial_calculations.server", "port": 8012},
]


def start():
    """Start all MCP servers."""
    print("Starting MCP servers...")

    for server in servers:
        try:
            subprocess.Popen([sys.executable, "-m", server["module"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            name = server["module"].split(".")[-2].replace("_", " ").title()
            print(f"✅ {name} - http://localhost:{server['port']}/sse")
        except Exception as e:
            print(f"❌ {server['module']}: {e}")

    time.sleep(3)  # Let servers start
    print("\nMCP servers started - test URLs above to verify")


if __name__ == "__main__":
    start()
