import asyncio
import httpx
from typing import Any

async def fetch_todo(client: httpx.AsyncClient, todo_id: int) -> dict[str, Any]:
    url = f"https://jsonplaceholder.typicode.com/todos/{todo_id}"
    response = await client.get(url)
    return response.json()

async def main() -> None:
    async with httpx.AsyncClient() as client:
        tasks = [fetch_todo(client, i) for i in range(1, 6)]

        results: list[dict[str, Any]] = await asyncio.gather(*tasks)
        for result in results:
            title = result.get("title", "Unknown")
            print(f"Fetched title: {title}")

if __name__ == "__main__":
    asyncio.run(main())