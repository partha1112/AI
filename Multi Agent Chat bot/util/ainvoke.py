import inspect


async def resolve_ainvoke(maybe_awaitable):
    if inspect.isasyncgen(maybe_awaitable):
        last = None
        async for chunk in maybe_awaitable:
            last = chunk
        return last

    if inspect.isawaitable(maybe_awaitable):
        return await maybe_awaitable

    return maybe_awaitable
