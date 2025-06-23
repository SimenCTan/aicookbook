# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///


import asyncio


async def producer(queue: asyncio.Queue, n: int) -> None:
    for i in range(n):
        await asyncio.sleep(1)
        await queue.put(f"Item {i}")
        print(f"Produced: item {i}")


async def consumer(queue: asyncio.Queue, name: str) -> None:
    while True:
        item = await queue.get()
        if item is None:
            await queue.put(None)
            break
        print(f"{name} consumed: {item}")
        await asyncio.sleep(2)


async def main() -> None:
    queue = asyncio.Queue(maxsize=3)
    await asyncio.gather(
        producer(queue, 10),
        consumer(queue, "Consumer 1"),
        consumer(queue, "Consumer 2"),
    )


if __name__ == "__main__":
    asyncio.run(main())
