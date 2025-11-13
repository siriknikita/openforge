"use client";

import { useEffect, useRef } from "react";

/**
 * Props for the GitHubEmbed component
 */
interface GitHubEmbedProps {
  /** The GitHub username/organization */
  user: string;
  /** The GitHub repository name */
  repo: string;
  /** Optional CSS height for the container. Defaults to '100%' */
  height?: string;
}

/**
 * A React component that embeds a GitHub repository in a VS Code-like IDE using StackBlitz SDK.
 * 
 * @param props - The component props
 * @returns A div element containing the embedded IDE
 */
export function GitHubEmbed({ user, repo, height = "100%" }: GitHubEmbedProps) {
  const embedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Only embed if we have both user and repo
    if (!user || !repo) {
      return;
    }

    let isMounted = true;

    // Dynamically import StackBlitz SDK to avoid SSR issues
    const embedRepository = async () => {
      try {
        // Wait for next frame to ensure element is fully rendered
        await new Promise(resolve => requestAnimationFrame(resolve));

        // Re-check element validity after async operations
        const currentElement = embedRef.current;
        if (!currentElement || !isMounted) {
          return;
        }

        // Ensure element is in the DOM and has dimensions
        const rect = currentElement.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) {
          // Retry after a short delay if element doesn't have dimensions yet
          setTimeout(() => {
            if (isMounted && embedRef.current) {
              embedRepository();
            }
          }, 100);
          return;
        }

        // Clear the container to prevent duplicate embeds when props change
        currentElement.innerHTML = "";

        const sdk = await import("@stackblitz/sdk");
        
        // Re-check again after SDK import
        if (!embedRef.current || !isMounted) {
          return;
        }

        // Use embedGithubProject method
        const sdkInstance = sdk.default || sdk;
        const embedMethod = sdkInstance.embedGithubProject;
        
        if (!embedMethod || typeof embedMethod !== 'function') {
          console.error("StackBlitz SDK embedGithubProject method not found");
          return;
        }

        // Final element check before embedding
        const finalElement = embedRef.current;
        if (!finalElement || !isMounted) {
          return;
        }

        // Embed the GitHub repository
        embedMethod(finalElement, `${user}/${repo}`, {
          height: "100%",
          width: "100%",
          openFile: "README.md",
          view: "editor",
          hideExplorer: false,
        });
      } catch (error) {
        console.error("Failed to embed GitHub repository:", error);
      }
    };

    embedRepository();

    // Cleanup function
    return () => {
      isMounted = false;
      if (embedRef.current) {
        embedRef.current.innerHTML = "";
      }
    };
  }, [user, repo]);

  return (
    <div
      ref={embedRef}
      style={{ height, width: "100%" }}
      className="w-full"
    />
  );
}

