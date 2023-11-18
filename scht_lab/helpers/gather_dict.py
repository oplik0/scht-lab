from asyncio import gather


async def gather_dict(tasks: dict):
    """Gather a dictionary of coroutines, preserving their keys."""
    async def mark(key, coro):
        return key, await coro

    return {
        key: result
        for key, result in await gather(
            *(mark(key, coro) for key, coro in tasks.items())
        )
    }