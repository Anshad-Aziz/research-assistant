from langgraph.graph import Graph, END
from typing import Dict, Any
from .state import ResearchState
from .nodes import (
    summarize_context,
    create_research_plan,
    execute_search,
    fetch_content,
    summarize_sources,
    synthesize_brief,
    post_process
)

def create_research_graph():
    """Create and configure the research workflow graph."""
    workflow = Graph()
    
    # Add nodes
    workflow.add_node("context_summarization", summarize_context)
    workflow.add_node("planning", create_research_plan)
    workflow.add_node("search", execute_search)
    workflow.add_node("content_fetching", fetch_content)
    workflow.add_node("source_summarization", summarize_sources)
    workflow.add_node("synthesis", synthesize_brief)
    workflow.add_node("post_processing", post_process)
    
    
    workflow.set_entry_point("context_summarization")
    
    
    workflow.add_conditional_edges(
        "context_summarization",
        lambda state: "planning" if state.get("error") is None else "post_processing",
        {
            "planning": "planning",
            "post_processing": "post_processing"
        }
    )
    
    workflow.add_edge("planning", "search")
    workflow.add_edge("search", "content_fetching")
    workflow.add_edge("content_fetching", "source_summarization")
    workflow.add_edge("source_summarization", "synthesis")
    workflow.add_edge("synthesis", "post_processing")
    workflow.add_edge("post_processing", END)
    
    
    app = workflow.compile()
    
    return app