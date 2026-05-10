# Data & Metrics

## Contents
- Example Objects
- Specifying Input Keys
- Training Data Patterns
- DataLoader
- Built-in Datasets
- Defining Metrics
- Simple Metrics
- AI Feedback Metrics
- Using Trace in Metrics
- Evaluation Utilities

## Example Objects

The core data type in DSPy is `dspy.Example`. Examples are similar to Python dicts but have useful utilities for marking inputs vs labels. Modules return `Prediction`, a special subclass of `Example`.

```python
qa_pair = dspy.Example(question="This is a question?", answer="This is an answer.")

print(qa_pair.question)  # 'This is a question?'
print(qa_pair.answer)    # 'This is an answer.'
```

Examples support dictionary-style iteration via `keys()`, `values()`, `items()`.

## Specifying Input Keys

Use `with_inputs()` to mark specific fields as inputs (the rest are metadata or labels):

```python
# Single input
qa_pair.with_inputs("question")

# Multiple inputs
qa_pair.with_inputs("question", "answer")
```

Separate inputs from labels:

```python
article = dspy.Example(article="This is an article.", summary="This is a summary.").with_inputs("article")

input_only = article.inputs()    # Example with input fields only
label_only = article.labels()    # Example with non-input fields only
```

Exclude keys with `without()`:

```python
example = dspy.Example(context="...", question="?", answer="A.", rationale="R.").with_inputs("context", "question")
reduced = example.without("answer", "rationale")
```

Update values with dot notation: `example.context = "new context"`.

## Training Data Patterns

```python
# Basic training set
trainset = [
    dspy.Example(report="LONG REPORT 1", summary="short summary 1"),
    dspy.Example(report="LONG REPORT 2", summary="short summary 2"),
]

# Mark inputs for all examples
trainset = [ex.with_inputs("report") for ex in trainset]
```

**How much data do you need?**

- Minimum: ~10 example inputs (even without labels)
- Recommended: 50-100 examples
- Best results: 300-500 examples

## DataLoader

DSPy provides a `DataLoader` for loading datasets from various sources:

```python
from dspy.datasets import DataLoader

dl = DataLoader()
```

**Loading from HuggingFace:**

```python
code_alpaca = dl.from_huggingface("HuggingFaceH4/CodeAlpaca_20K")
train_dataset = code_alpaca['train']

# Specific splits
code_alpaca = dl.from_huggingface("HuggingFaceH4/CodeAlpaca_20K", split=["train", "test"])

# Single split returns a list of Examples
code_alpaca = dl.from_huggingface("HuggingFaceH4/CodeAlpaca_20K", split="train")

# Slicing
code_alpaca_80 = dl.from_huggingface("HuggingFaceH4/CodeAlpaca_20K", split="train[:80%]")
```

**Loading from CSV:**

```python
dataset = dl.from_csv("data.csv", fields=("instruction", "context", "response"), input_keys=("instruction", "context"))
```

**Splitting and sampling:**

```python
splits = dl.train_test_split(dataset, train_size=0.8)
sampled = dl.sample(dataset, n=5)
```

## Built-in Datasets

DSPy provides built-in dataset loaders:

```python
from dspy.datasets import HotPotQA

dataset = HotPotQA(train_seed=1, train_size=5, eval_seed=2023, dev_size=50, test_size=0)
trainset = [x.with_inputs('question') for x in dataset.train]
devset = [x.with_inputs('question') for x in dataset.dev]
```

Available built-in datasets: **HotPotQA** (multi-hop QA), **GSM8K** (math questions), **Color** (basic color dataset).

## Defining Metrics

A metric is a Python function that takes an `example` from your data and a `pred` from your DSPy program, returning a score (float/int/bool):

```python
def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()
```

The optional `trace` argument enables powerful tricks during optimization. When `trace is None`, the metric is used for evaluation. When `trace` is provided, it's used during bootstrapping.

## Simple Metrics

```python
# Boolean metric
def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()

# Multi-property metric with trace awareness
def validate_context_and_answer(example, pred, trace=None):
    answer_match = example.answer.lower() == pred.answer.lower()
    context_match = any((pred.answer.lower() in c) for c in pred.context)

    if trace is None:  # evaluation/optimization
        return (answer_match + context_match) / 2.0
    else:  # bootstrapping
        return answer_match and context_match
```

**Built-in metrics:**

- `dspy.evaluate.metrics.answer_exact_match` — Exact string match
- `dspy.evaluate.metrics.answer_passage_match` — Passage-level matching

## AI Feedback Metrics

For long-form outputs, use AI feedback from LMs to check multiple dimensions:

```python
class Assess(dspy.Signature):
    """Assess the quality of a tweet along the specified dimension."""
    assessed_text = dspy.InputField()
    assessment_question = dspy.InputField()
    assessment_answer = dspy.OutputField(desc="Yes or No")

gpt4T = dspy.OpenAI(model='gpt-4-1106-preview', max_tokens=1000, model_type='chat')

def metric(gold, pred, trace=None):
    question, answer, tweet = gold.question, gold.answer, pred.output

    engaging = "Does the assessed text make for a self-contained, engaging tweet?"
    correct = f"The text should answer `{question}` with `{answer}`. Does it?"

    with dspy.context(lm=gpt4T):
        correct_pred = dspy.Predict(Assess)(assessed_text=tweet, assessment_question=correct)
        engaging_pred = dspy.Predict(Assess)(assessed_text=tweet, assessment_question=engaging)

    correct = correct_pred.assessment_answer.lower() == 'yes'
    engaging = engaging_pred.assessment_answer.lower() == 'yes'

    score = (correct + engaging) if correct and (len(tweet) <= 280) else 0

    if trace is not None:
        return score >= 2
    return score / 2.0
```

## Using Trace in Metrics

During compilation, DSPy traces your LM calls. The trace contains inputs/outputs to each DSPy predictor:

```python
def validate_hops(example, pred, trace=None):
    hops = [example.question] + [outputs.query for *_, outputs in trace if 'query' in outputs]

    # Check no hop is too long
    if max([len(h) for h in hops]) > 100:
        return False

    # Check no repeated queries
    if any(dspy.evaluate.answer_exact_match_str(hops[idx], hops[:idx], frac=0.8) for idx in range(2, len(hops))):
        return False

    return True
```

## Evaluation Utilities

Run evaluations with DSPy's built-in `Evaluate` utility:

```python
from dspy.evaluate import Evaluate

# Set up the evaluator
evaluator = Evaluate(devset=devset, metric=your_metric, num_threads=1, display_progress=True, display_table=5)

# Launch evaluation
evaluator(your_program)
```

Or run manually:

```python
scores = []
for x in devset:
    pred = program(**x.inputs())
    score = metric(x, pred)
    scores.append(score)

print(f"Average score: {sum(scores) / len(scores):.3f}")
```
