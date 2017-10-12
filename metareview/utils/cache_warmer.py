import asyncio

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError

from metareview import gerrit
from metareview.utils import cache


async def fetch(key, url, session):
    try:
        async with session.get(url) as response:
            response = await response.text()
            cache.save(key, response)
    except ClientError:
        print(key, "failed")


async def bound_fetch(key, sem, url, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(key, url, session)


async def run(end):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(20)

    async with ClientSession() as session:
        g = gerrit.Gerrit(end=end)
        for key, url in g.url_generator():
            if cache.is_saved(key):
                continue
            task = asyncio.ensure_future(bound_fetch(key, sem, url, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses

def start(end):
    loop = asyncio.get_event_loop()

    future = asyncio.ensure_future(run(end))
    loop.run_until_complete(future)
