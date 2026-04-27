# Modules API Reference

A **DSPy module** is a building block for programs that use LMs. Each built-in module abstracts a prompting technique and is generalized to handle any signature. Modules have learnable parameters (instructions, demonstrations, LM weights) and can be composed into larger programs.

## dspy.Module — Base Class

All DSPy programs inherit from `dspy.Module`. It provides the composition infrastructure:

```python
class MyProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict("question -> answer")

    def forward(self, question):
        return self.predictor(question=question)
```

**Key Methods:**

- `__call__(*args, **kwargs) -> Prediction` — Invoke the module (calls `forward`)
- `acall(*args, **kwargs)` — Async invocation
- `predictors()` — Iterate over all `Predict` instances in the module tree
- `named_predictors()` — Yield `(name, predictor)` pairs with path-based names
- `named_parameters()` — Yield all learnable parameters
- `parameters()` — List of all learnable parameters
- `save(path)` / `load(path)` — Serialize/deserialize program state
- `dump_state()` / `load_state(state)` — In-memory state management
- `set_lm(lm)` — Attach an LM to the entire module tree
- `get_lm()` — Retrieve the attached LM
- `inspect_history()` — View LM call history for this module
- `batch(...)` — Batch process examples
- `deepcopy()` — Deep copy the module
- `reset_copy()` — Copy with reset parameters
- `map_named_predictors(fn)` — Apply a function to each predictor

**Attributes:**

- `callbacks` — Registered callback handlers for instrumentation
- `history` — List of LM call history entries

## dspy.Predict — Basic Predictor

The fundamental building block. All other DSPy modules are built using `Predict`. Does not modify the signature.

```python
classify = dspy.Predict("sentence -> sentiment: bool")
result = classify(sentence="It's a charming journey.")
print(result.sentiment)  # True
```

**Constructor:** `dspy.Predict(signature, callbacks=None, **config)`

Config keys include `temperature`, `max_tokens`, and any other LM generation parameter.

**Key behavior:**
- Stores instructions and demonstrations as learnable parameters
- Calls the adapter to format the prompt
- Parses the LM response into a `Prediction` object
- Inherits from both `Module` and `Parameter` (making it optimizable)

## dspy.ChainOfThought — Step-by-Step Reasoning

Teaches the LM to reason step-by-step before producing output. Internally adds a `reasoning` field to the signature.

```python
summarize = dspy.ChainOfThought("document -> summary")
result = summarize(document=long_text)
print(result.reasoning)  # Internal reasoning steps
print(result.summary)    # Final output
```

**Constructor:** `dspy.ChainOfThought(signature, rationale_field=None, rationale_field_type=str, **config)`

Swapping `ChainOfThought` for `Predict` often improves quality without any other changes.

## dspy.ReAct — Tool-Using Agent

Implements the Reasoning and Acting pattern. The LM iteratively reasons about the current situation and decides which tools to call.

```python
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Sunny, 75F"

agent = dspy.ReAct(
    signature="question -> answer",
    tools=[get_weather],
    max_iters=10,
)
result = agent(question="What's the weather in Tokyo?")
print(result.answer)
print("Trajectory:", result.trajectory)  # Full reasoning + tool call history
```

**Constructor:** `dspy.ReAct(signature: type[Signature], tools: list[Callable], max_iters: int = 20)`

**Features:**
- Automatic reasoning with step-by-step thought process
- Tool selection based on situational analysis
- Iterative execution with multiple tool calls
- Built-in error recovery for failed tool calls
- Trajectory tracking (complete history of reasoning and tool calls)
- Generalized to work over any signature via signature polymorphism

## dspy.CodeAct — Code Interpreter Agent

Combines code execution with predefined tools. Inherits from both `ReAct` and `ProgramOfThought`.

```python
def factorial(n):
    """Calculate factorial of n"""
    if n == 1:
        return 1
    return n * factorial(n-1)

act = dspy.CodeAct("n -> factorial", tools=[factorial])
result = act(n=5)  # Returns 120
```

**Constructor:** `dspy.CodeAct(signature, tools: list[Callable], max_iters: int = 5, interpreter=None)`

Uses a sandboxed Python interpreter (Deno/Pyodide/WASM by default). Custom `CodeInterpreter` implementations can be provided.

## dspy.ProgramOfThought — Code Execution

Teaches the LM to output Python code whose execution results dictate the response. Requires Deno to be installed.

```python
pot = dspy.ProgramOfThought("question -> answer", max_iters=3)
result = pot(question="What is 1+1?")
print(result.answer)  # 2
```

**Constructor:** `dspy.ProgramOfThought(signature, max_iters: int = 3, interpreter=None)`

## dspy.RLM — Recursive Language Model

Uses a sandboxed REPL to let the LM programmatically explore large contexts through code execution. The LM writes Python code to examine data, call sub-LLMs for semantic analysis, and build up answers iteratively.

```python
rlm = dspy.RLM("context, query -> output", max_iterations=10)
result = rlm(context="...very long text...", query="What is the magic number?")
print(result.output)
```

**Constructor:** `dspy.RLM(signature, max_iterations: int = 20, max_llm_calls: int = 50, max_output_chars: int = 10000, verbose: bool = False, tools=None, sub_lm=None, interpreter=None)`

**Parameters:**
- `max_iterations`: Maximum exploration steps
- `max_llm_calls`: Budget for sub-LM calls within the REPL
- `max_output_chars`: Output size limit
- `sub_lm`: Separate LM for sub-calls (defaults to main LM)
- `tools`: Optional tools available in the REPL

Note: RLM instances are not thread-safe with custom interpreters. Use the default `PythonInterpreter` which creates a fresh instance per call.

## dspy.BestOfN — Multi-Rollout Selection

Runs a module up to N times with different rollout IDs at `temperature=1.0` and returns the best prediction or the first that passes a threshold.

```python
base = dspy.Predict("question -> answer")
best = dspy.BestOfN(module=base, N=5, reward_fn=my_reward, threshold=0.8)
result = best(question="What is 2+2?")
```

**Constructor:** `dspy.BestOfN(module: Module, N: int, reward_fn: Callable[[dict, Prediction], float], threshold: float, fail_count: int | None = None)`

Each attempt uses a fresh rollout ID and `temperature=1.0` to bypass caches.

## dspy.Refine — Iterative Refinement

Runs a module up to N times, selecting the best prediction. If no prediction meets the threshold, generates feedback to improve future predictions.

```python
base = dspy.Predict("question -> answer")
refined = dspy.Refine(module=base, N=5, reward_fn=my_reward, threshold=0.9)
result = refined(question="Explain quantum computing.")
```

**Constructor:** `dspy.Refine(module: Module, N: int, reward_fn: Callable[[dict, Prediction], float], threshold: float, fail_count: int | None = None)`

Key difference from `BestOfN`: automatically generates improvement feedback when no prediction meets the threshold.

## dspy.MultiChainComparison — Multi-Output Comparison

Compares multiple ChainOfThought outputs to produce a final prediction. Used internally by some optimizers.

```python
# Takes a signature and M number of student attempts
mcc = dspy.MultiChainComparison(signature, M=3, temperature=0.7)
```

**Constructor:** `dspy.MultiChainComparison(signature, M: int = 3, temperature: float = 0.7, **config)`

Internally appends M reasoning attempt fields to the signature, then asks the LM to compare them and produce a final answer.

## dspy.Parallel — Multi-Threaded Execution

Utility class for parallel, multi-threaded execution of (module, example) pairs.

```python
parallel = dspy.Parallel(num_threads=4)
predict = dspy.Predict("question -> answer")
results = parallel([
    (predict, dspy.Example(question="1+1").with_inputs("question")),
    (predict, dspy.Example(question="2+2").with_inputs("question")),
])
```

**Constructor:** `dspy.Parallel(num_threads=None, max_errors=None, access_examples=True, return_failed_examples=False, provide_traceback=None, disable_progress_bar=False, timeout: int = 120, straggler_limit: int = 3)`

Supports robust error handling, optional progress tracking, and can return failed examples with exceptions.

## Module Composition Patterns

Modules compose naturally into programs:

```python
class RAG(dspy.Module):
    def __init__(self, num_docs=5):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_docs)
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate_answer(context=context, question=question)

program = RAG()
result = program(question="When was the first FIFA World Cup?")
```

Key composition patterns:
- **Sequential**: Chain modules in `forward()`
- **Parallel**: Use `dspy.Parallel` for concurrent execution
- **Conditional**: Branch based on intermediate results
- **Iterative**: Loop with `Refine` or `BestOfN`
