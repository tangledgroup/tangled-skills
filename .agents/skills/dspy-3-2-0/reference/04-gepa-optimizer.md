# GEPA Reflective Optimizer

GEPA (Genetic-Pareto) is a reflective optimizer that uses LLMs to reflect on execution traces and evolve prompt instructions. Proposed in "GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning" (Agrawal et al., 2025, arxiv:2507.19457).

GEPA's key innovation is using **rich textual feedback** (not just scalar scores) as the optimization signal, combined with **Pareto-frontier candidate selection** to maintain diversity and avoid local optima.

## How GEPA Works — The Algorithm

### 1. Reflective Prompt Mutation

GEPA captures full execution traces (inputs, outputs, failures, intermediate steps) of the DSPy program. For a chosen predictor module, it:

1. Extracts the sub-trace corresponding to that specific predictor
2. Feeds the trace to a **reflection LM** along with the current instruction and textual feedback
3. The reflection LM proposes a new instruction tailored to observed failures

The default instruction proposer uses this meta-prompt template:

```
I provided an assistant with the following instructions to perform a task for me:
```
<curr_instructions>
```

The following are examples of different task inputs provided to the assistant along with the assistant's response for each of them, and some feedback on how the assistant's response could be better:
```
<inputs_outputs_feedback>
```

Your task is to write a new instruction for the assistant.

Read the inputs carefully and identify the input format and infer detailed task description about the task I wish to solve with the assistant.

Read all the assistant responses and the corresponding feedback. Identify all niche and domain specific factual information about the task and include it in the instruction, as a lot of it may not be available to the assistant in the future. The assistant may have utilized a generalizable strategy to solve the task, if so, include that in the instruction as well.

Provide the new instructions within ``` blocks.
```

### 2. Rich Textual Feedback as Optimization Signal

GEPA metrics return `dspy.Prediction(score=float, feedback=str)` — both a numerical score AND natural-language feedback explaining why. This preserves diagnostic information that scalar rewards discard.

Feedback can come from:
- Evaluation logs and error messages
- Failed unit tests or schema validations
- Stage-specific failures in multi-step pipelines
- LLM-as-a-judge assessments for non-verifiable tasks
- Decomposed multi-objective scores (correctness, latency, safety)

### 3. Pareto-Based Candidate Selection

Instead of evolving only the single best candidate, GEPA maintains a **Pareto frontier**: the set of candidates that achieve the highest score on at least one evaluation instance. Each iteration samples the next candidate from this frontier with probability proportional to coverage, ensuring both exploration and retention of complementary strategies.

### Complete Algorithm Summary

1. **Initialize** the candidate pool with the unoptimized program (map each predictor name to its current instruction)
2. **Iterate**:
   - **Sample a candidate** from the Pareto frontier
   - **Sample a minibatch** of `reflection_minibatch_size` examples from the train set
   - **Collect execution traces + feedbacks** by rolling out the candidate on the minibatch
   - **Select a module** of the candidate for targeted improvement (via component selector)
   - **LLM Reflection**: Propose a new instruction for the targeted module using the reflective meta-prompt and gathered feedback
   - **Roll out the new candidate** on the minibatch; if improved, evaluate on the Pareto validation set
   - **Update the candidate pool/Pareto frontier** with the new candidate
   - **[Optional] System-aware merge/crossover**: Combine best-performing modules from distinct lineages
3. **Continue** until rollout or metric budget is exhausted
4. **Return** the candidate with the best aggregate performance on validation

## GEPA Metric Interface

GEPA requires a special metric that accepts five arguments and returns score + feedback:

```python
from typing import Optional
from dspy import Example, Prediction

def my_metric(
    gold: Example,
    pred: Prediction,
    trace: Optional["DSPyTrace"] = None,
    pred_name: Optional[str] = None,
    pred_trace: Optional["DSPyTrace"] = None,
) -> float | dict[str, str]:
    """
    - gold: The ground truth example
    - pred: The predicted output
    - trace: Full program execution trace (optional)
    - pred_name: Name of the predictor currently being optimized
    - pred_trace: Sub-trace for the specific predictor being optimized

    Return either:
    - float: Just a score (GEPA auto-generates feedback from the score)
    - dict with 'score' (float) and 'feedback' (str): Score + textual feedback
    """
    score = compute_score(gold, pred)

    # Provide predictor-level feedback when optimizing individual predictors
    if pred_name is not None and pred_trace is not None:
        feedback = analyze_predictor_failure(pred_name, pred_trace, gold, pred)
        return {"score": score, "feedback": feedback}

    # Program-level feedback
    feedback = f"Score: {score}. {'Correct.' if score == 1.0 else 'Review the output for errors.'}"
    return {"score": score, "feedback": feedback}
```

If no feedback is returned, GEPA defaults to: `f"This trajectory got a score of {score}."`

## Configuration

### Budget Configuration

Exactly one of these must be set:

- `auto`: Preset — "light" (quick), "medium" (balanced), "heavy" (thorough)
- `max_full_evals`: Maximum full validation evaluations
- `max_metric_calls`: Maximum individual metric invocations

### Core Parameters

- `metric`: GEPAFeedbackMetric function (required)
- `reflection_lm`: LM for reflection (required, should be strong — e.g., GPT-5 at temperature=1.0)
- `reflection_minibatch_size`: Examples per reflection step (default: 3)
- `candidate_selection_strategy`: "pareto" (default) or "current_best"
- `skip_perfect_score`: Skip examples scoring perfectly during reflection (default: True)
- `use_merge`: Enable merge-based optimization (default: True)
- `max_merge_invocations`: Max merge attempts (default: 5)
- `component_selector`: "round_robin" (default), "all", or custom selector
- `failure_score` / `perfect_score`: Metric range boundaries (default: 0.0 / 1.0)
- `seed`: Random seed for reproducibility (default: 0)

```python
import dspy

gepa = dspy.GEPA(
    metric=my_metric,
    reflection_lm=dspy.LM(model='gpt-5', temperature=1.0, max_tokens=32000),
    auto="medium",
)
optimized = gepa.compile(student, trainset=trainset, valset=valset)
```

### Train/Val Split

GEPA uses the **trainset** for reflective updates and the **valset** for tracking Pareto scores. If no valset is provided, GEPA uses the trainset for both.

## Advanced Features

### Custom Instruction Proposers

Implement the `ProposalFn` protocol to customize how new instructions are generated:

```python
from dspy.teleprompt.gepa.gepa_utils import ReflectiveExample

class CustomProposer:
    def __call__(
        self,
        candidate: dict[str, str],                          # Current instruction per component
        reflective_dataset: dict[str, list[ReflectiveExample]],  # Examples with feedback
        components_to_update: list[str]                     # Which components to improve
    ) -> dict[str, str]:                                    # New instructions
        updated = {}
        for name in components_to_update:
            examples = reflective_dataset[name]
            current = candidate[name]
            # Custom logic to generate improved instruction
            updated[name] = generate_improved_instruction(current, examples)
        return updated
```

Built-in options:
- **Default Proposer**: Standard GEPA proposer (used when `instruction_proposer=None`)
- **MultiModalInstructionProposer**: Handles `dspy.Image` inputs

### Custom Component Selectors

Control which predictors are optimized each iteration:

- `"round_robin"`: Cycles through predictors sequentially (default)
- `"all"`: Optimizes all predictors simultaneously
- Custom `ReflectionComponentSelector`: LLM-driven selection based on optimization state

### Merge-Based Optimization

When `use_merge=True`, GEPA can combine best-performing modules from different candidate lineages. This is a form of crossover that propagates successful improvements across the population.

### Inference-Time Search

GEPA can act as test-time search:

```python
gepa = dspy.GEPA(metric=metric, track_stats=True, track_best_outputs=True)
new_prog = gepa.compile(student, trainset=my_tasks, valset=my_tasks)

# Access Pareto frontier and best outputs
pareto_frontier = new_prog.detailed_results.val_aggregate_scores
best_outputs = new_prog.detailed_results.best_outputs_valset
highest_scores = new_prog.detailed_results.highest_score_achieved_per_val_task
```

### Tracking and Logging

- `track_stats=True`: Access detailed optimization results via `program.detailed_results`
- `log_dir`: Save logs and enable checkpoint resuming
- `use_wandb=True`: Weights & Biases experiment tracking
- `use_mlflow=True`: MLflow integration

## Designing GEPA-Friendly Feedback

Practical recipes for effective feedback:

- **Leverage existing artifacts**: Logs, unit tests, evaluation scripts, profiler outputs
- **Decompose outcomes**: Break scores into per-objective components (correctness, latency, cost, safety)
- **Expose trajectories**: Label pipeline stages with pass/fail and salient errors
- **Ground in checks**: Use automatic validators (schemas, simulators) or LLM-as-a-judge
- **Prioritize clarity**: Focus on error coverage and decision points over complexity

Examples:
- **Document retrieval**: List correctly retrieved, incorrect, or missed documents
- **Multi-objective tasks**: Decompose aggregate scores to reveal tradeoffs
- **Code generation pipelines**: Expose stage-specific failures (parse → compile → run → evaluate)
