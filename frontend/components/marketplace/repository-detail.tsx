"use client";

import { useRouter } from "next/navigation";
import confetti from "canvas-confetti";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage } from "@/components/ui/avatar";
import { GitHubRepositoryDetail } from "@/lib/api/marketplace";
import { MarkdownViewer } from "./markdown-viewer";
import { 
  Star, 
  GitFork, 
  Eye, 
  AlertCircle, 
  ExternalLink,
  Code,
  Calendar,
  X,
  GitBranch,
  FileText
} from "lucide-react";

interface RepositoryDetailProps {
  repository: GitHubRepositoryDetail;
  onClose: () => void;
}

export function RepositoryDetail({ repository, onClose }: RepositoryDetailProps) {
  const router = useRouter();

  const handleJoinNow = () => {
    // Trigger confetti effect
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#22c55e', '#16a34a', '#15803d', '#ffffff'],
    });

    // Small delay to let confetti show before redirect
    setTimeout(() => {
      router.push(`/editor/${repository.owner.login}/${repository.name}`);
    }, 300);
  };

  return (
    <Card id="repository-detail" className="max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <CardTitle className="text-2xl">{repository.name}</CardTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="ml-auto"
                aria-label="Close"
              >
                <X className="size-4" />
              </Button>
            </div>
            {repository.description && (
              <p className="text-muted-foreground mb-4">{repository.description}</p>
            )}
            {repository.topics.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {repository.topics.map((topic) => (
                  <Badge key={topic} variant="secondary">
                    {topic}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Owner Info */}
          <div className="flex items-center gap-4">
            <Avatar>
              <AvatarImage src={repository.owner.avatar_url} alt={repository.owner.login} />
            </Avatar>
            <div>
              <p className="font-medium">{repository.owner.login}</p>
              <a
                href={repository.owner.html_url || `https://github.com/${repository.owner.login}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:text-primary"
              >
                View on GitHub
              </a>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <Star className="size-4 text-yellow-500" />
              <div>
                <p className="text-sm text-muted-foreground">Stars</p>
                <p className="font-semibold">{repository.stargazers_count.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <GitFork className="size-4" />
              <div>
                <p className="text-sm text-muted-foreground">Forks</p>
                <p className="font-semibold">{repository.forks_count.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Eye className="size-4" />
              <div>
                <p className="text-sm text-muted-foreground">Watchers</p>
                <p className="font-semibold">{repository.watchers_count.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <AlertCircle className="size-4" />
              <div>
                <p className="text-sm text-muted-foreground">Issues</p>
                <p className="font-semibold">{repository.open_issues_count.toLocaleString()}</p>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
            {repository.language && (
              <div className="flex items-center gap-2">
                <Code className="size-4" />
                <span>{repository.language}</span>
              </div>
            )}
            {repository.license && (
              <div className="flex items-center gap-2">
                <FileText className="size-4" />
                <span>License: {repository.license.name}</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <Calendar className="size-4" />
              <span>Updated {new Date(repository.updated_at).toLocaleDateString()}</span>
            </div>
            {repository.default_branch && (
              <div className="flex items-center gap-2">
                <GitBranch className="size-4" />
                <span>Branch: {repository.default_branch}</span>
              </div>
            )}
          </div>

          {/* Repository Links */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              variant="outline"
              onClick={() => window.open(repository.html_url, "_blank")}
              className="flex-1 w-full sm:w-auto"
            >
              <ExternalLink className="size-4 mr-2" />
              View Repository on GitHub
            </Button>
            <Button
              onClick={handleJoinNow}
              className="flex-1 w-full sm:w-auto bg-green-600 hover:bg-green-700 text-white font-semibold"
            >
              Join now!
            </Button>
          </div>

          {/* README */}
          {repository.readme.content && (
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">README</h3>
              <div className="bg-muted/50 rounded-lg p-4 max-h-[600px] overflow-y-auto">
                <MarkdownViewer content={repository.readme.content} />
              </div>
              {repository.readme.html_url && (
                <a
                  href={repository.readme.html_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline mt-2 inline-block"
                >
                  View README on GitHub
                </a>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

