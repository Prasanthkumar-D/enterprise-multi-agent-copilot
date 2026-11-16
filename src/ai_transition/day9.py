import asyncio
import os
from google import genai
from google.genai import types

client = genai.Client()

for model in client.models.list():
    print(model.name)

async def compare_error_handling(client : genai.Client(), concept: str) -> str | None:
    config = types.GenerateContentConfig(system_instruction = "You are a Senior Engineer. Explain the provided Java concept to a Python developer using Python analogies.",
                                         temperature=0.7)
    response = await client.aio.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"Explain {concept} in one sentence.",
        config=config
    )
    return response.text


async def main() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY is not set.")
        return

    print("Calling Gemini...")
    reply = await compare_error_handling(client, "Garbage Collection")
    print(f"AI: {reply}")


if __name__ == "__main__":
    asyncio.run(main())