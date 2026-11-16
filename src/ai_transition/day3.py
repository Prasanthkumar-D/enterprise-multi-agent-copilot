import asyncio
import random
import time

async def simulate_db_query(query_id: int) -> dict[str, int]:
    print(f"[{time.strftime('%X')}] Task {query_id}: Starting query...")
    await asyncio.sleep(random.uniform(1.0, 3.0))
    print(f"[{time.strftime('%X')}] Task {query_id}: Finished query!")
    return {"id": query_id, "status" : 200}

async def main() -> None:
    print(f"[{time.strftime('%X')}] Main: Scheduling tasks...")
    tasks: list[asyncio.Task[dict[str, int]]] = []
    for i in range(3):
        tasks.append(asyncio.create_task(simulate_db_query(i)))
    print(f"[{time.strftime('%X')}] Main: Tasks scheduled. Waiting for them to finish...\n")
    for task in tasks:
        result = await task
        print(f"[{time.strftime('%X')}] Main: Got result -> {result}")

if __name__ == "__main__":
    asyncio.run(main())
