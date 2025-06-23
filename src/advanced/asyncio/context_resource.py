# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import asyncio


class ContextResource:
    async def __aenter__(self):
        print("Entering context")
        await asyncio.sleep(2)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print("Exiting context")
        await asyncio.sleep(1)

    async def do_something(self):
        print("Doing something")
        await asyncio.sleep(1)
        print("Done something")


async def main() -> None:
    async with ContextResource() as resource:
        await resource.do_something()


if __name__ == "__main__":
    asyncio.run(main())
