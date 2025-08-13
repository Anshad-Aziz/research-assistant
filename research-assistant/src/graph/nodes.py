from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticOutputParser
from ..models.plan import ResearchPlan
from ..models.summary import SourceSummary
from ..models.brief import FinalBrief
from ..services.context import get_previous_interactions, generate_context_summary
from ..services.llm import get_llm
from ..services.storage import save_brief

def summarize_context(state: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize previous interactions if this is a follow-up query."""
    if state.get("is_follow_up"):
        previous_interactions = get_previous_interactions(state["user_id"])
        state["previous_interactions"] = previous_interactions
        state["context_summary"] = generate_context_summary(
            state["topic"], 
            previous_interactions
        )
    return state


def create_research_plan(state: Dict[str, Any]) -> Dict[str, Any]:
    """Create a research plan based on the topic and context."""
    llm = get_llm("planning")  # Use Llama 3 70B for planning
    
    parser = PydanticOutputParser(pydantic_object=ResearchPlan)
    
    prompt = f"""
    Create a detailed research plan for the topic: "{state['topic']}"
    
    Research depth: {state['depth']} (1=simple overview, 5=in-depth analysis)
    
    {f"Context from previous research: {state['context_summary']}" if state.get('context_summary') else ""}
    
    Instructions:
    1. Identify 3-5 key subtopics related to the main topic
    2. For each subtopic, create 1-2 specific search queries that will find high-quality sources
    3. Each query should be designed to retrieve comprehensive information
    4. Estimate the number of sources needed based on the research depth
    
    {parser.get_format_instructions()}
    """
    
    try:
        response = llm.invoke(prompt)
        research_plan = parser.parse(response.content)
        state["research_plan"] = research_plan
    except Exception as e:
        state["error"] = f"Error creating research plan: {str(e)}"
    
    return state

def execute_search(state: Dict[str, Any]) -> Dict[str, Any]:
    """Execute search queries based on the research plan."""
    from langchain_community.tools.tavily_search import TavilySearchResults
    
    search_tool = TavilySearchResults(max_results=state["depth"] * 2)
    search_results = []
    
    for query in state["research_plan"].queries:
        try:
            results = search_tool.invoke(query.query)
            search_results.extend(results)
        except Exception as e:
            
            print(f"Error executing search query '{query.query}': {str(e)}")
    
    state["search_results"] = search_results
    return state

def fetch_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch full content for each search result."""
    from langchain_community.document_loaders import WebBaseLoader
    
    fetched_results = []
    
    for result in state["search_results"]:
        try:
            loader = WebBaseLoader(result["url"])
            docs = loader.load()
            if docs:
                result["content"] = docs[0].page_content
            fetched_results.append(result)
        except Exception as e:
            
            print(f"Error fetching content from {result['url']}: {str(e)}")
            fetched_results.append(result)
    
    state["search_results"] = fetched_results
    return state


def summarize_sources(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate structured summaries for each source."""
    llm = get_llm("summarization")  
    
    parser = PydanticOutputParser(pydantic_object=SourceSummary)
    source_summaries = []
    
    for i, result in enumerate(state["search_results"]):
        if "content" not in result:
            continue
            
        prompt = f"""
        Analyze and summarize the following content from {result['url']} titled "{result.get('title', 'Unknown')}".
        
        Research topic: {state['topic']}
        
        Content:
        {result['content'][:4000]}  # Limit content length
        
        Instructions:
        1. Extract the key points relevant to the research topic
        2. Identify specific evidence or data that supports these points
        3. Assess the relevance of this source to the research topic (0-1 scale)
        4. Identify the type of content (article, paper, report, etc.)
        5. Create a concise summary focusing on the most important information
        
        {parser.get_format_instructions()}
        """
        
        try:
            response = llm.invoke(prompt)
            summary = parser.parse(response.content)
            source_summaries.append(summary)
        except Exception as e:
            
            print(f"Error summarizing source {result['url']}: {str(e)}")
    
    state["source_summaries"] = source_summaries
    return state


def synthesize_brief(state: Dict[str, Any]) -> Dict[str, Any]:
    """Synthesize all source summaries into a coherent brief."""
    llm = get_llm("synthesis")  
    
    parser = PydanticOutputParser(pydantic_object=FinalBrief)
    
    
    formatted_sources = []
    for i, summary in enumerate(state["source_summaries"]):
        formatted_sources.append(f"Source {i+1}: {summary.source_title}\nURL: {summary.source_url}\nKey Points: {', '.join(summary.key_points)}\nSummary: {summary.summary}")
    
    sources_text = "\n\n".join(formatted_sources)
    
    prompt = f"""
    Synthesize a comprehensive research brief on the topic: {state['topic']}
    
    Research plan: {state['research_plan']}
    
    Source summaries:
    {sources_text}
    
    {f"Context from previous research: {state['context_summary']}" if state.get('context_summary') else ""}
    
    Instructions:
    1. Create a well-structured brief with multiple sections
    2. Each section should have a clear heading and detailed content
    3. Include specific information from the sources
    4. Reference sources in each section using their index numbers (1, 2, 3, etc.)
    5. Include a complete references section at the end
    
    {parser.get_format_instructions()}
    """
    
    try:
        
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-4")  
        
        prompt_tokens = len(encoding.encode(prompt))
        response = llm.invoke(prompt)
        completion_tokens = len(encoding.encode(response.content))
        
        brief = parser.parse(response.content)
        
        
        if not brief.references and state["source_summaries"]:
            brief.references = []
            for summary in state["source_summaries"]:
                brief.references.append(Reference(
                    url=summary.source_url,
                    title=summary.source_title,
                    key_points=summary.key_points,
                    relevance_score=summary.relevance_score
                ))
        
        
        brief.token_usage = {
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": prompt_tokens + completion_tokens
        }
        
        state["final_brief"] = brief
    except Exception as e:
        state["error"] = f"Error synthesizing brief: {str(e)}"
    
    return state


def post_process(state: Dict[str, Any]) -> Dict[str, Any]:
    """Post-process the final brief and save it."""
    if state.get("final_brief"):
        
        state["final_brief"].metadata = {
            "user_id": state["user_id"],
            "depth": state["depth"],
            "is_follow_up": state["is_follow_up"],
            "created_at": state["created_at"].isoformat()
        }
        
        
        if not state["final_brief"].timestamp:
            state["final_brief"].timestamp = datetime.now()
        
        
        if not state["final_brief"].token_usage:
            state["final_brief"].token_usage = {
                "prompt": 0,
                "completion": 0,
                "total": 0
            }
        
        
        if not state["final_brief"].references and state.get("source_summaries"):
            state["final_brief"].references = []
            for summary in state["source_summaries"]:
                state["final_brief"].references.append(Reference(
                    url=summary.source_url,
                    title=summary.source_title,
                    key_points=summary.key_points,
                    relevance_score=summary.relevance_score
                ))
        
        
        save_brief(state["user_id"], state["final_brief"].dict())
    
    return state