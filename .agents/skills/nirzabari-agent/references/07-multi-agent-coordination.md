# Multi-Agent Coordination

How to scale from single agents to hundreds of parallel agents working on the same codebase for weeks at a time.

## The Problem

Single agents work well for focused tasks but are slow for complex projects. The natural next step is running multiple agents in parallel, but coordinating them is challenging.

**Cursor's experiments**: Hundreds of concurrent agents, single project, millions of lines of code, trillions of tokens over weeks of runtime.

## Failed Approaches

### Dynamic Coordination (Flat Structure)

Initial approach: Give agents equal status and let them self-coordinate through a shared file.

```python
# Each agent checks what others are doing, claims a task, updates status
while True:
    tasks = read_shared_task_file()
    available = [t for t in tasks if not t['assigned']]
    
    if available:
        task = claim_task(available[0])
        work_on(task)
        update_status('complete')
```

**Problems**:

1. **Lock contention**: Agents hold locks too long or forget to release them. Even when working correctly, locking became a bottleneck - 20 agents slowed to effective throughput of 2-3, with most time spent waiting.

2. **Brittleness**: Agents could fail while holding locks, try to acquire locks they already held, or update coordination file without acquiring lock at all.

3. **Risk aversion**: With no hierarchy, agents avoided difficult tasks and made small, safe changes instead. No agent took responsibility for hard problems or end-to-end implementation. Work churned for long periods without progress.

### Optimistic Concurrency Control

Replacement for locks: Agents could read state freely, but writes would fail if state changed since they last read it.

```python
def optimistic_write(task_id, new_state):
    current = read_task(task_id)
    if current['version'] != my_cached_version:
        raise ConflictError("Task changed, retry")
    
    write_task(task_id, new_state, version=current['version'] + 1)
```

**Better but still problematic**: Simpler and more robust than locks, but didn't solve the deeper problem of agents being risk-averse without hierarchy.

## Working Approach: Planners and Workers

Separate roles instead of flat structure where every agent does everything. Create a pipeline with distinct responsibilities.

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Planners                         │
│  - Explore codebase continuously                    │
│  - Create tasks from high-level goals               │
│  - Spawn sub-planners for specific areas            │
│  - Planning itself is parallel and recursive        │
└──────────────────────┬──────────────────────────────┘
                       │ Creates tasks
                       ▼
┌─────────────────────────────────────────────────────┐
│                  Task Queue                          │
│  - Unassigned tasks waiting for workers             │
│  - Tasks have clear definitions and acceptance      │
│    criteria                                          │
└──────────────────────┬──────────────────────────────┘
                       │ Workers pick up
                       ▼
┌─────────────────────────────────────────────────────┐
│                    Workers                          │
│  - Pick up tasks and focus entirely on completing   │
│  - Don't coordinate with other workers              │
│  - Don't worry about big picture                    │
│  - Just grind on assigned task until done           │
│  - Push changes when complete                       │
└──────────────────────┬──────────────────────────────┘
                       │ Cycle complete
                       ▼
┌─────────────────────────────────────────────────────┐
│                     Judge                            │
│  - Determines whether to continue at cycle end      │
│  - Evaluates progress toward goal                   │
│  - Starts next iteration fresh                      │
└─────────────────────────────────────────────────────┘
```

### Implementation Example

```python
# Planner agent
class PlannerAgent:
    def __init__(self, goal: str, codebase_path: str):
        self.goal = goal
        self.codebase = CodebaseExplorer(codebase_path)
        self.task_queue = TaskQueue()
    
    async def run(self):
        while not goal_achieved(self.goal):
            # Explore codebase to understand current state
            exploration = await self.codebase.explore()
            
            # Create tasks based on what needs to be done
            tasks = self.create_tasks(exploration, self.goal)
            
            # Spawn sub-planners for complex areas
            for complex_area in self.identify_complex_areas(exploration):
                sub_planner = SubPlanner(
                    goal=f"Implement {complex_area}",
                    codebase_path=self.codebase.path,
                    task_queue=self.task_queue
                )
                await sub_planner.run()
            
            # Add tasks to queue for workers
            for task in tasks:
                self.task_queue.add(task)
            
            # Wait for workers to make progress
            await self.wait_for_progress()

# Worker agent  
class WorkerAgent:
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
    
    async def run(self):
        while True:
            # Pick up next available task
            task = await self.task_queue.get()
            
            # Focus entirely on completing it
            result = await self.complete_task(task)
            
            # Push changes
            await self.push_changes(result)
            
            # Mark task complete and get next one
            task.mark_complete(result)

# Judge agent
class JudgeAgent:
    def __init__(self, goal: str, evaluation_criteria: list):
        self.goal = goal
        self.criteria = evaluation_criteria
    
    async def evaluate(self, current_state: CodebaseState) -> bool:
        # Check if goal is achieved
        for criterion in self.criteria:
            if not await self.check_criterion(criterion, current_state):
                return False
        return True
    
    async def check_criterion(self, criterion: str, state: CodebaseState) -> bool:
        # Use agent to evaluate criterion
        evaluation = await run_agent(
            prompt=f"Does this codebase satisfy: {criterion}\n\n{state.summary}",
            tools=[code_search, test_runner]
        )
        return evaluation.is_satisfied
```

### Why This Works

1. **Separation of concerns**: Planners think about what to do, workers focus on doing it
2. **No coordination overhead**: Workers don't talk to each other, just pick tasks and complete them
3. **Parallel planning**: Sub-planners can explore different areas simultaneously
4. **Clear progress**: Tasks have definitions and acceptance criteria
5. **Fresh starts**: Judge resets at cycle end to combat drift

## Real-World Results

### Building a Web Browser from Scratch

Cursor pointed the system at building a web browser:

- **Runtime**: Close to a week
- **Code written**: Over 1 million lines across 1,000 files
- **Agents**: Hundreds of workers running concurrently
- **Conflicts**: Minimal despite pushing to same branch

**Key insight**: Despite codebase size, new agents could still understand it and make meaningful progress.

### Solid to React Migration

In-place migration of Solid to React in Cursor's own codebase:

- **Runtime**: Over three weeks
- **Edits**: +266K/-193K lines
- **Status**: Passing CI and early checks, still needs careful review

### Other Experiments

- **Java LSP**: 7.4K commits, 550K LoC
- **Windows 7 emulator**: 14.6K commits, 1.2M LoC
- **Excel clone**: 12K commits, 1.6M LoC

## Anthropic's C Compiler Case Study

Anthropic published a case study about building a C compiler with parallel Claude agents.

### Architecture

Each Docker container:
1. Mounted shared bare git repo at `/upstream`
2. Cloned local workspace
3. Coordinated through lock files in `current_tasks/`

```bash
#!/bin/bash
while true; do
    COMMIT=$(git rev-parse --short=6 HEAD)
    LOGFILE="agent_logs/agent_${COMMIT}.log"
    
    claude --dangerously-skip-permissions \
           -p "$(cat AGENT_PROMPT.md)" \
           --model claude-opus-4-6-20260131 \
           &> "$LOGFILE"
done
```

**Coordination**: Pick a task by creating lock file, do work, pull, merge, push, remove lock. Simple git-based synchronization enabled parallelization without complex orchestration.

### Key Learnings

#### Continuous Task Loops Beat Interactive Sessions

Agent needs to immediately pick up next task without waiting for human input. The loop pattern is essential:

```
[Pick task] → [Do work] → [Push changes] → [Pick next task]
```

#### High-Quality Test Harnesses Are Critical

Tests define what the agent solves. Key practices:

1. **Minimal output**: Tests should print minimal output, log details to files (context window rotting is real)
2. **Fast modes**: Add `--fast` modes that run deterministic subsamples so agents don't spend hours on full test runs
3. **Clear failures**: Test output should clearly indicate what failed and why

#### READMEs and Progress Files Are Essential

Each fresh container starts with zero context. Need:

- Extensive READMEs explaining project structure
- Progress files tracking what's been done
- Clear task definitions in `current_tasks/`

#### Parallelization Works with Independent Tasks

**Success**: Independent failing tests - different agents could work on different bugs simultaneously.

**Failure**: Monolithic tasks caused all agents to hit same bugs. Solution: Use GCC as known-good oracle to narrow failure-inducing file subsets, letting different agents make progress on different bugs.

#### Agent Specialization

Dedicated agents for specific roles:
- Code consolidation
- Performance optimization
- Documentation
- Design critique

### Hard Limits Discovered

1. **Code quality degrades as complexity grows**: New features frequently broke existing functionality even with CI
2. **Generated code efficiency was poor**: Worse than `gcc -O0`
3. **Cost**: Just under $20k for roughly 100k lines (cost-effective vs human teams)
4. **Tests don't guarantee quality**: Passing tests still doesn't guarantee quality without human verification

## Model Choice for Long-Running Tasks

Different models excel at different roles:

### GPT-5.2 (Extended Thinking)

**Best for**: Extremely long-running autonomous work

**Strengths**:
- Following instructions over extended periods
- Keeping focus on goal
- Avoiding drift
- Implementing things precisely and completely

### Opus 4.5

**Behavior**: Tends to stop earlier and take shortcuts when convenient, yielding back control quickly.

**Best for**: Tasks requiring human collaboration, not fully autonomous work.

### Role-Specific Models

Cursor found GPT-5.2 is a better **planner** than GPT-5.1-Codex, even though latter is trained specifically for coding. Now they use model best suited for each role rather than one universal model.

## Coordination Patterns

### Lock-Free Task Queue

```python
class LockFreeTaskQueue:
    def __init__(self, task_file: str):
        self.task_file = task_file
    
    async def get_task(self, agent_id: str) -> Optional[Task]:
        tasks = self.read_tasks()
        
        # Find unassigned task
        for task in tasks:
            if task['status'] == 'available':
                # Optimistic assignment
                if self.try_assign(task['id'], agent_id):
                    return task
        
        return None
    
    def try_assign(self, task_id: str, agent_id: str) -> bool:
        tasks = self.read_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)
        
        if not task or task['status'] != 'available':
            return False
        
        task['status'] = 'in_progress'
        task['assigned_to'] = agent_id
        task['version'] += 1
        
        return self.write_tasks_optimistic(tasks, task['version'])
    
    def complete_task(self, task_id: str, result: dict):
        tasks = self.read_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)
        
        if task:
            task['status'] = 'complete'
            task['result'] = result
            self.write_tasks(tasks)
```

### Git-Based Coordination

```python
class GitCoordinator:
    def __init__(self, repo_path: str, task_branch_prefix: str = "task/"):
        self.repo = Repo(repo_path)
        self.task_branch_prefix = task_branch_prefix
    
    def create_task_branch(self, task_id: str) -> str:
        branch_name = f"{self.task_branch_prefix}{task_id}"
        
        # Pull latest main
        self.repo.remotes.origin.pull('main')
        
        # Create branch from main
        self.repo.create_head(branch_name)
        self.repo.heads[branch_name].checkout()
        
        return branch_name
    
    def submit_task(self, task_id: str):
        branch_name = f"{self.task_branch_prefix}{task_id}"
        
        # Commit changes
        self.repo.index.add([])
        self.repo.index.commit(f"Complete task {task_id}")
        
        # Push branch
        self.repo.remotes.origin.push(branch_name)
        
        # Create PR or merge
        self.create_pull_request(branch_name, task_id)
```

## Best Practices

### 1. Remove Complexity, Don't Add It

Many improvements came from removing complexity rather than adding it:

- Initially built integrator role for quality control and conflict resolution
- Found it created more bottlenecks than it solved
- Workers were already capable of handling conflicts themselves

**Lesson**: The best system is often simpler than you'd expect.

### 2. Right Amount of Structure

Too little structure → agents conflict, duplicate work, drift  
Too much structure → fragility and bottlenecks

The right amount is somewhere in the middle.

### 3. Prompt Quality Matters Most

Surprising amount of system's behavior comes down to how agents are prompted. Getting them to:
- Coordinate well
- Avoid pathological behaviors
- Maintain focus over long periods

Required extensive experimentation. The harness and models matter, but **prompts matter more**.

### 4. Periodic Fresh Starts

Even with good coordination, agents need periodic fresh starts to combat drift and tunnel vision.

```python
async def run_with_fresh_starts(max_runtime_hours: int = 24):
    start_time = time.time()
    
    while not goal_achieved():
        # Run agents for max_runtime_hours
        await run_agents(timeout=max_runtime_hours * 3600)
        
        # Check if time limit reached
        if time.time() - start_time > max_runtime_hours * 3600:
            # Fresh start with summarized context
            summary = await summarize_progress()
            start_time = time.time()
            
            # Spawn new agents with summary
            await spawn_fresh_agents(summary)
```

### 5. Model Specialization by Role

```python
def select_model_for_role(role: str) -> str:
    model_mapping = {
        'planner': 'gpt-5.2',      # Better at planning than coding-specific models
        'worker': 'gpt-5.1-codex',  # Trained for coding
        'reviewer': 'claude-opus',   # Good at code review
        'judge': 'gpt-5.2',        # Needs to maintain focus on goal
    }
    return model_mapping.get(role, 'gpt-5.1-codex')
```

## Common Mistakes

### ❌ Flat Agent Structure

All agents have equal status and try to coordinate with each other.

**Result**: Lock contention, risk aversion, no one takes responsibility for hard problems.

**Fix**: Planners and workers with clear separation of concerns.

### ❌ Complex Orchestration

Building integrator roles, conflict resolution systems, quality control layers.

**Result**: More bottlenecks, more failure modes.

**Fix**: Remove complexity. Workers can handle conflicts themselves.

### ❌ Single Model for All Roles

Using same model for planning, coding, reviewing, judging.

**Result**: Suboptimal performance in each role.

**Fix**: Specialized models for different roles.

### ❌ No Fresh Starts

Running agents indefinitely without reset.

**Result**: Drift, tunnel vision, degradation over time.

**Fix**: Periodic fresh starts with summarized context.

## References

- **Cursor Scaling Blog**: https://cursor.com/blog/scaling-agents
- **Anthropic C Compiler Case Study**: https://www.anthropic.com/engineering/building-c-compiler
- **Fastrender (Browser)**: https://github.com/wilsonzlin/fastrender
- **Harness Engineering**: https://openai.com/index/harness-engineering/

## Key Takeaways

1. **Planners and workers pattern** - Separate roles for planning vs execution
2. **Lock-free coordination** - Optimistic concurrency beats explicit locks
3. **Workers don't coordinate** - They just pick tasks and complete them
4. **Judge resets at cycle end** - Fresh evaluation combats drift
5. **Model specialization matters** - Different models excel at different roles
6. **Prompts > architecture** - Extensive prompt experimentation often matters more
7. **Remove complexity** - Best systems are simpler than expected
8. **Tests define what agents solve** - High-quality test harnesses are critical
9. **Periodic fresh starts** - Combat drift and tunnel vision
10. **Git-based coordination works** - Simple git workflows enable parallelization
