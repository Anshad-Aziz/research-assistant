from ..utils import patch
from fastapi import FastAPI, HTTPException
from typing import Optional
import uuid
import os
from pathlib import Path
from dotenv import dotenv_values
from .schemas import BriefRequest
from ..graph.workflow import create_research_graph
from ..graph.state import ResearchState


env_path = Path('.') / '.env'
if env_path.exists():
    config = dotenv_values(env_path)
    for key, value in config.items():
        os.environ[key] = value


if not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

app = FastAPI(title="Research Assistant API", version="1.0.0")



@app.post("/brief")
async def generate_brief(request: BriefRequest):
    """Generate a research brief on the given topic."""
    try:
        # Create a unique ID for this request
        request_id = str(uuid.uuid4())
        
        # Initialize state
        state = ResearchState(
            user_id=request.user_id,
            topic=request.topic,
            depth=request.depth,
            is_follow_up=request.follow_up
        )
        
        # Create and run the workflow
        workflow_app = create_research_graph()
        result = workflow_app.invoke(state.dict())
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        if not result.get("final_brief"):
            raise HTTPException(status_code=500, detail="Failed to generate brief")
        
        return result["final_brief"].dict()
    
    except ValueError as e:
        
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(error_detail) 
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)