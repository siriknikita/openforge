"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, PieLabelRenderProps } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TimeBreakdownChartProps {
  contributingToOSS: number; // hours
  workingOnOwnProjects: number; // hours
}

const COLORS = {
  contributing: "hsl(var(--chart-1))",
  ownProjects: "hsl(var(--chart-2))",
};

export function TimeBreakdownChart({
  contributingToOSS,
  workingOnOwnProjects,
}: TimeBreakdownChartProps) {
  const data = [
    {
      name: "Contributing to OSS",
      value: contributingToOSS,
      color: COLORS.contributing,
    },
    {
      name: "Working on Own Projects",
      value: workingOnOwnProjects,
      color: COLORS.ownProjects,
    },
  ];

  const total = contributingToOSS + workingOnOwnProjects;
  const contributingPercentage = total > 0 ? (contributingToOSS / total) * 100 : 0;
  const ownProjectsPercentage = total > 0 ? (workingOnOwnProjects / total) * 100 : 0;

  const formatTooltip = (entry: any) => {
    const percentage = total > 0 ? ((entry.value / total) * 100).toFixed(1) : "0";
    return `${entry.name}: ${entry.value.toFixed(1)}h (${percentage}%)`;
  };

  // Show placeholder when no time data
  if (total === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Time Breakdown</CardTitle>
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
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
            <p className="text-lg font-medium text-foreground">No time tracked yet</p>
            <p className="mt-2 text-sm text-muted-foreground">
              Start contributing to open source or working on your projects to see your time breakdown here.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Time Breakdown</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(props: PieLabelRenderProps) => {
                  const value = typeof props.value === 'number' ? props.value : 0;
                  const percent = total > 0 ? (value / total) * 100 : 0;
                  return `${props.name}: ${percent.toFixed(0)}%`;
                }}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={formatTooltip} />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div
                  className="size-3 rounded-full"
                  style={{ backgroundColor: COLORS.contributing }}
                />
                <span className="font-medium">Contributing to OSS</span>
              </div>
              <p className="text-muted-foreground pl-5">
                {contributingToOSS.toFixed(1)}h ({contributingPercentage.toFixed(1)}%)
              </p>
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div
                  className="size-3 rounded-full"
                  style={{ backgroundColor: COLORS.ownProjects }}
                />
                <span className="font-medium">Own Projects</span>
              </div>
              <p className="text-muted-foreground pl-5">
                {workingOnOwnProjects.toFixed(1)}h ({ownProjectsPercentage.toFixed(1)}%)
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

