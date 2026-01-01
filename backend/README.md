# PathForge Backend

FastAPI backend for PathForge - AI-powered learning roadmap platform.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Required variables:
- `MONGODB_URL`: MongoDB Atlas connection string
- `OPENAI_API_KEY`: OpenAI API key
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase admin SDK credentials

### 4. Firebase Setup
1. Go to Firebase Console
2. Download service account credentials
3. Save as `firebase-credentials.json` in backend root

### 5. Seed Database
```bash
python scripts/seed_data.py
```

### 6. Run Development Server
```bash
uvicorn main:app --reload
```

Server will start at http://localhost:8000

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── api/
│   └── routes/         # API endpoints
│       ├── auth.py     # Authentication
│       ├── users.py    # User management
│       ├── roadmaps.py # Learning roadmaps
│       ├── resources.py# Learning resources
│       ├── skills.py   # Skills & career roles
│       └── admin.py    # Admin panel
├── database/
│   └── connection.py   # MongoDB connection
├── models/             # Pydantic models
│   ├── user.py
│   ├── roadmap.py
│   ├── skill.py
│   └── resource.py
├── services/           # Business logic
│   ├── ai_service.py   # OpenAI integration
│   └── resume_parser.py# Resume processing
├── scripts/
│   └── seed_data.py    # Database seeding
├── main.py             # FastAPI app
└── requirements.txt    # Dependencies
```

## Key Features

### Authentication
- Firebase Authentication integration
- JWT token verification
- Role-based access control

### Resume Processing
- PDF and DOCX support
- AI-powered skill extraction
- Experience analysis

### AI-Powered Features
- Skill gap analysis
- Learning roadmap generation
- Resource recommendations
- Module summaries

### Roadmap Management
- Sequential resource unlocking
- Progress tracking
- Complete/Skip functionality
- Module completion summaries

## API Endpoints

### Authentication
- `POST /api/auth/verify` - Verify Firebase token
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users/{user_id}` - Get user profile
- `PUT /api/users/{user_id}` - Update user profile
- `POST /api/users/{user_id}/upload-resume` - Upload resume
- `POST /api/users/{user_id}/complete-profile` - Complete profile without resume

### Roadmaps
- `POST /api/roadmaps/generate/{user_id}` - Generate roadmap
- `GET /api/roadmaps/{user_id}` - Get user roadmap
- `POST /api/roadmaps/{user_id}/complete-resource` - Mark resource complete
- `POST /api/roadmaps/{user_id}/skip-resource` - Skip resource
- `GET /api/roadmaps/{user_id}/module-summary/{module_id}` - Get module summary

### Skills
- `GET /api/skills/career-roles` - Get all career roles
- `GET /api/skills/career-roles/{role_id}` - Get specific role
- `POST /api/skills/analyze-gap` - Analyze skill gap

### Resources
- `GET /api/resources/` - Get all resources
- `GET /api/resources/{resource_id}` - Get specific resource
- `GET /api/resources/search/by-skills` - Search by skills

### Admin
- `GET /api/admin/users` - Get all users
- `GET /api/admin/stats` - Dashboard statistics
- `POST /api/admin/career-roles` - Create career role
- `PUT /api/admin/career-roles/{role_id}` - Update career role
- `DELETE /api/admin/career-roles/{role_id}` - Delete career role

## Testing

```bash
pytest
```

## Deployment

The backend can be deployed to:
- Railway
- Render
- AWS EC2
- Google Cloud Run
- Heroku

Make sure to set environment variables in your deployment platform.
