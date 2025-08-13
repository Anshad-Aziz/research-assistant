# Import the patch first to handle Windows compatibility issues
from ..utils import patch

import click
import json
import requests
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
from typing import Dict, Any

# Load environment variables from .env file
env_path = Path('.') / '.env'
if env_path.exists():
    config = dotenv_values(env_path)
    for key, value in config.items():
        os.environ[key] = value

# Disable LangSmith tracing if API key is not set
if not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "false"

API_URL = "http://localhost:8000/brief"

@click.command()
@click.option("--topic", required=True, help="Research topic")
@click.option("--depth", default=3, type=int, help="Research depth (1-5)")
@click.option("--follow-up", is_flag=True, help="Is this a follow-up query?")
@click.option("--user-id", required=True, help="User ID for context tracking")
@click.option("--output", type=click.Path(), help="Output file path")
def generate_brief(topic: str, depth: int, follow_up: bool, user_id: str, output: str):
    """Generate a research brief using the Research Assistant API."""
    try:
        # Prepare request
        request_data = {
            "topic": topic,
            "depth": depth,
            "follow_up": follow_up,
            "user_id": user_id
        }
        
        # Make API request
        response = requests.post(API_URL, json=request_data)
        response.raise_for_status()
        
        brief = response.json()
        
        # Output results
        if output:
            with open(output, "w") as f:
                json.dump(brief, f, indent=2)
            click.echo(f"Brief saved to {output}")
        else:
            # Print a summary to console
            click.echo(f"Research Brief: {brief['topic']}")
            click.echo(f"Summary: {brief['summary']}")
            click.echo(f"Sections: {len(brief['sections'])}")
            click.echo(f"References: {len(brief['references'])}")
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            error_detail = e.response.json().get("detail", "Unknown error")
            if "GROQ_API_KEY" in error_detail:
                click.echo("Error: Groq API key not configured. Please set the GROQ_API_KEY environment variable in your .env file.", err=True)
            else:
                click.echo(f"Server error: {error_detail}", err=True)
        else:
            click.echo(f"HTTP error: {str(e)}", err=True)
    except requests.exceptions.RequestException as e:
        click.echo(f"Error calling API: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == "__main__":
    generate_brief()