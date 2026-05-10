import structlog
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.routers.auth_router import router as auth_router
from src.api.routers.role_router import router as role_router
from src.api.routers.user_router import router as user_router
from src.constants import JAEGER_ENDPOINT, SERVICE_NAME
from src.log import init_logger
from src.trace import init

init_logger()
init(SERVICE_NAME, JAEGER_ENDPOINT)

app = FastAPI(title="SSO Service")

FastAPIInstrumentor.instrument_app(app)

instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app, endpoint="/metrics")

logger = structlog.get_logger("sso")

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
