<!-- 5cd6d2b8-4894-48f2-96e4-778ceb73e288 95883ae8-f879-4348-ab53-ec552b3b4655 -->
# OpenForge MVP Development Plan

## Overview

This plan covers the MVP implementation of OpenForge, starting from the existing landing page repository. The MVP focuses on core infrastructure, authentication, Room UI with code editor (display-focused), and secure AI proxy endpoint. The frontend will prioritize displaying core functionality over complex interactions. The implementation follows the PRD specifications with Next.js App Router, FastAPI backend, and MongoDB.

## Technology Stack Confirmed

- **Frontend**: Next.js 14+ (App Router), React, TailwindCSS, ShadCN UI, Monaco Editor
- **Backend**: FastAPI, PyMongo, MongoDB (local with config-based connection)
- **Auth**: NextAuth.js v5 (Auth.js)
- **AI Proxy**: Mock/test endpoint (MVP)

---

## Epic 1: Project Infrastructure & Setup

### User Story 1.1: Initialize Next.js Frontend Project

**Priority**: P0 (Critical Path)

**Tasks**:

1. Initialize Next.js 14+ project with TypeScript and App Router

   - Files: `package.json`, `tsconfig.json`, `next.config.js`
   - Configure App Router directory structure (`app/` directory)

2. Install and configure TailwindCSS

   - Files: `tailwind.config.ts`, `postcss.config.js`, `app/globals.css`
   - Setup Tailwind directives

3. Setup ShadCN UI components

   - Files: `components.json`, `lib/utils.ts`
   - Install required dependencies (class-variance-authority, clsx, tailwind-merge)

4. Create basic layout structure

   - Files: `app/layout.tsx`, `app/page.tsx`
   - Implement root layout with metadata and providers

### User Story 1.2: Initialize FastAPI Backend Project

**Priority**: P0 (Critical Path)

**Tasks**:

1. Setup FastAPI project structure

   - Files: `backend/main.py`, `backend/requirements.txt`
   - Install FastAPI, uvicorn, pydantic, python-dotenv

2. Configure MongoDB connection with PyMongo

   - Files: `backend/config.py`, `backend/database.py`
   - Implement connection manager with configurable MongoDB URL (support local and cluster)
   - Environment variable: `MONGODB_URL` in `.env` file

3. Create basic FastAPI app structure

   - Files: `backend/main.py`
   - Setup CORS middleware for Next.js frontend
   - Create health check endpoint `/health`

4. Setup project dependencies and development scripts

   - Files: `backend/requirements.txt`
   - Create startup scripts or documentation

---

## Epic 2: Authentication (GitHub OAuth)

### User Story 2.1: Configure NextAuth.js v5 with GitHub Provider

**Priority**: P0 (Critical Path)

**Tasks**:

1. Install and configure NextAuth.js v5 (Auth.js)

   - Files: `package.json`, `app/api/auth/[...nextauth]/route.ts`
   - Configure GitHub OAuth provider
   - Environment variables: `AUTH_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

2. Create authentication configuration

   - Files: `auth.config.ts` (or inline in route handler)
   - Define GitHub provider configuration
   - Setup callback URLs

3. Create auth utility functions

   - Files: `lib/auth.ts` (if needed)
   - Helper functions for session management

### User Story 2.2: User Profile Creation on First Login

**Priority**: P1 (Required for MVP)

**Tasks**:

1. Create FastAPI endpoint for user profile creation

   - Files: `backend/routers/users.py`
   - Endpoint: `POST /api/users/create` or handle in callback
   - Accept GitHub user data (username, avatar, email)

2. Define MongoDB user schema/model

   - Files: `backend/models/user.py`
   - Schema: username, email, avatar_url, github_id, created_at

3. Implement user profile creation logic

   - Files: `backend/routers/users.py`
   - Check if user exists, create if new, return user profile

4. Update NextAuth callback to sync user data

   - Files: `app/api/auth/[...nextauth]/route.ts`
   - After successful GitHub auth, call backend API to create/update user

---

## Epic 3: Room MVP - UI Structure & Code Editor

### User Story 3.1: Create Room Route and Layout

**Priority**: P0 (Critical Path)

**Tasks**:

1. Create dynamic route for Room page

   - Files: `app/room/[repoId]/page.tsx`
   - Implement basic layout with sidebar and main editor area

2. Design Room UI structure with ShadCN components

   - Files: `app/room/[repoId]/page.tsx`, `components/room/`
   - Left sidebar: File tree (mock data for MVP)
   - Center: Monaco Editor
   - Right sidebar: Chat/AI panel placeholder

3. Create responsive layout components

   - Files: `components/room/RoomLayout.tsx`, `components/room/Sidebar.tsx`
   - Use ShadCN components (Sheet, Tabs, etc.)

### User Story 3.2: Integrate Monaco Editor (VS Code in Browser)

**Priority**: P0 (Critical Path)

**Tasks**:

1. Install Monaco Editor dependencies

   - Files: `package.json`
   - Install `@monaco-editor/react` or `monaco-editor`

2. Create Monaco Editor component wrapper

   - Files: `components/editor/CodeEditor.tsx`
   - Configure Monaco with TypeScript/JavaScript support
   - Setup basic theme and language detection

3. Implement file loading logic

   - Files: `components/editor/CodeEditor.tsx`, `app/room/[repoId]/page.tsx`
   - For MVP: Load mock `index.js` with "hello world" content
   - Store file content in component state

4. Add file tree navigation (mock data)

   - Files: `components/room/FileTree.tsx`
   - Display mock file structure (e.g., `index.js`)
   - Handle file selection to update editor content

---

## Epic 4: Secure AI Proxy Endpoint

### User Story 4.1: Create AI Query Proxy Endpoint

**Priority**: P0 (Critical Path)

**Tasks**:

1. Create FastAPI router for AI endpoints

   - Files: `backend/routers/ai.py`
   - Define endpoint: `POST /api/ai/query`
   - Request model: `user_prompt`, `context` (optional)

2. Implement system prompt injection

   - Files: `backend/routers/ai.py`
   - Hardcoded system prompt: "You are a helpful coding assistant. Adhere strictly to the user's plan."
   - Inject before processing user request

3. Create mock AI service handler

   - Files: `backend/services/ai_service.py`
   - For MVP: Return mock response (e.g., "Mock AI response for: {user_prompt}")
   - Structure response to match future AI API format

4. Implement response validation and error handling

   - Files: `backend/routers/ai.py`
   - Pydantic models for request/response validation
   - Error handling for malformed requests

5. Add security middleware (optional for MVP)

   - Files: `backend/routers/ai.py`
   - Basic rate limiting or request validation
   - Log requests (without secrets)

### User Story 4.2: Create Chat/AI Panel UI Component

**Priority**: P1 (Required for MVP)

**Tasks**:

1. Create AI chat panel component

   - Files: `components/room/AIChatPanel.tsx`
   - Use ShadCN components (Card, Input, Button, ScrollArea)

2. Implement chat interface

   - Files: `components/room/AIChatPanel.tsx`
   - Message display area
   - Input field for user prompts
   - Send button

3. Connect chat UI to AI proxy endpoint

   - Files: `components/room/AIChatPanel.tsx`
   - API call to `POST /api/ai/query`
   - Display responses in chat interface

---

## Epic 5: Configuration & Environment Setup

### User Story 5.1: Environment Configuration

**Priority**: P0 (Critical Path)

**Tasks**:

1. Create environment configuration files

   - Files: `.env.example`, `.env.local` (gitignored)
   - Document all required environment variables
   - Frontend: `NEXT_PUBLIC_API_URL`, `AUTH_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
   - Backend: `MONGODB_URL`, `API_KEY_*` (placeholder for future AI services)

2. Create backend configuration module

   - Files: `backend/config.py`
   - Load environment variables
   - Validate required config on startup
   - MongoDB URL configuration (local or cluster)

3. Setup development scripts

   - Files: `package.json`, `backend/requirements.txt`
   - Frontend: `npm run dev`
   - Backend: `uvicorn main:app --reload`

---

## File Structure Summary

```
openforge-landing-page/
├── app/                          # Next.js App Router
│   ├── api/
│   │   └── auth/[...nextauth]/
│   │       └── route.ts         # NextAuth.js v5 route handler
│   ├── room/[repoId]/
│   │   └── page.tsx             # Room page component
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home/dashboard page
│   └── globals.css              # TailwindCSS styles
├── components/
│   ├── room/
│   │   ├── RoomLayout.tsx       # Main room layout
│   │   ├── Sidebar.tsx          # File tree sidebar
│   │   ├── FileTree.tsx         # File navigation component
│   │   └── AIChatPanel.tsx      # AI chat interface
│   └── editor/
│       └── CodeEditor.tsx       # Monaco Editor wrapper
├── lib/
│   ├── utils.ts                 # ShadCN utility functions
│   └── auth.ts                  # Auth helper functions (if needed)
├── backend/
│   ├── main.py                  # FastAPI application entry
│   ├── config.py                # Configuration management
│   ├── database.py              # MongoDB connection
│   ├── routers/
│   │   ├── users.py             # User profile endpoints
│   │   └── ai.py                # AI proxy endpoint
│   ├── models/
│   │   └── user.py              # User MongoDB schema
│   ├── services/
│   │   └── ai_service.py        # Mock AI service handler
│   └── requirements.txt         # Python dependencies
├── components.json               # ShadCN configuration
├── tailwind.config.ts          # TailwindCSS configuration
├── package.json                 # Frontend dependencies
├── .env.example                 # Environment variables template
└── README.md                    # Project documentation
```

---

## Implementation Order

1. **Phase 1 - Infrastructure** (Epic 1): Setup both frontend and backend projects
2. **Phase 2 - Authentication** (Epic 2): Implement GitHub OAuth flow
3. **Phase 3 - Room UI** (Epic 3): Build Room page with Monaco Editor
4. **Phase 4 - AI Proxy** (Epic 4): Create secure AI endpoint and chat UI
5. **Phase 5 - Polish** (Epic 5): Configuration and documentation

---

## Key Implementation Details

### MongoDB Configuration

- Use `backend/config.py` to load `MONGODB_URL` from environment
- Support both local MongoDB (`mongodb://localhost:27017`) and MongoDB Atlas cluster URLs
- Connection handled in `backend/database.py` with error handling

### Monaco Editor Setup

- Use `@monaco-editor/react` for React integration
- Initialize with "hello world" `index.js` content for MVP
- Support JavaScript/TypeScript syntax highlighting

### AI Proxy Security

- System prompt injection: `"You are a helpful coding assistant. Adhere strictly to the user's plan."`
- Mock response for MVP testing
- Structured for easy replacement with real AI service later

### Authentication Flow

- NextAuth.js v5 with GitHub provider
- On first login, call FastAPI endpoint to create user profile in MongoDB
- Session management handled by NextAuth

### To-dos

- [ ] Initialize Next.js 14+ project with TypeScript, App Router, TailwindCSS, and ShadCN UI components
- [ ] Initialize FastAPI backend with MongoDB connection manager and configuration module
- [ ] Setup NextAuth.js v5 with GitHub OAuth provider and authentication routes
- [ ] Create FastAPI endpoint and MongoDB schema for user profile creation on first login
- [ ] Create Room page route with layout structure using ShadCN components (sidebar + editor area)
- [ ] Integrate Monaco Editor component with mock file loading (index.js with hello world)
- [ ] Create secure FastAPI endpoint /api/ai/query with system prompt injection and mock AI service
- [ ] Create AI chat panel UI component connected to AI proxy endpoint