# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import asyncio


async def task(name, delay) -> str:
    print(f"Task {name} started")
    await asyncio.sleep(delay)
    print(f"Task {name} completed")
    return f"Task {name} completed"


async def main():
    results = await asyncio.gather(
        task("Task 1", 1),
        task("Task 2", 2),
        task("Task 3", 3),
    )
    print(f"Results: {results}")

    task1 = asyncio.create_task(task("Task 1", 1))
    task2 = asyncio.create_task(task("Task 2", 2))
    result1 = await task1
    print(f"Task 1: {result1}")
    result2 = await task2
    print(f"Task 2: {result2}")


if __name__ == "__main__":
    asyncio.run(main())
