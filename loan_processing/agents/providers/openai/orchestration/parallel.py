"""
Parallel orchestration pattern executor.

This module implements the parallel execution pattern where certain agents
can process concurrently to improve performance and efficiency.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from loan_processing.agents.providers.openai.orchestration.engine import OrchestrationContext
from loan_processing.agents.providers.openai.orchestration.base import PatternExecutor, HandoffValidationService


class ParallelPatternExecutor(PatternExecutor):
    """Executor for parallel orchestration patterns."""
    
    def __init__(self, agent_registry=None):
        """Initialize parallel pattern executor."""
        super().__init__(agent_registry)
        self.handoff_service = HandoffValidationService()
    
    async def execute(
        self, 
        pattern_config: Dict[str, Any], 
        context: OrchestrationContext, 
        model: str | None
    ) -> None:
        """Execute parallel orchestration pattern."""
        
        context.add_audit_entry("Starting parallel orchestration execution")
        
        # Execute initial agent(s) (typically intake)
        await self._execute_initial_agents(pattern_config, context, model)
        
        # Execute parallel branches if configured
        if "parallel_branches" in pattern_config:
            await self._execute_parallel_branches(pattern_config["parallel_branches"], context, model)
        
        # Execute synthesis agents (typically risk)
        await self._execute_synthesis_agents(pattern_config, context, model)
        
        context.add_audit_entry("Parallel orchestration execution completed")
    
    async def _execute_initial_agents(
        self,
        pattern_config: Dict[str, Any],
        context: OrchestrationContext,
        model: str | None
    ) -> None:
        """Execute initial stage agents (usually intake)."""
        
        initial_agents = [
            agent for agent in pattern_config.get("agents", []) 
            if agent.get("execution_stage") == "initial"
        ]
        
        context.add_audit_entry(f"Executing {len(initial_agents)} initial agents")
        
        for agent_config in initial_agents:
            agent_type = agent_config["type"]
            context.add_audit_entry(f"Executing initial agent: {agent_type}")
            await self.agent_execution_service.execute_agent(agent_type, agent_config, context, model)
            context.add_audit_entry(f"Completed initial agent: {agent_type}")
    
    async def _execute_parallel_branches(
        self,
        branches: List[Dict[str, Any]],
        context: OrchestrationContext,
        model: str | None
    ) -> None:
        """Execute parallel branches concurrently."""
        
        context.add_audit_entry(f"Starting {len(branches)} parallel branches")
        
        # Create tasks for each branch
        tasks = []
        for branch in branches:
            branch_name = branch.get("branch_name", "unnamed")
            context.add_audit_entry(f"Creating task for branch: {branch_name}")
            
            for agent_config in branch.get("agents", []):
                task = self._execute_branch_agent(agent_config, context, model, branch_name)
                tasks.append(task)
        
        # Execute all branches concurrently
        if tasks:
            context.add_audit_entry(f"Executing {len(tasks)} branch agents concurrently")
            await asyncio.gather(*tasks, return_exceptions=True)
            context.add_audit_entry("All parallel branches completed")
    
    async def _execute_branch_agent(
        self,
        agent_config: Dict[str, Any],
        context: OrchestrationContext,
        model: str | None,
        branch_name: str
    ) -> None:
        """Execute a single agent within a parallel branch."""
        
        agent_type = agent_config["type"]
        context.add_audit_entry(f"Executing {agent_type} in branch: {branch_name}")
        
        try:
            # Check dependencies before execution
            depends_on = agent_config.get("depends_on", [])
            if depends_on:
                for dependency in depends_on:
                    dependency_result = getattr(context, f"{dependency}_result", None)
                    if dependency_result is None:
                        raise ValueError(f"Dependency '{dependency}' not satisfied for agent '{agent_type}'")
            
            await self.agent_execution_service.execute_agent(agent_type, agent_config, context, model)
            context.add_audit_entry(f"Completed {agent_type} in branch: {branch_name}")
            
        except Exception as e:
            context.add_audit_entry(f"Failed {agent_type} in branch {branch_name}: {str(e)}")
            # Handle branch failure according to configuration
            await self._handle_branch_failure(agent_type, branch_name, e, context)
    
    async def _execute_synthesis_agents(
        self,
        pattern_config: Dict[str, Any],
        context: OrchestrationContext,
        model: str | None
    ) -> None:
        """Execute synthesis agents that combine parallel results."""
        
        synthesis_agents = pattern_config.get("synthesis_agents", [])
        
        if synthesis_agents:
            context.add_audit_entry(f"Executing {len(synthesis_agents)} synthesis agents")
            
            for agent_config in synthesis_agents:
                agent_type = agent_config["type"]
                
                # Verify dependencies from parallel branches are satisfied
                depends_on = agent_config.get("depends_on", [])
                for dependency in depends_on:
                    dependency_result = getattr(context, f"{dependency}_result", None)
                    if dependency_result is None:
                        context.add_audit_entry(f"Warning: Synthesis agent {agent_type} missing dependency: {dependency}")
                
                context.add_audit_entry(f"Executing synthesis agent: {agent_type}")
                await self.agent_execution_service.execute_agent(agent_type, agent_config, context, model)
                context.add_audit_entry(f"Completed synthesis agent: {agent_type}")
    
    async def _handle_branch_failure(
        self,
        agent_type: str,
        branch_name: str,
        error: Exception,
        context: OrchestrationContext
    ) -> None:
        """Handle failure of a branch agent according to configuration."""
        
        # Log the failure
        error_msg = f"Branch failure in {branch_name}: {agent_type} failed with {str(error)}"
        context.add_audit_entry(error_msg)
        context.errors.append(error_msg)
        
        # For now, we continue with other branches
        # Future enhancement: implement sophisticated failure handling
        # based on synchronization configuration
    
    def validate_config(self, pattern_config: Dict[str, Any]) -> List[str]:
        """Validate parallel pattern configuration."""
        errors = self._validate_base_config(pattern_config)
        
        # Validate pattern type
        if pattern_config.get("pattern_type") != "parallel":
            errors.append("Pattern type must be 'parallel' for ParallelPatternExecutor")
        
        # Validate parallel branches
        if "parallel_branches" in pattern_config:
            errors.extend(self._validate_parallel_branches(pattern_config["parallel_branches"]))
        
        # Validate synthesis agents
        if "synthesis_agents" in pattern_config:
            errors.extend(self._validate_synthesis_agents(pattern_config["synthesis_agents"]))
        
        # Validate synchronization configuration
        if "synchronization" in pattern_config:
            errors.extend(self._validate_synchronization_config(pattern_config["synchronization"]))
        
        return errors
    
    def _validate_parallel_branches(self, branches: List[Dict[str, Any]]) -> List[str]:
        """Validate parallel branches configuration."""
        errors = []
        
        if not isinstance(branches, list):
            errors.append("'parallel_branches' must be a list")
            return errors
        
        if len(branches) < 2:
            errors.append("Parallel pattern requires at least 2 branches")
        
        branch_names = set()
        for i, branch in enumerate(branches):
            if not isinstance(branch, dict):
                errors.append(f"Branch {i} must be a dictionary")
                continue
            
            # Validate branch name uniqueness
            branch_name = branch.get("branch_name")
            if not branch_name:
                errors.append(f"Branch {i} missing 'branch_name'")
            elif branch_name in branch_names:
                errors.append(f"Duplicate branch name: '{branch_name}'")
            else:
                branch_names.add(branch_name)
            
            # Validate agents in branch
            if "agents" not in branch:
                errors.append(f"Branch {i} ({branch_name}) missing 'agents'")
            elif not isinstance(branch["agents"], list) or len(branch["agents"]) == 0:
                errors.append(f"Branch {i} ({branch_name}) must have at least one agent")
        
        return errors
    
    def _validate_synthesis_agents(self, synthesis_agents: List[Dict[str, Any]]) -> List[str]:
        """Validate synthesis agents configuration."""
        errors = []
        
        if not isinstance(synthesis_agents, list):
            errors.append("'synthesis_agents' must be a list")
            return errors
        
        for i, agent in enumerate(synthesis_agents):
            if not isinstance(agent, dict):
                errors.append(f"Synthesis agent {i} must be a dictionary")
                continue
            
            # Validate required fields
            if "type" not in agent:
                errors.append(f"Synthesis agent {i} missing 'type'")
            
            # Validate dependencies
            if "depends_on" not in agent:
                errors.append(f"Synthesis agent {i} should specify dependencies")
            elif not isinstance(agent["depends_on"], list):
                errors.append(f"Synthesis agent {i} 'depends_on' must be a list")
        
        return errors
    
    def _validate_synchronization_config(self, sync_config: Dict[str, Any]) -> List[str]:
        """Validate synchronization configuration."""
        errors = []
        
        if not isinstance(sync_config, dict):
            errors.append("'synchronization' must be a dictionary")
            return errors
        
        # Validate boolean fields
        bool_fields = ["wait_for_all_branches"]
        for field in bool_fields:
            if field in sync_config and not isinstance(sync_config[field], bool):
                errors.append(f"'{field}' must be a boolean")
        
        # Validate numeric fields
        if "branch_timeout_seconds" in sync_config:
            timeout = sync_config["branch_timeout_seconds"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                errors.append("'branch_timeout_seconds' must be a positive number")
        
        if "partial_completion_threshold" in sync_config:
            threshold = sync_config["partial_completion_threshold"]
            if not isinstance(threshold, (int, float)) or not (0.0 <= threshold <= 1.0):
                errors.append("'partial_completion_threshold' must be between 0.0 and 1.0")
        
        return errors


__all__ = ["ParallelPatternExecutor"]