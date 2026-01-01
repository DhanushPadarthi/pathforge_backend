from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api.routes import auth, users, roadmaps, resources, admin, skills, files, analytics, chatbot, trending
from api.routes import projects
from api.middleware import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from database.connection import connect_to_mongo, close_mongo_connection

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="PathForge API",
    description="AI-powered learning roadmap platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(roadmaps.router, prefix="/api/roadmaps", tags=["Roadmaps"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resources"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(trending.router, prefix="/api/trending", tags=["Trending Skills"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to PathForge API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
