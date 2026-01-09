# API Routes Package
from .auth import router as auth_router
from .users import router as users_router
from .roadmaps import router as roadmaps_router
from .resources import router as resources_router
from .skills import router as skills_router
from .admin import router as admin_router
from .files import router as files_router
from .projects import router as projects_router
from .analytics import router as analytics_router
from .chatbot import router as chatbot_router
from .trending import router as trending_router

__all__ = [
    "auth_router",
    "users_router",
    "roadmaps_router",
    "resources_router",
    "skills_router",
    "admin_router",
    "files_router",
    "projects_router",
    "analytics_router",
    "chatbot_router",
    "trending_router"
]
