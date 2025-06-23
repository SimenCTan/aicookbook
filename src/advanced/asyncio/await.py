# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import asyncio


async def fetch_data():
    print("Fetching data...")
    await asyncio.sleep(2)
    print("Data fetched")
    return "Data"


async def main():
    data = await fetch_data()
    print(data)


if __name__ == "__main__":
    asyncio.run(main())
