"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ProjectCard } from "./project-card";
import { Project } from "@/lib/api/dashboard";

interface ProjectListProps {
  owned: Project[];
  contributed: Project[];
  starred: Project[];
  clerkUserId: string;
  onStarToggle?: (projectId: string, starred: boolean) => void;
}

export function ProjectList({
  owned,
  contributed,
  starred,
  clerkUserId,
  onStarToggle,
}: ProjectListProps) {
  return (
    <Tabs defaultValue="owned" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="owned">Owned ({owned.length})</TabsTrigger>
        <TabsTrigger value="contributed">
          Contributed ({contributed.length})
        </TabsTrigger>
        <TabsTrigger value="starred">Starred ({starred.length})</TabsTrigger>
      </TabsList>
      <TabsContent value="owned" className="mt-4">
        {owned.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {owned.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                clerkUserId={clerkUserId}
                onStarToggle={onStarToggle}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No owned projects yet. Create your first project to get started!
          </div>
        )}
      </TabsContent>
      <TabsContent value="contributed" className="mt-4">
        {contributed.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {contributed.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                clerkUserId={clerkUserId}
                onStarToggle={onStarToggle}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No contributed projects yet. Join an open-source project to start contributing!
          </div>
        )}
      </TabsContent>
      <TabsContent value="starred" className="mt-4">
        {starred.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {starred.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                clerkUserId={clerkUserId}
                onStarToggle={onStarToggle}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No starred projects yet. Star projects to save them for later!
          </div>
        )}
      </TabsContent>
    </Tabs>
  );
}

