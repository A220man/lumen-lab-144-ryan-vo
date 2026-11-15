"""API v1 routes package initialization."""

from app.api.v1 import chart as chart_router  # noqa: F401

# Auth routes are registered directly in main.py via app.include_router(
# from app.api.v1.auth_routes import router  # noqa: F401 - avoid circular import
