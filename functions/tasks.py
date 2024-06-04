import requests
import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from functools import wraps, partial

def run_async(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5),
            partial(function, *args, **kwargs),
        )

    return wrapper

@run_async
def fetch(url) -> requests.Response:
    """Fetch a URL using requests."""
    return requests.get(url)