from langchain_groq import ChatGroq
from langchain.globals import set_debug
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Set debug mode based on environment variable
set_debug(os.getenv("LANGCHAIN_DEBUG", "false").lower() == "true")

# Disable LangSmith tracing if API key is not set
if not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

def get_llm(task_type: str):
    """Get an appropriate Groq LLM for the given task type."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not set. Please set it in your .env file.")
    
    # Use Llama 3 70B for complex reasoning tasks
    if task_type in ["planning", "synthesis"]:
        return ChatGroq(
            model="llama3-70b-8192",
            temperature=0.1,
            max_tokens=4000,
            groq_api_key=groq_api_key,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]) if os.getenv("LANGCHAIN_DEBUG", "false").lower() == "true" else None
        )
    
    # Use Mixtral for simpler tasks
    elif task_type in ["summarization", "formatting"]:
        return ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0.2,
            max_tokens=2000,
            groq_api_key=groq_api_key,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]) if os.getenv("LANGCHAIN_DEBUG", "false").lower() == "true" else None
        )
    
    # Default to Mixtral
    else:
        return ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0.2,
            max_tokens=2000,
            groq_api_key=groq_api_key,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]) if os.getenv("LANGCHAIN_DEBUG", "false").lower() == "true" else None
        )