# OpenForge Frontend

Next.js frontend application for OpenForge - A unified, real-time, AI-assisted platform for open-source collaboration.

## Tech Stack

- **Next.js 14+** (App Router)
- **React 18+**
- **TypeScript 5+**
- **Tailwind CSS 3.4+**
- **shadcn/ui** - Component library
- **Clerk** - Authentication

## Prerequisites

- Node.js 18+ and npm 9+

## Getting Started

### Installation

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

### Environment Setup

1. Set up Clerk authentication:
   - Create an account at [Clerk](https://clerk.com/)
   - Create a new application
   - Copy your API keys from the [Clerk Dashboard](https://dashboard.clerk.com/last-active?path=api-keys)

2. Create `.env.local` file in the `frontend` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
CLERK_SECRET_KEY=YOUR_SECRET_KEY

# Optional: Clerk Webhook Secret (if using webhooks)
# CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxx
```

See `env.example` for a complete template.

### Running the Development Server

```bash
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

## Development Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard pages
│   ├── editor/            # Code editor pages
│   ├── marketplace/       # Marketplace pages
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── dashboard/        # Dashboard-specific components
│   ├── marketplace/      # Marketplace-specific components
│   └── ui/               # shadcn/ui components
├── lib/                  # Utility functions and API clients
│   ├── api/             # API client functions
│   └── utils.ts         # General utilities
└── public/              # Static assets
```

## Authentication (Clerk)

Clerk is integrated into the frontend with:

- **Sign In/Sign Up buttons** in the header (modal-based)
- **UserButton** component for authenticated users
- **Protected routes** support (can be added as needed)

The authentication flow is handled entirely through Clerk's hosted UI. No custom forms needed initially, though they can be customized later.

For detailed Clerk setup instructions, see `CLERK_SETUP.md`.

## Features

- **Dashboard**: View user contributions, XP, stats, and activity
- **Marketplace**: Browse and explore open-source projects
- **Editor**: In-browser code editor (Monaco Editor - planned)

## API Integration

The frontend communicates with the backend API. Make sure the backend is running and the `NEXT_PUBLIC_API_URL` environment variable is set correctly.

## Deployment

This frontend is configured for deployment on Vercel. See `vercel.json` for deployment configuration.

For detailed deployment instructions, see the main project's `VERCEL_DEPLOYMENT.md`.
