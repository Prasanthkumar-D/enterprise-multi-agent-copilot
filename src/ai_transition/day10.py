import asyncio
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.environ.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")


async def translate_tech_concept(java_concept: str) -> None:
    messages = [
        {"role": "system",
         "content": "You are a Senior Engineer. Explain the provided Java concept to a Python developer using Python analogies."},
        {"role": "user", "content": java_concept}
    ]

    # 1. Swapped to Groq's most stable 2026 production model
    # 2. Removed the incorrect 'ChatCompletion' type hint
    response_stream = await client.chat.completions.create(
        messages=messages,
        model="openai/gpt-oss-20b",
        stream=True
    )

    print("AI: ", end="", flush=True)
    async for chunk in response_stream:
        # Safety check: The final streaming chunk is often empty and can cause an IndexError
        if len(chunk.choices) > 0:
            text_fragment = chunk.choices[0].delta.content
            if text_fragment is not None:
                print(text_fragment, end="", flush=True)

    print()  # Final newline to close the stream cleanly


async def main() -> None:
    if not os.environ.get("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable is not set.")
        return

    print("Calling Groq...")

    # FIXED: We no longer assign to a 'reply' variable.
    # We just await the function and let it print to the console!
    await translate_tech_concept("Multithreading")


if __name__ == "__main__":
    asyncio.run(main())