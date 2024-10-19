from fastapi.responses import JSONResponse


async def abort_on_failure(handler):
    try:
        return await handler()
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
