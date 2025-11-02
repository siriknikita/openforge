/**
 * API client for marketplace (GitHub repositories)
 */

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

/**
 * Helper function to construct API URLs without double slashes
 */
function buildApiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}

export interface GitHubOwner {
  login: string;
  avatar_url: string;
  html_url?: string;
  type?: string;
}

export interface GitHubRepository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  topics: string[];
  stargazers_count: number;
  forks_count: number;
  language: string | null;
  owner: GitHubOwner;
  created_at: string;
  updated_at: string;
}

export interface GitHubRepositoryDetail extends GitHubRepository {
  watchers_count: number;
  open_issues_count: number;
  languages_url: string;
  license: {
    key: string;
    name: string;
    spdx_id: string;
    url: string;
    node_id: string;
  } | null;
  default_branch: string;
  pushed_at: string;
  readme: {
    content: string | null;
    html_url: string | null;
  };
}

export interface RepositoriesResponse {
  total_count: number;
  repositories: GitHubRepository[];
}

/**
 * Fetch repositories with 'openforge-demo' topic
 */
export async function fetchRepositories(
  search?: string
): Promise<RepositoriesResponse> {
  const params = new URLSearchParams();
  if (search && search.trim()) {
    params.append('search', search.trim());
  }
  
  const url = buildApiUrl(`/api/marketplace/repos${params.toString() ? `?${params.toString()}` : ''}`);
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch repositories: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch detailed repository information including README
 */
export async function fetchRepositoryDetails(
  owner: string,
  repo: string
): Promise<GitHubRepositoryDetail> {
  const response = await fetch(
    buildApiUrl(`/api/marketplace/repos/${owner}/${repo}`),
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch repository details: ${response.statusText}`);
  }

  return response.json();
}

