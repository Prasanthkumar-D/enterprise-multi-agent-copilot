import os
import asyncio
import json
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessageParam
from typing import Iterable

client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def get_weather_report(area_name: str) -> str:
    print(f"--- SYSTEM: Executing get_weather_report for {area_name} ---")
    if area_name.lower() == "visakhapatnam":
        return "Based on the daily forecast for Visakhapatnam, Andhra Pradesh, the high temperature today is 29°C with mostly cloudy conditions and wind at 12 mph from the northeast."
    return "Weather data not found."

async def main() -> None:
    if not os.environ.get("GROQ_API_KEY"):
        return

    tools : Iterable[ChatCompletionToolParam] = [
        {
            "type": "function",
            "function": {
                "name": "get_weather_report",
                "description": "Fetch the today's weather data of a particular area",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "area_name":{
                            "type": "string",
                            "description": "area name"
                        }
                    },
                    "required": ["area_name"]
                }
            }
        }
    ]

    messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": "what will be highest tempeature reciorded today in Visakhapatnam"}]
    print("Calling AI (First Pass)...")
    response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=tools,
        tool_choice="auto"  # Let the AI decide if it needs to use the tool
    )

    message = response.choices[0].message
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        messages.append(message)
        arguments = json.loads(tool_call.function.arguments)
        area = arguments.get("area_name", "")
        result_string = get_weather_report(area)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result_string
        })
        print("Calling AI (Second Pass with tool data)...")
        final_response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages
        )
        print(f"\nFinal AI Answer: {final_response.choices[0].message.content}")
    else:
        print(f"AI just replied normally: {message.content}")

if __name__ == '__main__':
    asyncio.run(main())


