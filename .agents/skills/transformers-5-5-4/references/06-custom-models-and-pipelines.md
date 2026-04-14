# Custom Models and Pipelines - Complete Guide

Learn how to create custom models, pipelines, and integrate Transformers with external frameworks.

## Overview

This reference covers:
- Creating custom model architectures
- Implementing custom pipelines for specialized tasks
- Integrating with external frameworks
- Extending Transformers functionality

## Creating Custom Models

### Basic Custom Model

Create a simple custom model extending PreTrainedModel:

```python
from transformers import PreTrainedModel, PretrainedConfig
import torch.nn as nn
import torch

class MyModelConfig(PretrainedConfig):
    """Configuration for custom model"""
    model_type = "my_model"
    
    def __init__(
        self,
        hidden_size=768,
        num_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_attention_heads = num_attention_heads
        self.intermediate_size = intermediate_size

class MyModel(PreTrainedModel):
    config_class = MyModelConfig
    
    def __init__(self, config: MyModelConfig):
        super().__init__(config)
        
        self.embeddings = nn.Embedding(
            config.vocab_size,
            config.hidden_size
        )
        
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(
                d_model=config.hidden_size,
                nhead=config.num_attention_heads,
                dim_feedforward=config.intermediate_size
            )
            for _ in range(config.num_layers)
        ])
        
        self.final_layer_norm = nn.LayerNorm(config.hidden_size)
    
    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        **kwargs
    ):
        # Get embeddings
        embeddings = self.embeddings(input_ids)
        
        # Transformer encoder
        # Note: PyTorch expects [seq_len, batch, features]
        embeddings = embeddings.transpose(0, 1)
        outputs = layer(embeddings, src_key_padding_mask=attention_mask) 
            for layer in self.layers
        
        # Final layer norm
        outputs = self.final_layer_norm(outputs)
        
        # Transpose back to [batch, seq_len, features]
        outputs = outputs.transpose(0, 1)
        
        return outputs

# Usage
config = MyModelConfig(
    vocab_size=30522,
    hidden_size=768,
    num_layers=6
)

model = MyModel(config)
inputs = torch.randint(0, 30522, (2, 128))
outputs = model(input_ids=inputs)
```

### Custom Model for Specific Task

Create a model with task-specific head:

```python
from transformers import PreTrainedModel, PretrainedConfig
import torch.nn as nn
import torch

class MyModelForClassificationConfig(PretrainedConfig):
    model_type = "my_model_classification"
    
    def __init__(self, num_labels=2, **kwargs):
        super().__init__(**kwargs)
        self.num_labels = num_labels

class MyModelForSequenceClassification(PreTrainedModel):
    config_class = MyModelForClassificationConfig
    
    def __init__(self, config):
        super().__init__(config)
        
        # Base model
        self.base_model = MyModel(config)
        
        # Classification head
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(
            config.hidden_size,
            config.num_labels
        )
    
    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        labels=None,
        **kwargs
    ):
        # Get base model outputs
        outputs = self.base_model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token (first token) for classification
        cls_output = outputs[:, 0, :]
        
        # Classification head
        logits = self.classifier(self.dropout(cls_output))
        
        # Compute loss if labels provided
        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.config.num_labels), labels.view(-1))
        
        return {
            "loss": loss,
            "logits": logits,
            "hidden_states": outputs
        }

# Usage
config = MyModelForClassificationConfig(
    vocab_size=30522,
    hidden_size=768,
    num_labels=3
)

model = MyModelForSequenceClassification(config)
inputs = torch.randint(0, 30522, (4, 128))
labels = torch.randint(0, 3, (4,))

outputs = model(input_ids=inputs, labels=labels)
print(f"Loss: {outputs['loss'].item():.4f}")
```

### Registering Custom Model with Auto Classes

Make your custom model discoverable via AutoModel:

```python
from transformers import AutoModel, AutoConfig
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
import torch.nn as nn

# Define config
class CustomModelConfig(PretrainedConfig):
    model_type = "custom_model"

# Define model
class CustomModelForCausalLM(PreTrainedModel):
    config_class = CustomModelConfig
    
    def __init__(self, config):
        super().__init__(config)
        # Your model implementation
    
    def forward(self, input_ids, attention_mask=None, labels=None):
        # Your forward pass

# Register with Auto classes
from transformers.models.auto import modeling_auto

modeling_auto.MODEL_FOR_CAUSAL_LM_MAPPING.update({
    CustomModelConfig: CustomModelForCausalLM
})

# Now you can use AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("./my-custom-model")
```

## Creating Custom Pipelines

### Basic Custom Pipeline

Create a pipeline for a specialized task:

```python
from transformers import Pipeline, AddDictionaryExampleMixin
from typing import List, Dict, Any

class CustomTaskPipeline(Pipeline, AddDictionaryExampleMixin):
    """Custom pipeline for specialized task"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def _sanitize_parameters(self, **kwargs):
        """Define which parameters go to preprocess/forward/postprocess"""
        preprocess_params = {}
        forward_params = {}
        postprocess_params = {}
        
        if "top_k" in kwargs:
            postprocess_params["top_k"] = kwargs["top_k"]
        
        return preprocess_params, forward_params, postprocess_params
    
    def preprocess(self, input_text: str) -> Dict[str, Any]:
        """Preprocess input"""
        encoding = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        return encoding
    
    def _forward(self, model_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run model forward pass"""
        with torch.no_grad():
            outputs = self.model(**model_inputs)
        return outputs
    
    def postprocess(self, model_outputs: Dict[str, Any], top_k: int = 1) -> List[Dict]:
        """Postprocess model outputs"""
        import numpy as np
        
        logits = model_outputs["logits"]
        probabilities = torch.softmax(logits, dim=-1)
        
        # Get top-k predictions
        top_indices = torch.topk(probabilities, k=top_k, dim=-1)
        
        results = []
        for i in range(top_indices.indices.shape[0]):
            for j in range(top_k):
                label_id = top_indices.indices[i, j].item()
                score = top_indices.values[i, j].item()
                
                # Map label ID to name (customize this)
                label_name = f"label_{label_id}"
                
                results.append({
                    "label": label_name,
                    "score": float(score)
                })
        
        return results

# Register pipeline
from transformers import pipeline

@pipeline.register("custom-task")
def custom_task_pipeline(model=None, tokenizer=None, **kwargs):
    return CustomTaskPipeline(
        model=model,
        tokenizer=tokenizer,
        **kwargs
    )

# Usage
pipe = pipeline("custom-task", model=my_model, tokenizer=my_tokenizer)
result = pipe("Input text here")
```

### Multi-Step Pipeline

Create a pipeline with multiple processing steps:

```python
from transformers import Pipeline
from typing import List, Dict, Any

class MultiStepPipeline(Pipeline):
    """Pipeline with multiple sequential models"""
    
    def __init__(self, model1, model2, tokenizer, **kwargs):
        super().__init__(model=model1, tokenizer=tokenizer, **kwargs)
        self.model2 = model2
    
    def preprocess(self, input_text: str) -> Dict[str, Any]:
        encoding = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )
        return encoding
    
    def _forward(self, model_inputs: Dict[str, Any]) -> Dict[str, Any]:
        # First model
        with torch.no_grad():
            intermediate_outputs = self.model(**model_inputs)
        
        # Second model
        with torch.no_grad():
            final_outputs = self.model2(**intermediate_outputs)
        
        return final_outputs
    
    def postprocess(self, model_outputs: Dict[str, Any]) -> List[Dict]:
        # Convert outputs to desired format
        return [{"result": "processed"}]

# Usage
pipe = MultiStepPipeline(
    model1=model1,
    model2=model2,
    tokenizer=tokenizer
)
```

### Pipeline with Custom Preprocessing

```python
from transformers import Pipeline
import re

class TextCleaningPipeline(Pipeline):
    """Pipeline with custom text preprocessing"""
    
    def preprocess(self, input_text: str) -> Dict[str, Any]:
        # Custom text cleaning
        cleaned_text = self._clean_text(input_text)
        
        # Tokenize
        encoding = self.tokenizer(
            cleaned_text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )
        return encoding
    
    def _clean_text(self, text: str) -> str:
        """Custom text cleaning logic"""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Lowercase
        text = text.lower()
        
        return text

# Usage
pipe = TextCleaningPipeline(model=model, tokenizer=tokenizer)
result = pipe("Check out http://example.com for more info!!!")
```

## Integration with External Frameworks

### FastAPI Integration

Production-ready API server:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

app = FastAPI()

# Load model at startup
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model.eval()

class TextRequest(BaseModel):
    text: str
    top_k: int = 1

class ClassificationResponse(BaseModel):
    label: str
    score: float

@app.post("/classify", response_model=list[ClassificationResponse])
async def classify(text_request: TextRequest):
    try:
        # Tokenize
        inputs = tokenizer(
            text_request.text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        
        # Inference
        with torch.no_grad():
            outputs = model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
        
        # Get top-k predictions
        top_k = text_request.top_k
        values, indices = torch.topk(probabilities, k=top_k)
        
        results = []
        for i in range(top_k):
            label_id = indices[0, i].item()
            score = values[0, i].item()
            
            # Map label ID to name
            label_name = model.config.id2label[label_id]
            
            results.append(ClassificationResponse(
                label=label_name,
                score=float(score)
            ))
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": model_name}

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
```

### Flask Integration

Simple Flask server:

```python
from flask import Flask, request, jsonify
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

app = Flask(__name__)

# Load model
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)
tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)
model.eval()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Tokenize and predict
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1)
    
    label_id = torch.argmax(probabilities).item()
    score = probabilities[0, label_id].item()
    label = model.config.id2label[label_id]
    
    return jsonify({
        "label": label,
        "score": float(score)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Django Integration

Django view with Transformers:

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Load model at module level (singleton)
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)
tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)
model.eval()

@csrf_exempt
def classify_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            
            if not text:
                return JsonResponse({"error": "No text provided"}, status=400)
            
            # Tokenize and predict
            inputs = tokenizer(text, return_tensors="pt", truncation=True)
            
            with torch.no_grad():
                outputs = model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
            
            label_id = torch.argmax(probabilities).item()
            score = probabilities[0, label_id].item()
            label = model.config.id2label[label_id]
            
            return JsonResponse({
                "label": label,
                "score": float(score)
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)
```

### Streamlit Integration

Interactive web app:

```python
import streamlit as st
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# Page config
st.set_page_config(page_title="Text Classifier", layout="wide")

# Load model
@st.cache_resource
def load_model():
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased-finetuned-sst-2-english"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        "distilbert-base-uncased-finetuned-sst-2-english"
    )
    return model, tokenizer

model, tokenizer = load_model()

# Sidebar
st.sidebar.title("Settings")
top_k = st.sidebar.slider("Top K Predictions", 1, 5, 1)

# Main content
st.title("🤗 Text Classification")

text_input = st.text_area(
    "Enter text to classify:",
    placeholder="Type your text here...",
    height=150
)

if st.button("Classify"):
    if text_input:
        with st.spinner("Analyzing..."):
            # Tokenize and predict
            inputs = tokenizer(
                text_input,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
            
            # Get top-k predictions
            values, indices = torch.topk(probabilities, k=top_k)
            
            st.subheader("Results:")
            for i in range(top_k):
                label_id = indices[0, i].item()
                score = values[0, i].item()
                label = model.config.id2label[label_id]
                
                # Progress bar
                st.progress(float(score))
                st.write(f"**{label}**: {score:.4f}")
    else:
        st.warning("Please enter some text!")

# Run with: streamlit run app.py
```

## Custom Tokenizers

### Extending Tokenizer Vocabulary

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Add custom tokens
num_added = tokenizer.add_tokens(["<custom>", "<another>"])
print(f"Added {num_added} tokens")

# Add special tokens
num_added_special = tokenizer.add_special_tokens({
    "additional_special_tokens": ["<START>", "<END>"]
})

# Update model embeddings to match new vocabulary
model.resize_token_embeddings(len(tokenizer))

# Save updated tokenizer and model
tokenizer.save_pretrained("./updated-model")
model.save_pretrained("./updated-model")
```

### Custom Tokenization Logic

```python
from transformers import PreTrainedTokenizer

class CustomTokenizer(PreTrainedTokenizer):
    """Custom tokenizer with specialized logic"""
    
    def __init__(self, vocab_file, **kwargs):
        super().__init__(vocab_file, **kwargs)
    
    def tokenize(self, text: str, **kwargs) -> List[str]:
        """Custom tokenization logic"""
        # Preprocess text
        text = self._preprocess(text)
        
        # Custom splitting logic
        tokens = self._custom_split(text)
        
        return tokens
    
    def _preprocess(self, text: str) -> str:
        """Custom preprocessing"""
        # Add your preprocessing logic here
        return text.lower()
    
    def _custom_split(self, text: str) -> List[str]:
        """Custom token splitting"""
        # Implement custom splitting logic
        return text.split()

# Usage
tokenizer = CustomTokenizer(vocab_file="vocab.txt")
tokens = tokenizer("Hello, world!")
```

## Best Practices

1. **Inherit from PreTrainedModel** for automatic config handling and saving/loading
2. **Use Auto classes** to make custom models discoverable
3. **Implement proper forward signatures** with optional arguments
4. **Add documentation strings** for all methods
5. **Test with Trainer API** to ensure compatibility
6. **Save configs properly** with model_type attribute
7. **Handle device placement** correctly in custom code

## Troubleshooting

### Model Not Saving Properly

```python
# Ensure config has model_type attribute
class MyConfig(PretrainedConfig):
    model_type = "my_model"  # Required!

# Save both model and config
model.save_pretrained("./my-model")
config = model.config
config.save_pretrained("./my-model")
```

### Custom Pipeline Not Registered

```python
from transformers import pipeline

# Register with unique task name
@pipeline.register("my-custom-task")
def my_custom_pipeline(model=None, tokenizer=None, **kwargs):
    return MyCustomPipeline(model=model, tokenizer=tokenizer, **kwargs)

# Use with registered name
pipe = pipeline("my-custom-task", model=model, tokenizer=tokenizer)
```

### Auto Class Not Finding Custom Model

```python
from transformers.models.auto import modeling_auto

# Register mapping
modeling_auto.MODEL_MAPPING.update({
    MyConfig: MyModel
})

# Or use config's auto_map
config = MyConfig()
config.auto_map = {
    "AutoModel": "my_module.MyModel"
}
```
