import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from requests import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from src.metrics import ERRORS_TOTAL, REQUEST_DURATION, REQUESTS_TOTAL


class REDMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        endpoint = request.url.path
        method = request.method

        try:
            response = await call_next(request)
        except Exception as e:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            duration = time.perf_counter() - start_time

            REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()
            ERRORS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

            raise e

        duration = time.perf_counter() - start_time
        status_code = response.status_code

        REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()

        if status_code >= 400:
            ERRORS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        return response
