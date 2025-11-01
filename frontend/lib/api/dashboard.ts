/**
 * API client for dashboard data
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DashboardData {
  user: {
    id: string;
    name: string;
    email: string;
    avatarUrl: string | null;
    xp: number;
    level: number;
    role: 'admin' | 'user';
    githubConnected: boolean;
  };
  stats: {
    newProjects: number;
    joinedProjects: number;
    commits: number;
    pullRequests: number;
    issuesClosed: number;
    linesOfCode: number;
    timeSavedMinutes: number;
  };
  timeBreakdown: {
    contributingToOSS: number; // hours
    workingOnOwnProjects: number; // hours
  };
  projects: {
    owned: Project[];
    contributed: Project[];
    starred: Project[];
  };
  additionalMetrics: {
    totalContributions: number;
    activeProjects: number;
    streak: number; // days
    averagePRMergeTime: number | null; // hours, null when no data
  };
}

export interface Project {
  id: string;
  name: string;
  description: string;
  techStack: string[];
  starred: boolean;
  metadata: {
    commits: number;
    contributors: number;
    openIssues: number;
    timeSavedMinutes: number;
  };
  createdAt: string;
  updatedAt: string;
}

/**
 * Fetch dashboard data for the authenticated user
 */
export async function fetchDashboardData(
  clerkUserId: string
): Promise<DashboardData> {
  const response = await fetch(`${API_BASE_URL}/api/dashboard?user_id=${clerkUserId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    // Note: In production, pass Clerk JWT token in Authorization header
    // credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Toggle star status for a project
 */
export async function toggleProjectStar(
  projectId: string,
  clerkUserId: string
): Promise<{ starred: boolean }> {
  const response = await fetch(
    `${API_BASE_URL}/api/projects/${projectId}/star`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: clerkUserId }),
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to toggle star: ${response.statusText}`);
  }

  return response.json();
}

