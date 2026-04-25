# Safety Systems

How production agents implement approvals, sandboxes, AST parsing, and permission brokers to prevent catastrophic failures.

## The Problem

`sudo rm -rf /*`. Scary.

After all safety measures, users can still run dangerously. But good harnesses make accidents hard and intentional dangerous operations explicit.

**Safety isn't "add a warning." It's architecture** - approvals, policies, sandboxes, and undo mechanisms.

## Defense in Depth

Production agents layer multiple safety mechanisms:

```
┌─────────────────────────────────────┐
│ Layer 1: Policy & Allowlists        │ Define what's allowed
├─────────────────────────────────────┤
│ Layer 2: Approvals                  │ Ask before dangerous ops
├─────────────────────────────────────┤
│ Layer 3: AST Parsing                │ Understand commands before running
├─────────────────────────────────────┤
│ Layer 4: Sandboxing                 │ Contain execution environment
├─────────────────────────────────────┤
│ Layer 5: Snapshotting               │ Enable rollback and recovery
└─────────────────────────────────────┘
```

## Layer 1: Policy & Allowlists

### Command Allowlists/Denylists

```typescript
interface SafetyPolicy {
  allowedCommands: string[];     // Whitelist of safe commands
  deniedCommands: string[];      // Blacklist of dangerous commands
  allowedPaths: string[];        // Paths where operations are allowed
  deniedPaths: string[];         // Paths that are protected
  requireApproval: string[];     // Commands that always need approval
}

const defaultPolicy: SafetyPolicy = {
  allowedCommands: [
    'ls', 'cat', 'grep', 'find', 'head', 'tail',
    'git status', 'git diff', 'npm test', 'make'
  ],
  deniedCommands: [
    'rm -rf /', 'sudo rm', 'dd if=', ':(){ :|:&}',
    'mkfs', 'fdisk', 'dd of=/dev/'
  ],
  allowedPaths: ['./src', './test', './docs'],
  deniedPaths: ['/etc', '/root', '~/.ssh', '~/.aws'],
  requireApproval: [
    'rm', 'mv', 'cp --remove-destination',
    'chmod', 'chown', 'curl -X DELETE'
  ]
};
```

### Path-Based Policies

```typescript
function isPathAllowed(path: string, policy: SafetyPolicy): boolean {
  const absolutePath = resolveAbsolutePath(path);
  
  // Check denylist first
  if (policy.deniedPaths.some(denied => absolutePath.startsWith(denied))) {
    return false;
  }
  
  // Check allowlist if specified
  if (policy.allowedPaths.length > 0) {
    return policy.allowedPaths.some(allowed => 
      absolutePath.startsWith(allowed)
    );
  }
  
  // Default: allow if not denied
  return true;
}
```

## Layer 2: Approvals

### Approval Workflow

```typescript
enum ApprovalPolicy {
  NEVER = 'never',       // Always execute without asking
  ALWAYS = 'always',     // Always ask before executing
  DANGEROUS = 'dangerous', // Ask only for dangerous operations
  CONFIGURED = 'configured' // Based on policy configuration
}

interface ApprovalRequest {
  type: 'bash' | 'file_write' | 'file_delete' | 'network';
  description: string;
  details: any;
  riskLevel: 'low' | 'medium' | 'high';
  reversible: boolean;
}

async function requestApproval(
  request: ApprovalRequest,
  policy: ApprovalPolicy,
  ui: UserInterface
): Promise<boolean> {
  // Skip approval if policy says never ask
  if (policy === ApprovalPolicy.NEVER) {
    return true;
  }
  
  // Always ask if policy requires it
  if (policy === ApprovalPolicy.ALWAYS) {
    return await ui.confirm(request);
  }
  
  // Ask for dangerous operations
  if (policy === ApprovalPolicy.DANGEROUS && request.riskLevel === 'high') {
    return await ui.confirm(request);
  }
  
  // Policy-based decision
  if (policy === ApprovalPolicy.CONFIGURED) {
    const requiresApproval = safetyPolicy.requiresApproval.includes(request.type);
    if (requiresApproval) {
      return await ui.confirm(request);
    }
    return true;
  }
  
  return true;
}
```

### UI Presentation

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️  Approval Required                                   │
├─────────────────────────────────────────────────────────┤
│ The agent wants to execute:                             │
│                                                         │
│   $ rm -rf node_modules                                 │
│                                                         │
│ This will delete the node_modules directory.            │
│                                                         │
│ Risk Level: MEDIUM                                      │
│ Reversible: Yes (can reinstall with npm install)       │
│                                                         │
│ [ ✅ Approve ]  [ ❌ Deny ]  [ ⏸️  Approve Once ]      │
└─────────────────────────────────────────────────────────┘
```

## Layer 3: AST Parsing (OpenCode Pattern)

OpenCode parses bash commands with tree-sitter to understand what they do before executing:

```typescript
// packages/opencode/src/tool/bash.ts

async function analyzeCommand(command: string) {
  const parser = await getBashParser();
  const tree = parser.parse(command);
  
  const commands = [];
  for (const node of tree.rootNode.descendantsOfType('command')) {
    const cmdNode = node.child(0); // First child is the command name
    const args = node.children.slice(1).map(n => n.text.toString());
    
    commands.push({
      command: cmdNode?.text.toString() || '',
      arguments: args,
      risky: isRiskyCommand(cmdNode?.text.toString(), args)
    });
  }
  
  return commands;
}

function isRiskyCommand(cmd: string, args: string[]): boolean {
  const dangerousPatterns = [
    /^rm\s/,
    /^sudo\s/,
    /^dd\b/,
    /chmod\s+[0-7]{3,}/,
    /curl.*\|-d\s/POST|DELETE|PUT/i,
    /wget.*/
  ];
  
  const dangerousArgs = [
    '-rf', '--recursive', '--force',
    'yesh', '+y', '-y' // Auto-confirm prompts
  ];
  
  if (dangerousPatterns.some(p => p.test(cmd))) {
    return true;
  }
  
  if (dangerousArgs.some(a => args.some(arg => arg.includes(a)))) {
    return true;
  }
  
  return false;
}
```

### Permission Broker Pattern

```typescript
async function executeBashWithPermissions(
  command: string,
  context: ToolContext
) {
  // Parse command to understand what it does
  const analysis = await analyzeCommand(command);
  
  // Extract directories and patterns that need permission
  const directories = new Set<string>();
  const patterns = new Set<string>();
  
  for (const cmd of analysis.commands) {
    if (cmd.risky) {
      // Extract paths from arguments
      const paths = extractPaths(cmd.arguments);
      for (const path of paths) {
        if (isDirectory(path)) {
          directories.add(path);
        } else {
          patterns.add(path);
        }
      }
    }
  }
  
  // Request permissions
  if (directories.size > 0) {
    await context.ask({
      permission: 'external_directory',
      directories: Array.from(directories),
      command: command
    });
  }
  
  if (patterns.size > 0) {
    await context.ask({
      permission: 'bash',
      patterns: Array.from(patterns),
      command: command
    });
  }
  
  // Execute if approved
  return executeSandboxed(command);
}
```

**Source**: Based on `packages/opencode/src/tool/bash.ts` lines 84-164

## Layer 4: Sandboxing

### OS-Level Sandboxing (Codex Pattern)

Codex uses OS sandboxing for defense-in-depth:

```rust
// codex-rs/core/src/sandbox.rs

pub struct SandboxConfig {
    allowed_paths: Vec<PathBuf>,
    denied_paths: Vec<PathBuf>,
    network_access: NetworkPolicy,
    process_limits: ProcessLimits,
}

pub enum NetworkPolicy {
    Denied,
    Allowed,
    AllowedWithAllowlist(Vec<String>),
}

pub struct ProcessLimits {
    max_cpu_time: Duration,
    max_memory: usize,
    max_processes: usize,
}

impl Sandbox {
    pub fn new(config: SandboxConfig) -> Self {
        // On Linux: use namespaces and cgroups
        // On macOS: use sysctl and launchd constraints
        // On Windows: use Job Objects
    }
    
    pub async fn execute(
        &self,
        command: &str,
        cwd: &Path,
    ) -> Result<ExecutionResult, SandboxError> {
        // 1. Validate path is allowed
        self.validate_path(cwd)?;
        
        // 2. Apply process limits
        self.apply_limits()?;
        
        // 3. Execute in constrained environment
        let result = self.run_constrained(command).await;
        
        // 4. Verify no escape attempts
        self.verify_integrity()?;
        
        Ok(result)
    }
}
```

### Execution Containment

```rust
// Run command with containment
fn run_constrained(&self, command: &str) -> Result<Output, Error> {
    let mut cmd = Command::new("sh");
    cmd.arg("-c").arg(command);
    
    // Set resource limits
    #[cfg(unix)]
    {
        use nix::sys::resource::{setrlimit, Resource, RLIM_INFINITY};
        
        // Limit CPU time
        setrlimit(Resource::RLIMIT_CPU, self.config.max_cpu_time.as_secs() as _, RLIM_INFINITY)?;
        
        // Limit memory
        setrlimit(Resource::RLIMIT_AS, self.config.max_memory as _, RLIM_INFINITY)?;
    }
    
    // Execute and capture output
    cmd.output()
}
```

## Layer 5: Snapshotting & Recovery

### State Snapshots

```typescript
class StateSnapshotter {
  private snapshots: Map<string, StateSnapshot> = new Map();
  
  async createSnapshot(id: string): Promise<StateSnapshot> {
    const snapshot: StateSnapshot = {
      id,
      timestamp: new Date(),
      files: await this.snapshotFiles(),
      gitState: await this.snapshotGitState(),
      environment: await this.snapshotEnvironment()
    };
    
    this.snapshots.set(id, snapshot);
    return snapshot;
  }
  
  async snapshotFiles(): Promise<FileSnapshot[]> {
    const modifiedFiles = await gitStatus();
    return Promise.all(
      modifiedFiles.map(async (file) => ({
        path: file,
        content: await fs.readFile(file, 'utf-8'),
        hash: await hashFile(file)
      }))
    );
  }
  
  async restore(snapshotId: string): Promise<void> {
    const snapshot = this.snapshots.get(snapshotId);
    if (!snapshot) {
      throw new Error(`Snapshot ${snapshotId} not found`);
    }
    
    // Restore files to pre-change state
    for (const file of snapshot.files) {
      await fs.writeFile(file.path, file.content);
    }
    
    // Reset git state
    await this.restoreGitState(snapshot.gitState);
  }
}
```

### Git-Based Recovery

```typescript
async function createGitCheckpoint(description: string) {
  // Create a git branch for the current agent session
  const branchName = `agent-checkpoint-${Date.now()}`;
  
  await exec(`git checkout -b ${branchName}`);
  await exec(`git add -A`);
  await exec(`git commit -m "Agent checkpoint: ${description}"`);
  
  return branchName;
}

async function rollbackToCheckpoint(branchName: string) {
  // Reset to the checkpoint branch
  await exec(`git stash`); // Save any uncommitted changes
  await exec(`git checkout ${branchName}`);
  await exec(`git reset --hard HEAD`);
  
  // Clean up working directory
  await exec(`git clean -fd`);
}
```

## Risk Classification

### Command Risk Levels

```typescript
function classifyCommandRisk(command: string): {
  level: 'low' | 'medium' | 'high' | 'critical',
  reasons: string[],
  reversible: boolean
} {
  const reasons = [];
  
  // Critical: System-wide destructive operations
  if (/rm\s+-rf\s+\/($|\s)/.test(command)) {
    return { level: 'critical', reasons: ['Deletes entire filesystem'], reversible: false };
  }
  
  if (/sudo/.test(command)) {
    reasons.push('Runs with root privileges');
  }
  
  // High: Destructive but scoped
  if (/rm\s+-rf|rm\s+-r|--force-delete/.test(command)) {
    reasons.push('Recursively deletes files');
    return { level: 'high', reasons, reversible: false };
  }
  
  // Medium: Potentially destructive
  if (/chmod\s+[0-7]{3}|chown|curl.*-X\s+(DELETE|PUT|POST)/.test(command)) {
    reasons.push('Modifies permissions or remote state');
    return { level: 'medium', reasons, reversible: true };
  }
  
  // Low: Read operations
  if (/^(ls|cat|grep|find|head|tail|wc)\b/.test(command)) {
    return { level: 'low', reasons: ['Read-only operation'], reversible: true };
  }
  
  // Unknown: Default to medium
  return { level: 'medium', reasons: ['Unknown command'], reversible: true };
}
```

## Approval UI Patterns

### Inline Approval (TUI)

```
> Agent: I need to delete the old build directory
  
  ⚠️  Approval required for: rm -rf dist/
  
  [y/N] _
```

### Batch Approval

```
┌─────────────────────────────────────────────────────────┐
│ Pending Approvals (3)                                   │
├─────────────────────────────────────────────────────────┤
│ 1. ✅ Install dependencies                              │
│    $ npm install                                        │
│                                                         │
│ 2. ⏸️  Run production build                             │
│    $ npm run build                                      │
│                                                         │
│ 3. ⏸️  Deploy to staging                                 │
│    $ vercel --prod                                      │
│                                                         │
│ [Approve All] [Approve Selected] [Deny All]           │
└─────────────────────────────────────────────────────────┘
```

### Persistent Approval Rules

```typescript
class ApprovalRules {
  private rules: Map<string, 'always' | 'never'> = new Map();
  
  rememberDecision(tool: string, args: any, approved: boolean): void {
    const key = `${tool}:${JSON.stringify(args)}`;
    this.rules.set(key, approved ? 'always' : 'never');
  }
  
  shouldAsk(tool: string, args: any): boolean {
    const key = `${tool}:${JSON.stringify(args)}`;
    const rule = this.rules.get(key);
    
    if (rule === 'always') return false; // Always approved
    if (rule === 'never') return true;   // Always denied (or ask again)
    
    return true; // No rule exists, ask user
  }
}
```

## Safety Trade-offs

### Codex vs OpenCode Approaches

| Aspect | Codex | OpenCode |
|--------|-------|----------|
| **Primary mechanism** | Execution containment | Pre-execution understanding |
| **Approvals** | Orchestrator-enforced | Permission broker |
| **Sandboxing** | OS-level (namespaces, cgroups) | AST analysis + approvals |
| **Philosophy** | Defense-in-depth | Policy-first |

### Trade-off Analysis

**Codex (Execution Containment)**:
- ✅ Harder to escape sandbox even if model is compromised
- ✅ Consistent safety regardless of command complexity
- ❌ Performance overhead from sandboxing
- ❌ Some operations can't be sandboxed (network, certain syscalls)

**OpenCode (Pre-Execution Understanding)**:
- ✅ Faster execution (no sandbox overhead for approved commands)
- ✅ Better user understanding of what will happen
- ❌ AST parsing can miss edge cases
- ❌ Relies more on approval quality

## Best Practices

### 1. Defense in Depth

Never rely on a single safety mechanism:

```typescript
// Bad: Only approvals
if (await requestApproval(command)) {
  exec(command); // No sandbox!
}

// Good: Multiple layers
if (await requestApproval(command)) {
  if (isPathAllowed(command)) {
    if (!matchesDenylist(command)) {
      await sandbox.execute(command);
    }
  }
}
```

### 2. Default Deny

Start with everything denied, explicitly allow what's safe:

```typescript
// Bad: Default allow with denylist
const isAllowed = !denylist.includes(command);

// Good: Default deny with allowlist
const isAllowed = allowlist.includes(command) || 
                  (await requestApproval(command));
```

### 3. Explicit Confirmations for Irreversible Operations

```typescript
if (!riskAssessment.reversible) {
  // Require explicit confirmation, not just approval
  const confirmed = await ui.confirm({
    type: 'destructive',
    message: `This cannot be undone: ${command}`,
    requireTypeToConfirm: true // User must type "DELETE" to confirm
  });
  
  if (!confirmed) {
    throw new Error('Operation cancelled');
  }
}
```

### 4. Snapshot Before Changes

```typescript
async function makeChanges(changes: Change[]) {
  // Create recovery point
  const snapshot = await snapshotter.createSnapshot('pre-change');
  
  try {
    for (const change of changes) {
      await applyChange(change);
    }
  } catch (error) {
    // Rollback on failure
    await snapshotter.restore(snapshot.id);
    throw error;
  }
}
```

### 5. Clear Risk Communication

```typescript
// Bad: Vague risk description
{
  riskLevel: 'high',
  description: 'This is dangerous'
}

// Good: Specific and actionable
{
  riskLevel: 'high',
  description: 'Will delete 47 files in src/',
  consequences: [
    'All files in src/ will be permanently deleted',
    'You will need to restore from git',
    'This cannot be undone by the agent'
  ],
  suggestions: [
    'Review files with: find src/ -type f',
    'Create backup: cp -r src/ src.backup/',
    'Use git diff to see what will change'
  ]
}
```

## Common Mistakes

### ❌ Relying Only on Model Self-Restraint

```typescript
// Bad: Trusting the model not to do dangerous things
systemPrompt += "Please don't delete important files.";

// The model can still generate rm -rf / if prompted enough

// Good: Technical safeguards
if (command.includes('rm -rf')) {
  throw new Error('Dangerous command blocked by safety layer');
}
```

### ❌ Insufficient Path Validation

```typescript
// Bad: Simple string check
if (path.startsWith('./')) {
  // Allow
}

// Can be bypassed with: ../../etc/passwd

// Good: Resolve and validate absolute path
const absolutePath = resolveAbsolutePath(path);
if (!isWithinAllowedDirectories(absolutePath)) {
  throw new Error('Path outside allowed directories');
}
```

### ❌ No Timeout on Long-Running Commands

```typescript
// Bad: No timeout
exec(command); // Could run forever

// Good: Enforced timeout
exec(command, { timeout: 300000 }); // 5 minute max
```

## References

- **OpenCode Bash Safety**: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/tool/bash.ts
- **Codex Orchestrator**: https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/orchestrator.rs
- **Claude Code Security**: https://docs.anthropic.com/en/docs/claude-code/security

## Key Takeaways

1. **Safety is architecture, not warnings** - Implement technical safeguards, not just prompts
2. **Defense in depth** - Layer multiple safety mechanisms
3. **AST parsing enables understanding** - Parse commands before executing to understand intent
4. **Approvals based on risk** - Classify operations and ask accordingly
5. **Sandboxing contains damage** - OS-level isolation limits blast radius
6. **Snapshotting enables recovery** - Always create rollback points before changes
7. **Default deny** - Start with everything blocked, explicitly allow safe operations
8. **Clear risk communication** - Tell users exactly what will happen and consequences
