# Context Optimization

Managing context limits is critical for AI coding agents, especially when working with accounts that have restricted token allowances. This guide covers strategies to minimize context usage while maintaining agent effectiveness.

## Understanding the Problem

### The Context Stack Multiplier

Every LLM request sends the complete prompt stack:

```
Request 1 (Initial):
├── Model System Prompt: 500 tokens
├── Application System Prompt: 300 tokens  
├── Instruction.md: 400 tokens
├── Selected Skills: 600 tokens
└── User Prompt: 200 tokens
    Total: 2,000 tokens

Request 2 (After tool call):
├── Model System Prompt: 500 tokens ← Sent AGAIN
├── Application System Prompt: 300 tokens ← Sent AGAIN
├── Instruction.md: 400 tokens ← Sent AGAIN
├── Selected Skills: 600 tokens ← Sent AGAIN
├── Previous Messages: 200 tokens
├── Tool Result: 150 tokens
└── Follow-up Prompt: 100 tokens
    Total: 2,750 tokens

Request 3 (Second tool call):
├── All prompts again: 1,800 tokens ← Sent AGAIN
├── Message History: 450 tokens
├── Tool Results: 300 tokens
└── Current Prompt: 100 tokens
    Total: 3,650 tokens
```

**Key Insight:** System prompts are sent with EVERY request, not just the first one. This multiplies their impact dramatically.

### Real-World Impact

For a typical coding session with 20-30 back-and-forth messages:

| Component | Tokens per Request | × Requests | Total Tokens Sent |
|-----------|-------------------|------------|-------------------|
| System Prompts | 800 | 25 | 20,000 |
| Instructions | 400 | 25 | 10,000 |
| Skills | 600 | 25 | 15,000 |
| Messages/Tools | 200 avg | 25 | 5,000 |
| **Total** | | | **50,000 tokens** |

A simple session can easily exceed 40k-80k token limits on restricted accounts.

## Strategy 1: Minimize Prompt Content

### System Prompt Optimization

#### ❌ Before (Verbose)

```markdown
# System Prompt

Welcome! You are an AI assistant that helps with coding tasks. This document 
contains important instructions about how you should behave and what tools 
you have available. Please read these carefully and follow them in all 
your responses.

## About Your Role

Your role is to help developers write code for Power Platform Code Apps. 
This is a specialized environment that uses vanilla JavaScript and has a 
specific SDK. It's important that you understand this is not a standard 
web development environment, and you should not suggest patterns from 
other frameworks like React or Angular.

## What You Should Do

When helping with code, you should always make sure to reference the 
Code App SDK documentation and use only features that are supported in 
the Code Apps runtime environment. This means avoiding modern ES6+ 
features that might not be compatible, and sticking to vanilla JavaScript 
patterns that work reliably.
```

**Token Count:** ~200 tokens

#### ✅ After (Concise)

```markdown
# System Prompt

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

**Token Count:** ~120 tokens  
**Savings:** 80 tokens per request = 2,000 tokens over 25 requests

### Instruction.md Optimization

#### Use Tables Instead of Prose

```markdown
## Naming Conventions

| Element | Format | Example |
|---------|--------|---------|
| Files | kebab-case | `user-profile.js` |
| Functions | camelCase | `fetchUserData()` |
| Constants | UPPER_SNAKE_CASE | `API_ENDPOINT` |
| Variables | camelCase | `userData` |
| Classes | PascalCase | `UserService` |
```

**Savings:** 50-100 tokens vs prose descriptions

#### Remove Meta-Talk

```markdown
❌ BEFORE:
## About This Document

This document contains instructions for our project. These instructions 
are important and should be followed by the AI assistant when working 
on this codebase. The team has decided on these conventions after much 
discussion and they help us maintain consistency across the project.

✅ AFTER:
## Conventions
- Files: kebab-case
- Functions: camelCase  
- Constants: UPPER_SNAKE_CASE
```

**Savings:** 60 tokens, zero information loss

### Skill File Optimization

#### Consolidate Examples

```markdown
❌ BEFORE (Multiple similar examples):

### Creating Records - Example 1
```javascript
const account = await sdk.dataverse.create("account", {
  name: "Contoso"
});
```

### Creating Records - Example 2
```javascript
const contact = await sdk.dataverse.create("contact", {
  fullname: "John Doe"
});
```

### Creating Records - Example 3
```javascript
const opportunity = await sdk.dataverse.create("opportunity", {
  subject: "New Deal"
});
```

✅ AFTER (One parameterized example):

### Creating Records
```javascript
// Create any record type
async function createRecord(entityType, data) {
  try {
    const result = await sdk.dataverse.create(entityType, data);
    sdk.ui.showToast(`${entityType} created successfully`);
    return result;
  } catch (error) {
    sdk.ui.showToast(`Error: ${error.message}`);
    throw error;
  }
}

// Usage examples:
createRecord("account", { name: "Contoso" });
createRecord("contact", { fullname: "John Doe" });
createRecord("opportunity", { subject: "New Deal" });
```
```

**Savings:** 100-150 tokens per skill

#### Use Inline Comments Instead of Explanations

```markdown
❌ BEFORE:
First, you need to check if the connection is active. This is important 
because all Dataverse operations require an active connection. If the 
connection is not active, you should prompt the user to connect.

```javascript
if (!sdk.isConnectionActive('dataverse')) {
  sdk.ui.showToast('Please connect to Dataverse first');
  return;
}
```

✅ AFTER:
```javascript
// Check connection (required for all Dataverse operations)
if (!sdk.isConnectionActive('dataverse')) {
  sdk.ui.showToast('Please connect to Dataverse first');
  return;
}
```
```

**Savings:** 40-50 tokens per pattern

## Strategy 2: Selective Skill Loading

### Keyword-Based Pre-Filtering

```typescript
interface SkillMetadata {
  name: string;
  keywords: string[];
  description: string;
  tokenCount: number;
}

async function prefilterSkills(userPrompt: string, allSkills: SkillMetadata[]): Promise<SkillMetadata[]> {
  const promptKeywords = extractKeywords(userPrompt.toLowerCase());
  
  return allSkills.filter(skill => {
    // Check if any skill keywords match prompt keywords
    const hasKeywordMatch = skill.keywords.some(skillKeyword => 
      promptKeywords.some(promptKeyword => 
        skillKeyword.includes(promptKeyword) || promptKeyword.includes(skillKeyword)
      )
    );
    
    // Also check description for matches
    const hasDescriptionMatch = promptKeywords.some(keyword =>
      skill.description.toLowerCase().includes(keyword)
    );
    
    return hasKeywordMatch || hasDescriptionMatch;
  });
}

// Usage
const allSkills = await loadAllSkillMetadata(); // Lightweight metadata only
const candidates = prefilterSkills(userPrompt, allSkills);
// Load full content only for matched skills
const selectedSkills = await loadFullSkillContent(candidates.map(s => s.name));
```

**Benefit:** Avoids loading irrelevant skills at all

### LLM-Based Selection from Metadata

```typescript
async function selectSkillsWithLLM(userPrompt: string, skillMetadata: SkillMetadata[]): Promise<string[]> {
  // Create compact skill list (metadata only, ~20 tokens per skill)
  const skillList = skillMetadata.map(s => 
    `${s.name}: ${s.description} [${s.tokenCount} tokens]`
  ).join('\n');
  
  const selectionPrompt = `
Available Skills (${skillMetadata.length} total):
${skillList}

User Request: "${userPrompt}"

Select ONLY the most relevant skills (max 3). Consider:
1. What domain knowledge is needed?
2. Which skills provide necessary patterns?
3. Minimize total token count while covering requirements

Return JSON array of skill names: ["skill-1", "skill-2"]
  `;
  
  // This selection request uses ~200 tokens vs loading all skills (~2000 tokens)
  const response = await llm.chat(selectionPrompt);
  const selectedNames = JSON.parse(response.trim());
  
  // Now load only selected skills
  return await loadFullSkillContent(selectedNames);
}
```

**Token Savings:** 
- Loading metadata: 20 tokens × 20 skills = 400 tokens
- Loading all full skills: 600 tokens × 20 skills = 12,000 tokens
- Selection via LLM: 200 tokens
- Loading 3 selected skills: 600 tokens × 3 = 1,800 tokens
- **Total with optimization:** 2,400 tokens vs 12,400 tokens
- **Savings:** 10,000 tokens per session

### Progressive Skill Loading

```typescript
async function loadSkillsProgressively(userPrompt: string, contextBudget: number): Promise<string[]> {
  const allSkills = await loadAllSkillMetadata();
  const selectedNames = await selectSkillsWithLLM(userPrompt, allSkills);
  
  const loadedSkills = [];
  let currentTokenCount = countTokens(systemPrompt + applicationPrompt + instructions + userPrompt);
  
  // Load skills one by one until budget exhausted
  for (const skillName of selectedNames) {
    const skillMetadata = allSkills.find(s => s.name === skillName);
    
    // Check if we have room for this skill
    if (currentTokenCount + skillMetadata.tokenCount > contextBudget * 0.7) {
      console.log(`Skipping ${skillName}: would exceed context budget`);
      break;
    }
    
    // Load skill content
    const skillContent = await loadSkillContent(skillName);
    loadedSkills.push(skillContent);
    currentTokenCount += skillMetadata.tokenCount;
  }
  
  return loadedSkills;
}
```

**Benefit:** Guarantees staying within context limits while loading most important skills first

## Strategy 3: File Tree Optimization

### Tight File Trees

Instead of sending entire directory structures, send only relevant files:

```typescript
❌ BEFORE (Wide file tree):

Project Structure:
/src/
  /components/
    button.js (2.1 KB)
    form.js (3.4 KB)
    modal.js (2.8 KB)
    table.js (4.2 KB)
    card.js (1.9 KB)
  /utils/
    api.js (5.6 KB)
    validation.js (3.2 KB)
    formatting.js (2.1 KB)
    auth.js (4.8 KB)
  /services/
    dataverse.js (8.4 KB)
    sharepoint.js (6.2 KB)
    custom-api.js (4.1 KB)
  app.js (3.7 KB)
  index.html (1.2 KB)
  styles.css (2.4 KB)

Total: ~47 KB of file tree content

✅ AFTER (Focused file tree):

Relevant Files for "Create user form":
/src/components/
  form.js (3.4 KB) ← Similar component pattern
/src/utils/
  validation.js (3.2 KB) ← Needed for form validation
/src/services/
  dataverse.js (8.4 KB) ← Likely data source
```

**Savings:** 30+ KB per request

### Smart File Selection

```typescript
async function selectRelevantFiles(userPrompt: string, workspaceFolder: string): Promise<string[]> {
  const allFiles = await getAllFiles(workspaceFolder);
  const keywords = extractKeywords(userPrompt);
  
  // Score each file based on relevance
  const scoredFiles = allFiles.map(file => ({
    path: file.path,
    score: calculateRelevanceScore(file, keywords)
  }));
  
  // Sort by score and take top N
  const relevantFiles = scoredFiles
    .sort((a, b) => b.score - a.score)
    .slice(0, 10)
    .map(f => f.path);
  
  return relevantFiles;
}

function calculateRelevanceScore(file: File, keywords: string[]): number {
  let score = 0;
  
  // Bonus for filename matches
  for (const keyword of keywords) {
    if (file.name.toLowerCase().includes(keyword)) {
      score += 10;
    }
  }
  
  // Bonus for file type relevance
  const typeScores = {
    '.js': 5,
    '.ts': 5,
    '.jsx': 3,
    '.tsx': 3,
    '.html': 2,
    '.css': 1
  };
  score += typeScores[file.extension] || 0;
  
  // Bonus for location (src/ > tests/ > docs/)
  const locationScores = {
    'src/': 5,
    'lib/': 4,
    'components/': 3,
    'utils/': 3,
    'tests/': 1,
    'docs/': 0
  };
  for (const [location, locScore] of Object.entries(locationScores)) {
    if (file.path.includes(location)) {
      score += locScore;
    }
  }
  
  return score;
}
```

## Strategy 4: History Management

### Decision Log Approach

Instead of keeping full conversation history, maintain a structured decision log:

```typescript
interface DecisionLogEntry {
  task: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  decisions: string[];
  filesModified: string[];
  keyLearnings: string[];
  timestamp: Date;
}

class DecisionLogger {
  private logPath = '.agents/decision-log.md';
  
  async beginTask(task: string): Promise<void> {
    const entry: DecisionLogEntry = {
      task,
      status: 'pending',
      decisions: [],
      filesModified: [],
      keyLearnings: [],
      timestamp: new Date()
    };
    
    await this.appendEntry(entry);
  }
  
  async recordDecision(decision: string): Promise<void> {
    const current = await this.getCurrentEntry();
    current.decisions.push(decision);
    await this.saveCurrentEntry(current);
  }
  
  async completeTask(): Promise<void> {
    const current = await this.getCurrentEntry();
    current.status = 'completed';
    
    // Clear conversation history, keep only decision log
    await this.clearConversationHistory();
    
    // Summarize for next session
    const summary = this.createSummary(current);
    await this.appendToContext(summary);
  }
  
  private async clearConversationHistory(): Promise<void> {
    // Remove tool calls and reasoning from context
    // Keep only final results and decisions
    console.log('Cleared conversation history, saved decision log');
  }
  
  private createSummary(entry: DecisionLogEntry): string {
    return `
## Completed: ${entry.task}

**Decisions Made:**
${entry.decisions.map(d => `- ${d}`).join('\n')}

**Files Modified:**
${entry.filesModified.map(f => `- ${f}`).join('\n')}

**Key Learnings:**
${entry.keyLearnings.map(l => `- ${l}`).join('\n')}
    `.trim();
  }
}
```

### Context After History Clearing

```typescript
// Before clearing (3,650 tokens):
Full conversation with all tool calls, reasoning, back-and-forth

// After clearing (800 tokens):
System Prompts: 800 tokens
Decision Log Summary: 200 tokens
Current Task Prompt: 100 tokens
Total: 1,100 tokens

Savings: 2,550 tokens per major task completion
```

### Compact History Summarization

Alternative to decision logs: ask LLM to summarize history periodically:

```typescript
async function compactHistory(messages: Message[], maxTokens: number): Promise<Message[]> {
  // Check if history exceeds threshold
  const currentTokens = countTokens(messages.map(m => m.content).join('\n'));
  
  if (currentTokens < maxTokens * 0.6) {
    return messages; // Still under limit, no compaction needed
  }
  
  // Ask LLM to summarize older messages
  const oldMessages = messages.slice(0, Math.floor(messages.length * 0.7));
  const newMessages = messages.slice(Math.floor(messages.length * 0.7));
  
  const summaryPrompt = `
Summarize this conversation history concisely. Preserve:
- Key decisions made
- Important technical details
- File paths and names
- Error messages and solutions
- User requirements and constraints

Remove:
- Small talk and pleasantries
- Redundant explanations
- Intermediate reasoning steps
- Successful tool call confirmations

Conversation to summarize:
${oldMessages.map(m => `${m.role}: ${m.content}`).join('\n\n')}

Provide a concise summary (max 200 words):
  `;
  
  const summary = await llm.chat(summaryPrompt);
  
  // Replace old messages with summary
  return [
    { role: 'system', content: '[Summarized previous conversation]\n\n' + summary },
    ...newMessages
  ];
}
```

**Trade-off:** Some detail loss, but maintains key information

## Strategy 5: Task-Based Context Isolation

### Break Projects into Independent Tasks

Instead of one long conversation, break work into discrete tasks with isolated contexts:

```typescript
class TaskManager {
  async executeTask(taskDefinition: TaskDefinition): Promise<TaskResult> {
    // Create fresh context for this task
    const taskContext = await this.buildTaskContext(taskDefinition);
    
    // Execute task with isolated context
    const result = await this.runTaskInIsolation(taskContext);
    
    // Save results and clear context
    await this.saveResults(result);
    await this.clearContext();
    
    return result;
  }
  
  private async buildTaskContext(task: TaskDefinition): Promise<Context> {
    return {
      systemPrompt: this.systemPrompt,
      applicationPrompt: this.applicationPrompt,
      instructions: await this.loadRelevantInstructions(task.type),
      skills: await this.selectSkillsForTask(task.type),
      files: await this.loadRelevantFiles(task.files),
      taskDescription: task.description
    };
  }
  
  private async runTaskInIsolation(context: Context): Promise<TaskResult> {
    // Run LLM with isolated context
    // No history from previous tasks
    // Fresh start each time
    const result = await llm.chat(this.buildPrompt(context));
    
    return this.parseResult(result);
  }
}

// Usage
const tasks = [
  { type: 'create-component', files: ['requirements.md'], description: 'Create user profile component' },
  { type: 'add-validation', files: ['user-profile.js'], description: 'Add form validation' },
  { type: 'connect-api', files: ['config/api.json'], description: 'Connect to Dataverse' }
];

for (const task of tasks) {
  const result = await taskManager.executeTask(task);
  console.log(`Task completed: ${task.description}`);
}
```

**Benefits:**
- Each task uses minimal context (~1,000-2,000 tokens)
- No history accumulation
- Easier to retry failed tasks
- Parallel execution possible

**Trade-offs:**
- Tasks can't reference previous task reasoning
- Need decision log to maintain continuity
- More overhead managing task boundaries

## Monitoring and Measurement

### Token Counter Utility

```typescript
class TokenCounter {
  private counts = {
    systemPrompt: 0,
    applicationPrompt: 0,
    instructions: 0,
    skills: 0,
    messages: 0,
    total: 0
  };
  
  countAndLog(promptStack: PromptStack): void {
    this.counts.systemPrompt = countTokens(promptStack.systemPrompt);
    this.counts.applicationPrompt = countTokens(promptStack.applicationPrompt);
    this.counts.instructions = countTokens(promptStack.instructions);
    this.counts.skills = promptStack.skills.reduce((sum, s) => sum + countTokens(s), 0);
    this.counts.messages = countTokens(promptStack.userPrompt);
    this.counts.total = Object.values(this.counts).slice(0, -1).reduce((a, b) => a + b, 0);
    
    console.log('Token Breakdown:');
    console.log(`  System Prompt: ${this.counts.systemPrompt}`);
    console.log(`  Application Prompt: ${this.counts.applicationPrompt}`);
    console.log(`  Instructions: ${this.counts.instructions}`);
    console.log(`  Skills: ${this.counts.skills}`);
    console.log(`  Messages: ${this.counts.messages}`);
    console.log(`  TOTAL: ${this.counts.total}`);
    
    if (this.counts.total > this.limit * 0.8) {
      console.warn('⚠️ Approaching context limit!');
    }
  }
  
  getOptimizationSuggestions(): string[] {
    const suggestions = [];
    
    if (this.counts.systemPrompt > 300) {
      suggestions.push('System prompt exceeds 300 tokens. Consider condensing.');
    }
    
    if (this.counts.instructions > 500) {
      suggestions.push('Instructions exceed 500 tokens. Use tables, remove meta-talk.');
    }
    
    if (this.counts.skills > 1000) {
      suggestions.push('Skills total exceeds 1000 tokens. Use selective loading.');
    }
    
    return suggestions;
  }
}
```

### Session Analytics

```typescript
class ContextAnalytics {
  private sessionData = {
    totalRequests: 0,
    totalTokensSent: 0,
    averageTokensPerRequest: 0,
    peakContextSize: 0,
    optimizationSavings: 0
  };
  
  trackRequest(requestTokens: number, optimizationsApplied: number): void {
    this.sessionData.totalRequests++;
    this.sessionData.totalTokensSent += requestTokens;
    this.sessionData.optimizationSavings += optimizationsApplied;
    
    this.sessionData.peakContextSize = Math.max(
      this.sessionData.peakContextSize,
      requestTokens
    );
    
    this.sessionData.averageTokensPerRequest = 
      this.sessionData.totalTokensSent / this.sessionData.totalRequests;
  }
  
  getReport(): string {
    return `
## Context Usage Report

**Session Statistics:**
- Total Requests: ${this.sessionData.totalRequests}
- Total Tokens Sent: ${this.sessionData.totalTokensSent.toLocaleString()}
- Average per Request: ${Math.round(this.sessionData.averageTokensPerRequest).toLocaleString()}
- Peak Context Size: ${this.sessionData.peakContextSize.toLocaleString()}

**Optimization Impact:**
- Tokens Saved: ${this.sessionData.optimizationSavings.toLocaleString()}
- Efficiency: ${((this.sessionData.optimizationSavings / this.sessionData.totalTokensSent) * 100).toFixed(1)}%

**Recommendations:**
${this.getRecommendations()}
    `.trim();
  }
  
  private getRecommendations(): string {
    const recommendations = [];
    
    if (this.sessionData.averageTokensPerRequest > 2000) {
      recommendations.push('- High average tokens. Implement selective skill loading.');
    }
    
    if (this.sessionData.peakContextSize > 5000) {
      recommendations.push('- Peak context exceeds 5k. Consider task-based isolation.');
    }
    
    if (this.sessionData.optimizationSavings < this.sessionData.totalTokensSent * 0.2) {
      recommendations.push('- Low optimization savings. Review prompt content for bloat.');
    }
    
    return recommendations.join('\n') || '- Context usage is well optimized!';
  }
}
```

## Optimization Checklist

Before deploying your agent, verify these optimizations:

### Content Optimization
- [ ] System prompt under 300 tokens
- [ ] Instructions use tables, not prose
- [ ] No meta-talk or explanations of the document itself
- [ ] Skills have parameterized examples, not multiple similar ones
- [ ] Inline comments instead of separate explanations
- [ ] Removed redundant information across layers

### Loading Optimization
- [ ] Skills loaded selectively based on task
- [ ] Metadata-based prefiltering implemented
- [ ] LLM selects from skill descriptions, not full content
- [ ] Progressive loading respects context budget
- [ ] File trees focused on relevant files only

### History Management
- [ ] Decision log captures key information
- [ ] Conversation history cleared after task completion
- [ ] Or: History compaction implemented
- [ ] Task-based isolation for major features

### Monitoring
- [ ] Token counter logs breakdown per request
- [ ] Analytics track session statistics
- [ ] Alerts when approaching limits
- [ ] Optimization suggestions generated automatically

## Expected Results

With all optimizations applied:

| Scenario | Before Optimization | After Optimization | Savings |
|----------|-------------------|-------------------|---------|
| Simple task (5 requests) | 10,000 tokens | 3,500 tokens | 65% |
| Medium session (20 requests) | 40,000 tokens | 12,000 tokens | 70% |
| Complex project (50 requests) | 100,000 tokens | 28,000 tokens | 72% |

**Impact:** Can work within 40k token limits instead of requiring 100k+ token allowances.

## Next Steps

After optimizing context usage:

1. **Establish Training Workflow** - See [Training Workflow](05-training-workflow.md)
2. **Test with Real Projects** - Measure actual token usage
3. **Iterate on Optimizations** - Continue refining based on analytics
