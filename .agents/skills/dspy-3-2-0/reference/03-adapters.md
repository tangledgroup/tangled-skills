# Adapters

Adapters are the interface layer between DSPy modules and Language Models. They handle the complete transformation pipeline from DSPy inputs to LM calls and back to structured outputs.

## What Adapters Do

- Transform user inputs and signatures into properly formatted LM prompts
- Instruct the LM to format responses in a specific structure
- Parse LM outputs into dictionaries matching the signature's output fields
- Enable/disable native LM features (function calling, citations)
- Handle conversation history, few-shot examples, and custom type processing

## The Adapter Flow

1. User calls a DSPy module with inputs
2. Inner `dspy.Predict` is invoked
3. `Predict` calls **Adapter.format()** to convert signature, inputs, and demos into multi-turn messages
4. Messages are sent to the LM via `dspy.LM` (thin wrapper around `litellm`)
5. LM generates a response
6. **Adapter.parse()** converts the response into structured `Prediction` outputs

## Configuration

```python
# Global adapter
dspy.configure(adapter=dspy.ChatAdapter())

# Per-module or scoped
with dspy.context(adapter=dspy.JSONAdapter()):
    result = predict(question="What is 2+2?")
```

If no adapter is specified, every `dspy.Predict.__call__` defaults to `dspy.ChatAdapter`.

## Inspecting Adapter Output

View the messages sent to the LM:

```python
signature = dspy.Signature("question -> answer")
adapter = dspy.ChatAdapter()
print(adapter.format(signature, demos=[], inputs={"question": "What is 2+2?"}))
```

The output uses delimiter patterns like `[[ ## field_name ## ]]` to clearly separate fields:

```
Your input fields are:
1. `question` (str):
Your output fields are:
1. `answer` (str):
All interactions will be structured in the following way...

[[ ## question ## ]]
What is 2+2?

[[ ## answer ## ]]
...

[[ ## completed ## ]]
```

Fetch just the system message:

```python
system_msg = dspy.ChatAdapter().format_system_message(signature)
```

## Adapter Types

### ChatAdapter (Default)

Formats DSPy signatures into a format compatible with most language models using `[[ ## field_name ## ]]` delimiter patterns.

- Structures inputs and outputs with clear field headers
- Provides automatic fallback to JSONAdapter if chat format fails
- Base class for XMLAdapter

**Constructor:** `dspy.ChatAdapter(callbacks=None, use_native_function_calling=False, native_response_types=None, use_json_adapter_fallback=True)`

### JSONAdapter

Uses native function calling by default. Formats the request as a structured JSON schema that LMs with tool-calling support can parse reliably.

- Uses native function calling (`use_native_function_calling=True` by default)
- Better for models with strong JSON/tool-calling capabilities
- Inherits from ChatAdapter

**Constructor:** `dspy.JSONAdapter(callbacks=None, use_native_function_calling=True)`

### XMLAdapter

Wraps fields in XML tags instead of delimiter patterns. Uses regex-based parsing (`<fieldname>content</fieldname>`).

- Better for models that handle XML well
- Cleaner parsing for nested/structured content
- Inherits from ChatAdapter

**Constructor:** `dspy.XMLAdapter(callbacks=None)`

### TwoStepAdapter

Two-stage adapter for reasoning models (e.g., o3-mini, DeepSeek R1) that struggle with structured outputs:

1. Main LM generates a natural-language response using a simple prompt
2. A smaller extraction LM uses ChatAdapter to parse structured data from the response

```python
lm = dspy.LM(model="openai/o3-mini", max_tokens=16000, temperature=1.0)
adapter = dspy.TwoStepAdapter(extraction_model=dspy.LM("openai/gpt-4o-mini"))
dspy.configure(lm=lm, adapter=adapter)

program = dspy.ChainOfThought("question -> answer")
result = program(question="What is the capital of France?")
```

**Constructor:** `dspy.TwoStepAdapter(extraction_model: BaseLM, **kwargs)`

## Custom Adapters

Extend the base `Adapter` class to implement custom formatting/parsing:

```python
class MyAdapter(dspy.Adapter):
    def __call__(self, lm, lm_kwargs, signature, demos, inputs):
        # Format inputs into messages
        messages = self.format_messages(signature, demos, inputs)
        # Call the LM
        response = lm(messages, **lm_kwargs)
        # Parse response
        return self.parse(response, signature)
```

## Native Function Calling

The `use_native_function_calling` flag (available on Adapter, ChatAdapter, JSONAdapter) controls whether to use the LM's native tool/function calling interface:

- `True`: Uses OpenAI-style function calling format
- `False`: Uses text-based prompting with structured delimiters

JSONAdapter enables this by default. ChatAdapter disables it by default.
