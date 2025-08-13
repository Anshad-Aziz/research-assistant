# src/models/brief.py

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Reference(BaseModel):
    url: str = Field(description="URL of the reference")
    title: str = Field(description="Title of the reference")
    key_points: List[str] = Field(description="Key points from this reference")
    relevance_score: float = Field(description="Relevance score (0-1)")

class BriefSection(BaseModel):
    heading: str = Field(description="Section heading")
    content: str = Field(description="Section content")
    references: List[int] = Field(description="Indices to the references list")

class TokenUsage(BaseModel):
    prompt: int = Field(description="Number of tokens in the prompt")
    completion: int = Field(description="Number of tokens in the completion")
    total: int = Field(description="Total number of tokens")

class FinalBrief(BaseModel):
    topic: str = Field(description="Research topic")
    summary: str = Field(description="Overall summary of the research")
    sections: List[BriefSection] = Field(description="Research sections")
    references: List[Reference] = Field(description="List of references")
    metadata: Dict[str, Any] = Field(description="Additional metadata")
    timestamp: datetime = Field(description="Timestamp when the brief was created")
    token_usage: TokenUsage = Field(description="Token usage statistics")