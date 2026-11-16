import httpx
from pydantic import BaseModel, Field
import asyncio

class Todo(BaseModel):
    userId: int
    id: int
    title: str
    complete: bool = Field(alias="completed", default=True)

async def fetch_todo(client: httpx.AsyncClient, id: int) -> Todo:
    url = f"https://jsonplaceholder.typicode.com/todos/{id}"
    response = await client.get(url)
    todoResponse = Todo.model_validate(response.json())
    return todoResponse

async def main() -> None:
    async with httpx.AsyncClient() as clienter:
        tasks = [fetch_todo(clienter, i) for i in range(1, 6)]
        todos: list[Todo] = await asyncio.gather(*tasks)
        for todo in todos:
            print(f"[{todo.id}] {todo.title} - Completed: {todo.complete}")

if __name__=="__main__":
    asyncio.run(main())