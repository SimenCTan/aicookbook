# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
import asyncio


async def hello_world():
    print("Hello, World!")
    await asyncio.sleep(2)
    print("Hello, World! 2")


def main() -> None:
    asyncio.run(hello_world())


if __name__ == "__main__":
    main()
