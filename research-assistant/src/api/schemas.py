from pydantic import BaseModel

class BriefRequest(BaseModel):
    topic: str
    depth: int
    follow_up: bool
    user_id: str