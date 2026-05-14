# Advanced Signatures

## Contents
- Prompt Structure
- Field Options (desc, prefix, format)
- Inspecting Generated Prompts
- Internal Signatures and Signature.replace
- Updating Multiple Signatures
- Custom LM Clients

## Prompt Structure

DSPy automatically constructs prompts from signatures. For `dspy.Predict("question -> answer")`, the generated prompt follows this format:

```
Given the fields `question`, produce the fields `answer`.

---

Follow the following format.

Question: ${question}
Answer: ${answer}

---

Question:
```

Different modules apply different instructional templates. `dspy.ChainOfThought` injects a `rationale` field before the output. `dspy.ReAct` uses a Thought/Action/Observation format. `dspy.ProgramOfThought` generates Python code with execution feedback loops.

## Field Options (desc, prefix, format)

Both `InputField` and `OutputField` accept three optional parameters:

- **`desc`** — Description of the field, included in the prompt as guidance
- **`prefix`** — Placeholder text that replaces the default `${field_name}` label in the prompt
- **`format`** — Method to handle non-string inputs (e.g., lists)

```python
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""

    question = dspy.InputField()
    answer = dspy.OutputField(
        desc="often between 1 and 5 words",
        prefix="Question's Answer:",
    )
```

Generated prompt:

```
Answer questions with short factoid answers.

---

Follow the following format.

Question: ${question}
Question's Answer: often between 1 and 5 words

---

Question:
```

## Inspecting Generated Prompts

After running a program, inspect the prompts DSPy sent to the LM:

```python
turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.configure(lm=turbo)

predictor = dspy.Predict(BasicQA)
pred = predictor(question="Are both Cangzhou and Qionghai in Hebei?")

# Inspect last N prompts
turbo.inspect_history(n=1)
```

Access raw history via `turbo.history[0]`, which contains `prompt`, `response`, and `kwargs` (including the full messages payload, model, temperature, etc.).

## Internal Signatures and Signature.replace

DSPy uses signatures internally to define optimizer tasks. You can access and replace any internal signature using the `dspy.Signature.replace` context manager:

```python
from dspy.teleprompt import copro_optimizer
import dspy

class MyBasicGenerateInstruction(copro_optimizer.BasicGenerateInstruction):
    """
    <PERSONA>
    You are an instruction optimizer for large language models.
    </PERSONA>
    <TASK>
    I will give you a ``signature`` of fields (inputs and outputs) in English.
    Your task is to propose an instruction that will lead a good language
    model to perform the task well. Don't be afraid to be creative, but the
    new instruction you propose should be clear and concise.
    </TASK>
    """
    basic_instruction = dspy.InputField(
        desc="The unoptimized instruction. New instructions should achieve the same goals."
    )

with copro_optimizer.BasicGenerateInstruction.replace(MyBasicGenerateInstruction):
    teleprompter = COPRO(prompt_model=prompt_model, metric=metric, breadth=10, depth=10)
    compiled = teleprompter.compile(program.deepcopy(), trainset=trainset, eval_kwargs=kwargs)
```

The replacement is active only within the context manager.

## Updating Multiple Signatures

Use `dspy.update_signatures` to replace multiple internal signatures at once:

```python
class MyGenerateInstruction(copro_optimizer.GenerateInstructionGivenAttempts):
    """Custom instruction for generating improved instructions given past attempts."""
    pass

with dspy.update_signatures({
    copro_optimizer.BasicGenerateInstruction: MyBasicGenerateInstruction,
    copro_optimizer.GenerateInstructionGivenAttempts: MyGenerateInstruction,
}):
    # All DSPy calls within this block use the replaced signatures
    teleprompter = COPRO(...)
    compiled = teleprompter.compile(...)
```

This is useful for customizing how optimizers like COPRO and MIPRO generate and refine instructions.

## Custom LM Clients

Create custom LM clients by subclassing `dsp.LM` (or `dspy.LM`):

```python
from dsp import LM

class CustomLMClient(LM):
    def __init__(self, model, api_key):
        self.model = model
        self.api_key = api_key
        self.provider = "default"
        self.history = []

    def basic_request(self, prompt: str, **kwargs):
        # Make API call, append to self.history
        self.history.append({"prompt": prompt, "response": response, "kwargs": kwargs})
        return response

    def __call__(self, prompt, only_completed=True, return_sorted=False, **kwargs):
        response = self.request(prompt, **kwargs)
        return [result["text"] for result in response["content"]]
```

Key requirements:
- `__init__`: Set `self.provider` and `self.history = []`
- `basic_request`: Make the API call, update `self.history` with `{"prompt": ..., "response": ...}`
- `__call__`: Return list of completions; calls `self.request()` which updates history

Configure and use like any built-in client:

```python
custom = CustomLMClient(model='my-model', api_key='key')
dspy.configure(lm=custom)
```
