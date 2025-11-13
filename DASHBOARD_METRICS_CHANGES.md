# Dashboard Metrics Changes Documentation

## Overview

This document describes the comprehensive changes made to the dashboard metrics tracking system in OpenForge. These changes improve metric accuracy, add new tracking capabilities, and reorganize the dashboard UI for better user experience.

## Table of Contents

1. [Model Changes](#model-changes)
2. [Dashboard Metrics Overview](#dashboard-metrics-overview)
3. [Dashboard Metrics Logic](#dashboard-metrics-logic)
4. [API Changes](#api-changes)
5. [UI Changes](#ui-changes)
6. [Testing Guide](#testing-guide)
7. [Migration Notes](#migration-notes)

---

## Model Changes

### User Model (`backend/app/models/user.py`)

**New Fields:**
- `last_visit_date` (Optional[datetime]): Tracks the last time the user visited the dashboard. Used for streak calculation.
- `current_streak` (int, default: 0): Stores the user's current consecutive days streak.

**Purpose:** Enables daily streak tracking to gamify user engagement and encourage consistent platform usage.

### Project Model (`backend/app/models/project.py`)

**New Fields:**
- `joined_members` (List[str], default: []): Array of usernames who have joined the project as contributors.
- `setup_time_estimate_minutes` (int, default: 7): Estimated time saved in minutes when a user joins this project. Set by the project author, defaults to 7 minutes.

**Purpose:** 
- `joined_members`: Tracks which users have joined a project for community visibility and metrics.
- `setup_time_estimate_minutes`: Allows project authors to specify how much time their project setup saves, contributing to the "Time Saved" metric.

---

## Dashboard Metrics Overview

### Active Projects

**What it means:**
- **Technical:** Count of projects the user has joined (via project memberships), not owned.
- **Business:** Indicates user engagement and active participation in the open-source community. Shows how many projects a user is actively contributing to.

**Why it matters:** 
- Demonstrates community involvement
- Helps users see their contribution footprint
- Encourages joining more projects to increase engagement

**Current Implementation:** Uses count of joined projects (fake data placeholder for future enhancement).

---

### Streak

**What it means:**
- **Technical:** Number of consecutive days the user has visited the dashboard. Increments by 1 each day, resets to 1 if a day is skipped.
- **Business:** Gamification metric that encourages daily platform engagement. Creates habit formation and increases user retention.

**Why it matters:**
- Builds user habits through daily engagement
- Increases platform stickiness
- Provides a sense of achievement and progress
- Can be used for rewards/badges in the future

**How it works:**
- First visit: Streak starts at 1
- Same day visit: Streak remains unchanged
- Next day visit: Streak increments by 1
- Skip a day: Streak resets to 1

---

### New Projects

**What it means:**
- **Technical:** Count of projects created by the user in the current calendar month only. Resets each month.
- **Business:** Measures monthly project creation activity. Shows how actively users are creating new open-source projects.

**Why it matters:**
- Tracks monthly productivity in project creation
- Encourages regular project creation
- Provides a monthly goal/challenge for users
- Helps identify active project creators

**Calculation:** Filters owned projects by `created_at` date, only counting those from the current month.

---

### Joined Projects

**What it means:**
- **Technical:** Total count of projects the user has joined as a contributor (via project memberships).
- **Business:** Measures community participation and collaboration. Shows how many projects a user is contributing to.

**Why it matters:**
- Indicates level of community engagement
- Shows collaborative spirit
- Demonstrates willingness to contribute to others' work
- Higher numbers indicate active community member

**Calculation:** Counts all `ProjectMembership` documents where `user_id` matches and `role` is "contributor".

---

### Total Contributions

**What it means:**
- **Technical:** Total number of commits made by the user in projects they have joined (not owned projects).
- **Business:** Measures actual code contribution activity. Shows real productivity in terms of commits made to joined projects.

**Why it matters:**
- Quantifies actual code contributions
- Shows productivity and activity level
- Only counts contributions to projects user has joined (more meaningful metric)
- Encourages joining projects before contributing

**Calculation:** Counts contributions of type "commit" where:
- `user_id` matches the current user
- `project_id` is in the list of projects the user has joined

---

### Pull Requests

**What it means:**
- **Technical:** Count of pull requests created by the user in projects they have joined.
- **Business:** Measures contribution quality and collaboration. PRs represent more substantial contributions than individual commits.

**Why it matters:**
- Indicates meaningful code contributions
- Shows ability to work collaboratively
- Demonstrates code review participation
- Higher PR count suggests active contributor

**Calculation:** Counts contributions of type "pull_request" from joined projects only.

---

### Issues Closed

**What it means:**
- **Technical:** Count of issues closed/resolved by the user in projects they have joined.
- **Business:** Measures problem-solving activity and community support. Shows users helping maintain and improve projects.

**Why it matters:**
- Demonstrates community support
- Shows problem-solving skills
- Indicates project maintenance participation
- Encourages helping others

**Calculation:** Counts contributions of type "issue" from joined projects only.

---

### Time Saved

**What it means:**
- **Technical:** Sum of `setup_time_estimate_minutes` from all projects the user has joined. Defaults to 7 minutes per project if not specified.
- **Business:** Quantifies the value provided by the platform. Shows how much time users save by using pre-configured project setups instead of starting from scratch.

**Why it matters:**
- Demonstrates platform value proposition
- Shows cumulative benefit of using OpenForge
- Encourages joining more projects
- Can be used in marketing ("Users have saved X hours")
- Project authors can set custom time estimates

**Calculation:** Sums `setup_time_estimate_minutes` from all projects in user's joined projects list.

---

### Time Breakdown

**What it means:**
- **Technical:** Visual breakdown showing hours spent "Contributing to OSS" vs "Working on Own Projects" (currently using fake 50/50 split data).
- **Business:** Provides insight into how users allocate their development time between contributing to others' projects vs working on their own.

**Why it matters:**
- Helps users understand their contribution patterns
- Encourages balance between creating and contributing
- Future: Can be used for time management insights
- Visual representation makes data more digestible

**Current Implementation:** Returns fake data (5.0h / 5.0h split) as placeholder for future time tracking implementation.

---

## Dashboard Metrics Logic

### Monthly Project Filtering

**Implementation:** `backend/app/routers/dashboard.py`

Projects are filtered by comparing `created_at` with the current month's start date:

```python
current_month_start = datetime(now_utc.year, now_utc.month, 1)
owned_projects_this_month = [
    p for p in owned_projects 
    if p.get("created_at") >= current_month_start
]
```

**Edge Cases Handled:**
- Handles both datetime objects and ISO string formats
- Gracefully skips projects with invalid dates

---

### Contribution Filtering

**Implementation:** `backend/app/routers/dashboard.py`

Contributions are filtered to only include those from projects the user has joined:

```python
# Get project IDs from joined projects
joined_project_ids = [str(p["_id"]) for p in contributed_projects]

# Filter contributions
contributions = [
    c for c in all_contributions 
    if c.get("project_id") in joined_project_ids
]
```

**Why this matters:**
- Prevents counting contributions to projects user hasn't joined
- Makes metrics more meaningful and accurate
- Encourages proper project joining workflow

---

### Streak Calculation

**Implementation:** `backend/app/routers/dashboard.py`

Streak is calculated on every dashboard visit:

1. Get user's `last_visit_date` and `current_streak`
2. Calculate days difference from today
3. Update streak based on difference:
   - Same day: Keep streak unchanged
   - Yesterday: Increment streak by 1
   - More than 1 day: Reset streak to 1
4. Update `last_visit_date` to current time

**Edge Cases:**
- Handles first visit (no `last_visit_date`)
- Handles string and datetime formats
- Gracefully handles parsing errors

---

### Time Saved Calculation

**Implementation:** `backend/app/routers/dashboard.py`

Time saved is calculated from joined projects only:

```python
time_saved_minutes = sum(
    p.get("setup_time_estimate_minutes", 7) 
    for p in contributed_projects
)
```

**Default Value:** 7 minutes per project if `setup_time_estimate_minutes` is not set.

---

## API Changes

### New Endpoint: Join Project

**Endpoint:** `POST /api/projects/{project_id}/join`

**Purpose:** Allows a user to join a project as a contributor.

**Request:**
```json
{
  "user_id": "clerk_user_id"  // Optional if authenticated via Clerk
}
```

**Response:**
```json
{
  "message": "Successfully joined project",
  "project_id": "project_id"
}
```

**What it does:**
1. Creates a `ProjectMembership` document
2. Adds user's name to project's `joined_members` array
3. Sets `setup_time_estimate_minutes` to 7 if not already set

**Error Cases:**
- 401: Authentication required
- 400: User already a member or is the project owner
- 404: Project or user not found
- 503: Database unavailable

---

### Updated Dashboard Endpoint

**Endpoint:** `GET /api/dashboard`

**Response Changes:**

**Removed Fields:**
- `stats.linesOfCode` - No longer tracked
- `additionalMetrics.averagePRMergeTime` - Removed from response

**Updated Fields:**
- `stats.newProjects` - Now counts only current month's projects
- `stats.commits` - Now filtered by joined projects only
- `stats.pullRequests` - Now filtered by joined projects only
- `stats.issuesClosed` - Now filtered by joined projects only
- `stats.timeSavedMinutes` - Now calculated from joined projects only
- `additionalMetrics.totalContributions` - Now uses commits count
- `additionalMetrics.activeProjects` - Now uses joined projects count
- `additionalMetrics.streak` - Now calculated from daily visits

**New Response Structure:**
```json
{
  "user": { ... },
  "stats": {
    "newProjects": 2,           // Current month only
    "joinedProjects": 5,
    "commits": 42,              // From joined projects only
    "pullRequests": 8,          // From joined projects only
    "issuesClosed": 3,          // From joined projects only
    "timeSavedMinutes": 35     // Sum from joined projects
  },
  "timeBreakdown": {
    "contributingToOSS": 5.0,   // Fake data
    "workingOnOwnProjects": 5.0 // Fake data
  },
  "additionalMetrics": {
    "totalContributions": 42,   // Same as commits
    "activeProjects": 5,        // Count of joined projects
    "streak": 7                // Daily streak
  }
}
```

---

## UI Changes

### Dashboard Layout Updates

**File:** `frontend/app/dashboard/page.tsx`

**Changes:**
1. **Moved to Top:** "Active Projects" and "Streak" cards are now the first two metrics displayed
2. **Removed Cards:**
   - "Lines of Code" - Completely removed
   - "Avg PR Merge Time" - Completely removed
3. **Renamed:** "Total Commits" → "Total Contributions"
4. **Removed Duplicate:** "Total Contributions" card from additional metrics section (now only in main stats)

**New Card Order:**
1. Active Projects
2. Streak
3. New Projects
4. Joined Projects
5. Total Contributions
6. Pull Requests
7. Issues Closed
8. Time Saved

---

### TypeScript Interface Updates

**File:** `frontend/lib/api/dashboard.ts`

**Removed:**
- `stats.linesOfCode`
- `additionalMetrics.averagePRMergeTime`

**Updated:**
- All metric calculations now reflect the new filtering logic

---

### Component Fixes

**File:** `frontend/components/dashboard/time-breakdown-chart.tsx`

**Fixed:** Tooltip formatter to handle Recharts' parameter format correctly, preventing runtime errors when tooltip values are undefined.

---

## Testing Guide

### Prerequisites

1. **Backend Running:** FastAPI server on port 8000
2. **Frontend Running:** Next.js dev server on port 3000
3. **MongoDB:** Database connected and accessible
4. **Authentication:** Clerk configured (or use `user_id` query param for dev)

### Test Cases

#### 1. Monthly Project Tracking

**Test:** "New Projects" should only count current month's projects

**Steps:**
1. Create a project with `created_at` = current date
2. Create a project with `created_at` = last month
3. Check dashboard - should only show 1 project

**MongoDB Test:**
```javascript
// Current month project
db.projects.insertOne({
  name: "Current Month Project",
  owner_id: "test_user",
  created_at: new Date(),
  joined_members: [],
  setup_time_estimate_minutes: 7
})

// Last month project
db.projects.insertOne({
  name: "Last Month Project",
  owner_id: "test_user",
  created_at: new Date("2024-01-15"),
  joined_members: [],
  setup_time_estimate_minutes: 7
})
```

#### 2. Join Project Functionality

**Test:** Joining a project should update metrics

**Steps:**
1. Create a project (as User A)
2. Join project (as User B) via API:
   ```bash
   curl -X POST "http://localhost:8000/api/projects/{project_id}/join" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user_b_id"}'
   ```
3. Verify:
   - `joined_members` array contains User B's name
   - `ProjectMembership` document created
   - Dashboard shows increased "Joined Projects" count
   - "Time Saved" increases by 7 minutes (or project's custom value)

#### 3. Streak Tracking

**Test:** Streak increments on daily visits

**Steps:**
1. Visit dashboard - streak should be 1
2. Visit again same day - streak should stay 1
3. Wait until next day and visit - streak should be 2
4. Skip a day and visit - streak should reset to 1

**MongoDB Verification:**
```javascript
db.users.findOne({clerk_user_id: "test_user"})
// Check: last_visit_date and current_streak fields
```

#### 4. Contribution Filtering

**Test:** Contributions only count from joined projects

**Steps:**
1. Create contributions for a project (before joining)
2. Check dashboard - contributions should NOT appear
3. Join the project
4. Check dashboard - contributions should NOW appear

**MongoDB Test:**
```javascript
// Create contribution before joining
db.contributions.insertOne({
  user_id: "test_user",
  project_id: "project_id",
  type: "commit",
  title: "Test commit",
  created_at: new Date()
})

// After joining, contribution should appear in dashboard
```

#### 5. Time Saved Calculation

**Test:** Time saved sums from joined projects

**Steps:**
1. Join Project A (7 min default)
2. Join Project B (7 min default)
3. Dashboard should show 14 minutes
4. Update Project A's `setup_time_estimate_minutes` to 10
5. Dashboard should show 17 minutes

#### 6. UI Layout

**Test:** Verify new card layout

**Steps:**
1. Visit `/dashboard`
2. Verify "Active Projects" and "Streak" are first two cards
3. Verify "Lines of Code" and "Avg PR Merge Time" are removed
4. Verify "Total Commits" is renamed to "Total Contributions"

---

## Migration Notes

### Database Migration

**Existing Projects:**
- Projects without `joined_members` field will default to empty array `[]`
- Projects without `setup_time_estimate_minutes` will default to `7` when first user joins

**Existing Users:**
- Users without `last_visit_date` will start with streak = 1 on first dashboard visit
- Users without `current_streak` will default to 0, then set to 1 on first visit

**No Breaking Changes:**
- All new fields have defaults
- Existing data remains compatible
- API responses maintain backward compatibility (removed fields are simply omitted)

### Code Migration

**Frontend:**
- Remove any references to `linesOfCode` in components
- Remove any references to `averagePRMergeTime` in components
- Update any hardcoded metric calculations to use new filtered logic

**Backend:**
- No action required - changes are backward compatible
- New fields are optional with defaults

### API Consumers

**If consuming dashboard API:**
- Remove handling for `linesOfCode` field
- Remove handling for `averagePRMergeTime` field
- Update logic to expect monthly filtering for `newProjects`
- Update logic to expect filtered contributions (joined projects only)

---

## Business Impact

### User Engagement

**Streak Tracking:**
- Encourages daily platform visits
- Creates habit formation
- Increases user retention
- Potential for future rewards/badges

**Monthly Project Tracking:**
- Provides monthly goals/challenges
- Encourages regular project creation
- Creates sense of progress and achievement

### Community Building

**Joined Projects Metric:**
- Encourages collaboration
- Shows community participation
- Demonstrates willingness to contribute

**Contribution Filtering:**
- Encourages proper workflow (join before contribute)
- Makes metrics more meaningful
- Shows actual engagement vs. passive viewing

### Value Demonstration

**Time Saved Metric:**
- Quantifies platform value
- Shows cumulative benefit
- Can be used in marketing materials
- Encourages joining more projects

**Active Projects:**
- Shows engagement level
- Helps users see their footprint
- Encourages continued participation

---

## Future Enhancements

### Planned Improvements

1. **Time Breakdown:** Replace fake data with actual time tracking
2. **Active Projects:** More sophisticated calculation (e.g., projects with recent activity)
3. **Streak Rewards:** Badges or XP bonuses for maintaining streaks
4. **Monthly Challenges:** Goals based on monthly project creation
5. **Contribution Quality:** Weight contributions by project size/importance

### Technical Debt

1. **Time Tracking:** Need to implement actual time tracking for accurate breakdown
2. **Active Projects:** Currently uses simple count, could be enhanced with activity-based calculation
3. **Contribution Sync:** May need to sync contributions from external sources (GitHub, etc.)

---

## Support

For questions or issues related to these changes:
- Check the code comments in `backend/app/routers/dashboard.py`
- Review the model definitions in `backend/app/models/`
- Test using the provided test cases above

---

**Last Updated:** [Current Date]
**Version:** 1.0.0

