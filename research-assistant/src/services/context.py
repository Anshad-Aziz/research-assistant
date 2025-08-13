from typing import Dict, List, Any
from .llm import get_llm
from .storage import get_previous_interactions

def generate_context_summary(topic: str, previous_interactions: List[Dict[str, Any]]) -> str:
    """Generate a summary of previous interactions for context."""
    if not previous_interactions:
        return "No previous research available."
    
    # Extract relevant information from previous briefs
    previous_topics = [brief.get("topic", "") for brief in previous_interactions]
    previous_summaries = [brief.get("summary", "") for brief in previous_interactions]
    
    # Create a prompt for context summarization
    prompt = f"""
    The user is researching: {topic}
    
    Previous research topics: {', '.join(previous_topics)}
    
    Previous research summaries:
    {chr(10).join([f"- {summary}" for summary in previous_summaries])}
    
    Generate a concise summary of the previous research that would be relevant
    to the user's current research topic. Focus on key findings, conclusions,
    and any gaps that might need further exploration.
    """
    
    # Use LLM to generate context summary
    llm = get_llm("summarization")
    response = llm.invoke(prompt)
    
    return response.content