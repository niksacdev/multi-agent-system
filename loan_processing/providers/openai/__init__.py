"""OpenAI provider for loan processing agents.

This package provides OpenAI Agents SDK-specific implementations
using natural OpenAI patterns like Runner and autonomous tool selection.

Usage:
    # Import OpenAI-specific agents
    from loan_processing.providers.openai.agents import credit_agent
    
    # Import OpenAI-specific orchestrators
    from loan_processing.providers.openai.orchestrators import process_application_sequential
    
    # Use OpenAI natural patterns
    agent = credit_agent(model="gpt-4")
    result = await Runner.run(agent, input="...")
"""

from .agents.credit import credit_agent
from .orchestrators.sequential import process_application_sequential

__all__ = ["credit_agent", "process_application_sequential"]
