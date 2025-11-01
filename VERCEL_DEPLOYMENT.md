# Vercel Deployment Guide for OpenForge

This guide explains how to deploy the OpenForge monorepo to Vercel with separate deployments for the frontend and backend, supporting both development and production environments.

## Overview

- **Frontend**: Next.js application deployed as a Vercel project
- **Backend**: FastAPI application deployed as a separate Vercel project using Python serverless functions
- **Databases**: Two MongoDB databases:
  - `openforge-dev` - Development database
  - `openforge-prod` - Production database

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **MongoDB Atlas Account**: For hosting your databases
4. **Clerk Account**: For authentication (see [frontend/CLERK_SETUP.md](./frontend/CLERK_SETUP.md))

## Step 1: Set Up MongoDB Databases

1. Log in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create two databases:
   - **Development Database**: `openforge-dev`
   - **Production Database**: `openforge-prod`
3. Create connection strings for each:
   - Note the connection strings (you'll need them for environment variables)
   - Ensure network access is configured to allow Vercel IPs (or 0.0.0.0/0 for testing)

## Step 2: Deploy Backend to Vercel

### 2.1 Create Backend Project in Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Project Name**: `openforge-backend` (or your preferred name)
   - **Root Directory**: `backend`
   - **Framework Preset**: Other
   - **Build Command**: `uv sync`
   - **Output Directory**: `.` (leave empty or use `.`)
   - **Install Command**: `uv sync`

### 2.2 Configure Backend Environment Variables

In the Vercel project settings, add these environment variables:

#### For Development Environment:
```
ENVIRONMENT=dev
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=openforge-dev
FRONTEND_URL=http://localhost:3000
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
```

#### For Production Environment:
```
ENVIRONMENT=prod
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=openforge-prod
FRONTEND_URL=https://your-frontend-url.vercel.app
CLERK_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
```

**Note**: 
- The database name will automatically be set to `openforge-dev` or `openforge-prod` based on `ENVIRONMENT`, but you can override with `MONGODB_DB_NAME`
- `FRONTEND_URL` should match your frontend deployment URL
- Use different Clerk keys for dev and prod if you have separate Clerk applications

### 2.3 Install uv on Vercel

Vercel doesn't have `uv` installed by default. You have two options:

**Option A: Use Vercel Build Command (Recommended)**
Update your build command to install `uv` first:

```bash
pip install uv && uv sync
```

**Option B: Add requirements.txt (Alternative)**
If `uv` doesn't work, create a `requirements.txt` in the backend directory:

```bash
fastapi>=0.120.4
pymongo>=4.15.3
python-dotenv>=1.2.1
pydantic-settings>=2.0.0
uvicorn[standard]>=0.38.0
mangum>=0.18.0
```

Then update the build command to:
```bash
pip install -r requirements.txt
```

### 2.4 Deploy

1. Click **"Deploy"**
2. Wait for the deployment to complete
3. Note the deployment URL (e.g., `https://openforge-backend.vercel.app`)

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Frontend Project in Vercel

1. In Vercel Dashboard, click **"Add New..."** → **"Project"**
2. Import the same GitHub repository
3. Configure the project:
   - **Project Name**: `openforge-frontend` (or your preferred name)
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (should auto-detect)
   - Vercel will auto-configure build settings for Next.js

### 3.2 Configure Frontend Environment Variables

In the Vercel project settings, add these environment variables:

#### For Development Environment:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
```

#### For Production Environment:
```
NEXT_PUBLIC_API_URL=https://openforge-backend.vercel.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
```

**Important**: 
- `NEXT_PUBLIC_API_URL` must match your backend deployment URL
- Use production Clerk keys for production environment
- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser

### 3.3 Deploy

1. Click **"Deploy"**
2. Wait for the deployment to complete
3. Note the deployment URL (e.g., `https://openforge.vercel.app`)

## Step 4: Update Backend CORS Configuration

After deploying the frontend, update the backend's `FRONTEND_URL` environment variable:

1. Go to backend project settings → **Environment Variables**
2. Update `FRONTEND_URL` for production to match your frontend URL
3. Redeploy the backend

## Step 5: Local Development Setup

### 5.1 Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Copy the example environment file:
   ```bash
   cp env.example .env.local
   ```

3. Update `.env.local` with your local values:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
   CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
   ```

4. Install dependencies and run:
   ```bash
   npm install
   npm run dev
   ```

### 5.2 Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

3. Update `.env` with your local values:
   ```bash
   ENVIRONMENT=dev
   MONGODB_URL=mongodb://localhost:27017
   FRONTEND_URL=http://localhost:3000
   CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
   ```

4. Install dependencies and run:
   ```bash
   uv sync
   uv run uvicorn main:app --reload
   ```

### 5.3 Run Both Locally

From the root directory:
```bash
# Terminal 1: Frontend
npm run dev:frontend

# Terminal 2: Backend
npm run dev:backend
```

## Environment Variables Reference

### Backend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ENVIRONMENT` | Yes | Environment name (`dev` or `prod`) | `dev` |
| `MONGODB_URL` | Yes | MongoDB connection string | `mongodb+srv://...` |
| `MONGODB_DB_NAME` | No | Database name (auto-set based on ENVIRONMENT) | `openforge-dev` |
| `FRONTEND_URL` | Yes | Frontend URL for CORS | `https://openforge.vercel.app` |
| `CLERK_SECRET_KEY` | No | Clerk backend secret key | `sk_test_...` |

### Frontend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | `https://openforge-backend.vercel.app` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key | `pk_test_...` |
| `CLERK_SECRET_KEY` | Yes | Clerk secret key (server-side) | `sk_test_...` |

## Troubleshooting

### Backend Issues

**Problem**: `uv` command not found
- **Solution**: Use `pip install uv && uv sync` in build command, or use `requirements.txt`

**Problem**: CORS errors in production
- **Solution**: Ensure `FRONTEND_URL` is set correctly in backend environment variables

**Problem**: Database connection errors
- **Solution**: 
  - Verify MongoDB connection string
  - Check network access in MongoDB Atlas
  - Ensure database name matches (`openforge-dev` or `openforge-prod`)

### Frontend Issues

**Problem**: API calls failing
- **Solution**: Check `NEXT_PUBLIC_API_URL` matches your backend deployment URL

**Problem**: Clerk authentication not working
- **Solution**: Verify Clerk keys are correct and match the environment (test vs live)

### General Issues

**Problem**: Changes not deploying
- **Solution**: Ensure you're pushing to the correct branch and Vercel is watching that branch

**Problem**: Environment variables not updating
- **Solution**: Redeploy after changing environment variables

## Project Structure

```
openforge/
├── frontend/
│   ├── vercel.json          # Frontend Vercel config
│   ├── env.example          # Frontend env template
│   └── ...
├── backend/
│   ├── vercel.json          # Backend Vercel config
│   ├── api/
│   │   └── index.py         # Serverless function entry point
│   ├── env.example          # Backend env template
│   └── ...
└── VERCEL_DEPLOYMENT.md     # This file
```

## Next Steps

1. ✅ Set up MongoDB databases (dev and prod)
2. ✅ Deploy backend to Vercel
3. ✅ Deploy frontend to Vercel
4. ✅ Configure environment variables
5. ✅ Test both deployments
6. ✅ Set up custom domains (optional)
7. ✅ Configure preview deployments (optional)

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI on Vercel](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs)
- [MongoDB Atlas](https://www.mongodb.com/docs/atlas/)

