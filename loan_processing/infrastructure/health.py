"""
Backend infrastructure health monitoring and service management.

This module provides health checking for MCP servers and other backend dependencies.
It's designed to provide user-friendly status information without exposing infrastructure details.
"""

import asyncio
import aiohttp
import yaml
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import logging


class ServiceStatus(Enum):
    """Service health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Health status of a single service."""
    name: str
    status: ServiceStatus
    message: str
    last_checked: Optional[str] = None
    response_time_ms: Optional[float] = None


@dataclass
class InfrastructureHealth:
    """Overall infrastructure health summary."""
    overall_status: ServiceStatus
    services: List[ServiceHealth]
    user_message: str
    detailed_errors: List[str]
    services_available: int
    services_total: int


class InfrastructureHealthService:
    """Manages health checking for backend infrastructure."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "infrastructure.yaml"
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self) -> dict:
        """Load infrastructure configuration."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"Failed to load infrastructure config: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> dict:
        """Get fallback configuration when config file is unavailable."""
        return {
            "mcp_servers": {
                "application_verification": {
                    "url": "http://localhost:8010/sse",
                    "health_check_path": "/health",
                    "timeout_seconds": 30,
                    "required": True,
                    "description": "Application verification service"
                },
                "document_processing": {
                    "url": "http://localhost:8011/sse", 
                    "health_check_path": "/health",
                    "timeout_seconds": 45,
                    "required": True,
                    "description": "Document processing service"
                },
                "financial_calculations": {
                    "url": "http://localhost:8012/sse",
                    "health_check_path": "/health", 
                    "timeout_seconds": 30,
                    "required": True,
                    "description": "Financial calculations service"
                }
            },
            "infrastructure": {
                "health_check_timeout_seconds": 5,
                "fail_fast_on_missing_services": True
            }
        }
    
    async def check_service_health(self, service_name: str, service_config: dict) -> ServiceHealth:
        """Check health of a single MCP server."""
        try:
            url = service_config["url"]
            health_path = service_config.get("health_check_path", "/health")
            timeout = service_config.get("timeout_seconds", 30)
            
            # Extract base URL and construct health check URL
            base_url = url.replace("/sse", "")  # Remove SSE endpoint
            health_url = f"{base_url}{health_path}"
            
            import time
            start_time = time.time()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.get(health_url) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    if response.status == 200:
                        return ServiceHealth(
                            name=service_name,
                            status=ServiceStatus.HEALTHY,
                            message="Service operational",
                            response_time_ms=response_time
                        )
                    else:
                        return ServiceHealth(
                            name=service_name,
                            status=ServiceStatus.DEGRADED,
                            message=f"Service responding but status {response.status}",
                            response_time_ms=response_time
                        )
                        
        except asyncio.TimeoutError:
            return ServiceHealth(
                name=service_name,
                status=ServiceStatus.UNAVAILABLE,
                message="Service health check timed out"
            )
        except aiohttp.ClientError as e:
            return ServiceHealth(
                name=service_name,
                status=ServiceStatus.UNAVAILABLE,
                message=f"Connection failed: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Health check error for {service_name}: {e}")
            return ServiceHealth(
                name=service_name,
                status=ServiceStatus.UNKNOWN,
                message=f"Health check failed: {str(e)}"
            )
    
    async def get_infrastructure_health(self) -> InfrastructureHealth:
        """Get comprehensive infrastructure health status."""
        mcp_servers = self.config.get("mcp_servers", {})
        
        # Check all services concurrently
        health_checks = []
        for service_name, service_config in mcp_servers.items():
            health_checks.append(
                self.check_service_health(service_name, service_config)
            )
        
        service_healths = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Process results
        services = []
        detailed_errors = []
        healthy_count = 0
        
        for i, result in enumerate(service_healths):
            if isinstance(result, Exception):
                service_name = list(mcp_servers.keys())[i]
                service_health = ServiceHealth(
                    name=service_name,
                    status=ServiceStatus.UNKNOWN,
                    message=f"Health check exception: {str(result)}"
                )
                detailed_errors.append(f"{service_name}: {str(result)}")
            else:
                service_health = result
                if service_health.status == ServiceStatus.HEALTHY:
                    healthy_count += 1
                elif service_health.status in [ServiceStatus.UNAVAILABLE, ServiceStatus.DEGRADED]:
                    detailed_errors.append(f"{service_health.name}: {service_health.message}")
            
            services.append(service_health)
        
        # Determine overall status
        total_services = len(services)
        required_services = sum(1 for name, config in mcp_servers.items() 
                               if config.get("required", True))
        
        if healthy_count == total_services:
            overall_status = ServiceStatus.HEALTHY
            user_message = "All services operational"
        elif healthy_count >= required_services:
            overall_status = ServiceStatus.DEGRADED  
            user_message = f"Core services operational, {total_services - healthy_count} services degraded"
        else:
            overall_status = ServiceStatus.UNAVAILABLE
            user_message = "Critical services unavailable - cannot process requests"
        
        return InfrastructureHealth(
            overall_status=overall_status,
            services=services,
            user_message=user_message,
            detailed_errors=detailed_errors,
            services_available=healthy_count,
            services_total=total_services
        )
    
    def get_user_friendly_status(self, health: InfrastructureHealth) -> tuple[bool, str]:
        """
        Convert infrastructure health to user-friendly status.
        
        Returns:
            tuple[bool, str]: (can_process_requests, user_message)
        """
        if health.overall_status == ServiceStatus.HEALTHY:
            return True, "✅ All services ready"
        elif health.overall_status == ServiceStatus.DEGRADED:
            return True, f"⚠️  Some services degraded but processing available: {health.user_message}"
        else:
            return False, f"❌ Services unavailable: {health.user_message}"
    
    def get_startup_instructions(self) -> List[str]:
        """Get user-friendly instructions for starting required services."""
        mcp_servers = self.config.get("mcp_servers", {})
        instructions = []
        
        instructions.append("To start required backend services, run these in separate terminals:")
        instructions.append("")
        
        for service_name, service_config in mcp_servers.items():
            if service_config.get("required", True):
                # Extract module path from URL for now (fallback)
                # In a proper implementation, this would come from service registry
                module_mapping = {
                    "application_verification": "loan_processing.tools.mcp_servers.application_verification.server",
                    "document_processing": "loan_processing.tools.mcp_servers.document_processing.server", 
                    "financial_calculations": "loan_processing.tools.mcp_servers.financial_calculations.server"
                }
                
                module = module_mapping.get(service_name, f"loan_processing.tools.mcp_servers.{service_name}.server")
                description = service_config.get("description", f"{service_name} service")
                
                instructions.append(f"# {description}")
                instructions.append(f"uv run python -m {module}")
                instructions.append("")
        
        return instructions


# Global health service instance
_health_service: Optional[InfrastructureHealthService] = None


def get_health_service() -> InfrastructureHealthService:
    """Get the global health service instance."""
    global _health_service
    if _health_service is None:
        _health_service = InfrastructureHealthService()
    return _health_service


async def get_backend_health() -> InfrastructureHealth:
    """Convenience function to get backend infrastructure health."""
    health_service = get_health_service()
    return await health_service.get_infrastructure_health()