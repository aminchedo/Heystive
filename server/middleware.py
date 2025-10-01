import time, uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .logging_setup import get_logger
logger = get_logger()
class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start = time.time()
        response = await call_next(request)
        dur = round((time.time() - start) * 1000, 2)
        try:
            response.headers["X-Request-ID"] = rid
        except Exception:
            pass
        logger.info("", extra={"rid": rid, "path": request.url.path, "method": request.method, "status": response.status_code, "dur_ms": dur})
        return response