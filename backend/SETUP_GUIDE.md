# PathForge Backend Setup Guide

## Prerequisites
- Python 3.11 or higher
- MongoDB Compass (local installation)
- OpenAI API Key
- Firebase Project

## Step-by-Step Setup

### 1. Install MongoDB Compass
Download and install MongoDB Compass from: https://www.mongodb.com/products/compass

Start MongoDB locally (default: mongodb://localhost:27017/)

### 2. Clone and Navigate
```bash
cd d:\projects\PATHFORGE1\backend
```

### 3. Create Virtual Environment
```bash
python -m venv venv
```

### 4. Activate Virtual Environment
```bash
# Windows PowerShell
venv\Scripts\activate

# Windows CMD
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Setup Environment Variables
```bash
# Copy example file
cp .env.example .env
```

Edit `.env` file with your values:
```env
# MongoDB Configuration (Local)
MONGODB_URL=mongodb://localhost:27017/
DATABASE_NAME=pathforge

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Application Settings
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

### 7. Setup Firebase Admin SDK

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings > Service Accounts
4. Click "Generate New Private Key"
5. Save the downloaded JSON file as `firebase-credentials.json` in the backend folder

### 8. Verify MongoDB Connection
Open MongoDB Compass and connect to `mongodb://localhost:27017/`

### 9. Seed Database with Initial Data
```bash
python scripts/seed_data.py
```

This will create:
- 6 career roles (Full Stack, Frontend, Backend, Data Scientist, DevOps, Mobile)
- Sample skills
- Admin user (email: admin@pathforge.com)

### 10. Run Development Server
```bash
uvicorn main:app --reload
```

The server will start at: http://localhost:8000

### 11. Test the API
Open your browser and go to:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Common Issues & Solutions

### Issue: ModuleNotFoundError
**Solution:** Make sure virtual environment is activated and dependencies are installed
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: MongoDB Connection Failed
**Solution:** 
- Ensure MongoDB Compass is running
- Check if MongoDB service is started
- Verify connection string in `.env` is `mongodb://localhost:27017/`

### Issue: Firebase Authentication Error
**Solution:**
- Verify `firebase-credentials.json` exists in backend folder
- Check file path in `.env` matches the actual file location
- Ensure the JSON file is valid and from the correct Firebase project

### Issue: OpenAI API Error
**Solution:**
- Verify your OpenAI API key in `.env`
- Check if you have credits in your OpenAI account
- Ensure API key has correct permissions

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Database Management

### View Database in MongoDB Compass
1. Open MongoDB Compass
2. Connect to `mongodb://localhost:27017/`
3. Select `pathforge` database
4. Browse collections: users, roadmaps, career_roles, skills, resources

### Reset Database
```bash
# Drop database in MongoDB Compass or run:
python scripts/reset_database.py  # (create this if needed)
```

## Next Steps

1. Test all endpoints using Swagger UI at http://localhost:8000/docs
2. Create a test user via Firebase Authentication
3. Upload a resume and test skill extraction
4. Generate a learning roadmap
5. Move to frontend development

## API Documentation

All available endpoints are documented at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Production Deployment Checklist

Before deploying to production:
- [ ] Change SECRET_KEY in `.env`
- [ ] Update CORS_ORIGINS to production domain
- [ ] Use MongoDB Atlas instead of local MongoDB
- [ ] Set ENVIRONMENT=production
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerts
