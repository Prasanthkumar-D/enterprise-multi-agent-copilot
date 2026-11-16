from fastapi import FastAPI
from pydantic import BaseModel
import asyncio


app = FastAPI()

class Todo(BaseModel):
    userId: int
    id: int
    title: str
    complete: bool

@app.get("/todos/{todo_id}")
async def get_todo(todo_id:int) -> Todo:
    return Todo(userId = 101, id = todo_id, title = "Engineer", complete = True)

@app.post("/todos")
async def create_todo(todo : Todo) -> dict[str, str]:
    print(f"Saving todo to database: {todo.title}")
    return {"status": "success", "message": f"Created todo {todo.id}"}
