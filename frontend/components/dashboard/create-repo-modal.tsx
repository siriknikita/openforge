"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { getGitHubStatus, createGitHubRepository, connectGitHub, CreateRepoRequest } from "@/lib/api/projects";
import { AlertCircle, Loader2, Github, CheckCircle2 } from "lucide-react";

interface CreateRepoModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  clerkUserId: string;
  onSuccess?: () => void;
}

const COMMON_TECH_STACK = [
  "Python",
  "JavaScript",
  "TypeScript",
  "React",
  "Next.js",
  "Node.js",
  "FastAPI",
  "Django",
  "Flask",
  "Vue",
  "Angular",
  "Go",
  "Rust",
  "Java",
  "C++",
  "C#",
  "PHP",
  "Ruby",
  "Swift",
  "Kotlin",
];

export function CreateRepoModal({
  open,
  onOpenChange,
  clerkUserId,
  onSuccess,
}: CreateRepoModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [techStack, setTechStack] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [githubStatus, setGithubStatus] = useState<{
    connected: boolean;
    username: string | null;
    hasScope: boolean;
  } | null>(null);
  const [createdRepo, setCreatedRepo] = useState<{ url: string; name: string } | null>(null);

  useEffect(() => {
    if (open) {
      checkGitHubStatus();
      // Reset form when modal opens
      setName("");
      setDescription("");
      setTechStack([]);
      setError(null);
      setSuccess(false);
      setCreatedRepo(null);
    }
  }, [open, clerkUserId]);

  const checkGitHubStatus = async () => {
    setIsCheckingStatus(true);
    try {
      const status = await getGitHubStatus(clerkUserId);
      setGithubStatus({
        connected: status.github_connected,
        username: status.github_username,
        hasScope: status.has_repo_scope,
      });
    } catch (err) {
      console.error("Failed to check GitHub status:", err);
      setGithubStatus({
        connected: false,
        username: null,
        hasScope: false,
      });
    } finally {
      setIsCheckingStatus(false);
    }
  };

  const handleConnectGitHub = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await connectGitHub(clerkUserId);
      setGithubStatus({
        connected: true,
        username: result.github_username,
        hasScope: result.has_repo_scope,
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to connect GitHub account. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleTechStackToggle = (tech: string) => {
    setTechStack((prev) =>
      prev.includes(tech) ? prev.filter((t) => t !== tech) : [...prev, tech]
    );
  };

  const validateName = (repoName: string): string | null => {
    if (!repoName || repoName.trim().length === 0) {
      return "Repository name is required";
    }
    if (repoName.length > 100) {
      return "Repository name must be 100 characters or less";
    }
    if (repoName.startsWith(".") || repoName.startsWith("-") || repoName.startsWith("_")) {
      return "Repository name cannot start with . - or _";
    }
    if (repoName.endsWith(".") || repoName.endsWith("-") || repoName.endsWith("_")) {
      return "Repository name cannot end with . - or _";
    }
    const validPattern = /^[a-zA-Z0-9._-]+$/;
    if (!validPattern.test(repoName)) {
      return "Repository name can only contain letters, numbers, dots, hyphens, and underscores";
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const nameError = validateName(name);
    if (nameError) {
      setError(nameError);
      return;
    }

    if (!githubStatus?.connected) {
      setError("GitHub is not connected. Please connect your GitHub account first.");
      return;
    }

    if (!githubStatus?.hasScope) {
      setError("Your GitHub token doesn't have the 'repo' scope. Please reconnect your GitHub account with proper permissions.");
      return;
    }

    setIsLoading(true);

    try {
      const request: CreateRepoRequest = {
        name: name.trim(),
        description: description.trim() || undefined,
        tech_stack: techStack.length > 0 ? techStack : undefined,
        is_private: false,
      };

      const response = await createGitHubRepository(request, clerkUserId);
      setSuccess(true);
      setCreatedRepo({
        url: response.project.github_url,
        name: response.project.name,
      });

      // Call onSuccess callback after a short delay
      setTimeout(() => {
        onSuccess?.();
        onOpenChange(false);
      }, 2000);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create repository. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New GitHub Repository</DialogTitle>
          <DialogDescription>
            Create a new repository on GitHub with the openforge-demo topic. The repository will be
            initialized with a README and .gitignore file.
          </DialogDescription>
        </DialogHeader>

        {isCheckingStatus ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-sm text-muted-foreground">Checking GitHub status...</span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* GitHub Status */}
            {githubStatus && (
              <div
                className={`p-3 rounded-md flex items-center gap-2 ${
                  githubStatus.connected && githubStatus.hasScope
                    ? "bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800"
                    : "bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800"
                }`}
              >
                {githubStatus.connected && githubStatus.hasScope ? (
                  <>
                    <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-green-900 dark:text-green-100">
                        GitHub Connected
                      </p>
                      {githubStatus.username && (
                        <p className="text-xs text-green-700 dark:text-green-300">
                          Connected as @{githubStatus.username}
                        </p>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                        GitHub Not Connected
                      </p>
                      <p className="text-xs text-yellow-700 dark:text-yellow-300 mb-2">
                        {githubStatus.connected && !githubStatus.hasScope
                          ? "Your GitHub token doesn't have 'repo' scope. Please reconnect with proper permissions."
                          : "You're signed in with GitHub, but we need to verify your access token. Click the button below to connect."}
                      </p>
                      <Button
                        type="button"
                        onClick={handleConnectGitHub}
                        disabled={isLoading}
                        size="sm"
                        variant="outline"
                        className="mt-2"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Connecting...
                          </>
                        ) : (
                          <>
                            <Github className="mr-2 h-4 w-4" />
                            Connect GitHub
                          </>
                        )}
                      </Button>
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Success Message */}
            {success && createdRepo && (
              <div className="p-3 rounded-md bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-900 dark:text-green-100">
                      Repository created successfully!
                    </p>
                    <a
                      href={createdRepo.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-green-700 dark:text-green-300 hover:underline flex items-center gap-1 mt-1"
                    >
                      <Github className="h-3 w-3" />
                      View on GitHub
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-md bg-destructive/10 border border-destructive/20">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-destructive" />
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              </div>
            )}

            {/* Repository Name */}
            <div className="space-y-2">
              <Label htmlFor="name">
                Repository Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="my-awesome-project"
                disabled={isLoading || success}
                required
              />
              <p className="text-xs text-muted-foreground">
                Only letters, numbers, dots, hyphens, and underscores. 1-100 characters.
              </p>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="A brief description of your project"
                rows={3}
                disabled={isLoading || success}
              />
            </div>

            {/* Tech Stack */}
            <div className="space-y-2">
              <Label>Tech Stack (optional)</Label>
              <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-2 border rounded-md">
                {COMMON_TECH_STACK.map((tech) => (
                  <button
                    key={tech}
                    type="button"
                    onClick={() => handleTechStackToggle(tech)}
                    disabled={isLoading || success}
                    className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                      techStack.includes(tech)
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background hover:bg-muted border-border"
                    }`}
                  >
                    {tech}
                  </button>
                ))}
              </div>
              {techStack.length > 0 && (
                <p className="text-xs text-muted-foreground">
                  Selected: {techStack.join(", ")}
                </p>
              )}
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={
                  isLoading ||
                  success ||
                  !githubStatus?.connected ||
                  !githubStatus?.hasScope ||
                  !name.trim()
                }
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : success ? (
                  <>
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Created!
                  </>
                ) : (
                  <>
                    <Github className="mr-2 h-4 w-4" />
                    Create Repository
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}

