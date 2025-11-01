"use client";

import { GitHubRepository } from "@/lib/api/marketplace";
import { RepositoryCard } from "./repository-card";

interface RepositoryListProps {
  repositories: GitHubRepository[];
  searchQuery?: string;
}

export function RepositoryList({ repositories, searchQuery = "" }: RepositoryListProps) {
  if (repositories.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">No repositories found.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {repositories.map((repository) => (
        <RepositoryCard
          key={repository.id}
          repository={repository}
          searchQuery={searchQuery}
        />
      ))}
    </div>
  );
}

