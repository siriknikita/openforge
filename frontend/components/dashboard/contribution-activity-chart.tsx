"use client";

import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid, Cell } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ContributionActivityChartProps {
  commits: number;
  pullRequests: number;
  issuesClosed: number;
}

const COLORS = {
  commits: "hsl(var(--chart-1))",
  pullRequests: "hsl(var(--chart-2))",
  issuesClosed: "hsl(var(--chart-3))",
};

export function ContributionActivityChart({
  commits,
  pullRequests,
  issuesClosed,
}: ContributionActivityChartProps) {
  const data = [
    {
      name: "Commits",
      value: commits,
      color: COLORS.commits,
    },
    {
      name: "Pull Requests",
      value: pullRequests,
      color: COLORS.pullRequests,
    },
    {
      name: "Issues Closed",
      value: issuesClosed,
      color: COLORS.issuesClosed,
    },
  ];

  const total = commits + pullRequests + issuesClosed;

  const formatTooltip = (value: number) => {
    return value.toLocaleString();
  };

  // Show placeholder when no data
  if (total === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Contribution Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="mb-4 rounded-full bg-muted p-6">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-muted-foreground"
              >
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
            <p className="text-lg font-medium text-foreground">No contributions yet</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Start contributing to see your activity breakdown here.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Contribution Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="name"
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
              />
              <YAxis
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
              />
              <Tooltip
                formatter={formatTooltip}
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Bar
                dataKey="value"
                radius={[8, 8, 0, 0]}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div
                  className="size-3 rounded-full"
                  style={{ backgroundColor: COLORS.commits }}
                />
                <span className="font-medium">Commits</span>
              </div>
              <p className="text-muted-foreground pl-5">
                {commits.toLocaleString()}
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div
                  className="size-3 rounded-full"
                  style={{ backgroundColor: COLORS.pullRequests }}
                />
                <span className="font-medium">Pull Requests</span>
              </div>
              <p className="text-muted-foreground pl-5">
                {pullRequests.toLocaleString()}
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div
                  className="size-3 rounded-full"
                  style={{ backgroundColor: COLORS.issuesClosed }}
                />
                <span className="font-medium">Issues Closed</span>
              </div>
              <p className="text-muted-foreground pl-5">
                {issuesClosed.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

