# Evaluation & Metrics

## Defining Metrics

A DSPy metric is a Python function that takes an `example` (from your dataset) and the program's output `pred`, and returns a score quantifying quality.

### Basic Metric Signature

```python
def my_metric(example, pred, trace=None):
    """
    Args:
        example: A dspy.Example with ground truth
        pred: A dspy.Prediction from your program
        trace: Optional execution trace (used during optimization)
    Returns:
        float, int, or bool score (higher is better)
    """
    return example.answer.lower() == pred.answer.lower()
```

### Metric Behavior by Context

The `trace` parameter signals whether the metric is used for evaluation or optimization:

```python
def validate_context_and_answer(example, pred, trace=None):
    answer_match = example.answer.lower() == pred.answer.lower()
    context_match = any(pred.answer.lower() in c for c in pred.context)

    if trace is None:  # Evaluation or optimization scoring
        return (answer_match + context_match) / 2.0
    else:              # Bootstrapping — needs strict pass/fail
        return answer_match and context_match
```

When `trace is not None`, the metric is being used to validate bootstrapped demonstrations, so it should be strict (returning `True` only for fully correct outputs).

### Built-in Metrics

- `dspy.evaluate.metrics.answer_exact_match`: Case-insensitive exact string match
- `dspy.evaluate.metrics.answer_passage_match`: Checks if answer appears within a passage
- `dspy.SemanticF1()`: LM-based semantic F1 score for long-form outputs
- `dspy.CompleteAndGrounded`: Checks completeness and groundedness of outputs

## The Evaluate Utility

The `Evaluate` class provides parallel evaluation with progress tracking:

```python
from dspy.evaluate import Evaluate

evaluator = Evaluate(
    devset=devset,
    num_threads=4,
    display_progress=True,
    display_table=5,  # Show top 5 examples in a table
)

score = evaluator(program, metric=my_metric)
print(f"Score: {score}")
```

### Parameters

- `devset`: Examples to evaluate on
- `num_threads`: Parallel threads (default: 1)
- `display_progress`: Show progress bar
- `display_table`: Number of examples to display in results table
- `max_errors`: Stop after N errors
- `provide_traceback`: Include tracebacks in error reporting

## AI-Based Metrics

For complex outputs, use LLMs as judges:

```python
class Assess(dspy.Signature):
    """Assess the quality of text along a specified dimension."""

    assessed_text = dspy.InputField()
    assessment_question = dspy.InputField()
    assessment_answer: bool = dspy.OutputField()

def tweet_metric(gold, pred, trace=None):
    question, answer, tweet = gold.question, gold.answer, pred.output

    # Check correctness
    correct_q = f"The text should answer '{question}' with '{answer}'. Does it?"
    correct = dspy.Predict(Assess)(assessed_text=tweet, assessment_question=correct_q)

    # Check engagement
    engaging_q = "Does the assessed text make for a self-contained, engaging tweet?"
    engaging = dspy.Predict(Assess)(assessed_text=tweet, assessment_question=engaging_q)

    # Length constraint
    length_ok = len(tweet) <= 280

    return (correct.assessment_answer + engaging.assessment_answer + length_ok) / 3.0
```

## GEPA Feedback Metrics

GEPA requires metrics that return both a score and textual feedback:

```python
def gepa_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
    score = compute_accuracy(gold, pred)

    # Predictor-level feedback (when optimizing individual predictors)
    if pred_name is not None:
        if score < 1.0:
            feedback = f"Predictor '{pred_name}' produced incorrect output. " \
                       f"Expected: {gold.answer}, Got: {pred.answer}"
        else:
            feedback = f"Predictor '{pred_name}' produced correct output."
        return {"score": score, "feedback": feedback}

    # Program-level feedback
    feedback = f"Overall score: {score}. "
    if hasattr(pred, 'reasoning'):
        feedback += f"Reasoning: {pred.reasoning[:200]}"
    return {"score": score, "feedback": feedback}
```

Key points:
- GEPA calls the metric with `pred_name` and `pred_trace` when optimizing individual predictors
- If predictor-level feedback is unavailable, program-level feedback is acceptable
- If no feedback dict is returned, GEPA defaults to: `f"This trajectory got a score of {score}."`
- The metric must accept five arguments: `(gold, pred, trace, pred_name, pred_trace)`

## Data Handling

### Example Objects

```python
qa_pair = dspy.Example(question="This is a question?", answer="This is an answer.")
print(qa_pair.question)   # "This is a question?"
print(qa_pair.answer)     # "This is an answer."
```

### Specifying Input Keys

```python
# Mark specific fields as inputs (rest are labels/metadata)
qa_pair = qa_pair.with_inputs("question")

# Access only input fields
input_only = qa_pair.inputs()

# Access only label fields
label_only = qa_pair.labels()
```

### Building Trainsets

```python
trainset = [
    dspy.Example(report="LONG REPORT 1", summary="short summary 1").with_inputs("report"),
    dspy.Example(report="LONG REPORT 2", summary="short summary 2").with_inputs("report"),
]
```

## Saving and Loading Programs

After optimization, save the compiled program:

```python
optimized_program.save("my_optimized_program.json")
```

The JSON file contains all parameters — instructions, demonstrations, and configuration for every predictor. It is human-readable.

Load it later:

```python
loaded_program = MyProgramClass()
loaded_program.load(path="my_optimized_program.json")
```

## Choosing an Optimizer

Guidance based on data size and goals:

- **~10 examples**: `BootstrapFewShot` — bootstraps demonstrations from minimal data
- **50+ examples**: `BootstrapFewShotWithRandomSearch` — random search over demo combinations
- **Instruction-only (zero-shot)**: `MIPROv2` with `max_bootstrapped_demos=0, max_labeled_demos=0`
- **200+ examples, long runs**: `MIPROv2` with 40+ trials — Bayesian Optimization needs data
- **Rich feedback available**: `GEPA` — leverages textual diagnostics for sample-efficient optimization
- **Need efficiency**: `BootstrapFinetune` — distill prompt program into fine-tuned small model
- **Best of both worlds**: `BetterTogether` — combine prompt + weight optimization

A typical simple optimization run costs ~$2 and takes ~10 minutes, but costs vary with LM, dataset size, and configuration.
