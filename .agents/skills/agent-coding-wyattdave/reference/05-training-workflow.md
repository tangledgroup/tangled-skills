# Training Workflow

The "secret sauce" for building effective AI coding agents is iterative training through real-world usage. This guide covers the complete workflow for testing, learning, and documenting improvements.

## The Learning Cycle

### Overview

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌─────────────┐
│   BUILD     │ ──▶ │    USE       │ ──▶ │   ANALYZE    │ ──▶ │   UPDATE    │
│  Initial    │     │  in Real     │     │  Reasoning   │     │  Prompts    │
│    Prompt   │     │   Projects   │     │   & Errors   │     │  & Skills   │
└─────────────┘     └──────────────┘     └──────────────┘     └──────┬──────┘
          ▲                                                          │
          └──────────────────────────────────────────────────────────┘
```

**Key Principle:** You don't build a perfect agent upfront. You learn through extensive testing and document every lesson.

## Phase 1: Initial Build

### Start with Core Knowledge

Before testing begins, create baseline prompts based on your expertise:

```markdown
# instruction.md (Initial Version)

## Tech Stack
- Vanilla JavaScript
- Power Platform Code App SDK
- PAC CLI for deployment

## Known Patterns
(Start with what you know works)
- Use sdk.dataverse.* for data operations
- Check connection status before operations
- Handle errors with try/catch

## Known Pitfalls  
(Start with mistakes you've made before)
- Don't use React patterns
- Table names are lowercase
- Always validate connections
```

### Create Basic Skills

```markdown
# SKILL.md (Initial Version)

---
name: dataverse-basics
description: Basic Dataverse operations in Code Apps
version: "0.1.0"
---

# Dataverse Basics

## When to Use
- CRUD operations on Dataverse tables
- Querying with filters
- Working with relationships

## Core Patterns
(Add patterns you know work)

## Known Issues
(Document problems you've encountered)
```

**Important:** Don't wait for perfection. Start testing immediately and improve iteratively.

## Phase 2: Extensive Testing

### Build Many Apps

The author built numerous Code Apps during training. Each app revealed new issues:

```
App #1: Customer Portal
├── Discovered: Connection check pattern needed
├── Discovered: Error handling for offline mode
└── Updated: dataverse-operations skill

App #2: Inventory Tracker  
├── Discovered: Relationship query direction confusion
├── Discovered: Pagination for large result sets
└── Updated: Added relationship patterns, pagination examples

App #3: Approval Workflow
├── Discovered: Async/await timing issues
├── Discovered: UI update after create pattern
└── Updated: Added async patterns, UI refresh examples
```

### Testing Strategy

#### 1. Diverse Use Cases

Test across different scenarios to expose edge cases:

| Category | Test Apps | What It Reveals |
|----------|-----------|-----------------|
| **Simple CRUD** | 2-3 apps | Basic operation patterns, error handling |
| **Complex Queries** | 2-3 apps | Filter syntax, pagination, performance |
| **Relationships** | 2-3 apps | Parent-child queries, lookup handling |
| **UI Integration** | 2-3 apps | Display patterns, user feedback |
| **Error Scenarios** | Intentional failures | Recovery patterns, edge cases |

#### 2. Read Reasoning Every Time

If your LLM provides reasoning (Claude's "thinking" output, Chain of Thought):

```typescript
// Enable reasoning capture
const response = await llm.chatWithReasoning(userPrompt);

console.log('=== REASONING ===');
console.log(response.reasoning);

console.log('=== RESPONSE ===');  
console.log(response.content);

// Save for analysis
await this.saveInteraction({
  prompt: userPrompt,
  reasoning: response.reasoning,
  response: response.content,
  timestamp: new Date()
});
```

**What to look for in reasoning:**
- Does the LLM understand the domain correctly?
- Is it referencing the right patterns?
- Where does it show uncertainty?
- What assumptions is it making?

#### 3. Track Every Bug

Create a structured bug log:

```markdown
# Training Bug Log

## Bug #1: Wrong Table Name Case
**Date:** 2024-04-10  
**App:** Customer Portal  
**Prompt:** "Query all active accounts"  

**LLM Response:**
```javascript
const results = await sdk.dataverse.query("Account", "statecode eq 0");
```

**Error:**
```
Error: Table 'Account' not found. Use lowercase schema name 'account'.
```

**Root Cause:**
LLM used PascalCase "Account" instead of lowercase "account". System prompt mentioned this, but not emphatically enough.

**Fix Applied:**
Updated system prompt to emphasize lowercase requirement with explicit examples:

```
CRITICAL: All table and column names MUST be lowercase schema names.
✅ CORRECT: sdk.dataverse.query("account", ...)
❌ WRONG: sdk.dataverse.query("Account", ...)
```

**Test to Prevent Recurrence:**
Added test case: "Query accounts" → verify lowercase in response

---

## Bug #2: Missing Connection Check
**Date:** 2024-04-11  
**App:** Inventory Tracker  
**Prompt:** "Create new inventory item"  

**LLM Response:**
```javascript
await sdk.dataverse.create("inventoryitem", data);
```

**Error:**
```
Error: Connection not active. Call sdk.connect() first.
```

**Root Cause:**
Skill showed connection check in one example but not all. LLM didn't generalize the pattern.

**Fix Applied:**
1. Added connection check to ALL examples in skill
2. Created separate "connection-management" skill
3. Added negative constraint: "Do NOT assume connection is active"

**Test to Prevent Recurrence:**
Any create/update/delete prompt → verify connection check present

---
```

### Usage Metrics

Track when and how the agent is used:

```typescript
class UsageTracker {
  async logUsage(sessionData: SessionData): Promise<void> {
    const metrics = {
      date: new Date(),
      totalPrompts: sessionData.prompts.length,
      successfulCompletions: sessionData.successfulCompletions,
      errorsEncountered: sessionData.errors.length,
      skillsUsed: sessionData.skillsUsed,
      averageTokensPerRequest: sessionData.totalTokens / sessionData.prompts.length,
      timeToComplete: sessionData.durationMs
    };
    
    await this.appendMetrics(metrics);
  }
  
  getInsights(): string {
    const data = this.loadAllMetrics();
    
    // Find patterns in usage
    const mostUsedSkills = this.getMostUsedSkills(data);
    const commonErrors = this.getCommonErrors(data);
    const peakUsageTimes = this.getPeakUsageTimes(data);
    
    return `
## Usage Insights

**Most Used Skills:**
${mostUsedSkills.map((s, i) => `${i + 1}. ${s.name} (${s.count} times)`).join('\n')}

**Common Errors:**
${commonErrors.map((e, i) => `${i + 1}. ${e.error}: ${e.count} occurrences`).join('\n')}

**Recommendations:**
- Expand documentation for frequently used skills
- Add error handling patterns for common failures
- Consider creating new skills for repeated complex tasks
    `.trim();
  }
}
```

## Phase 3: Analysis

### Pattern Analysis

Identify recurring themes in bugs and fixes:

```markdown
# Pattern Analysis (Updated: 2024-04-13)

## Category 1: Naming Conventions (5 bugs)
**Pattern:** LLM consistently uses wrong case/format for names
- Table names: Account vs account
- Column names: Name vs name  
- Function names: GetData vs getData

**Root Cause:** General training emphasizes PascalCase/CamelCase conventions

**Solution:** 
- Explicit examples showing correct format
- Negative constraints with ❌ symbols
- Multiple reinforcements across system prompt and skills

## Category 2: Connection Management (4 bugs)
**Pattern:** LLM assumes connection is always available
- Missing connection checks before operations
- Not handling connection failures
- Not re-establishing after timeout

**Root Cause:** Web development patterns don't require explicit connections

**Solution:**
- Made connection check mandatory in all examples
- Created dedicated connection-management skill
- Added error patterns for connection failures

## Category 3: Error Handling (3 bugs)
**Pattern:** Inconsistent or missing error handling
- No try/catch around async operations
- Not checking error codes
- Silent failures without user feedback

**Root Cause:** Examples showed happy path, not error cases

**Solution:**
- All examples now include error handling
- Added error-handling patterns section
- Documented specific error codes and responses
```

### Reasoning Quality Assessment

Evaluate how the LLM thinks about problems:

```markdown
# Reasoning Quality Analysis

## Good Reasoning Patterns (Keep These)

### Pattern 1: Explicit SDK Reference
**Example:**
> "I need to use the Code App SDK for this. Let me check what methods are available for Dataverse operations..."

**Why It's Good:** Shows awareness of domain constraints, references correct API

**How to Reinforce:** 
- Keep SDK documentation prominent in skills
- Continue emphasizing "reference SDK docs" in system prompt

### Pattern 2: Connection Awareness
**Example:**
> "Before making this call, I should verify the connection is active since all Dataverse operations require it..."

**Why It's Good:** Demonstrates learned pattern from examples

**How to Reinforce:**
- Keep connection checks in all examples
- Add more varied connection scenarios

## Poor Reasoning Patterns (Fix These)

### Pattern 1: React Assumptions
**Example:**
> "I'll create a functional component with useState for managing the form data..."

**Why It's Bad:** Ignores system prompt constraint about no React

**How to Fix:**
- Strengthen negative constraints
- Add "What This Is NOT" section
- Include examples of wrong vs right approach

### Pattern 2: Generic Web Patterns
**Example:**
> "I'll use fetch() to call the API endpoint..."

**Why It's Bad:** Uses standard web API instead of SDK wrapper

**How to Fix:**
- Explicitly forbid fetch() for Dataverse
- Show SDK method as only correct approach
- Add error that would occur with fetch()
```

## Phase 4: Updates

### System Prompt Evolution

Track how system prompts evolve through testing:

```markdown
# System Prompt Version History

## v0.1.0 (Initial)
```
You are a Power Platform Code Apps expert. Use vanilla JavaScript and the SDK.
Don't use React patterns.
```

**Issues Found:**
- Too vague, LLM still suggested React
- Didn't emphasize constraints strongly enough

## v0.2.0 (After 5 apps)
```
You are a Power Platform Code Apps expert using vanilla JavaScript.

IMPORTANT: This is NOT standard web development. Do not use React, TypeScript, or modern ES6+ features.

Use the Code App SDK for all operations.
```

**Issues Found:**
- Better, but still occasional React suggestions
- LLM confused about which JS features are allowed

## v0.3.0 (After 10 apps) - CURRENT
```
You are a Power Platform Code Apps expert using vanilla JavaScript and the Code App SDK.

CRITICAL: This is NOT standard web development. Do NOT suggest:
- React patterns (hooks, components, JSX)
- TypeScript features (interfaces, types, TSX)  
- ES6+ features not in SDK
- npm packages not approved
- Standard browser APIs

ALWAYS:
- Reference Code App SDK documentation
- Use vanilla JavaScript (ES5 compatible)
- Check connection status before operations
- Follow patterns in /docs/patterns/

WHEN UNSURE: Ask clarifying questions, don't guess.
```

**Improvements:**
- Explicit lists of forbidden patterns
- Clear "ALWAYS" guidelines
- Escalation path when unsure
- Uses formatting (bold, lists) for emphasis

## Planned v0.4.0 Updates
Based on recent testing:
- Add specific examples of wrong vs right code
- Include more SDK method names
- Strengthen connection management emphasis
```

### Skill File Evolution

Document how skills improve:

```markdown
# Skill Evolution: dataverse-operations

## v0.1.0 (2024-04-01)
**Content:** Basic CRUD examples, no error handling  
**Bugs Encountered:** 8  
**Major Issues:**
- Missing connection checks
- No error handling
- Wrong table name case in examples
- Inconsistent patterns

## v0.2.0 (2024-04-05)
**Changes:**
- Added connection check to all examples
- Added try/catch blocks
- Fixed table name casing
- Standardized pattern structure

**Bugs Encountered:** 3  
**Remaining Issues:**
- Relationship queries still confusing
- Pagination not documented
- Error codes not explained

## v0.3.0 (2024-04-10) - CURRENT
**Changes:**
- Added relationship patterns (parent-to-child, child-to-parent)
- Added pagination examples
- Documented common error codes
- Added performance tips section
- Split into smaller focused sections

**Bugs Encountered:** 1  
**Quality:** Good - only 1 bug in last 5 uses

## Planned v0.4.0 Updates
- Add batch operation patterns
- Include more complex filter examples
- Document offline behavior
- Add troubleshooting section
```

### Instruction.md Evolution

Track project instruction changes:

```markdown
# Instruction.md Change Log

## 2024-04-01: Initial Version
Added basic tech stack and folder structure

## 2024-04-03: Added Naming Conventions
**Trigger:** Multiple bugs with inconsistent naming
**Change:** Added table showing correct formats for files, functions, constants

## 2024-04-07: Added Skill Usage Guidelines  
**Trigger:** LLM using wrong skills for tasks
**Change:** Explicit mapping of task types to skill names

## 2024-04-10: Added Learnings Section
**Trigger:** Repeating same mistakes across sessions
**Change:** Created self-updating section for persistent learnings

## 2024-04-13: Consolidated Redundant Info
**Trigger:** Token usage optimization
**Change:** Removed duplicate information, converted prose to tables
```

## Automation Tools

### Bug Detection Script

Automatically identify patterns in errors:

```typescript
class BugPatternDetector {
  async analyzeBugLog(): Promise<BugPatternReport> {
    const bugs = await this.loadBugLog();
    
    // Group by category
    const byCategory = this.groupByCategory(bugs);
    
    // Find recurring root causes
    const recurringCauses = this.findRecurringCauses(bugs);
    
    // Suggest fixes
    const suggestions = this.generateSuggestions(byCategory, recurringCauses);
    
    return {
      totalBugs: bugs.length,
      categories: byCategory,
      recurringCauses,
      suggestions,
      timeline: this.createTimeline(bugs)
    };
  }
  
  private groupByCategory(bugs: Bug[]): Record<string, Bug[]> {
    return bugs.reduce((acc, bug) => {
      const category = bug.category || 'uncategorized';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(bug);
      return acc;
    }, {});
  }
  
  private findRecurringCauses(bugs: Bug[]): string[] {
    const causeCounts = bugs.reduce((acc, bug) => {
      const cause = bug.rootCause;
      acc[cause] = (acc[cause] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(causeCounts)
      .filter(([_, count]) => count >= 2)
      .map(([cause]) => cause);
  }
  
  private generateSuggestions(byCategory: Record<string, Bug[]>, recurringCauses: string[]): string[] {
    const suggestions = [];
    
    // Suggest new skills for bug-heavy categories
    for (const [category, categoryBugs] of Object.entries(byCategory)) {
      if (categoryBugs.length >= 3) {
        suggestions.push(
          `Consider creating dedicated skill for "${category}" (${categoryBugs.length} bugs)`
        );
      }
    }
    
    // Suggest system prompt updates for recurring causes
    for (const cause of recurringCauses) {
      suggestions.push(
        `Add stronger constraint in system prompt addressing: ${cause}`
      );
    }
    
    return suggestions;
  }
}
```

### Usage Analytics Dashboard

Visualize training progress:

```typescript
class TrainingDashboard {
  async generateReport(): Promise<string> {
    const bugData = await this.loadBugData();
    const usageData = await this.loadUsageData();
    const versionHistory = await this.loadVersionHistory();
    
    return `
# Training Progress Report

## Bug Trend
${this.generateBugTrendChart(bugData)}

**Analysis:** ${this.analyzeBugTrend(bugData)}

## Skill Effectiveness
${this.generateSkillEffectivenessTable(usageData)}

## Version Impact
${this.generateVersionImpactChart(versionHistory)}

## Next Steps
${this.recommendNextActions(bugData, usageData)}
    `.trim();
  }
  
  private analyzeBugTrend(bugData: BugData[]): string {
    const recentBugs = bugData.slice(-10);
    const olderBugs = bugData.slice(0, -10);
    
    const recentRate = recentBugs.length / 5; // Per 5 apps
    const olderRate = olderBugs.length / Math.max(olderBugs.length / 5, 1);
    
    if (recentRate < olderRate * 0.5) {
      return '✅ Excellent progress! Bug rate decreased significantly.';
    } else if (recentRate < olderRate) {
      return '📈 Good progress. Bug rate trending down.';
    } else {
      return '⚠️ Bug rate not improving. Reconsider training approach.';
    }
  }
  
  private recommendNextActions(bugData: BugData[], usageData: UsageData[]): string {
    const recommendations = [];
    
    // If certain categories still have bugs
    const bugCategories = this.getBugCategories(bugData);
    for (const [category, count] of Object.entries(bugCategories)) {
      if (count >= 2) {
        recommendations.push(`- Focus testing on "${category}" (${count} remaining bugs)`);
      }
    }
    
    // If certain skills underused
    const skillUsage = this.getSkillUsage(usageData);
    for (const [skill, count] of Object.entries(skillUsage)) {
      if (count === 0) {
        recommendations.push(`- Test unused skill: ${skill}`);
      }
    }
    
    return recommendations.join('\n') || '- Continue current training approach';
  }
}
```

## Measuring Success

### Quality Metrics

Track these metrics to assess agent quality:

```typescript
interface QualityMetrics {
  // Effectiveness
  firstTrySuccessRate: number;      // % of prompts that work without revision
  averageRevisionsPerTask: number;  // How many times users need to revise
  
  // Efficiency  
  averageTokensPerTask: number;     // Context usage optimization
  averageTimeToComplete: number;    // Speed of task completion
  
  // Reliability
  errorRate: number;                // % of responses with errors
  commonErrorTypes: Record<string, number>;
  
  // User Satisfaction (if collecting feedback)
  userRating: number;               // 1-5 scale
  wouldUseAgain: number;            // % who would use again
}

class QualityTracker {
  async calculateMetrics(sessionData: SessionData[]): Promise<QualityMetrics> {
    const totalTasks = sessionData.reduce((sum, s) => sum + s.tasksCompleted, 0);
    const totalRevisions = sessionData.reduce((sum, s) => sum + s.revisions, 0);
    const totalErrors = sessionData.reduce((sum, s) => sum + s.errors.length, 0);
    
    return {
      firstTrySuccessRate: ((totalTasks - totalRevisions) / totalTasks) * 100,
      averageRevisionsPerTask: totalRevisions / totalTasks,
      averageTokensPerTask: this.calculateAverageTokens(sessionData),
      averageTimeToComplete: this.calculateAverageTime(sessionData),
      errorRate: (totalErrors / totalTasks) * 100,
      commonErrorTypes: this.categorizeErrors(sessionData),
      userRating: await this.collectUserRatings(),
      wouldUseAgain: await this.collectUsageIntent()
    };
  }
  
  isReadyForProduction(metrics: QualityMetrics): boolean {
    const thresholds = {
      firstTrySuccessRate: 80,      // 80%+ work on first try
      averageRevisionsPerTask: 1.5, // Less than 1.5 revisions avg
      errorRate: 10,                // Less than 10% error rate
      userRating: 4.0               // 4/5 or higher satisfaction
    };
    
    const passes = [
      metrics.firstTrySuccessRate >= thresholds.firstTrySuccessRate,
      metrics.averageRevisionsPerTask <= thresholds.averageRevisionsPerTask,
      metrics.errorRate <= thresholds.errorRate,
      metrics.userRating >= thresholds.userRating
    ];
    
    return passes.every(p => p); // All thresholds must pass
  }
}
```

### Milestone Checklist

Use this to track training progress:

```markdown
## Training Milestones

### Milestone 1: Basic Functionality (5 apps built)
- [ ] Core CRUD operations work reliably
- [ ] Connection management handled correctly
- [ ] Error handling present in all examples
- [ ] First-time success rate > 50%

### Milestone 2: Pattern Consistency (10 apps built)
- [ ] Naming conventions applied consistently
- [ ] Relationship queries working correctly
- [ ] UI integration patterns established
- [ ] First-time success rate > 70%

### Milestone 3: Edge Case Coverage (15 apps built)
- [ ] Pagination implemented correctly
- [ ] Offline behavior handled
- [ ] Complex filters work as expected
- [ ] First-time success rate > 80%

### Milestone 4: Production Ready (20+ apps built)
- [ ] Error rate < 10%
- [ ] Average revisions < 1.5 per task
- [ ] User satisfaction > 4/5
- [ ] All common patterns documented
- [ ] Context optimization applied
```

## Best Practices Summary

### Do's ✅

1. **Build Many Apps** - Quantity leads to discovering edge cases
2. **Read Every Reasoning** - Understand how LLM thinks
3. **Log Every Bug** - Structured tracking enables pattern recognition
4. **Update Incrementally** - Small, focused changes are easier to validate
5. **Version Everything** - Track prompt/skill changes like code changes
6. **Measure Progress** - Use metrics to know when you're improving
7. **Test Diverse Scenarios** - Different use cases reveal different issues

### Don'ts ❌

1. **Don't Wait for Perfection** - Start testing with basic versions
2. **Don't Skip Reasoning Analysis** - It reveals root causes
3. **Don't Make Large Changes** - Hard to identify what fixed the issue
4. **Don't Ignore Metrics** - You can't improve what you don't measure
5. **Don't Repeat Tests** - Once a pattern works, move to new scenarios
6. **Don't Train in Isolation** - Get feedback from other users when possible

## Common Training Patterns

### Pattern 1: The "Obvious" Mistake

**Scenario:** You think you made it clear, but LLM keeps making the same mistake

**Example:** Table name casing mentioned in system prompt, still gets wrong

**Solution:** 
- Use stronger language ("CRITICAL" vs "IMPORTANT")
- Add explicit examples with ❌ and ✅ symbols
- Reinforce in multiple places (system prompt + skill + instruction)
- Check if conflicting information exists elsewhere

### Pattern 2: The Context Dependency

**Scenario:** Works in some contexts but not others

**Example:** Connection checks work for create() but not for query()

**Solution:**
- Ensure ALL examples show the pattern, not just some
- Create dedicated skill for cross-cutting concerns
- Add negative constraint: "Do NOT assume X"
- Test specifically for missing context

### Pattern 3: The Over-Correction

**Scenario:** Fix one issue, create another

**Example:** Emphasize vanilla JS so strongly that LLM avoids useful features

**Solution:**
- Balance constraints with positive guidance
- Show what IS allowed, not just what isn't
- Test after each change to catch new issues
- Keep change log to understand trade-offs

### Pattern 4: The Hidden Assumption

**Scenario:** LLM makes assumption you didn't know about

**Example:** Assumes TypeScript available because project has .ts files

**Solution:**
- Read reasoning to surface assumptions
- Be explicit about what seems obvious to you
- Test with varied prompts to expose assumptions
- Document assumptions in instruction.md

## Timeline Expectations

Realistic timeline for training a domain-specific agent:

| Phase | Duration | Apps Built | Expected Quality |
|-------|----------|------------|------------------|
| **Initial Build** | 1-2 days | 0 | Basic functionality, many bugs |
| **Early Testing** | 1 week | 5-7 | 50-60% first-time success |
| **Pattern Recognition** | 2 weeks | 10-12 | 70-80% first-time success |
| **Refinement** | 2-3 weeks | 15-20 | 80-90% first-time success |
| **Production Ready** | 4-6 weeks | 20+ | 90%+ first-time success, <10% error rate |

**Total Time:** 4-8 weeks of active development and testing

**Key Insight:** The author's usage graph showed spikes on days they were testing/learning. Expect intensive usage during training phases.

## Next Steps After Training

Once your agent reaches production quality:

1. **Document the Process** - Share learnings with team
2. **Set Up Monitoring** - Continue tracking quality in production
3. **Plan Maintenance** - Schedule periodic reviews and updates
4. **Gather User Feedback** - Real users will find new edge cases
5. **Iterate Continuously** - Even production agents need occasional updates

**Remember:** Training never truly ends. New SDK versions, new patterns, and new use cases will require ongoing maintenance and improvement.
