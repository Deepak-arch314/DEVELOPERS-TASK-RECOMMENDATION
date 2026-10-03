"""Routes package initialization."""
from backend.routes.developers import router as developers_router
from backend.routes.recommendations import router as recommendations_router
from backend.routes.tasks import router as tasks_router

__all__ = ["developers_router", "tasks_router", "recommendations_router"]