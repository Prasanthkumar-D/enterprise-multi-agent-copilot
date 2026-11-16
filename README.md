# Enterprise Multi-Agent Support Copilot

An asynchronous, multi-agent AI orchestration API built with **FastAPI** and **Python 3.12**. 

This project demonstrates an enterprise-grade AI architecture using the **Supervisor/Worker Pattern**. Instead of a monolithic LLM prompt, a Supervisor API Gateway routes incoming customer queries to specialized domain agents (Billing vs. L3 Tech Support) which execute isolated tool calls to fetch mock database records.

## Architecture & Tech Stack
* **Framework:** FastAPI (with Pydantic for strict DTO validation)
* **AI Orchestration:** OpenAI SDK (configured for Groq/Llama 3 open-weight models)
* **Concurrency:** `asyncio` for non-blocking agent execution
* **Key Patterns:** 
  * LLM Tool Calling (Function Calling)
  * Multi-Agent Supervisor Routing
  * Dependency Injection (`Depends()`) for client lifecycle management

## The 15-Day Transition Journey
This repository also serves as my documented transition from Java/Spring Boot to modern Python AI Engineering. The files `day1.py` through `day14.py` contain my progression through core AI engineering concepts:

* **Days 1-4:** Python dependency management (`uv`), strict typing (`pyright`), and asynchronous I/O (`asyncio`).
* **Days 5-7:** Data validation and schema enforcement using `Pydantic` (translating Java POJO/Jackson patterns to Python).
* **Days 8-10:** Interfacing with LLMs (Groq, Google GenAI SDK) and handling real-time streaming (`async for`).
* **Days 11-14:** Forcing structured JSON outputs and building autonomous Tool Calling (Function Calling) loops.
* **Day 15 (`app.py`):** The final Capstone — integrating it all into a unified FastAPI orchestration layer.

## How It Works
1. **The Gateway:** The `/api/copilot` endpoint receives a JSON payload containing a `customer_id` and `user_query`.
2. **Context Injection:** The Supervisor Agent analyzes the intent without answering it directly, determining the routing path.
3. **Delegation:** The request is handed off to either the `Billing Agent` or `Tech Support Agent`.
4. **Tool Execution:** The domain agent executes local Python functions (simulating SQL queries and Splunk log searches) to fetch real-world context.
5. **Synthesis:** The domain agent synthesizes the retrieved data into a concise, API-friendly JSON response.

## Running Locally
```bash
# 1. Install uv (if not installed)
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# 2. Clone and install dependencies
git clone <your-repo-url>
cd ai-transition
uv sync

# 3. Set your API Key
export GROQ_API_KEY="your_api_key_here" # Linux/Mac
set GROQ_API_KEY="your_api_key_here" # Windows cmd

# 4. Run the server
uv run fastapi dev src/ai_transition/app.py
