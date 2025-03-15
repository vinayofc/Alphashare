import asyncio
from aiohttp import ClientSession, ClientTimeout


async def ping_server(url, sleep_time):
    while True:
        await asyncio.sleep(sleep_time)
        try:
            async with ClientSession(
                timeout= ClientTimeout(total=10)
            ) as session:
                async with session.get(url) as resp:
                    print("Pinged server with response: {}".format(resp.status))
        except TimeoutError:
            print(f"Couldn't connect to the site {url}..!")
        except Exception as e:
            print(e)
