---
description: Research and fix any issue or implement any feature
---

# Fix Command

Research the codebase and implement: **$ARGUMENTS**

## Phase 1: Research
1. **Understand the request** - What needs to be fixed/built?
2. **Search codebase** - Find all relevant files and patterns
3. **Read key files** - Understand current implementation
4. **Check online** - Verify approach with documentation/best practices -> it's aug 2025

## Phase 2: Plan
1. **Design solution** - Match existing patterns
2. **List changes needed** - Which files, what changes
3. **Check dependencies** - Ensure libraries/tools available

## Phase 3: Document
**IMPORTANT**: `docs/TASK.md` already exists. Clear its contents first, then write your plan.

1. **Clear TASK.md** - Delete all existing content in `docs/TASK.md`
2. **Write new plan** - Add your implementation guide:

```markdown
# Task: [NAME]

## What We're Doing
[Brief description]

## Files to Change
- `path/file.tsx` - [what changes]

## Steps

### Step 1: [Action]
**File**: `path/file.tsx`
**Change**: [specific change]
```code
[exact code]
```

### Step 2: [Next action]
[continue...]

## Testing
- [ ] Works as expected
- [ ] No console errors
- [ ] [specific checks]
```

**DO NOT implement anything. Only research and document.**

## Phase 4: Execute
Launch task-executor agent to implement the documented plan:
```
Use Task tool: "Execute the implementation in docs/TASK.md step-by-step"
```

Keep it simple. Research → Plan → Document → Execute.