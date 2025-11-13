"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GitHubEmbed } from "@/components/editor/github-embed";
import { MarkdownViewer } from "@/components/marketplace/markdown-viewer";
import { fetchRepositoryDetails, GitHubRepositoryDetail } from "@/lib/api/marketplace";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

type ViewMode = "editor" | "preview" | "both";

export default function EditorPage() {
  const params = useParams();
  const owner = params.owner as string;
  const repo = params.repo as string;

  const [repository, setRepository] = useState<GitHubRepositoryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("both");
  const [leftPanelWidth, setLeftPanelWidth] = useState(50); // percentage
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadRepository = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const details = await fetchRepositoryDetails(owner, repo);
        setRepository(details);
      } catch (err) {
        console.error("Failed to load repository details:", err);
        setError(err instanceof Error ? err.message : "Failed to load repository details");
      } finally {
        setIsLoading(false);
      }
    };

    if (owner && repo) {
      loadRepository();
    }
  }, [owner, repo]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing || !containerRef.current) return;

    const container = containerRef.current;
    const containerRect = container.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    
    // Constrain between 20% and 80%
    const constrainedWidth = Math.max(20, Math.min(80, newLeftWidth));
    setLeftPanelWidth(constrainedWidth);
  }, [isResizing]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    } else {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  if (isLoading) {
    return (
      <main className="h-screen flex flex-col">
        <div className="border-b px-6 py-4">
          <Skeleton className="h-6 w-64" />
        </div>
        <div className="flex-1 flex">
          <div className="w-1/2 border-r p-6">
            <Skeleton className="h-full w-full" />
          </div>
          <div className="w-1/2 p-6">
            <Skeleton className="h-full w-full" />
          </div>
        </div>
      </main>
    );
  }

  if (error || !repository) {
    return (
      <main className="container mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Editor - {owner}/{repo}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-destructive">
              {error || "Repository not found"}
            </p>
          </CardContent>
        </Card>
      </main>
    );
  }

  const showPreview = viewMode === "preview" || viewMode === "both";
  const showEditor = viewMode === "editor" || viewMode === "both";

  return (
    <main className="h-screen flex flex-col">
      {/* Header */}
      <div className="border-b px-6 py-4 bg-background flex items-center justify-between">
        <h1 className="text-xl font-semibold">Editor - {owner}/{repo}</h1>
        
        {/* View Mode Toggle */}
        <div className="flex gap-2">
          <Button
            variant={viewMode === "editor" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("editor")}
          >
            Editor
          </Button>
          <Button
            variant={viewMode === "preview" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("preview")}
          >
            Preview
          </Button>
          <Button
            variant={viewMode === "both" ? "default" : "outline"}
            size="sm"
            onClick={() => setViewMode("both")}
          >
            Both
          </Button>
        </div>
      </div>

      {/* Split Layout */}
      <div ref={containerRef} className="flex-1 flex overflow-hidden relative">
        {/* Left Panel - README */}
        {showPreview && (
          <>
            <div
              className="overflow-y-auto bg-background border-r"
              style={{ width: `${leftPanelWidth}%` }}
            >
              <div className="p-6">
                {repository.readme.content ? (
                  <div>
                    <h2 className="text-lg font-semibold mb-4">README</h2>
                    <div className="prose prose-sm max-w-none">
                      <MarkdownViewer content={repository.readme.content} />
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted-foreground py-12">
                    <p>No README found for this repository.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Resizer */}
            {viewMode === "both" && (
              <div
                className="w-1 bg-border hover:bg-primary cursor-col-resize transition-colors relative z-10"
                onMouseDown={handleMouseDown}
              >
                <div className="absolute inset-y-0 -left-1 -right-1" />
              </div>
            )}
          </>
        )}

        {/* Right Panel - StackBlitz Editor */}
        {showEditor && (
          <div
            className="overflow-hidden bg-background"
            style={{ width: showPreview && viewMode === "both" ? `${100 - leftPanelWidth}%` : "100%" }}
          >
            <GitHubEmbed user={owner} repo={repo} height="100%" />
          </div>
        )}
      </div>
    </main>
  );
}

