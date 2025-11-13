"use client";

import { useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";
import { UserRank } from "@/components/dashboard/user-rank";
import { StatsCard } from "@/components/dashboard/stats-card";
import { TimeBreakdownChart } from "@/components/dashboard/time-breakdown-chart";
import { ContributionActivityChart } from "@/components/dashboard/contribution-activity-chart";
import { ProjectList } from "@/components/dashboard/project-list";
import { DashboardSkeleton } from "@/components/dashboard/dashboard-skeleton";
import { CreateRepoModal } from "@/components/dashboard/create-repo-modal";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  fetchDashboardData,
  DashboardData,
  Project,
} from "@/lib/api/dashboard";
import {
  FolderPlus,
  Users,
  GitCommit,
  GitPullRequest,
  CheckCircle,
  Clock,
  Plus,
} from "lucide-react";

export default function DashboardPage() {
  const { user, isLoaded } = useUser();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateRepoModalOpen, setIsCreateRepoModalOpen] = useState(false);

  useEffect(() => {
    if (!isLoaded) return;

    if (!user) {
      setError("Please sign in to view your dashboard");
      setIsLoading(false);
      return;
    }

    const loadDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchDashboardData(user.id);
        setDashboardData(data);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
        setError(
          err instanceof Error ? err.message : "Failed to load dashboard data"
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, [user, isLoaded]);

  const handleStarToggle = (projectId: string, starred: boolean) => {
    if (!dashboardData) return;

    // Update local state optimistically
    const updateProjectStar = (projects: Project[]) =>
      projects.map((p) => (p.id === projectId ? { ...p, starred } : p));

    const updatedOwned = updateProjectStar(dashboardData.projects.owned);
    const updatedContributed = updateProjectStar(
      dashboardData.projects.contributed
    );

    // Update starred list
    let updatedStarred = [...dashboardData.projects.starred];
    if (starred) {
      // Add to starred if not already there
      const project =
        updatedOwned.find((p) => p.id === projectId) ||
        updatedContributed.find((p) => p.id === projectId);
      if (project && !updatedStarred.find((p) => p.id === projectId)) {
        updatedStarred.push({ ...project, starred: true });
      }
    } else {
      // Remove from starred
      updatedStarred = updatedStarred.filter((p) => p.id !== projectId);
    }

    setDashboardData({
      ...dashboardData,
      projects: {
        owned: updatedOwned,
        contributed: updatedContributed,
        starred: updatedStarred,
      },
    });
  };

  const handleRepoCreated = async () => {
    // Reload dashboard data to show the new project
    if (user) {
      try {
        const data = await fetchDashboardData(user.id);
        setDashboardData(data);
      } catch (err) {
        console.error("Failed to reload dashboard data:", err);
      }
    }
  };

  if (!isLoaded || isLoading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <DashboardSkeleton />
      </main>
    );
  }

  if (error || !dashboardData) {
    return (
      <main className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-destructive">
              {error || "Failed to load dashboard"}
            </p>
          </CardContent>
        </Card>
      </main>
    );
  }

  const timeSavedHours = dashboardData.stats.timeSavedMinutes / 60;

  return (
    <main className="container mx-auto px-4 py-8 space-y-6">
      {/* User Rank Section */}
      <UserRank
        name={dashboardData.user.name}
        avatarUrl={dashboardData.user.avatarUrl}
        xp={dashboardData.user.xp}
        level={dashboardData.user.level}
      />

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Active Projects"
          value={dashboardData.additionalMetrics.activeProjects}
          icon={FolderPlus}
          description="Projects you're working on"
        />
        <StatsCard
          title="Streak"
          value={`${dashboardData.additionalMetrics.streak} days`}
          icon={Clock}
          description="Current contribution streak"
        />
        <StatsCard
          title="New Projects"
          value={dashboardData.stats.newProjects}
          icon={FolderPlus}
          description="Projects you created"
        />
        <StatsCard
          title="Joined Projects"
          value={dashboardData.stats.joinedProjects}
          icon={Users}
          description="Projects you contributed to"
        />
        <StatsCard
          title="Total Contributions"
          value={dashboardData.stats.commits}
          icon={GitCommit}
          description="Total commits from joined projects"
        />
        <StatsCard
          title="Pull Requests"
          value={dashboardData.stats.pullRequests}
          icon={GitPullRequest}
          description="PRs merged"
        />
        <StatsCard
          title="Issues Closed"
          value={dashboardData.stats.issuesClosed}
          icon={CheckCircle}
          description="Issues resolved"
        />
        <StatsCard
          title="Time Saved"
          value={
            timeSavedHours >= 1
              ? `${timeSavedHours.toFixed(1)}h`
              : `${dashboardData.stats.timeSavedMinutes}m`
          }
          icon={Clock}
          description="Setup time saved"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TimeBreakdownChart
          contributingToOSS={dashboardData.timeBreakdown.contributingToOSS}
          workingOnOwnProjects={dashboardData.timeBreakdown.workingOnOwnProjects}
        />
        <ContributionActivityChart
          commits={dashboardData.stats.commits}
          pullRequests={dashboardData.stats.pullRequests}
          issuesClosed={dashboardData.stats.issuesClosed}
        />
      </div>

      {/* Project Lists */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle>Your Projects</CardTitle>
          <Button
            onClick={() => setIsCreateRepoModalOpen(true)}
            size="sm"
            className="gap-2"
          >
            <Plus className="h-4 w-4" />
            Create New Project
          </Button>
        </CardHeader>
        <CardContent>
          <ProjectList
            owned={dashboardData.projects.owned}
            contributed={dashboardData.projects.contributed}
            starred={dashboardData.projects.starred}
            clerkUserId={dashboardData.user.id}
            onStarToggle={handleStarToggle}
          />
        </CardContent>
      </Card>

      {/* Create Repository Modal */}
      {user && (
        <CreateRepoModal
          open={isCreateRepoModalOpen}
          onOpenChange={setIsCreateRepoModalOpen}
          clerkUserId={user.id}
          onSuccess={handleRepoCreated}
        />
      )}
    </main>
  );
}

