# OpenForge

A unified, real-time, AI-assisted platform that fundamentally redefines open-source collaboration.

## Project Structure

This is a monorepo containing:

- **Frontend**: Next.js application with React, TypeScript, TailwindCSS, and ShadCN UI
- **Backend**: FastAPI application with Python

```text
openforge/
├── frontend/          # Next.js frontend application
├── backend/           # FastAPI backend application
├── PRD.md            # Product Requirements Document
├── AI_REPLICATION_GUIDE.md  # Design system documentation
└── README.md         # This file
```

## Tech Stack

This is a full-stack monorepo with separate frontend and backend applications:

- **Frontend**: Next.js application with React, TypeScript, TailwindCSS, and ShadCN UI
- **Backend**: FastAPI application with Python and MongoDB

For detailed tech stack information and setup instructions, see:

- [Frontend README](./frontend/README.md#tech-stack)
- [Backend README](./backend/README.md)

## Getting Started

### Prerequisites

- Node.js 18+ and npm 9+ (for frontend)
- Python 3.12+ (for backend)
- [uv](https://github.com/astral-sh/uv) - Python package manager (for backend)
- MongoDB (for backend development)

### Quick Start

1. **Frontend Setup**: See [frontend/README.md](./frontend/README.md#getting-started)
2. **Backend Setup**: See [backend/README.md](./backend/README.md#getting-started)

## Development Scripts

### Root Level

```bash
npm run dev:frontend    # Start frontend dev server
npm run dev:backend     # Start backend dev server
npm run build:frontend  # Build frontend for production
npm run lint:frontend   # Lint frontend code
```

For more detailed development scripts, see the respective README files:

- [Frontend Development Scripts](./frontend/README.md#development-scripts)
- [Backend Development Scripts](./backend/README.md#development-scripts)

## Project Status

This is an initial setup. Future development will include:

- Real-time collaboration (WebSockets)
- In-browser IDE (Monaco Editor)
- AI integration
- GitHub integration
- MongoDB database models

See [`PRD.md`](PRD.md) for detailed requirements.

## Contributing

This is a personal project. See the PRD for feature requirements and architecture decisions.

## License

[Your License Here]
