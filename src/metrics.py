from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter(
    "http_requests_total_manual", "Total HTTP requests", labelnames=["method", "endpoint", "status"]
)

ERRORS_TOTAL = Counter(
    "http_errors_total_manual",
    "Total HTTP errors (status >= 400)",
    labelnames=["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds_manual",
    "HTTP request duration in seconds",
    labelnames=["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
