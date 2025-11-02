# OpenForge Backend

FastAPI backend API for OpenForge - A unified, real-time, AI-assisted platform for open-source collaboration.

## Tech Stack

- **FastAPI** (Python) - Modern, fast web framework
- **MongoDB** (with PyMongo) - NoSQL database
- **Python 3.11+** (requires Python 3.12+ per pyproject.toml)
- **uv** - Python package manager

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - Python package manager
- MongoDB (local or MongoDB Atlas)

## Getting Started

### Installation

1. Navigate to the backend directory:

```bash
cd backend
```

2. Install dependencies (uv will create a virtual environment automatically):

```bash
uv sync
```

### Environment Setup

1. Create `.env` file in the `backend` directory:

```bash
# Environment
ENVIRONMENT=dev

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
# Or use MongoDB Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Clerk Authentication (optional but recommended)
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx

# GitHub API (optional but recommended for higher rate limits)
# GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
```

See `env.example` for a complete template.

### Running the Development Server

Option 1: Using uvicorn directly

```bash
uv run uvicorn main:app --reload
```

Option 2: Using the convenience script

```bash
uv run python main.py
```

The backend API will be available at [http://localhost:8000](http://localhost:8000)

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Development Scripts

```bash
# Start development server with auto-reload
uv run uvicorn main:app --reload

# Alternative: Start using the main.py script
uv run python main.py

# Install new dependencies
uv add package-name

# Sync dependencies (after changes to pyproject.toml)
uv sync
```

## Project Structure

```
backend/
├── app/
│   ├── auth/              # Authentication modules (Clerk integration)
│   ├── models/            # MongoDB database models
│   ├── routers/           # FastAPI route handlers
│   │   ├── dashboard.py   # Dashboard endpoints
│   │   ├── marketplace.py # Marketplace endpoints
│   │   └── projects.py    # Project management endpoints
│   ├── services/          # Business logic services
│   │   ├── time_tracker.py
│   │   └── xp_calculator.py
│   ├── config.py          # Application configuration
│   └── database.py        # Database connection
├── api/                   # Vercel serverless functions
├── main.py                # FastAPI application entry point
└── pyproject.toml         # Python dependencies and project config
```

## API Endpoints

### Health & Debug

- `GET /` - Health check endpoint
- `GET /api/health` - Detailed health check
- `GET /api/cors-debug` - CORS configuration debug

### Dashboard

- Endpoints for user dashboard data, contributions, XP, and activity

### Projects

- Endpoints for project management and CRUD operations

### Marketplace

- Endpoints for browsing and searching open-source projects

## Database

The backend uses MongoDB with automatic database name selection based on environment:

- Development: `openforge-dev`
- Production: `openforge-prod`

This can be overridden using the `MONGODB_DB_NAME` environment variable.

## CORS Configuration

CORS is configured to allow requests from:

- Local development: `http://localhost:3000`
- Production: Your frontend Vercel deployment URL
- Vercel preview deployments (via regex pattern)

Configuration is managed in `app/config.py`.

## Authentication

The backend integrates with Clerk for authentication. JWT tokens can be verified using the `CLERK_SECRET_KEY` environment variable.

See `app/auth/` for authentication modules.

## Deployment

This backend is configured for deployment on Vercel as serverless functions. See `vercel.json` for deployment configuration.

For detailed deployment instructions, see the main project's `VERCEL_DEPLOYMENT.md`.
