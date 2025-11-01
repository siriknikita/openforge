"use client";

import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface UserRankProps {
  name: string;
  avatarUrl: string | null;
  xp: number;
  level: number;
}

/**
 * Calculate XP progress for current level
 * Level thresholds: 0-1000 (L1), 1000-2500 (L2), 2500-5000 (L3), 5000-10000 (L4), etc.
 */
function getLevelThresholds(level: number): { min: number; max: number } {
  if (level === 1) return { min: 0, max: 1000 };
  if (level === 2) return { min: 1000, max: 2500 };
  if (level === 3) return { min: 2500, max: 5000 };
  if (level === 4) return { min: 5000, max: 10000 };
  if (level === 5) return { min: 10000, max: 20000 };
  
  // For levels 6+, exponential growth
  const base = 20000;
  const multiplier = Math.pow(1.5, level - 5);
  const max = base * multiplier;
  const min = level > 5 ? getLevelThresholds(level - 1).max : max;
  
  return { min, max };
}

function getXPProgress(xp: number, level: number): number {
  const { min, max } = getLevelThresholds(level);
  const current = xp - min;
  const total = max - min;
  return Math.max(0, Math.min(100, (current / total) * 100));
}

function getLevelName(level: number): string {
  if (level <= 3) return "Junior Developer";
  if (level <= 5) return "Mid-Level Developer";
  if (level <= 7) return "Senior Developer";
  if (level <= 10) return "Expert Developer";
  return "Master Developer";
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function UserRank({ name, avatarUrl, xp, level }: UserRankProps) {
  const progress = getXPProgress(xp, level);
  const { min, max } = getLevelThresholds(level);
  const xpToNextLevel = max - xp;
  const levelName = getLevelName(level);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Profile</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <Avatar className="size-16">
            {avatarUrl && <AvatarImage src={avatarUrl} alt={name} />}
            <AvatarFallback>{getInitials(name)}</AvatarFallback>
          </Avatar>
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-semibold">{name}</h3>
              <Badge variant="secondary">Level {level}</Badge>
              <Badge variant="outline">{levelName}</Badge>
            </div>
            <div className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">XP Progress</span>
                <span className="font-medium">
                  {xp.toLocaleString()} / {max.toLocaleString()} XP
                </span>
              </div>
              <Progress value={progress} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {xpToNextLevel.toLocaleString()} XP needed for Level {level + 1}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

