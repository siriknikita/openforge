# OpenForge

A unified, real-time, AI-assisted platform that fundamentally redefines open-source collaboration.

## Project Structure

This is a monorepo containing:

- **Frontend**: Next.js application with React, TypeScript, TailwindCSS, and ShadCN UI
- **Backend**: FastAPI application with Python

```
openforge/
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend application
├── PRD.md            # Product Requirements Document
├── AI_REPLICATION_GUIDE.md  # Design system documentation
└── README.md         # This file
```

## Tech Stack

### Frontend
- **Next.js 14+** (App Router)
- **React 18+**
- **TypeScript 5+**
- **Tailwind CSS 3.4+**
- **shadcn/ui** - Component library
- **Clerk** - Authentication

### Backend
- **FastAPI** (Python)
- **MongoDB** (with PyMongo)
- **Python 3.11+**
- **uv** - Python package manager

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Python package manager
- MongoDB (for backend development)

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up Clerk authentication:

   - Create an account at [Clerk](https://clerk.com/)
   - Create a new application
   - Copy your API keys from the [Clerk Dashboard](https://dashboard.clerk.com/last-active?path=api-keys)

4. Create `.env.local` file in the `frontend` directory:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
CLERK_SECRET_KEY=YOUR_SECRET_KEY
```

5. Run the development server:
```bash
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies (uv will create a virtual environment automatically):
```bash
uv sync
```

3. Create `.env` file in the `backend` directory (for future MongoDB connection):
```bash
MONGODB_URI=mongodb://localhost:27017/openforge
```

4. Run the development server:
```bash
uv run uvicorn main:app --reload
```

Or use the convenience script:
```bash
uv run python main.py
```

The backend API will be available at [http://localhost:8000](http://localhost:8000)

API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Development Scripts

### Root Level

```bash
npm run dev:frontend    # Start frontend dev server
npm run dev:backend     # Start backend dev server
npm run build:frontend  # Build frontend for production
npm run lint:frontend   # Lint frontend code
```

### Frontend

```bash
cd frontend
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Backend

```bash
cd backend
uv run uvicorn main:app --reload  # Start development server
uv run python main.py              # Alternative start method
```

## Authentication (Clerk)

Clerk is integrated into the frontend with:

- **Sign In/Sign Up buttons** in the header (modal-based)
- **UserButton** component for authenticated users
- **Protected routes** support (can be added as needed)

The authentication flow is handled entirely through Clerk's hosted UI. No custom forms needed initially, though they can be customized later.
## Project Status

This is an initial setup. Future development will include:

- Real-time collaboration (WebSockets)
- In-browser IDE (Monaco Editor)
- AI integration
- GitHub integration
- MongoDB database models

See `PRD.md` for detailed requirements.

## Contributing

This is a personal project. See the PRD for feature requirements and architecture decisions.

## License

[Your License Here]
