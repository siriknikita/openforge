"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { RepositoryDetail } from "@/components/marketplace/repository-detail";
import { RepositoryDetailSkeleton } from "@/components/marketplace/repository-detail-skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { fetchRepositoryDetails, GitHubRepositoryDetail } from "@/lib/api/marketplace";
import { ArrowLeft } from "lucide-react";

export default function RepositoryDetailPage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const owner = params.owner as string;
  const repo = params.repo as string;
  const searchQuery = searchParams.get("search") || "";

  const [repository, setRepository] = useState<GitHubRepositoryDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const handleBack = () => {
    // Navigate back to homepage with search query preserved
    const search = searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : "";
    router.push(`/${search}`);
  };

  if (isLoading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Button variant="ghost" onClick={handleBack}>
            <ArrowLeft className="size-4 mr-2" />
            Back
          </Button>
        </div>
        <RepositoryDetailSkeleton />
      </main>
    );
  }

  if (error || !repository) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Button variant="ghost" onClick={handleBack}>
            <ArrowLeft className="size-4 mr-2" />
            Back
          </Button>
        </div>
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-destructive">
              {error || "Repository not found"}
            </p>
          </CardContent>
        </Card>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button variant="ghost" onClick={handleBack}>
          <ArrowLeft className="size-4 mr-2" />
          Back
        </Button>
      </div>
      <RepositoryDetail repository={repository} onClose={handleBack} />
    </main>
  );
}

