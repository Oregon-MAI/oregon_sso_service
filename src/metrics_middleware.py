import time
from typing import cast

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from src.metrics import ERRORS_TOTAL, REQUEST_DURATION, REQUESTS_TOTAL


class REDMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware для сбора RED-метрик (Request rate, Error rate, Duration)
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Обработка запроса и запись метрик
        :return: HTTP ответ
        """
        start_time = time.perf_counter()
        endpoint = request.url.path
        method = request.method

        try:
            response = await call_next(request)
        except Exception:
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            duration = time.perf_counter() - start_time

            REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()
            ERRORS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

            raise

        duration = time.perf_counter() - start_time
        status_code = cast(int, response.status_code)

        REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()

        if status_code >= 400:
            ERRORS_TOTAL.labels(method=method, endpoint=endpoint, status=status_code).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        return response
