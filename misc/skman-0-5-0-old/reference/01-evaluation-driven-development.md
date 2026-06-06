# Evaluation-Driven Skill Development

## Contents
- Why Evaluations Matter
- The Five-Step Process
- Evaluation Structure Template
- Iterative Refinement with Two Agents
- Gathering Team Feedback

## Why Evaluations Matter

Build evaluations **before** writing extensive skill documentation. This ensures the skill solves real problems rather than documenting imagined ones. Without evaluations, it's easy to over-engineer a skill with content that no agent actually needs, or miss critical gaps that cause failures in real usage.

**Evaluation-driven development** flips the traditional approach:
- **Traditional**: Write all instructions → hope they work → fix after failures
- **Evaluation-driven**: Identify failure modes → create test scenarios → write minimal instructions to pass → iterate

## The Five-Step Process

### Step 1: Identify Gaps

Run the target agent on representative tasks **without** the skill. Document specific failures or missing context. Look for:
- Tasks where the agent makes repeated mistakes
- Information you had to provide manually multiple times
- Procedural knowledge that's hard to articulate in a single prompt

### Step 2: Create Evaluations

Build at least three scenarios that test the identified gaps. Each scenario should:
- Represent a real task an agent would encounter
- Have a clear expected outcome
- Be reproducible across agent sessions

### Step 3: Establish Baseline

Measure the agent's performance without the skill. This gives you a concrete number to improve against and helps determine whether the skill is actually needed for each scenario.

### Step 4: Write Minimal Instructions

Create just enough content in SKILL.md to address the gaps and pass evaluations. Resist the urge to document everything — start with the minimum that works. If an evaluation passes without additional instructions, don't add them.

### Step 5: Iterate

Execute evaluations, compare against baseline, and refine. Each iteration should be driven by observed failures, not assumptions about what the agent might need.

## Evaluation Structure Template

Use this structure for each evaluation scenario:

```markdown
## Scenario: <name>

**Task**: What the user asks the agent to do
**Expected Outcome**: Specific, verifiable result
**Success Criteria**:
- [ ] Criterion 1 (e.g., "Output contains correct version number")
- [ ] Criterion 2 (e.g., "No hallucinated API methods")
- [ ] Criterion 3 (e.g., "Uses the recommended approach, not alternatives")

**Baseline Score**: X/3 (without skill)
**Current Score**: Y/3 (with skill)
```

## Iterative Refinement with Two Agents

The most effective skill development process involves alternating between two agent roles:

**Agent A (the refiner)**: Works with you to design and refine the skill. This agent helps write instructions, reorganize content, and suggest improvements based on your observations.

**Agent B (the tester)**: A fresh agent instance that uses the skill to perform real tasks. Its behavior reveals gaps that Agent A can't anticipate.

### The Cycle

1. **Complete a task with Agent A** — Work through a problem normally. Notice what context you repeatedly provide, what preferences you explain, what procedural knowledge you share.

2. **Identify the reusable pattern** — After completing the task, extract what would be useful for similar future tasks.

3. **Ask Agent A to create or update the skill** — "Create a skill that captures this pattern." The agent understands skill format natively — no special prompts needed.

4. **Review for conciseness** — Check that Agent A hasn't added unnecessary explanations. Ask: "Remove the explanation about what X means — the target agent already knows that."

5. **Test with Agent B** — Load the skill in a fresh agent session and run related tasks. Observe whether Agent B finds the right information, applies rules correctly, and handles edge cases.

6. **Return to Agent A with observations** — "When Agent B used this skill, it forgot to do X. Should we make that rule more prominent?"

7. **Repeat** — Each cycle improves the skill based on real agent behavior, not assumptions.

### Observing Agent Behavior

As you iterate, pay attention to how the test agent actually uses the skill:

- **Unexpected exploration paths**: Does the agent read files in an order you didn't anticipate? Your structure might not be intuitive.
- **Missed connections**: Does the agent fail to follow references to important files? Your links might need to be more explicit.
- **Overreliance on certain sections**: If the agent repeatedly reads the same file, consider whether that content should be in the main SKILL.md instead.
- **Ignored content**: If the agent never accesses a bundled reference file, it might be unnecessary or poorly signaled in the main instructions.

## Gathering Team Feedback

When skills are used by multiple people:

1. Share the skill with teammates and observe their usage
2. Ask three questions:
   - Does the skill activate when expected?
   - Are instructions clear?
   - What's missing?
3. Incorporate feedback to address blind spots in your own usage patterns

Different users will trigger different paths through the skill, revealing gaps that single-user testing misses.
