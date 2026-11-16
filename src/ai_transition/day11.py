import asyncio
import os
from openai import AsyncOpenAI
from pydantic import BaseModel
from openai.types.chat import ChatCompletionMessageParam

class TechTranslation(BaseModel):
    concept_name: str
    java_concept: str
    python_analogy: str
    difficulty_level: int
    example_code_snippet: str


client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

async def fetch_structured_translation(concept: str) -> TechTranslation:
    messages : list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": "You are a Senior Engineer. Output your response strictly in JSON matching this structure: concept_name, java_concept, python_analogy, difficulty_level in int and example_code_snippet."
        },
        {"role": "user", "content": concept}
    ]

    response = await client.chat.completions.create(
        messages= messages,
        model="openai/gpt-oss-20b",
        response_format={"type": "json_object"}
    )
    raw_json_string = response.choices[0].message.content

    if raw_json_string is None:
        raise ValueError("AI returned an empty response")

    return TechTranslation.model_validate_json(raw_json_string)


async def main() -> None:
    if not os.environ.get("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY is missing.")
        return

    print("Asking AI for structured data...")
    translation = await fetch_structured_translation("Interfaces")

    # Notice the full IDE autocomplete and type safety here!
    print(f"\n--- {translation.concept_name} ---")
    print(f"Java: {translation.java_concept}")
    print(f"Python: {translation.python_analogy}")
    print(f"Difficulty to learn: {translation.difficulty_level}/10")
    print(f"example code: {translation.example_code_snippet}")


if __name__ == "__main__":
    asyncio.run(main())