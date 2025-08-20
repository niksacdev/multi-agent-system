#!/usr/bin/env python3
"""Enhanced MCP server starter with comprehensive logging."""

import subprocess
import sys
import time
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Add project root to path for utils imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from loan_processing.utils import correlation_context, get_logger  # noqa: E402

# Initialize logging
logger = get_logger(__name__)

servers = [
    {
        "module": "loan_processing.tools.mcp_servers.application_verification.server",
        "port": 8010,
        "name": "Application Verification",
    },
    {
        "module": "loan_processing.tools.mcp_servers.document_processing.server",
        "port": 8011,
        "name": "Document Processing",
    },
    {
        "module": "loan_processing.tools.mcp_servers.financial_calculations.server",
        "port": 8012,
        "name": "Financial Calculations",
    },
]


def start():
    """Start all MCP servers with user-friendly output."""
    with correlation_context("mcp_server_startup") as session_id:
        logger.info(
            "Starting MCP server startup sequence",
            component="server_manager",
            total_servers=len(servers),
            session_id=session_id,
        )

        started_servers = []
        failed_servers = []

        print("Starting data services...")
        print()

        for i, server in enumerate(servers, 1):
            server_name = server["name"]
            print(f"[{i}/{len(servers)}] Starting {server_name}...", end=" ", flush=True)

            try:
                logger.info(
                    "Starting MCP server",
                    server_name=server_name,
                    module=server["module"],
                    port=server["port"],
                    component="server_manager",
                )

                # Start server process (SSE by default as per architect recommendation)
                process = subprocess.Popen(
                    [sys.executable, "-m", server["module"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                logger.info(
                    "MCP server process started",
                    server_name=server_name,
                    pid=process.pid,
                    sse_url=f"http://localhost:{server['port']}/sse",
                    component="server_manager",
                )

                started_servers.append(
                    {
                        "name": server_name,
                        "port": server["port"],
                        "pid": process.pid,
                        "url": f"http://localhost:{server['port']}/sse",
                    }
                )

                print(f"✅ (port {server['port']})")

            except Exception as e:
                logger.error(
                    "Failed to start MCP server",
                    server_name=server_name,
                    error_message=str(e),
                    error_type=type(e).__name__,
                    component="server_manager",
                )

                failed_servers.append({"name": server_name, "error": str(e)})
                print(f"❌ ERROR: {e}")

        # Allow servers time to initialize
        print()
        print("⏳ Initializing services...", end=" ", flush=True)
        logger.info("Waiting for servers to initialize", wait_seconds=3, component="server_manager")
        time.sleep(3)
        print("✅")

        # Log final status
        logger.info(
            "MCP server startup completed",
            started_count=len(started_servers),
            failed_count=len(failed_servers),
            total_servers=len(servers),
            component="server_manager",
        )

        if started_servers:
            logger.info(
                "Started servers summary", servers=[s["name"] for s in started_servers], component="server_manager"
            )

        if failed_servers:
            logger.warning(
                "Failed servers summary", failed_servers=[s["name"] for s in failed_servers], component="server_manager"
            )

        print()
        if len(started_servers) == len(servers):
            print("🎉 All data services started successfully!")
            print("🔗 Service endpoints:")
            for server in started_servers:
                print(f"   • {server['name']}: http://localhost:{server['port']}/sse")
        else:
            print(f"⚠️  Started {len(started_servers)}/{len(servers)} services")
            if failed_servers:
                print("❌ Failed services:")
                for server in failed_servers:
                    print(f"   • {server['name']}: {server['error']}")

        return len(started_servers) == len(servers)


if __name__ == "__main__":
    success = start()
    sys.exit(0 if success else 1)
