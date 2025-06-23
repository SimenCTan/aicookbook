# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import asyncio


class AsyncIterator:
    def __init__(self, start, stop) -> None:
        self.current = start
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current < self.stop:
            await asyncio.sleep(1)
            self.current += 1
            return self.current - 1
        else:
            raise StopAsyncIteration


async def main() -> None:
    async for i in AsyncIterator(1, 10):
        print(i)


if __name__ == "__main__":
    asyncio.run(main())
