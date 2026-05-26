from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from src.metrics_middleware import REDMetricsMiddleware


def _create_test_app(raise_exception: bool = False) -> Starlette:
    async def ok_endpoint(_request: Request) -> Response:
        if raise_exception:
            raise ValueError("Downstream test exception")
        return PlainTextResponse("OK")

    async def err_endpoint(_request: Request) -> Response:
        return PlainTextResponse("Bad Request", status_code=400)

    app = Starlette(
        routes=[
            Route("/ok", ok_endpoint, methods=["GET", "POST"]),
            Route("/err", err_endpoint),
        ]
    )

    app.add_middleware(REDMetricsMiddleware)  # type: ignore[invalid-argument-type]
    return app


@pytest.fixture
def mock_metrics() -> Iterator[tuple[MagicMock, MagicMock, MagicMock]]:
    with (
        patch("src.metrics_middleware.REQUESTS_TOTAL") as m_req,
        patch("src.metrics_middleware.ERRORS_TOTAL") as m_err,
        patch("src.metrics_middleware.REQUEST_DURATION") as m_dur,
    ):
        yield m_req, m_err, m_dur


class TestREDMetricsMiddleware:
    def test_success_request_records_metrics(
        self, mock_metrics: tuple[MagicMock, MagicMock, MagicMock]
    ) -> None:
        m_req, m_err, m_dur = mock_metrics
        app = _create_test_app()
        client = TestClient(app)

        response = client.get("/ok")
        assert response.status_code == 200

        m_req.labels.assert_called_once_with(method="GET", endpoint="/ok", status=200)
        m_req.labels.return_value.inc.assert_called_once()

        m_err.labels.assert_not_called()
        m_err.labels.return_value.inc.assert_not_called()

        m_dur.labels.assert_called_once_with(method="GET", endpoint="/ok")
        m_dur.labels.return_value.observe.assert_called_once()
        observed_duration = m_dur.labels.return_value.observe.call_args[0][0]
        assert observed_duration > 0

    def test_client_error_records_error_metrics(
        self, mock_metrics: tuple[MagicMock, MagicMock, MagicMock]
    ) -> None:
        m_req, m_err, m_dur = mock_metrics
        app = _create_test_app()
        client = TestClient(app)

        response = client.get("/err")
        assert response.status_code == 400

        m_req.labels.assert_called_once_with(method="GET", endpoint="/err", status=400)
        m_req.labels.return_value.inc.assert_called_once()

        m_err.labels.assert_called_once_with(method="GET", endpoint="/err", status=400)
        m_err.labels.return_value.inc.assert_called_once()

        m_dur.labels.assert_called_once_with(method="GET", endpoint="/err")
        m_dur.labels.return_value.observe.assert_called_once()

    def test_exception_records_500_and_reraises(
        self, mock_metrics: tuple[MagicMock, MagicMock, MagicMock]
    ) -> None:
        m_req, m_err, m_dur = mock_metrics
        app = _create_test_app(raise_exception=True)
        client = TestClient(app, raise_server_exceptions=True)

        with pytest.raises(ValueError, match="Downstream test exception"):
            client.get("/ok")

        m_req.labels.assert_called_once_with(method="GET", endpoint="/ok", status=500)
        m_req.labels.return_value.inc.assert_called_once()

        m_err.labels.assert_called_once_with(method="GET", endpoint="/ok", status=500)
        m_err.labels.return_value.inc.assert_called_once()

        m_dur.labels.assert_called_once_with(method="GET", endpoint="/ok")
        m_dur.labels.return_value.observe.assert_called_once()

    def test_post_method_label_extraction(
        self, mock_metrics: tuple[MagicMock, MagicMock, MagicMock]
    ) -> None:
        m_req, _, _ = mock_metrics
        app = _create_test_app()
        client = TestClient(app)

        client.post("/ok")
        m_req.labels.assert_called_once_with(method="POST", endpoint="/ok", status=200)
