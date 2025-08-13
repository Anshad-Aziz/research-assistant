from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
from ..models.plan import ResearchPlan
from ..models.summary import SourceSummary
from ..models.brief import FinalBrief

class ResearchState(BaseModel):
    """State for the research workflow."""
    user_id: str
    topic: str
    depth: int
    is_follow_up: bool
    previous_interactions: Optional[List[Dict]] = None
    context_summary: Optional[str] = None
    research_plan: Optional[ResearchPlan] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    source_summaries: Optional[List[SourceSummary]] = None
    final_brief: Optional[FinalBrief] = None
    error: Optional[str] = None
    created_at: datetime = datetime.now()