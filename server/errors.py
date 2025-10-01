from fastapi import Request
from fastapi.responses import JSONResponse
from .logging_setup import get_logger
logger = get_logger()
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("", extra={"path": str(request.url), "error": str(exc)})
    return JSONResponse(status_code=500, content={"ok": False, "error": "internal_error"})