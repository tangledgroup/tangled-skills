# Implementation Guide

This guide covers building the three core components that give custom AI coding agents their advantage over generic assistants: simplified UI-based CLI commands, custom system prompts, and skill files.

## Component 1: Simplified UI-Based CLI Commands

### Why Abstract CLI Commands

Complex CLI tools create friction for users and increase error rates. Abstraction through UI provides:

1. **Reduced Cognitive Load** - Button clicks instead of memorizing flags
2. **Error Prevention** - Validation before execution
3. **State Management** - Automatically update config files
4. **Progress Feedback** - Visual indicators during long operations
5. **Consistent Workflows** - Enforce correct command sequences

### Pipeline-Based Command Design

Instead of individual commands, design as a pipeline where each step prepares for the next:

```
Setup → Authenticate → Select Environment → Create Connections → Deploy
  ↓          ↓                  ↓                   ↓            ↓
Initialize   Validate         Update Config       Analyze Code   Publish
Files        Token            Files               Dependencies   to Prod
```

### Implementation Example: Power Platform CLI Pipeline

#### Step 1: Setup CodeApp JS Files

```typescript
// src/commands/setup.ts
import * as fs from 'fs';
import * as path from 'path';

export async function setupCodeAppJS(workspaceFolder: string): Promise<void> {
  // Create project structure
  const directories = ['src', 'src/components', 'src/utils', 'config'];
  directories.forEach(dir => {
    fs.mkdirSync(path.join(workspaceFolder, dir), { recursive: true });
  });
  
  // Initialize config files
  const packageJson = {
    name: path.basename(workspaceFolder),
    version: '1.0.0',
    scripts: {
      dev: 'pac start',
      build: 'pac build',
      deploy: 'pac deploy'
    },
    dependencies: {
      '@microsoft/powerapps-codeapp-sdk': '^1.0.0'
    }
  };
  
  fs.writeFileSync(
    path.join(workspaceFolder, 'package.json'),
    JSON.stringify(packageJson, null, 2)
  );
  
  // Create initial instruction.md for AI agent
  const instruction = `# Code App JS Project
  
## Tech Stack
- Vanilla JavaScript (no frameworks)
- Power Platform Code App SDK
- PAC CLI for deployment

## File Structure
- src/ - Application code
- src/components/ - Reusable UI components  
- src/utils/ - Helper functions
- config/ - Environment configurations

## Deployment
Use the extension buttons to deploy, not CLI commands directly.
`;
  
  fs.writeFileSync(path.join(workspaceFolder, 'instruction.md'), instruction);
  
  vscode.window.showInformationMessage('Code App JS project initialized');
}
```

#### Step 2: Authenticate with Tenant

```typescript
// src/commands/authenticate.ts
import { authentication, window } from 'vscode';

export async function authenticateWithTenant(): Promise<boolean> {
  // Check if PAC CLI is installed
  const pacVersion = await checkPACInstalled();
  if (!pacVersion) {
    const install = await window.showWarningMessage(
      'Power Apps CLI not found. Install now?',
      'Install',
      'Cancel'
    );
    
    if (install === 'Install') {
      return await installPACCLI();
    }
    return false;
  }
  
  // Execute PAC auth command
  const terminal = window.createTerminal('Power Apps Auth');
  terminal.sendText('pac auth login');
  terminal.show(true);
  
  // Wait for completion (user confirms in terminal)
  const confirm = await window.showInputBox({
    prompt: 'Press Enter when authentication completes',
    placeHolder: 'Authentication completed...'
  });
  
  if (confirm) {
    // Store auth status
    const config = workspace.getConfiguration('codeappjsplus');
    await config.update('authenticated', true, ConfigurationTarget.Global);
    
    window.showInformationMessage('Authentication successful');
    return true;
  }
  
  return false;
}

async function checkPACInstalled(): Promise<string | null> {
  const { execSync } = require('child_process');
  try {
    const version = execSync('pac --version', { encoding: 'utf-8' });
    return version.trim();
  } catch (error) {
    return null;
  }
}
```

#### Step 3: List and Select Environment

```typescript
// src/commands/selectEnvironment.ts
import { window, workspace } from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface Environment {
  id: string;
  name: string;
  url: string;
  type: 'Production' | 'Development' | 'Sandbox';
}

export async function selectEnvironment(): Promise<Environment | undefined> {
  // Fetch environments using PAC CLI
  const { execSync } = require('child_process');
  const output = execSync('pac env list --output json', { encoding: 'utf-8' });
  const environments: Environment[] = JSON.parse(output);
  
  // Create quick pick items
  const picks = environments.map(env => ({
    label: env.name,
    description: env.type,
    detail: env.url,
    environment: env
  }));
  
  const selected = await window.showQuickPick(picks, {
    placeHolder: 'Select Power Platform environment',
    matchOnDescription: true,
    matchOnDetail: true
  });
  
  if (!selected) {
    return undefined;
  }
  
  // Update config file
  const configPath = path.join(getWorkspaceFolder(), 'config', 'environment.json');
  fs.writeFileSync(configPath, JSON.stringify({
    environmentId: selected.environment.id,
    environmentName: selected.environment.name,
    environmentUrl: selected.environment.url,
    lastUpdated: new Date().toISOString()
  }, null, 2));
  
  // Also update VS Code settings
  const config = workspace.getConfiguration('codeappjsplus');
  await config.update('environment', selected.environment.id, ConfigurationTarget.Workspace);
  
  window.showInformationMessage(`Selected environment: ${selected.environment.name}`);
  return selected.environment;
}
```

#### Step 4: Create Connections Based on Code Analysis

```typescript
// src/commands/createConnections.ts
import { workspace } from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

interface ConnectionRequirement {
  type: 'Dataverse' | 'SharePoint' | 'SQL' | 'Custom API';
  name: string;
  configuration: Record<string, unknown>;
}

export async function createConnections(): Promise<void> {
  // Analyze code to find connection requirements
  const requirements = await analyzeCodeForConnections();
  
  if (requirements.length === 0) {
    window.showInformationMessage('No connections required based on current code');
    return;
  }
  
  // Show what will be created
  const summary = requirements.map(r => `${r.type}: ${r.name}`).join('\n');
  const confirm = await window.showWarningMessage(
    `Create these connections?\n\n${summary}`,
    'Create',
    'Cancel'
  );
  
  if (confirm !== 'Create') {
    return;
  }
  
  // Create each connection
  for (const requirement of requirements) {
    const success = await createSingleConnection(requirement);
    
    if (success) {
      window.showInformationMessage(`Created: ${requirement.name}`);
    } else {
      window.showErrorMessage(`Failed to create: ${requirement.name}`);
    }
  }
}

async function analyzeCodeForConnections(): Promise<ConnectionRequirement[]> {
  const requirements: ConnectionRequirement[] = [];
  
  // Scan JavaScript files for SDK calls
  const jsFiles = await findFiles('**/*.js');
  
  for (const file of jsFiles) {
    const content = fs.readFileSync(file.fsPath, 'utf-8');
    
    // Look for Dataverse calls
    if (content.includes('sdk.dataverse.') || content.includes('msdyn.')) {
      requirements.push({
        type: 'Dataverse',
        name: 'Dataverse Connection',
        configuration: {
          autoCreate: true
        }
      });
    }
    
    // Look for SharePoint calls
    if (content.includes('sdk.sharePoint.') || content.includes('SP.RequestExecutor')) {
      requirements.push({
        type: 'SharePoint',
        name: 'SharePoint Connection',
        configuration: {
          siteUrl: promptForSharePointSite()
        }
      });
    }
    
    // Look for custom API calls
    const apiMatches = content.match(/fetch\(['"]([^'"]+)['"]\)/g);
    if (apiMatches) {
      requirements.push({
        type: 'Custom API',
        name: 'Custom API Connections',
        configuration: {
          endpoints: apiMatches.map(m => m.extractURL())
        }
      });
    }
  }
  
  // Remove duplicates
  return requirements.filter(
    (req, index, self) => self.findIndex(r => r.type === req.type && r.name === req.name) === index
  );
}
```

#### Step 5: Deploy App

```typescript
// src/commands/deploy.ts
import { window, ProgressLocation } from 'vscode';

export async function deployApp(): Promise<void> {
  // Validate prerequisites
  const checks = [
    { name: 'Authentication', check: isAuthenticated },
    { name: 'Environment Selection', check: isEnvironmentSelected },
    { name: 'Connections', check: areConnectionsCreated }
  ];
  
  for (const check of checks) {
    if (!await check.check()) {
      window.showWarningMessage(`Deployment blocked: ${check.name} required`);
      return;
    }
  }
  
  // Execute deployment with progress
  await window.withProgress(
    {
      location: ProgressLocation.Notification,
      title: 'Deploying Code App...',
      cancellable: false
    },
    async (progress) => {
      progress.report({ message: 'Building application...' });
      await executeCommand('pac build');
      
      progress.report({ message: 'Validating package...' });
      await executeCommand('pac validate');
      
      progress.report({ message: 'Deploying to environment...' });
      await executeCommand('pac deploy --environment ${envId}');
      
      progress.report({ message: 'Publishing customizations...' });
      await executeCommand('pac publish');
    }
  );
  
  window.showInformationMessage('Deployment completed successfully!');
}

async function executeCommand(command: string): Promise<void> {
  const { execSync } = require('child_process');
  try {
    execSync(command, { stdio: 'inherit' });
  } catch (error) {
    throw new Error(`Command failed: ${command}`);
  }
}
```

### Button Integration in VS Code Sidebar

```typescript
// Create custom view with buttons
export function activate(context: ExtensionContext) {
  // Create tree data provider for sidebar
  const provider = new CommandTreeProvider();
  
  const view = window.createTreeView('codeappjsplus.commands', {
    treeDataProvider: provider,
    showCollapseAll: false
  });
  
  context.subscriptions.push(view);
}

class CommandTreeProvider implements TreeDataProvider<CommandTreeItem> {
  getTreeItem(element: CommandTreeItem): TreeItem {
    return element;
  }
  
  getChildren(): Thenable<CommandTreeItem[]> {
    return Promise.resolve([
      new CommandTreeItem(
        '🔧 Setup Project',
        TreeItemCollapsibleState.None,
        'codeappjsplus.setup'
      ),
      new CommandTreeItem(
        '🔐 Authenticate',
        TreeItemCollapsibleState.None,
        'codeappjsplus.authenticate'
      ),
      new CommandTreeItem(
        '🌍 Select Environment',
        TreeItemCollapsibleState.None,
        'codeappjsplus.selectEnvironment'
      ),
      new CommandTreeItem(
        ' 🔗 Create Connections',
        TreeItemCollapsibleState.None,
        'codeappjsplus.createConnections'
      ),
      new CommandTreeItem(
        '🚀 Deploy',
        TreeItemCollapsibleState.None,
        'codeappjsplus.deploy'
      )
    ]);
  }
}
```

## Component 2: Custom System Prompt

### Purpose of Custom System Prompts

The system prompt is your first line of defense against the LLM using its general training data incorrectly. For niche domains, this is critical.

### Key Elements of Effective System Prompts

#### 1. Domain Declaration

```
You are an expert in Power Platform Code Apps with vanilla JavaScript.
This is NOT a standard web development context.
```

#### 2. Critical Constraints (What NOT to Do)

```
CRITICAL CONSTRAINTS:
- Do NOT suggest React patterns or components
- Do NOT assume TypeScript is available
- Do NOT use modern ES6+ features not supported in Code Apps
- Do NOT suggest npm packages unless explicitly approved
- Do NOT assume standard browser APIs are available
```

#### 3. Correct Patterns (What TO Do)

```
CORRECT APPROACHES:
- Always use the Code App SDK for data operations
- Reference sdk.dataverse.*, sdk.sharePoint.*, etc.
- Use vanilla JavaScript with ES5 compatibility
- Check connection status before making calls
- Follow the patterns in /docs/patterns/
```

#### 4. Escalation Guidelines

```
WHEN UNSURE:
1. Ask clarifying questions about the specific requirement
2. Reference the Code App SDK documentation
3. Suggest checking existing code in the project for patterns
4. Do NOT guess or assume standard web development approaches
```

### Complete System Prompt Example

```markdown
# System Prompt: Power Platform Code Apps Expert

## Identity
You are an expert developer specializing in Power Platform Code Apps with vanilla JavaScript. You have deep knowledge of the Code App SDK, PAC CLI, and Power Platform integration patterns.

## CRITICAL: What This Is NOT
- This is NOT standard web development
- This is NOT React or any framework
- This is NOT TypeScript (despite .ts extensions sometimes used)
- This is NOT a regular browser environment

## Required Approach
1. ALWAYS reference the Code App SDK documentation before suggesting code
2. Use ONLY vanilla JavaScript features supported in the Code App runtime
3. Check for existing patterns in the project's /src/ directory
4. Validate that suggested APIs exist in the SDK
5. Consider connection requirements and authentication

## Common Pitfalls to Avoid
❌ Suggesting React hooks (useState, useEffect, etc.)
❌ Assuming TypeScript type checking or interfaces
❌ Using fetch() without SDK wrapper
❌ Importing npm packages not in approved list
❌ Standard DOM manipulation (use SDK UI components)
❌ Assuming all browser APIs are available

## Correct Patterns to Use
✅ sdk.dataverse.query(), sdk.dataverse.create(), etc.
✅ sdk.ui.showModal(), sdk.ui.showToast(), etc.
✅ Vanilla JavaScript with ES5 compatibility
✅ SDK authentication and connection management
✅ Error handling through SDK promise patterns
✅ Configuration through config/environment.json

## When You're Unsure
If a request is ambiguous or you're not certain about SDK support:
1. Ask for clarification about the specific requirement
2. Suggest checking the Code App SDK documentation
3. Recommend reviewing existing code in the project
4. Do NOT provide potentially incorrect code

## Response Format
- Provide complete, working code examples
- Include necessary imports from the SDK
- Add comments explaining Code App-specific behavior
- Mention any connection or configuration requirements
- Note any limitations or constraints

## Learning from Mistakes
If you make an error or receive feedback that code doesn't work:
1. Acknowledge the mistake
2. Update your understanding of the SDK
3. Document the correct approach for future reference
4. Do NOT repeat the same pattern
```

### Testing Your System Prompt

```typescript
// Test cases to validate system prompt effectiveness
const testCases = [
  {
    prompt: 'Create a user profile component',
    shouldNotInclude: ['React', 'useState', 'useEffect', 'function Component'],
    shouldInclude: ['sdk.ui', 'vanilla JavaScript', 'Code App SDK']
  },
  {
    prompt: 'How do I fetch data from an API?',
    shouldNotInclude: ['fetch(', 'axios.', 'XMLHttpRequest'],
    shouldInclude: ['sdk.dataverse', 'SDK method', 'connection']
  },
  {
    prompt: 'Add type safety to my functions',
    shouldNotInclude: ['TypeScript', 'interface', 'type ', 'TS '],
    ShouldInclude: ['JSDoc', 'comments', 'runtime validation']
  }
];

async function testSystemPrompt() {
  for (const testCase of testCases) {
    const response = await llm.chat(testCase.prompt);
    
    // Verify constraints
    for (const forbidden of testCase.shouldNotInclude) {
      if (response.includes(forbidden)) {
        console.error(`❌ Found forbidden pattern: ${forbidden}`);
      }
    }
    
    // Verify correct patterns
    const hasCorrect = testCase.shouldInclude.some(pattern => 
      response.includes(pattern)
    );
    
    if (!hasCorrect) {
      console.error('❌ Missing required patterns');
    }
  }
}
```

## Component 3: Skill Files

### What Are Skill Files?

Skill files are modular knowledge repositories loaded dynamically based on task context. They contain domain-specific expertise, patterns, and learned behaviors.

### When to Create Skills

Create a skill file when you have:

1. **Repeated Patterns** - Same solution applied multiple times
2. **Domain Expertise** - Specialized knowledge not in general training
3. **Learned Behaviors** - Mistakes fixed through testing
4. **Tool-Specific Knowledge** - How to use particular APIs or SDKs
5. **Project Conventions** - Team-specific standards and practices

### Skill File Structure

```markdown
---
name: <skill-name>
description: <what this skill covers> + <when to use it>
version: "0.1.0"
tags:
  - <keyword-1>
  - <keyword-2>
category: <domain-category>
---

# Skill Name

## When to Use
- <trigger-condition-1>
- <trigger-condition-2>

## Core Concepts
<fundamental knowledge>

## Patterns and Examples

### Pattern 1: <Name>
<code example with explanation>

### Pattern 2: <Name>
<another example>

## Common Pitfalls
- <mistake-1> and how to avoid it
- <mistake-2> and the correct approach

## References
- [Documentation link](url)
- Related skills: <skill-name>
```

### Example Skill: Dataverse Operations

```markdown
---
name: dataverse-operations
description: Performing CRUD operations with Microsoft Dataverse through Code App SDK. Use when creating, reading, updating, or deleting records in Dataverse tables within Power Platform Code Apps.
version: "0.1.0"
tags:
  - dataverse
  - crud
  - sdk
category: data-operations
---

# Dataverse Operations Skill

## When to Use
- Creating new records in Dataverse tables
- Querying existing records with filters
- Updating record fields
- Deleting records
- Working with relationships between tables

## Core Concepts

### Authentication Requirement
All Dataverse operations require an active connection. Check connection status before operations:

```javascript
// Check if connected
if (!sdk.isConnectionActive('dataverse')) {
  sdk.ui.showToast('Please connect to Dataverse first');
  return;
}
```

### Record Structure
Dataverse records use specific field naming:
- Primary key: `<name>_id` (e.g., `accountid`)
- Lookup fields end with `_id` or `_ref`
- Display names use `_displayName` suffix

## Patterns and Examples

### Pattern 1: Query Records

```javascript
// Simple query with filter
async function getActiveAccounts() {
  const filters = "statecode eq 0"; // Active records only
  const columns = ["name", "telephone1", "accountownerid"];
  
  try {
    const results = await sdk.dataverse.query(
      "account",
      filters,
      columns
    );
    
    return results.value;
  } catch (error) {
    sdk.ui.showToast('Error querying accounts: ' + error.message);
    return [];
  }
}
```

### Pattern 2: Create Record

```javascript
// Create new record with validation
async function createAccount(accountData) {
  // Validate required fields
  if (!accountData.name) {
    throw new Error("Account name is required");
  }
  
  const newRecord = {
    name: accountData.name,
    telephone1: accountData.phone,
    industrycode: accountData.industry
  };
  
  try {
    const result = await sdk.dataverse.create("account", newRecord);
    sdk.ui.showToast("Account created successfully");
    return result;
  } catch (error) {
    sdk.ui.showToast('Error creating account: ' + error.message);
    throw error;
  }
}
```

### Pattern 3: Update Record

```javascript
// Update existing record with optimistic concurrency
async function updateAccount(accountId, updates) {
  try {
    // First get current record
    const current = await sdk.dataverse.getById("account", accountId);
    
    // Merge updates (don't overwrite unchanged fields)
    const updatedRecord = { ...current, ...updates };
    
    // Update the record
    const result = await sdk.dataverse.update(
      "account", 
      accountId, 
      updatedRecord
    );
    
    return result;
  } catch (error) {
    if (error.code === 'CONFLICT') {
      sdk.ui.showToast('Record was updated by someone else. Please refresh.');
    } else {
      sdk.ui.showToast('Error updating account: ' + error.message);
    }
    throw error;
  }
}
```

### Pattern 4: Delete Record

```javascript
// Delete with confirmation
async function deleteAccount(accountId) {
  const confirmed = await sdk.ui.confirm(
    'Are you sure you want to delete this account?'
  );
  
  if (!confirmed) {
    return false;
  }
  
  try {
    await sdk.dataverse.delete("account", accountId);
    sdk.ui.showToast("Account deleted successfully");
    return true;
  } catch (error) {
    sdk.ui.showToast('Error deleting account: ' + error.message);
    throw error;
  }
}
```

### Pattern 5: Working with Relationships

```javascript
// Get related records (one-to-many)
async function getAccountContacts(accountId) {
  // Parent to child relationship
  const filters = `parentcustomerid_${accountId}_id eq '${accountId}'`;
  
  const contacts = await sdk.dataverse.query(
    "contact",
    filters,
    ["fullname", "emailaddress1", "telephone1"]
  );
  
  return contacts.value;
}

// Get parent record (many-to-one)
async function getAccountFromContact(contactId) {
  const columns = ["parentcustomerid_account_id", "parentcustomerid_account_name"];
  
  const contact = await sdk.dataverse.getById(
    "contact", 
    contactId,
    columns
  );
  
  return contact.parentcustomerid_account;
}
```

## Common Pitfalls

### ❌ Using Wrong Field Names
**Mistake:** Using display names instead of schema names
```javascript
// WRONG
const results = await sdk.dataverse.query("Account", "Name eq 'Contoso'");

// CORRECT  
const results = await sdk.dataverse.query("account", "name eq 'Contoso'");
```

**Rule:** Table names and column names are always lowercase schema names.

### ❌ Missing Connection Check
**Mistake:** Assuming connection is always active
```javascript
// WRONG - will fail if not connected
const results = await sdk.dataverse.query("account", null);

// CORRECT - check first
if (!sdk.isConnectionActive('dataverse')) {
  await sdk.connect('dataverse');
}
const results = await sdk.dataverse.query("account", null);
```

### ❌ Not Handling Errors
**Mistake:** Letting errors crash the app
```javascript
// WRONG
await sdk.dataverse.create("account", record);

// CORRECT
try {
  await sdk.dataverse.create("account", record);
} catch (error) {
  if (error.code === 'ALREADY_EXISTS') {
    sdk.ui.showToast('This account already exists');
  } else {
    sdk.ui.showToast('Error: ' + error.message);
  }
}
```

### ❌ Loading All Columns
**Mistake:** Querying unnecessary data
```javascript
// WRONG - slow and wasteful
const accounts = await sdk.dataverse.query("account", null, null);

// CORRECT - only needed columns
const accounts = await sdk.dataverse.query(
  "account", 
  "statecode eq 0",
  ["name", "telephone1"]  // Only what you need
);
```

## Performance Tips

1. **Use Filters Early** - Filter in Dataverse, not in JavaScript
2. **Limit Columns** - Only request fields you actually use
3. **Paginate Large Results** - Use `$top` and skip tokens
4. **Batch Operations** - Use batch API for multiple operations
5. **Cache Results** - Store frequently-accessed data locally

## Related Skills
- `authentication-management` - Handling connection lifecycle
- `error-handling` - Comprehensive error management patterns
- `ui-components` - Displaying Dataverse data in UI

## References
- [Code App SDK Documentation](https://codeappjs.com/docs/sdk)
- [Dataverse Web API](https://learn.microsoft.com/en-us/powerapps/developer/data-platform/webapi/overview)
- [Power Platform CLI](https://learn.microsoft.com/en-us/power-platform/alm/use-power-platform-cli)
```

### Skill Selection Strategies

#### Strategy 1: Keyword Matching (Simple but Limited)

```typescript
function selectSkillsByKeywords(userPrompt: string): string[] {
  const keywords = extractKeywords(userPrompt);
  const skillMap = {
    'dataverse': ['dataverse-operations', 'authentication-management'],
    'create': ['dataverse-operations', 'validation-patterns'],
    'query': ['dataverse-operations', 'performance-optimization'],
    'ui': ['ui-components', 'user-experience']
  };
  
  const selected = new Set<string>();
  for (const keyword of keywords) {
    if (skillMap[keyword]) {
      skillMap[keyword].forEach(skill => selected.add(skill));
    }
  }
  
  return Array.from(selected);
}
```

**Problem:** Often misses relevant skills or includes irrelevant ones.

#### Strategy 2: LLM-Based Selection (Recommended)

```typescript
async function selectSkillsWithLLM(userPrompt: string, workspaceFolder: string): Promise<string[]> {
  // Get list of available skills with descriptions
  const availableSkills = await listAvailableSkills();
  
  // Create selection prompt
  const selectionPrompt = `
Available Skills:
${availableSkills.map(s => `- ${s.name}: ${s.description}`).join('\n')}

User Request: "${userPrompt}"

Which skills are relevant for this task? Return only the skill names as a JSON array.
Consider:
- What domain knowledge is needed?
- What patterns might be applied?
- What pitfalls should be avoided?

Respond with JSON only: ["skill-name-1", "skill-name-2"]
  `;
  
  const response = await llm.chat(selectionPrompt);
  
  // Parse JSON response
  try {
    const selectedSkills = JSON.parse(response.trim());
    return selectedSkills;
  } catch (error) {
    console.error('Failed to parse skill selection:', error);
    return [];
  }
}
```

**Benefit:** More accurate, understands context and nuance.

#### Strategy 3: Hybrid Approach (Best for Large Skill Sets)

```typescript
async function selectSkillsHybrid(userPrompt: string): Promise<string[]> {
  // Step 1: Keyword filter to reduce candidate pool
  const keywordMatches = selectSkillsByKeywords(userPrompt);
  
  // Step 2: LLM selects from reduced pool
  if (keywordMatches.length <= 3) {
    // Small enough, use directly
    return keywordMatches;
  } else {
    // Too many, let LLM choose best ones
    const skillDescriptions = await getSkillDescriptions(keywordMatches);
    
    const selectionPrompt = `
From these potentially relevant skills, select the TOP 3 most relevant:
${skillDescriptions}

User Request: "${userPrompt}"

Return JSON array with top 3: ["best", "second-best", "third-best"]
    `;
    
    return await llm.selectTopSkills(selectionPrompt);
  }
}
```

## Building Skills Through Testing

### The Learning Cycle

1. **Build Initial Version** - Create basic skill with known patterns
2. **Use in Real Projects** - Apply skill to actual development tasks
3. **Monitor Failures** - Track where the LLM makes mistakes
4. **Analyze Reasoning** - Read LLM's thought process (if available)
5. **Update Skill** - Add constraints, examples, clarifications
6. **Repeat** - Continuous improvement

### Documenting Learnings

```markdown
## Learnings from Testing (Updated: 2024-04-13)

### Bug #1: Incorrect Field Names
**Date:** 2024-04-10  
**Issue:** LLM kept using "Account" instead of "account" for table name  
**Fix:** Added explicit note about lowercase schema names in Common Pitfalls  
**Test Case Added:** Verify all table/column names are lowercase

### Bug #2: Missing Error Handling
**Date:** 2024-04-11  
**Issue:** Generated code didn't handle connection failures  
**Fix:** Made error handling mandatory in all patterns  
**Test Case Added:** Test behavior when connection is inactive

### Bug #3: Wrong Relationship Direction
**Date:** 2024-04-12  
**Issue:** Confused parent-to-child vs child-to-parent queries  
**Fix:** Added separate patterns for each direction with clear examples  
**Test Case Added:** Query both directions of relationship
```

## Best Practices Summary

### UI Commands
- ✅ Design as pipeline (each step prepares next)
- ✅ Validate prerequisites before execution
- ✅ Provide visual feedback during operations
- ✅ Update config files automatically
- ❌ Don't expose raw CLI to users
- ❌ Don't skip validation steps

### System Prompts
- ✅ Be explicit about what NOT to do
- ✅ Provide correct patterns with examples
- ✅ Include escalation guidelines
- ✅ Test with edge cases
- ❌ Don't be vague or ambiguous
- ❌ Don't assume general knowledge applies

### Skill Files
- ✅ Focus on one domain per skill
- ✅ Include working code examples
- ✅ Document common pitfalls
- ✅ Update through testing
- ✅ Version control changes
- ❌ Don't make skills too broad
- ❌ Don't leave out negative constraints

## Next Steps

After implementing these components:

1. **Optimize Context Usage** - See [Context Optimization](04-context-optimization.md)
2. **Establish Training Workflow** - See [Training Workflow](05-training-workflow.md)
3. **Test Extensively** - Real usage reveals issues testing won't catch
