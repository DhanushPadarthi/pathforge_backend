# PathForge Backend

AI-powered learning roadmap platform - Backend API

## Tech Stack

- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Firebase Admin** - Authentication
- **LangChain** - AI/RAG pipeline
- **GridFS** - File storage

## Project Structure

```
backend/
├── app/
│   ├── main.py           # Application entry point
│   ├── api/              # API routes
│   │   └── routes/       # Route modules
│   ├── models/           # Pydantic models/schemas
│   ├── services/         # Business logic services
│   ├── core/             # Core functionality
│   │   ├── database.py   # Database connection
│   │   └── middleware.py # Exception handlers
│   ├── config/           # Configuration
│   └── utils/            # Utility functions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Python 3.10+
- MongoDB instance
- Firebase project

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\\venv\\Scripts\\activate
# Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Update .env with your configuration
```

### Development

```bash
# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file with the following variables:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=pathforge

# CORS
CORS_ORIGINS=http://localhost:3000

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# API Keys (if needed)
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Main Features

- User authentication and authorization
- AI-powered roadmap generation
- Resume parsing and skill extraction
- Resource recommendations
- Progress tracking and analytics
- Admin dashboard
- File upload/download with GridFS

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Project Modules

- **api/routes** - API endpoints organized by feature
- **models** - Pydantic models for data validation
- **services** - Business logic and external service integrations
- **core** - Database connections, middleware, exceptions
- **config** - Application configuration
- **utils** - Helper functions and utilities

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [MongoDB Motor Documentation](https://motor.readthedocs.io)
- [Pydantic Documentation](https://docs.pydantic.dev)
