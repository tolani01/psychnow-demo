# 🚀 PsychNow Backend

FastAPI backend for AI-guided psychiatric assessment platform.

## 📋 Prerequisites

- Python 3.11+ (you have Python 3.13.7 ✓)
- pip (Python package manager)
- OpenAI API key

## 🛠️ Quick Start Setup

### Step 1: Navigate to Backend Directory

```powershell
cd C:\Users\gbtol\PsychNow\backend
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it (PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 4: Create Environment File

```powershell
# Copy the example file
copy env.example .env

# Now edit .env with your actual values
```

**Edit `.env` file** (use Notepad or VS Code):
```
SECRET_KEY=your-super-secret-key-min-32-characters-long-change-this
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

To generate a secure SECRET_KEY, run:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Initialize Database

```powershell
# Create initial migration
alembic revision --autogenerate -m "Initial database setup"

# Apply migration to create tables
alembic upgrade head
```

### Step 6: Run the Server

```powershell
# Start development server
python main.py

# Or use uvicorn directly:
uvicorn main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
backend/
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Python dependencies
├── alembic.ini              # Database migration config
├── alembic/                 # Migration scripts
├── app/
│   ├── core/                # Core utilities
│   │   ├── config.py        # Settings management
│   │   ├── security.py      # JWT & password hashing
│   │   └── deps.py          # FastAPI dependencies
│   ├── db/                  # Database setup
│   │   ├── base.py          # SQLAlchemy base
│   │   └── session.py       # Database session
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── provider_profile.py
│   │   ├── intake_session.py
│   │   ├── intake_report.py
│   │   └── provider_review.py
│   ├── schemas/             # Pydantic schemas (API contracts)
│   ├── api/v1/              # API endpoints
│   ├── services/            # Business logic
│   ├── screeners/           # Mental health screeners (30 total)
│   ├── prompts/             # LLM prompt templates
│   └── utils/               # Utility functions
└── tests/                   # Test suite
```

## 🔧 Common Commands

### Database Migrations

```powershell
# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_screeners.py
```

### Development

```powershell
# Start server with auto-reload
python main.py

# Check Python version
python --version

# List installed packages
pip list

# Update a specific package
pip install --upgrade package-name
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🎯 Next Steps

1. ✅ Backend structure created
2. ⏳ **Next**: Create API endpoints (auth, intake, reports)
3. ⏳ **Next**: Implement 30 screeners
4. ⏳ **Next**: Build conversation engine
5. ⏳ **Next**: Integrate OpenAI
6. ⏳ **Next**: Connect frontend

## 🐛 Troubleshooting

### "Module not found" errors
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### "Cannot import name" errors
```powershell
# Make sure you're in the backend directory
cd backend

# Check Python path
python -c "import sys; print(sys.path)"
```

### Database locked errors (SQLite)
```powershell
# Stop all running servers
# Delete database file and recreate
rm psychnow.db
alembic upgrade head
```

### Port 8000 already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use a different port
uvicorn main:app --reload --port 8001
```

## 📝 Environment Variables

All environment variables and their defaults are in `env.example`.

Key variables:
- `SECRET_KEY`: JWT signing key (generate with Python secrets module)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: gpt-4o-mini (default) or gpt-4o
- `DATABASE_URL`: sqlite:///./psychnow.db (default)

## 🔐 Security Notes

- **NEVER commit `.env` file** to Git (already in .gitignore)
- Change `SECRET_KEY` before any production use
- Set appropriate `ALLOWED_ORIGINS` for CORS
- Keep OpenAI API key secure

## 📞 Support

If you encounter issues:
1. Check this README's troubleshooting section
2. Review error messages carefully
3. Ensure virtual environment is activated
4. Verify `.env` file is configured correctly

---

**Status**: ✅ Backend structure complete - Ready for API implementation

**Next**: Implementing API endpoints and screeners

