#!/bin/bash
# Production startup script for Render
cd backend
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

