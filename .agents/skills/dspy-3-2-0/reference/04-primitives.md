# Primitives

DSPy's core data types that flow through modules, optimizers, and evaluation pipelines.

## dspy.Example

The fundamental data container for DSPy training and evaluation data. Roughly one row from a dataset — behaves like a dictionary with dot-access.

```python
example = dspy.Example(
    question="What is the capital of France?",
    answer="Paris",
).with_inputs("question")

print(example.question)      # "What is the capital of France?"
print(example.answer)        # "Paris"
print(example.inputs())      # Example with only input keys
print(example.labels())      # Example with only non-input keys (labels)
```

**Key Methods:**

- `with_inputs(*keys)` — Mark specific fields as inputs (rest are labels/metadata)
- `inputs()` — Return a new Example containing only input fields
- `labels()` — Return a new Example containing only non-input fields
- `toDict()` — Convert to plain dictionary

**Building trainsets:**

```python
trainset = [
    dspy.Example(question="What is 2+2?", answer="4").with_inputs("question"),
    dspy.Example(question="What is 3+3?", answer="6").with_inputs("question"),
]
```

## dspy.Prediction

Output of a DSPy module call. Inherits from `Example` with additional capabilities:

```python
result = predict(question="What is 2+2?")
print(result.answer)          # "4"
print(result._completions)    # All raw completions (if available)
print(result._lm_usage)       # Token usage info
```

**Additional features:**
- Supports comparison operations (`<`, `>`, `<=`, `>=`) when a `score` field exists
- Arithmetic operations on `score` values
- `copy(**kwargs)` — Shallow copy with optional field overrides

## dspy.Tool

Wraps a Python function for LLM tool calling (function calling).

```python
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Sunny, 75F in {city}"

tool = dspy.Tool(get_weather)
```

**Constructor:** `dspy.Tool(func: Callable, name=None, desc=None, args=None, arg_types=None, arg_desc=None)`

Automatically infers `name`, `desc`, `args`, and `arg_types` from the function's signature and docstring. Override any of them explicitly.

## dspy.ToolCalls

Output type for manual tool handling. Represents a list of tool calls returned by the LM.

```python
class ToolSignature(dspy.Signature):
    question: str = dspy.InputField()
    tools: list[dspy.Tool] = dspy.InputField()
    outputs: dspy.ToolCalls = dspy.OutputField()

predictor = dspy.Predict(ToolSignature)
response = predictor(question="What's the weather?", tools=[weather_tool])

# Execute tool calls (dspy >= 3.0.4b2)
for call in response.outputs.tool_calls:
    result = call.execute()
```

## dspy.Image

Multimodal image type for vision models:

```python
img = dspy.Image(url="https://example.com/photo.jpg")
img = dspy.Image(url=open("local.png", "rb").read())  # bytes
img = dspy.Image(url=pil_image_instance)               # PIL Image
```

Supports HTTP(S)/GS URLs, local file paths, raw bytes, and PIL instances.

## dspy.Audio

Multimodal audio type for speech models:

```python
audio = dspy.Audio(url="https://example.com/speech.mp3")
```

## dspy.Code

Specialized code type for code generation tasks:

```python
code = dspy.Code("def hello():\n    print('world')", language="python")
```

## dspy.History

Conversation history type for multi-turn interactions:

```python
history = dspy.History(messages=[
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
])
```
