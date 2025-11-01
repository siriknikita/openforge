"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star } from "lucide-react";
import { Project } from "@/lib/api/dashboard";
import { useState } from "react";
import { toggleProjectStar } from "@/lib/api/dashboard";

interface ProjectCardProps {
  project: Project;
  clerkUserId: string;
  onStarToggle?: (projectId: string, starred: boolean) => void;
}

export function ProjectCard({ project, clerkUserId, onStarToggle }: ProjectCardProps) {
  const [starred, setStarred] = useState(project.starred);
  const [isToggling, setIsToggling] = useState(false);

  const handleStarToggle = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsToggling(true);
    try {
      const result = await toggleProjectStar(project.id, clerkUserId);
      setStarred(result.starred);
      onStarToggle?.(project.id, result.starred);
    } catch (error) {
      console.error("Failed to toggle star:", error);
      // Revert on error
      setStarred(!starred);
    } finally {
      setIsToggling(false);
    }
  };

  const timeSavedHours = project.metadata.timeSavedMinutes / 60;

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{project.name}</CardTitle>
            {project.description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {project.description}
              </p>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0"
            onClick={handleStarToggle}
            disabled={isToggling}
            aria-label={starred ? "Unstar project" : "Star project"}
          >
            <Star
              className={`size-5 ${
                starred
                  ? "fill-yellow-500 text-yellow-500"
                  : "text-muted-foreground"
              }`}
            />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {project.techStack.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {project.techStack.slice(0, 4).map((tech) => (
                <Badge key={tech} variant="secondary" className="text-xs">
                  {tech}
                </Badge>
              ))}
              {project.techStack.length > 4 && (
                <Badge variant="secondary" className="text-xs">
                  +{project.techStack.length - 4} more
                </Badge>
              )}
            </div>
          )}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Commits</span>
              <p className="font-semibold">{project.metadata.commits.toLocaleString()}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Contributors</span>
              <p className="font-semibold">
                {project.metadata.contributors.toLocaleString()}
              </p>
            </div>
            <div>
              <span className="text-muted-foreground">Open Issues</span>
              <p className="font-semibold">
                {project.metadata.openIssues.toLocaleString()}
              </p>
            </div>
            <div>
              <span className="text-muted-foreground">Time Saved</span>
              <p className="font-semibold">
                {timeSavedHours >= 1
                  ? `${timeSavedHours.toFixed(1)}h`
                  : `${project.metadata.timeSavedMinutes}m`}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

