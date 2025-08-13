# tests/unit/test_nodes.py
import pytest
from unittest.mock import Mock, patch
from src.graph.nodes import summarize_context, create_research_plan, execute_search
from src.graph.state import ResearchState

def test_create_research_plan():
    """Test research plan creation."""
    state = {
        "user_id": "test_user",
        "topic": "Climate Change",
        "depth": 3,
        "is_follow_up": False,
        "context_summary": None
    }
    
    with patch('src.graph.nodes.get_llm') as mock_get_llm:
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = '{"main_topic": "Climate Change", "subtopics": ["Causes", "Effects"], "queries": [{"query": "What causes climate change?", "purpose": "Understand causes", "subtopic": "Causes"}], "expected_depth": 3, "estimated_sources": 5}'
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        result = create_research_plan(state)
        
        assert "research_plan" in result
        assert result["research_plan"]["main_topic"] == "Climate Change"
        mock_get_llm.assert_called_once_with("planning")