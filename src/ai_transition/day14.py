import os
import json
from typing import Iterable
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

app = FastAPI(title="Multi-Agent Orchestrator API", version="1.0")

class OrchestrationRequest(BaseModel):
    user_query: str

class OrchestrationResponse(BaseModel):
    ai_answer: str
    executed_tools: list[str]

def get_ai_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

def get_weather_report(area_name: str) -> str:
    print(f"--- SYSTEM: Executing get_weather_report for {area_name} ---")
    if area_name.lower() == "visakhapatnam":
        return "29°C, mostly cloudy."
    return "Weather data not found."

@app.post("/orchestrate")
async def orchestrate_request(
    request: OrchestrationRequest,
    # Injecting the client here via Depends()
    client: AsyncOpenAI = Depends(get_ai_client)
) -> OrchestrationResponse:
    print(f"Processing Query: {request.user_query}")

    tools: Iterable[ChatCompletionToolParam] = [{
        "type": "function",
        "function": {
            "name": "get_weather_report",
            "description": "Fetch the today's weather data of a particular area",
            "parameters": {
                "type": "object",
                "properties": {"area_name": {"type": "string"}},
                "required": ["area_name"]
            }
        }
    }]

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system",
         "content": "You are a highly capable routing agent. Answer questions using the provided tools if necessary."},
        {"role": "user", "content": request.user_query}
    ]

    # PASS 1: Let the AI decide if a tool is needed
    response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message
    executed_tools = []
    final_answer = ""

    # Check if a tool was requested
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        executed_tools.append(tool_call.function.name)

        messages.append(message)

        # Execute local Python function
        arguments = json.loads(tool_call.function.arguments)
        area = arguments.get("area_name", "")
        result_string = get_weather_report(area)

        # Add result to history
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result_string
        })

        # PASS 2: AI generates final answer with tool data
        final_response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages
        )
        final_answer = final_response.choices[0].message.content or "No response generated."
    else:
        # AI didn't need a tool
        final_answer = message.content or "No response generated."

    # Return structured JSON to the client
    return OrchestrationResponse(
        ai_answer=final_answer,
        executed_tools=executed_tools
    )