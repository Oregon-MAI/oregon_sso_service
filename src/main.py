import logging

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.api.routers.auth_router import router as auth_router
from src.api.routers.role_router import router as role_router
from src.api.routers.user_router import router as user_router

app = FastAPI()

logging.basicConfig(
    level=logging.DEBUG,
    filename="sso.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)s %(message)s",
)

FastAPIInstrumentor.instrument_app(app)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)
