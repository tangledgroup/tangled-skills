# Platform Implementation Guide

Choosing the right platform for your AI coding agent depends on your specific needs, existing tooling, and distribution requirements. This guide covers the three main approaches with implementation details.

## Platform Comparison

| Factor | VS Code Extension | CLI Wrapper | GitHub Copilot Extension |
|--------|-------------------|-------------|-------------------------|
| **Authentication** | Built-in (GitHub, Azure, etc.) | Manual implementation | Built-in (GitHub) |
| **Terminal Access** | Integrated terminal API | Native shell | Limited |
| **Custom UI** | Full capabilities (panels, views, buttons) | Text-based menus | Chat interface only |
| **File System** | Workspace API with IntelliSense | Direct access | Through Copilot |
| **Distribution** | VS Code Marketplace (free) | npm, Homebrew, manual | GitHub Marketplace |
| **Context Limits** | You control everything | You control everything | Subject to Copilot limits |
| **Learning Curve** | Medium (VS Code API) | Low (shell scripting) | High (Copilot constraints) |
| **Best For** | Integrated workflows | Automation/DevOps | Enhancing existing Copilot |

## VS Code Extension Approach

### Why Choose VS Code Extensions

1. **Built-in Authentication** - Leverage existing GitHub, Azure, or other auth providers
2. **Integrated Terminal** - Execute commands without leaving the editor
3. **Custom UI Elements** - Buttons, dropdowns, status bars for simplified workflows
4. **No Backend Required** - Everything runs locally in the extension
5. **Free Distribution** - Publish to VS Code Marketplace at no cost
6. **Workspace Awareness** - Full access to project structure and files

### Extension Architecture

```
codeappjsplus/
├── package.json              # Extension manifest
├── tsconfig.json             # TypeScript configuration
├── src/
│   ├── extension.ts          # Entry point
│   ├── providers/
│   │   └── chatProvider.ts   # Chat interface handler
│   ├── commands/
│   │   ├── authenticate.ts   # Auth command
│   │   ├── deploy.ts         # Deploy command
│   │   └── connect.ts        # Create connections
│   ├── services/
│   │   ├── copilotService.ts # GitHub Copilot API wrapper
│   │   └── cliService.ts     # Power Platform CLI wrapper
│   └── utils/
│       └── promptBuilder.ts  # Constructs prompt stack
├── resources/
│   ├── skills/               # Skill.md files
│   └── icons/                # UI icons
└── tests/
```

### Core Components

#### 1. Extension Entry Point

```typescript
// src/extension.ts
import { WorkspaceFolder, ExtensionContext } from 'vscode';
import { ChatProvider } from './providers/chatProvider';
import { registerCommands } from './commands';

export function activate(context: ExtensionContext) {
  const chatProvider = new ChatProvider(context);
  
  // Register chat interface
  context.subscriptions.push(
    vscode.window.registerWebviewPanelProvider('aiChat', chatProvider)
  );
  
  // Register CLI commands as buttons
  registerCommands(context, chatProvider);
  
  console.log('AI Coding Agent is now active');
}
```

#### 2. Prompt Stack Builder

```typescript
// src/utils/promptBuilder.ts
import * as fs from 'fs';
import * as path from 'path';

interface PromptStack {
  systemPrompt: string;
  applicationPrompt: string;
  instructions: string;
  skills: string[];
  userPrompt: string;
}

export class PromptBuilder {
  private readonly skillsPath = path.join(__dirname, '../../resources/skills');
  
  async build(userPrompt: string, workspaceFolder: WorkspaceFolder): Promise<PromptStack> {
    // Load system prompt (custom for your domain)
    const systemPrompt = this.loadSystemPrompt();
    
    // Load application prompt (tool capabilities)
    const applicationPrompt = this.loadApplicationPrompt();
    
    // Load project instructions if exists
    const instructions = await this.loadInstructions(workspaceFolder);
    
    // Select relevant skills based on keywords/context
    const skills = await this.selectSkills(userPrompt, workspaceFolder);
    
    return {
      systemPrompt,
      applicationPrompt,
      instructions,
      skills,
      userPrompt
    };
  }
  
  private loadSystemPrompt(): string {
    // Custom system prompt to prevent using general JS training
    return `You are an expert in Power Platform Code Apps with vanilla JavaScript.
    
CRITICAL: Do NOT use React patterns or TypeScript assumptions.
Code Apps use a specific SDK and vanilla JavaScript only.
Always reference the Code App SDK documentation before suggesting code.
    
When unsure, ask clarifying questions rather than assuming React patterns.`;
  }
  
  private loadApplicationPrompt(): string {
    return `Available Tools:
- read_file: Read file contents
- write_file: Create or update files
- execute_cli: Run Power Platform CLI commands
- list_environments: Show available environments
- create_connection: Set up data connections

Authentication is handled through the extension UI, not CLI commands.`;
  }
  
  private async loadInstructions(workspaceFolder: WorkspaceFolder): Promise<string> {
    const instructionPath = path.join(workspaceFolder.uri.fsPath, 'instruction.md');
    if (fs.existsSync(instructionPath)) {
      return fs.readFileSync(instructionPath, 'utf-8');
    }
    return '';
  }
  
  private async selectSkills(userPrompt: string, workspaceFolder: WorkspaceFolder): Promise<string[]> {
    // Strategy: Pass skill list/descriptions to LLM and let it choose
    const availableSkills = await this.listAvailableSkills();
    
    // Alternative: Keyword-based selection (less reliable)
    const keywords = this.extractKeywords(userPrompt);
    const matchedSkills = this.matchSkillsByKeywords(keywords, availableSkills);
    
    // Best approach: Let LLM decide from descriptions
    return this.formatSkillSelectionPrompt(availableSkills);
  }
}
```

#### 3. Chat Provider with Copilot Integration

```typescript
// src/providers/chatProvider.ts
import { GitHubCopilotService } from '../services/copilotService';

export class ChatProvider {
  private copilot: GitHubCopilotService;
  private promptBuilder: PromptBuilder;
  
  async handleUserMessage(userPrompt: string, workspaceFolder: WorkspaceFolder): Promise<string> {
    // Build complete prompt stack
    const promptStack = await this.promptBuilder.build(userPrompt, workspaceFolder);
    
    // Combine into single context
    const fullContext = this.combinePromptStack(promptStack);
    
    // Send to Copilot/LLM
    const response = await this.copilot.chat(fullContext);
    
    // Process response (may include tool calls)
    return this.processResponse(response, workspaceFolder);
  }
  
  private combinePromptStack(stack: PromptStack): string {
    return `
${stack.systemPrompt}

${stack.applicationPrompt}

${stack.instructions ? `Project Instructions:\n${stack.instructions}` : ''}

${stack.skills.join('\n\n')}

User Request: ${stack.userPrompt}
    `.trim();
  }
  
  private async processResponse(response: string, workspaceFolder: WorkspaceFolder): Promise<string> {
    // Check for tool calls in response
    if (response.includes('read_file:') || response.includes('write_file:')) {
      // Execute tool and continue conversation
      const toolResult = await this.executeToolCall(response, workspaceFolder);
      
      // Send follow-up with tool result
      const followUpContext = `${response}\n\nTool Result: ${toolResult}`;
      return this.copilot.chat(followUpContext);
    }
    
    return response;
  }
}
```

#### 4. UI-Based CLI Commands

```typescript
// src/commands/deploy.ts
import { ExtensionContext } from 'vscode';

export function registerDeployCommand(context: ExtensionContext, chatProvider: ChatProvider) {
  const deployCommand = vscode.commands.registerCommand('codeappjsplus.deploy', async () => {
    // Step 1: Check authentication
    if (!await isAuthenticated()) {
      vscode.window.showWarningMessage('Please authenticate first');
      return;
    }
    
    // Step 2: Select environment
    const environments = await listEnvironments();
    const selected = await vscode.window.showQuickPick(environments);
    
    if (!selected) return;
    
    // Step 3: Update config files
    await updateConfig(selected);
    
    // Step 4: Execute deploy through CLI
    vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: 'Deploying...' },
      async () => {
        const result = await executeDeployCommand(selected);
        
        if (result.success) {
          vscode.window.showInformationMessage(`Deployed to ${selected.name}`);
        } else {
          vscode.window.showErrorMessage(`Deploy failed: ${result.error}`);
        }
      }
    );
  });
  
  context.subscriptions.push(deployCommand);
}
```

### Package.json Configuration

```json
{
  "name": "codeappjsplus",
  "displayName": "Code App JS Plus AI Agent",
  "version": "1.0.0",
  "description": "AI coding agent for Power Platform Code Apps with vanilla JavaScript",
  "publisher": "powerdevbox",
  "engine": {
    "vscode": "^1.75.0"
  },
  "categories": [
    "AI",
    "Programming Languages",
    "Other"
  ],
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "codeappjsplus.authenticate",
        "title": "Code App JS: Authenticate"
      },
      {
        "command": "codeappjsplus.deploy",
        "title": "Code App JS: Deploy"
      },
      {
        "command": "codeappjsplus.createConnection",
        "title": "Code App JS: Create Connection"
      }
    ],
    "menus": {
      "view/title": [
        {
          "command": "codeappjsplus.authenticate",
          "when": "view == codeappjsplus.chat",
          "group": "navigation"
        }
      ]
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  }
}
```

## CLI Wrapper Approach

### Why Choose CLI Wrapper

1. **Cross-Platform** - Works on any system with the runtime installed
2. **Scriptable** - Easy to integrate into CI/CD pipelines
3. **Lightweight** - No IDE dependencies or complex setup
4. **Version Control** - Simple to version and distribute via package managers

### Implementation Example

```bash
#!/bin/bash
# ai-agent.sh

# Load configuration
source ~/.ai-agent/config.sh

# Parse arguments
case "$1" in
  chat)
    start_chat_mode
    ;;
  file)
    analyze_file "$2"
    ;;
  setup)
    initialize_project
    ;;
  *)
    show_help
    ;;
esac

start_chat_mode() {
  # Load prompt stack from config files
  SYSTEM_PROMPT=$(cat ~/.ai-agent/system-prompt.md)
  INSTRUCTIONS=$(cat ./instruction.md 2>/dev/null || echo "")
  
  # Interactive chat loop
  while true; do
    read -p "You: " user_input
    
    # Build context and send to LLM API
    response=$(curl -s "$LLM_API" \
      -H "Authorization: Bearer $API_KEY" \
      -d "{\"prompt\": \"$SYSTEM_PROMPT $INSTRUCTIONS $user_input\"}")
    
    echo "Agent: $response"
    
    [[ "$user_input" == "quit" ]] && break
  done
}
```

## GitHub Copilot Extension Approach

### Why Choose Copilot Extensions

1. **Leverage Existing License** - Use organization's Copilot subscription
2. **Familiar Interface** - Users already know how to use Copilot chat
3. **Integrated Suggestions** - Can enhance inline code suggestions
4. **No New UI** - Works within existing VS Code Copilot interface

### Limitations

- Cannot modify system prompts
- Subject to Copilot's context limits
- Less control over prompt stack construction
- May not work with all Copilot features

### Implementation Strategy

```typescript
// Use GitHub Actions or custom instructions to extend Copilot
// Since direct extension is limited, focus on:
// 1. Well-crafted instruction.md files
// 2. Skill-like documentation in repo
// 3. Custom snippets and templates

// Example: .github/copilot-instructions.md
# AI Coding Agent Instructions

You are an expert in this specific codebase. Follow these guidelines:

## Tech Stack
- Vanilla JavaScript (NO React, NO TypeScript)
- Power Platform Code App SDK
- Custom utility library in /src/utils/

## Patterns to Use
See /docs/patterns.md for approved patterns

## Common Pitfalls
- Don't assume React hooks exist
- Always use the Code App SDK for data operations
- Check connection status before API calls
```

## Platform Selection Decision Tree

```
Do you need custom UI (buttons, panels)?
├── YES → VS Code Extension
│
└── NO → Do you need CI/CD integration?
    ├── YES → CLI Wrapper
    │
    └── NO → Do you already use GitHub Copilot?
        ├── YES → GitHub Copilot Extension (via instructions)
        └── NO → VS Code Extension (most flexible)
```

## Hybrid Approach

Many successful agents use a combination:

1. **Core Logic in CLI** - Reusable, testable, platform-independent
2. **VS Code Extension as UI** - Leverages CLI for heavy lifting
3. **Instruction Files Everywhere** - Works across all platforms

```
project/
├── ai-agent-cli/          # Core logic (npm package)
├── ai-agent-vscode/       # VS Code extension (uses CLI)
└── docs/
    └── instructions.md    # Works standalone or with any platform
```

## Distribution Strategies

### VS Code Marketplace

```bash
# Install vsce (VS Code Extension Manager)
npm install -g @vscode/vsce

# Package extension
vsce package

# Publish (requires Microsoft account)
vsce publish

# Benefits:
# - Free distribution
# - Automatic updates
# - Rating and review system
# - Discovery through search
```

### npm Package (CLI)

```bash
# Initialize package
npm init -y

# Add bin field in package.json
"bin": {
  "ai-agent": "./cli.js"
}

# Publish
npm publish

# Users install globally:
npm install -g @yourorg/ai-agent
```

### GitHub Releases

```bash
# Create release with binaries
gh release create v1.0.0 \
  --title "AI Agent v1.0.0" \
  --notes "Initial release with prompt stack support" \
  ai-agent-linux.xz \
  ai-agent-darwin.xz \
  ai-agent-windows.zip
```

## Testing Your Implementation

### VS Code Extension Testing

```typescript
// test/suite/extension.test.ts
import * as assert from 'assert';
import { promptBuilder } from '../../src/utils/promptBuilder';

suite('Prompt Builder Tests', () => {
  test('Should select correct skills based on keywords', async () => {
    const userPrompt = 'Create a React component for user profile';
    const skills = await promptBuilder.selectSkills(userPrompt, mockWorkspace);
    
    assert.ok(skills.some(s => s.includes('react-components')));
  });
  
  test('Should load instructions from workspace', async () => {
    const instructions = await promptBuilder.loadInstructions(mockWorkspace);
    
    assert.ok(instructions.length > 0);
    assert.ok(instructions.includes('Naming Conventions'));
  });
});
```

### CLI Testing

```bash
#!/bin/bash
# test/cli-test.sh

# Test chat mode
echo "Testing chat mode..."
./ai-agent chat <<EOF
What files are in the current directory?
quit
EOF

# Verify output contains expected response
assert_output_contains "Files found:"
```

## Common Implementation Challenges

### Challenge 1: Authentication Management

**Problem:** Need to authenticate with multiple services (GitHub, Azure, custom APIs)

**Solution (VS Code):** Use built-in authentication API

```typescript
const session = await vscode.authentication.getSession('github', [
  'repo',
  'workflow'
], { createIfMissing: true });
```

**Solution (CLI):** Store tokens securely

```bash
# Use OS keychain
keychain set ai-agent-github-token "$TOKEN"

# Or encrypted config file
openssl enc -aes-256-cbc -salt -in token.txt -out token.enc
```

### Challenge 2: Context Limit Management

**Problem:** Prompt stack exceeds LLM context limits

**Solution:** Implement progressive loading

```typescript
async function buildOptimizedPrompt(userPrompt: string): Promise<string> {
  // Start with essential prompts only
  let context = systemPrompt + applicationPrompt;
  
  // Add instructions if space allows
  if (countTokens(context) < MAX_TOKENS * 0.5) {
    context += await loadInstructions();
  }
  
  // Load only relevant skills
  const neededSkills = await identifyNeededSkills(userPrompt);
  for (const skill of neededSkills) {
    if (countTokens(context) < MAX_TOKENS * 0.8) {
      context += await loadSkill(skill);
    }
  }
  
  return context + userPrompt;
}
```

### Challenge 3: Error Handling and Recovery

**Problem:** LLM makes mistakes, needs to recover gracefully

**Solution:** Implement decision log with rollback

```typescript
interface DecisionLogEntry {
  task: string;
  status: 'pending' | 'completed' | 'failed';
  decisions: string[];
  filesModified: string[];
  timestamp: Date;
}

class DecisionLogger {
  async beginTask(task: string): Promise<void> {
    const entry: DecisionLogEntry = {
      task,
      status: 'pending',
      decisions: [],
      filesModified: [],
      timestamp: new Date()
    };
    
    await this.log.push(entry);
  }
  
  async recordDecision(decision: string): Promise<void> {
    const current = this.log[this.log.length - 1];
    current.decisions.push(decision);
  }
  
  async rollback(): Promise<void> {
    const current = this.log[this.log.length - 1];
    
    // Restore files to previous state
    for (const file of current.filesModified) {
      await restoreFileVersion(file, current.timestamp);
    }
    
    current.status = 'failed';
  }
}
```

## Best Practices Summary

1. **Start Simple** - Begin with instruction.md before building full extension
2. **Test Extensively** - Real usage reveals prompt stack issues
3. **Document Everything** - Skills and instructions are your training data
4. **Respect Context Limits** - Optimize for token efficiency from the start
5. **Provide Escape Hatches** - Users should bypass agent when needed
6. **Version Your Prompts** - Track changes like code changes
7. **Monitor Usage** - Understand how users interact with your agent

## Next Steps

After choosing and implementing your platform, focus on:

1. **Building UI Commands** - See [Implementation Guide](03-implementation.md)
2. **Optimizing Context** - See [Context Optimization](04-context-optimization.md)
3. **Training Through Testing** - See [Training Workflow](05-training-workflow.md)
