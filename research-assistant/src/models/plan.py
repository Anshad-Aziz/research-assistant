from typing import List, Optional
from pydantic import BaseModel, Field

class ResearchQuery(BaseModel):
    query: str = Field(description="The search query to execute")
    purpose: str = Field(description="The purpose of this query in the research")
    subtopic: str = Field(description="The subtopic this query addresses")

class ResearchPlan(BaseModel):
    main_topic: str = Field(description="The main research topic")
    subtopics: List[str] = Field(description="List of subtopics to explore")
    queries: List[ResearchQuery] = Field(description="List of search queries to execute")
    expected_depth: int = Field(description="Expected depth of research (1-5)")
    estimated_sources: int = Field(description="Estimated number of sources to find")