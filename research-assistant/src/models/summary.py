from typing import List
from pydantic import BaseModel, Field

class SourceSummary(BaseModel):
    source_url: str = Field(description="URL of the source")
    source_title: str = Field(description="Title of the source")
    key_points: List[str] = Field(description="Key points from the source")
    evidence: List[str] = Field(description="Evidence or supporting information")
    relevance_score: float = Field(description="Score indicating relevance to the topic (0-1)")
    summary: str = Field(description="Brief summary of the source content")
    content_type: str = Field(description="Type of content (e.g., article, paper, report)")

    