# Training Examples

Practical training examples for common tasks.

## Semantic Textual Similarity (STS)

```python
from sentence_transformers import SentenceTransformer, evaluator, datasets
from sentence_transformers.losses import CosineSimilarityLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

# Load model and data
model = SentenceTransformer("all-MiniLM-L6-v2")
train_dataset = datasets.StsBenchmark(name="stsbenchmark", split="train")
eval_dataset = datasets.StsBenchmark(name="stsbenchmark", split="test")

# Configure training
loss_fn = CosineSimilarityLoss(model)
evaluator = evaluator.SentenceSimilarityEvaluator(
    sentences1=eval_dataset.sentences1,
    sentences2=eval_dataset.sentences2,
    scores=np.array(eval_dataset.scores),
    batch_size=32,
)

train_args = SentenceTransformerTrainingArguments(
    output_dir="./sts-model",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    evaluation_strategy="steps",
    eval_steps=500,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_dataset,
    loss=loss_fn,
    evaluator=evaluator,
)

trainer.train()
```

## Paraphrase Mining (Quora Duplicate Questions)

```python
from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.losses import MultipleNegativesRankingLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer
import pandas as pd

# Load Quora dataset
df = pd.read_csv("quora_duplicate_questions.csv")

# Create training examples (one sentence per example)
train_examples = [
    InputExample(texts=[str(row[q1])]) 
    for _, row in df.iterrows()
]

# Train with in-batch negatives
model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = MultipleNegativesRankingLoss(model)

train_args = SentenceTransformerTrainingArguments(
    output_dir="./quora-model",
    num_train_epochs=5,
    per_device_train_batch_size=32,
    learning_rate=1e-5,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_examples,
    loss=loss_fn,
)

trainer.train()
```

## Natural Language Inference (NLI)

```python
from sentence_transformers import SentenceTransformer, datasets
from sentence_transformers.losses import SoftmaxLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

# Load MNLI dataset
train_dataset = datasets.NLI(name="mnli", split="train")

# Train for 3-class classification (entailment, neutral, contradiction)
model = SentenceTransformer("all-MiniLM-L6-v2")
loss_fn = SoftmaxLoss(model, num_labels=3)

train_args = SentenceTransformerTrainingArguments(
    output_dir="./nli-model",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_dataset,
    loss=loss_fn,
)

trainer.train()
```

## MS MARCO Information Retrieval

```python
from sentence_transformers import SentenceTransformer, datasets
from sentence_transformers.losses import MultipleNegativesRankingLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer
import evaluator as se

# Load MS MARCO dataset
train_dataset = datasets.MSMarco(split="train")
eval_dataset = datasets.MSMarco(split="dev")

# Train bi-encoder for retrieval
model = SentenceTransformer("msmarco-roberta-base-v3")
loss_fn = MultipleNegativesRankingLoss(model)

# Create IR evaluator
evaluator = se.InformationRetrievalEvaluator(
    queries=eval_dataset.queries,
    corpus=eval_dataset.corpus,
    relevant_docs=eval_dataset.positive_docs,
    main_info_retrieval_metric="ndcgAt10",
)

train_args = SentenceTransformerTrainingArguments(
    output_dir="./msmarco-model",
    num_train_epochs=2,
    per_device_train_batch_size=32,
    learning_rate=1e-5,
    evaluation_strategy="steps",
    eval_steps=1000,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_dataset,
    loss=loss_fn,
    evaluator=evaluator,
)

trainer.train()
```

## Matryoshka Embeddings Training

Train models with nested embeddings:

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers.losses import MultipleNegativesRankingLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

# Load base model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")

# Configure for Matryoshka training
train_args = SentenceTransformerTrainingArguments(
    output_dir="./matryoshka-model",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=1e-5,
    # Enable Matryoshka dimensions
    matryoshka_dims=[64, 128, 256, 512, 768],
)

loss_fn = MultipleNegativesRankingLoss(model)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_data,
    loss=loss_fn,
)

trainer.train()

# Use different dimensions at inference
embedding_full = model.encode("Hello world")  # 768 dims
embedding_256 = model.encode("Hello world", max_length=256)  # 256 dims
```

## Multilingual Training

```python
from sentence_transformers import SentenceTransformer, datasets
from sentence_transformers.losses import CosineSimilarityLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

# Load multilingual model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Train on multiple languages
train_datasets = [
    datasets.StsBenchmark(name="stsbenchmark", split="train"),  # English
    datasets.StsPairs(name="stspairs-de", split="train"),  # German
    datasets.StsPairs(name="stspairs-fr", split="train"),  # French
]

loss_fn = CosineSimilarityLoss(model)

train_args = SentenceTransformerTrainingArguments(
    output_dir="./multilingual-model",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    learning_rate=1e-5,
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_datasets=train_datasets,  # Multi-dataset training
    loss=loss_fn,
)

trainer.train()
```

## Domain Adaptation (Medical)

```python
from sentence_transformers import SentenceTransformer, InputExample
from sentence_transformers.losses import MultipleNegativesRankingLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer

# Start from general model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Prepare medical domain data
medical_examples = [
    InputExample(texts=["patient has fever and cough"]),
    InputExample(texts=["symptoms include elevated temperature"]),
    InputExample(texts=["treatment with antibiotics"]),
    # ... more medical texts
]

loss_fn = MultipleNegativesRankingLoss(model)

train_args = SentenceTransformerTrainingArguments(
    output_dir="./medical-model",
    num_train_epochs=10,  # More epochs for domain adaptation
    per_device_train_batch_size=16,
    learning_rate=5e-6,  # Lower LR for fine-tuning
)

trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=medical_examples,
    loss=loss_fn,
)

trainer.train()
```

## Cross-Encoder Training (Reranker)

```python
from sentence_transformers import CrossEncoder, InputExample
from sentence_transformers.training_args import CrossEncoderTrainingArguments
from sentence_transformers.trainer import CrossEncoderTrainer

# Load base cross-encoder
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")

# Prepare training data (pairs with relevance scores)
train_examples = [
    InputExample(texts=["query", "relevant doc"], label=1.0),
    InputExample(texts=["query", "irrelevant doc"], label=0.0),
]

train_args = CrossEncoderTrainingArguments(
    output_dir="./reranker-model",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
)

trainer = CrossEncoderTrainer(
    model=model,
    args=train_args,
    train_dataset=train_examples,
)

trainer.train()
```

## Hyperparameter Optimization

Using Optuna for automatic hyperparameter tuning:

```python
import optuna
from sentence_transformers import SentenceTransformer
from sentence_transformers.losses import MultipleNegativesRankingLoss
from sentence_transformers.training_args import SentenceTransformerTrainingArguments
from sentence_transformers.trainer import SentenceTransformerTrainer
from sentence_transformers import evaluator as se

def objective(trial):
    # Suggest hyperparameters
    learning_rate = trial.suggest_float("learning_rate", 1e-6, 1e-4, log=True)
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
    num_epochs = trial.suggest_int("num_epochs", 2, 5)
    
    # Train model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    loss_fn = MultipleNegativesRankingLoss(model)
    
    train_args = SentenceTransformerTrainingArguments(
        output_dir=f"./trial-{trial.number}",
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        learning_rate=learning_rate,
        report_to="none",  # Disable logging for speed
    )
    
    trainer = SentenceTransformerTrainer(
        model=model,
        args=train_args,
        train_dataset=train_data,
        loss=loss_fn,
        evaluator=evaluator,
    )
    
    trainer.train()
    
    # Evaluate and return score to optimize
    eval_result = evaluator(model)
    return eval_result["cosine_similarity"]  # Maximize this

# Run optimization
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=20)

print(f"Best params: {study.best_params}")
print(f"Best score: {study.best_value}")
```

## Tips for Successful Training

1. **Start with pretrained models**: Fine-tuning is more efficient than training from scratch
2. **Use appropriate batch size**: Larger batches improve in-batch negative sampling
3. **Monitor evaluation metrics**: Don't just watch training loss
4. **Early stopping**: Prevent overfitting by stopping when eval metrics plateau
5. **Learning rate scheduling**: Use cosine or linear decay
6. **Mixed precision**: Enable fp16/bf16 for faster GPU training
7. **Save checkpoints**: Keep multiple versions to compare later
