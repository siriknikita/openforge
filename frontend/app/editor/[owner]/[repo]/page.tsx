"use client";

import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function EditorPage() {
  const params = useParams();
  const owner = params.owner as string;
  const repo = params.repo as string;

  return (
    <main className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle>Editor - {owner}/{repo}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Monaco editor will be integrated here. This is a placeholder page.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Repository: {owner}/{repo}
          </p>
        </CardContent>
      </Card>
    </main>
  );
}

