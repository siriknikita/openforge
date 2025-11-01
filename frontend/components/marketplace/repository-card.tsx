"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { GitHubRepository } from "@/lib/api/marketplace";
import { Star, GitFork, Circle } from "lucide-react";

interface RepositoryCardProps {
  repository: GitHubRepository;
  searchQuery?: string;
}

export function RepositoryCard({ repository, searchQuery = "" }: RepositoryCardProps) {
  const router = useRouter();

  const handleClick = () => {
    // Navigate to repository detail page with search query preserved
    const search = searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : "";
    router.push(`/marketplace/${repository.owner.login}/${repository.name}${search}`);
  };
  return (
    <Card 
      className="hover:shadow-md transition-shadow cursor-pointer"
      onClick={handleClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg line-clamp-1">{repository.name}</CardTitle>
            {repository.description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {repository.description}
              </p>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {repository.topics.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {repository.topics.slice(0, 4).map((topic) => (
                <Badge key={topic} variant="secondary" className="text-xs">
                  {topic}
                </Badge>
              ))}
              {repository.topics.length > 4 && (
                <Badge variant="secondary" className="text-xs">
                  +{repository.topics.length - 4} more
                </Badge>
              )}
            </div>
          )}
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Star className="size-4" />
              <span>{repository.stargazers_count.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-1">
              <GitFork className="size-4" />
              <span>{repository.forks_count.toLocaleString()}</span>
            </div>
            {repository.language && (
              <div className="flex items-center gap-1">
                <Circle className="size-3 fill-current" />
                <span>{repository.language}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{repository.owner.login}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

