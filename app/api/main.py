from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.query import router as analytics_router
from app.config.settings import get_settings
from app.database.session import check_database_connection

settings = get_settings()

check_database_connection(settings)

app = FastAPI(
title="Analytics API",
version="1.0.0"
)

app.include_router(health_router)
app.include_router(analytics_router)
