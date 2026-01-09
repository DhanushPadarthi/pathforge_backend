from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.api.routes import auth, users, roadmaps, resources, admin, skills, files, analytics
from app.core.middleware import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.core.database import connect_to_mongo, close_mongo_connection

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
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(roadmaps.router, prefix="/api/roadmaps", tags=["roadmaps"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"message": "PathForge API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
