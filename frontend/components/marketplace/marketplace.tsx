"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SearchBar } from "./search-bar";
import { RepositoryList } from "./repository-list";
import { RepositoryListSkeleton } from "./repository-list-skeleton";
import {
  fetchRepositories,
  GitHubRepository,
} from "@/lib/api/marketplace";
function useDebouncedValue<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export function Marketplace() {
  const searchParams = useSearchParams();
  
  // Initialize search from URL params if present
  const [searchQuery, setSearchQuery] = useState(searchParams.get("search") || "");
  const [repositories, setRepositories] = useState<GitHubRepository[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  const debouncedSearch = useDebouncedValue(searchQuery, 500);
  
  // Sync search query with URL params when they change externally (e.g., browser back button)
  useEffect(() => {
    const urlSearch = searchParams.get("search") || "";
    // Only update if URL param differs from current state (avoids unnecessary updates)
    if (urlSearch !== searchQuery && urlSearch !== debouncedSearch) {
      setSearchQuery(urlSearch);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // Update URL when search changes (but don't trigger navigation)
  useEffect(() => {
    const params = new URLSearchParams();
    if (debouncedSearch.trim()) {
      params.set("search", debouncedSearch.trim());
    }
    const newUrl = params.toString() ? `?${params.toString()}` : "/";
    // Update URL without navigation
    window.history.replaceState({}, "", newUrl);
  }, [debouncedSearch]);

  // Fetch repositories
  useEffect(() => {
    const loadRepositories = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchRepositories(debouncedSearch || undefined);
        setRepositories(data.repositories);
        setTotalCount(data.total_count);
      } catch (err) {
        console.error("Failed to load repositories:", err);
        setError(err instanceof Error ? err.message : "Failed to load repositories");
      } finally {
        setIsLoading(false);
      }
    };

    loadRepositories();
  }, [debouncedSearch]);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>OpenForge Marketplace</CardTitle>
          <p className="text-sm text-muted-foreground mt-2">
            Discover new exciting Open-Source projects on GitHub!
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search repositories by name..."
            />
            {totalCount > 0 && (
              <p className="text-sm text-muted-foreground">
                Found {totalCount} {totalCount === 1 ? "repository" : "repositories"}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <RepositoryListSkeleton />
      ) : (
        <RepositoryList
          repositories={repositories}
          searchQuery={searchQuery}
        />
      )}
    </div>
  );
}

