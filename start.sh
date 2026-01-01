#!/bin/bash
# Production startup script (alternative to direct command in Render)
# For Render: use this as Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
# Or: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
cd backend
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2

