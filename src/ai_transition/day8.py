import asyncio
import os
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion


client = AsyncOpenAI(api_key=os.environ.get("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

async def translate_tech_concept(java_concept : str) -> str | None:
    messages = [{"role": "system", "content": "You are a Senior Engineer. Explain the provided Java concept to a Python developer using Python analogies."},
                {"role": "user", "content": java_concept}]
    response: ChatCompletion = await client.chat.completions.create(messages= messages, model="openai/gpt-oss-20b", temperature=0.7)
    return response.choices[0].message.content

async def main() -> None:
    if not os.environ.get("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable is not set.")
        return

    print("Calling OpenAI...")
    reply = await translate_tech_concept("Multithreading")
    print(f"AI: {reply}")


if __name__ == "__main__":
    asyncio.run(main())