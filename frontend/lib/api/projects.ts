/**
 * API client for project operations
 */

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

/**
 * Helper function to construct API URLs without double slashes
 */
function buildApiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}

export interface GitHubStatus {
  github_connected: boolean;
  github_username: string | null;
  has_repo_scope: boolean;
}

export interface CreateRepoRequest {
  name: string;
  description?: string;
  tech_stack?: string[];
  is_private?: boolean;
}

export interface CreateRepoResponse {
  message: string;
  project: {
    id: string;
    name: string;
    description?: string;
    github_repo_id: string;
    github_url: string;
    tech_stack: string[];
    created_at: string;
  };
}

/**
 * Get user's GitHub connection status
 */
export async function getGitHubStatus(
  clerkUserId: string
): Promise<GitHubStatus> {
  const response = await fetch(
    buildApiUrl(`/api/projects/github-status?user_id=${clerkUserId}`),
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch GitHub status: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Connect GitHub account
 */
export async function connectGitHub(
  clerkUserId: string
): Promise<{ message: string; github_username: string; has_repo_scope: boolean }> {
  const response = await fetch(
    buildApiUrl('/api/projects/connect-github'),
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: clerkUserId }),
      credentials: 'include',
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Failed to connect GitHub: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Create a new GitHub repository
 */
export async function createGitHubRepository(
  request: CreateRepoRequest,
  clerkUserId: string
): Promise<CreateRepoResponse> {
  const response = await fetch(
    buildApiUrl('/api/projects/create-github-repo'),
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...request,
        user_id: clerkUserId,
      }),
      credentials: 'include',
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Failed to create repository: ${response.statusText}`);
  }

  return response.json();
}

