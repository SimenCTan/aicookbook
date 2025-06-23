# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiohttp",
# ]
# ///

import asyncio
import aiohttp


async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.get(url) as response:
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Error fetching {url}: {e}")
        return f"Error fetching {url}: {e}"


async def fetch_all_urls(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)


async def fetch_with_semaphore(
    url, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore
) -> str:
    async with semaphore:
        async with session.get(url) as response:
            return await response.text()


async def limit_concurrent_fetch(urls: list[str], limit: int) -> list[str]:
    semaphore = asyncio.Semaphore(limit)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_semaphore(url, session, semaphore) for url in urls]
        return await asyncio.gather(*tasks)


urls = [
    "https://api.github.com",
    "https://httpbin.org/delay/1",
    "https://jsonplaceholder.typicode.com/posts/1",
]


async def task_with_timeout():
    try:
        await asyncio.wait_for(fetch_all_urls(urls), timeout=1)
    except asyncio.TimeoutError:
        print("Timeout")
        return ["Timeout"]


async def main() -> None:
    # results = await fetch_all_urls(urls)
    # print(results)
    # results = await limit_concurrent_fetch(urls, 2)
    # print(results)
    results = await task_with_timeout()
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
