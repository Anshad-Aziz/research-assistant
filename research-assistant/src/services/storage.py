# src/services/storage.py
import json
import os
import platform
from typing import Dict, List, Any
from datetime import datetime

# Simple file-based storage for demonstration
# In production, use a database like PostgreSQL or MongoDB

STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

def ensure_storage_dir():
    """Ensure the storage directory exists."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

def get_user_file_path(user_id: str) -> str:
    """Get the file path for a user's data."""
    ensure_storage_dir()
    return os.path.join(STORAGE_DIR, f"{user_id}.json")

def load_user_data(user_id: str) -> Dict[str, Any]:
    """Load user data from file."""
    file_path = get_user_file_path(user_id)
    
    if not os.path.exists(file_path):
        return {"briefs": []}
    
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading user data for {user_id}: {str(e)}")
        return {"briefs": []}

def save_user_data(user_id: str, data: Dict[str, Any]):
    """Save user data to file."""
    file_path = get_user_file_path(user_id)
    
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving user data for {user_id}: {str(e)}")

def get_previous_interactions(user_id: str) -> List[Dict[str, Any]]:
    """Get previous interactions for a user."""
    user_data = load_user_data(user_id)
    return user_data.get("briefs", [])

def save_brief(user_id: str, brief: Dict[str, Any]):
    """Save a brief to the user's history."""
    user_data = load_user_data(user_id)
    
    # Add timestamp if not present
    if "timestamp" not in brief:
        brief["timestamp"] = datetime.now().isoformat()
    
    user_data["briefs"].append(brief)
    save_user_data(user_id, user_data)