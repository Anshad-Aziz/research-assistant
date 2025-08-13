# Research Assistant: Context-Aware Research Brief Generator

## Overview

This project implements a research assistant system that generates structured, evidence-linked research briefs in response to user topics. The application supports follow-up queries by summarizing prior user interactions and incorporating this context into subsequent outputs.

## Features

- LangGraph-based workflow orchestration
- Structured output and schema enforcement
- Context summarization for follow-up queries
- LangChain integration with Groq API
- REST API and CLI interfaces
- Comprehensive testing and documentation

## Technologies Used

- Python
- LangGraph
- LangChain
- Groq API
- FastAPI
- Pydantic
- Docker
## Demo Video 
[Watch the video on Google Drive](https://drive.google.com/drive/folders/1GMmJ14Hmy1hVEhIUJU2Jc0G729sFKxtW?usp=sharing)

## Installation

1. Clone the repository:
     ```bash
     git clone https://github.com/your-username/research-assistant.git
     cd research-assistant

2. Create a virtual environment:
     ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install dependencies:
     ```bash
     pip install -r requirements.txt
4. Set up environment variables:
     ```bash
     GROQ_API_KEY=gsk_******************************
    TAVILY_API_KEY=tvly-dev-**************************
    LANGCHAIN_API_KEY=sv2_pt_**************************
    LANGCHAIN_PROJECT=research-assistant
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_DEBUG=false
    STORAGE_DIR=./storage   
     
          
     
