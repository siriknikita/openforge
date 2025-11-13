# GitHub Token Setup Guide

This guide explains how to configure GitHub authentication for repository creation in OpenForge.

## Overview

OpenForge supports two methods for GitHub authentication:

1. **Clerk OAuth Integration** (Preferred for production)
   - Users sign in with GitHub through Clerk
   - Automatic token management
   - Requires `repo` scope to be configured in Clerk

2. **GitHub Personal Access Token** (Fallback/Development)
   - Manual token configuration
   - Useful when Clerk OAuth lacks `repo` scope
   - Configured via environment variable

The system automatically uses the best available token:
- If Clerk OAuth token has `repo` scope → uses Clerk token
- If Clerk token lacks `repo` scope → falls back to `GITHUB_TOKEN`
- If no Clerk token available → uses `GITHUB_TOKEN` directly

## Setup Methods

### Method 1: GitHub Personal Access Token (Recommended for Quick Setup)

This is the fastest way to get started if you're having issues with Clerk OAuth.

#### Step 1: Create a GitHub Personal Access Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Configure the token:
   - **Note**: `OpenForge Repository Creation` (or any descriptive name)
   - **Expiration**: Choose your preference (30 days, 90 days, or no expiration)
   - **Scopes**: Check the following:
     - ✅ **`repo`** - Full control of private repositories
       - This includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`
4. Click **"Generate token"**
5. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

#### Step 2: Add Token to Backend Configuration

1. Open your backend `.env` file:
   ```bash
   cd backend
   nano .env  # or use your preferred editor
   ```

2. Add the token:
   ```bash
   GITHUB_TOKEN=ghp_your_token_here
   ```

3. Save the file

4. **Restart your backend server** for changes to take effect:
   ```bash
   # Stop the current server (Ctrl+C)
   # Then restart:
   uvicorn main:app --reload
   # Or your usual start command
   ```

#### Step 3: Verify Token Works

1. Open the OpenForge dashboard
2. Click **"Create New Project"**
3. Click **"Connect GitHub"** button
4. You should see "GitHub Connected" with your username

### Method 2: Clerk OAuth with Repo Scope (Production Setup)

For production, you should configure Clerk to request the `repo` scope when users connect GitHub.

#### Step 1: Configure Clerk GitHub OAuth

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Select your application
3. Navigate to **"User & Authentication"** → **"Social Connections"** → **"GitHub"**
4. Ensure GitHub is enabled as a connection method
5. Configure OAuth scopes:
   - Add `repo` to the requested scopes
   - This may require updating your GitHub OAuth App settings

#### Step 2: Update GitHub OAuth App (if needed)

1. Go to [GitHub Settings → Developer settings → OAuth Apps](https://github.com/settings/developers)
2. Find your Clerk OAuth App (or create one if needed)
3. Ensure the app has `repo` scope permissions
4. Update the callback URL if needed

#### Step 3: Reconnect GitHub Account

1. In your OpenForge app, disconnect your GitHub account
2. Sign in again with GitHub
3. When prompted, grant repository access permissions
4. The system should now detect the `repo` scope

## How It Works

### Token Priority

The system checks tokens in this order:

1. **Clerk OAuth Token** (if available)
   - Checks if it has `repo` scope
   - If yes → uses it
   - If no → continues to fallback

2. **GITHUB_TOKEN from environment** (fallback)
   - Checks if it has `repo` scope
   - If yes → uses it
   - If no → returns error

### Token Scope Verification

The system automatically verifies that any token has the `repo` scope before using it. This ensures repository creation will work.

### Logging

The backend logs which token is being used:
- `"Using Clerk OAuth token with repo scope"` - Using Clerk token
- `"Falling back to GITHUB_TOKEN from environment (has repo scope)"` - Using manual token
- `"Clerk OAuth token lacks 'repo' scope"` - Clerk token insufficient, trying fallback

Check your backend logs to see which token is active.

## Troubleshooting

### Error: "GitHub token does not have 'repo' scope"

**Solution**: 
- If using Clerk OAuth: Reconnect GitHub through Clerk and grant repository access
- If using GITHUB_TOKEN: Create a new token with `repo` scope checked

### Error: "No GitHub OAuth token found"

**Solution**:
- Ensure you're signed in with GitHub via Clerk, OR
- Configure `GITHUB_TOKEN` in your backend `.env` file

### Error: "Clerk secret key not configured"

**Solution**:
- Add `CLERK_SECRET_KEY` to your backend `.env` file
- Get the key from [Clerk Dashboard → API Keys](https://dashboard.clerk.com/last-active?path=api-keys)

### Token Not Working After Adding to .env

**Solution**:
1. Verify the token is correct (no extra spaces, correct format: `ghp_...`)
2. **Restart your backend server** - environment variables are only loaded on startup
3. Check backend logs for error messages

### Which Token Is Being Used?

Check your backend server logs. You'll see messages like:
- `"Using Clerk OAuth token with repo scope"` - Clerk token
- `"Falling back to GITHUB_TOKEN from environment"` - Manual token

## Security Best Practices

1. **Never commit tokens to version control**
   - `.env` files should be in `.gitignore`
   - Use `.env.example` for documentation only (without real tokens)

2. **Use environment-specific tokens**
   - Different tokens for development and production
   - Rotate tokens regularly

3. **Limit token scope**
   - Only grant `repo` scope (not all scopes)
   - Use fine-grained tokens when possible

4. **Set token expiration**
   - Don't use tokens with "No expiration"
   - Set reasonable expiration dates (30-90 days)

## Environment Variables Reference

### Backend `.env` File

```bash
# Clerk Authentication (Required for OAuth)
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx

# GitHub Personal Access Token (Fallback)
# Required scopes: 'repo'
# Optional but recommended for repository creation
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
```

### Frontend `.env.local` File

```bash
# Clerk (for authentication)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
```

## API Endpoints

### Check GitHub Status
```
GET /api/projects/github-status?user_id={clerk_user_id}
```

Returns:
```json
{
  "github_connected": true,
  "github_username": "your-username",
  "has_repo_scope": true
}
```

### Connect GitHub
```
POST /api/projects/connect-github
Body: { "user_id": "clerk_user_id" }
```

Connects GitHub account and verifies token has `repo` scope.

### Create Repository
```
POST /api/projects/create-github-repo
Body: {
  "name": "repository-name",
  "description": "Description",
  "tech_stack": ["Python", "React"],
  "is_private": false
}
```

Creates a new GitHub repository with `openforge-demo` topic.

## Testing Your Setup

1. **Test Token Scope**:
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" \
        https://api.github.com/user \
        -I | grep x-oauth-scopes
   ```
   Should include `repo` in the output.

2. **Test Repository Creation**:
   - Open dashboard
   - Click "Create New Project"
   - Fill in repository details
   - Click "Create Repository"
   - Should create repository on GitHub

## Support

If you continue to have issues:

1. Check backend logs for detailed error messages
2. Verify token format and scope
3. Ensure backend server was restarted after adding token
4. Test token directly with GitHub API (see Testing section)

For more information, see:
- [GitHub Personal Access Tokens Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Clerk Social Connections Documentation](https://clerk.com/docs/authentication/social-connections/overview)

