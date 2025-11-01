# Clerk Authentication Setup

## Quick Start

1. **Create a Clerk Account**
   - Visit [https://clerk.com](https://clerk.com) and sign up
   - Create a new application

2. **Get Your API Keys**
   - Go to [API Keys page](https://dashboard.clerk.com/last-active?path=api-keys)
   - Copy your **Publishable Key** and **Secret Key**

3. **Set Environment Variables**
   - Create a `.env.local` file in the `frontend` directory
   - Add the following:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxx
```

4. **Start Development Server**
   ```bash
   npm run dev
   ```

## Features Configured

- ✅ `ClerkProvider` wrapping the entire app in `app/layout.tsx`
- ✅ `SignInButton` and `SignUpButton` in the header (modal mode)
- ✅ `UserButton` for authenticated users
- ✅ `clerkMiddleware()` in `middleware.ts` for route protection
- ✅ Clerk's hosted sign-in/sign-up UI

## Next Steps

- Configure authentication methods (email, OAuth providers, etc.) in Clerk Dashboard
- Customize the sign-in/sign-up appearance in Clerk Dashboard
- Add protected routes as needed using Clerk's `auth()` helper

For more information, visit: https://clerk.com/docs/quickstarts/nextjs

