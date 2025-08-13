import pytest
from unittest.mock import Mock, patch
from src.graph.workflow import create_research_graph
from src.graph.state import ResearchState

def test_complete_workflow():
    """Test the complete research workflow with mocked components."""
    # Create a test state
    state = ResearchState(
        user_id="test_user",
        topic="Climate Change",
        depth=2,
        is_follow_up=False
    ).dict()
    
    # Mock all external dependencies
    with patch('src.graph.nodes.get_previous_interactions') as mock_get:
        with patch('src.graph.nodes.generate_context_summary') as mock_gen:
            with patch('src.graph.nodes.get_llm') as mock_llm:
                with patch('src.graph.nodes.TavilySearchResults') as mock_search:
                    with patch('src.graph.nodes.WebBaseLoader') as mock_loader:
                        with patch('src.graph.nodes.save_brief') as mock_save:
                            
                            # Setup mocks
                            mock_get.return_value = []
                            mock_search.return_value.invoke.return_value = [
                                {"url": "https://example.com", "title": "Example Article"}
                            ]
                            mock_loader.return_value.load.return_value = [
                                Mock(page_content="This is an example article about climate change.")
                            ]
                            
                            # Mock LLM responses
                            mock_llm_instance = Mock()
                            mock_llm.return_value = mock_llm_instance
                            
                            # Mock planning response
                            mock_plan_response = Mock()
                            mock_plan_response.content = '{"main_topic": "Climate Change", "subtopics": ["Causes", "Effects"], "queries": [{"query": "What causes climate change?", "purpose": "Understand causes", "subtopic": "Causes"}], "expected_depth": 2, "estimated_sources": 3}'
                            
                            # Mock summary response
                            mock_summary_response = Mock()
                            mock_summary_response.content = '{"source_url": "https://example.com", "source_title": "Example Article", "key_points": ["Point 1", "Point 2"], "evidence": ["Evidence 1"], "relevance_score": 0.9, "summary": "This is a summary.", "content_type": "article"}'
                            
                            # Mock synthesis response
                            mock_synthesis_response = Mock()
                            mock_synthesis_response.content = '{"topic": "Climate Change", "summary": "Climate change is a global issue.", "sections": [{"heading": "Introduction", "content": "Content here", "references": [0]}], "references": [{"url": "https://example.com", "title": "Example Article", "key_points": ["Point 1", "Point 2"], "relevance_score": 0.9}], "metadata": {}, "timestamp": "2023-01-01T00:00:00", "token_usage": {"prompt": 1000, "completion": 500}}'
                            
                            # Configure LLM to return different responses based on input
                            def mock_invoke(prompt):
                                if "Create a research plan" in prompt:
                                    return mock_plan_response
                                elif "Summarize the following content" in prompt:
                                    return mock_summary_response
                                elif "Synthesize a research brief" in prompt:
                                    return mock_synthesis_response
                                return Mock()
                            
                            mock_llm_instance.invoke.side_effect = mock_invoke
                            
                            # Create and run the workflow
                            workflow = create_research_graph()
                            result = workflow.invoke(state)
                            
                            # Verify the result
                            assert "final_brief" in result
                            assert result["final_brief"]["topic"] == "Climate Change"
                            assert len(result["final_brief"]["sections"]) == 1
                            assert len(result["final_brief"]["references"]) == 1
                            mock_save.assert_called_once()