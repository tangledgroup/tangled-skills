# Evaluation Guide

Comprehensive guide to evaluating Sentence Transformer models using MTEB and custom metrics.

## MTEB (Massive Text Embedding Benchmark)

### What is MTEB?

MTEB is a comprehensive benchmark for evaluating embedding models across:
- 60+ tasks
- 40+ languages  
- Multiple task types (retrieval, STS, clustering, etc.)

### Installation

```bash
pip install mteb
```

### Basic Evaluation

```python
import mteb
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create MTEB model wrapper
mteb_model = mteb.get_model(model)

# Run evaluation on specific tasks
tasks = [
    "STSBenchmark",  # Semantic textual similarity
    "QuoraDuplicateQuestions",  # Duplicate detection
    "SumEvalClustering",  # Clustering
]

# Create task list
task_list = mteb.get_tasks(task_names=tasks)

# Run evaluation
results = mteb.run(
    mteb_model,
    tasks=task_list,
    output_folder="./mteb-results",
    verbosity=2,  # 0=quiet, 1=normal, 2=verbose
)

# View results
print(results)
```

### Evaluate All Tasks

```python
import mteb

model = SentenceTransformer("all-MiniLM-L6-v2")
mteb_model = mteb.get_model(model)

# Get all English tasks
tasks = mteb.get_tasks(languages=["eng"])

# Run evaluation (this takes hours!)
results = mteb.run(
    mteb_model,
    tasks=tasks,
    output_folder="./mteb-results-full",
)
```

### Evaluate Specific Task Type

```python
import mteb

model = SentenceTransformer("all-MiniLM-L6-v2")
mteb_model = mteb.get_model(model)

# Get all retrieval tasks
retrieval_tasks = mteb.get_tasks(task_types=["Retrieval"])

# Get all clustering tasks
clustering_tasks = mteb.get_tasks(task_types=["Clustering"])

# Run on retrieval tasks only
results = mteb.run(
    mteb_model,
    tasks=retrieval_tasks,
)
```

### Filter by Language

```python
import mteb

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
mteb_model = mteb.get_model(model)

# Get all German tasks
german_tasks = mteb.get_tasks(languages=["deu"])

# Get all multilingual tasks
multilingual_tasks = mteb.get_tasks(languages=["eng", "fra", "deu", "spa"])

results = mteb.run(
    mteb_model,
    tasks=german_tasks,
)
```

## Custom Evaluation

### Sentence Similarity Evaluator

```python
from sentence_transformers import evaluator as se
import numpy as np

# Prepare evaluation data
sentences1 = [
    "The cat sits on the mat",
    "I love programming",
    "Weather is nice today",
]
sentences2 = [
    "A feline is sitting on a rug",
    "Coding is my passion",
    "It's sunny outside",
]
scores = np.array([0.9, 0.85, 0.8])  # Ground truth similarity scores

# Create evaluator
evaluator = se.SentenceSimilarityEvaluator(
    sentences1=sentences1,
    sentences2=sentences2,
    scores=scores,
    main_si_model="cosine",  # or "euclidean", "manhattan"
    batch_size=32,
    output_path="./eval-results",
)

# Use during training
trainer = SentenceTransformerTrainer(
    model=model,
    args=train_args,
    train_dataset=train_data,
    loss=loss_fn,
    evaluator=evaluator,  # Will be called between epochs
)

# Or call manually
eval_result = evaluator(model)
print(eval_result)
# {'cosine_similarity': 0.85, 'pearson_cosine': 0.92, ...}
```

### Information Retrieval Evaluator

```python
from sentence_transformers import evaluator as se

# Prepare IR evaluation data
queries = {
    "0": "How to install Python?",
    "1": "Best programming languages for beginners",
}
corpus = {
    "doc1": "Python installation guide for Windows, Mac, and Linux",
    "doc2": "Top 10 programming languages to learn in 2024",
    "doc3": "Advanced C++ programming techniques",
}
relevant_docs = {
    "0": {"doc1": 1.0},  # Query 0 -> doc1 is relevant
    "1": {"doc2": 1.0},  # Query 1 -> doc2 is relevant
}

# Create evaluator
evaluator = se.InformationRetrievalEvaluator(
    queries=queries,
    corpus=corpus,
    relevant_docs=relevant_docs,
    main_info_retrieval_metric="ndcgAt10",
    batch_size=32,
    output_path="./ir-eval",
)

# Evaluate model
eval_result = evaluator(model)
print(f"MRR: {eval_result['mrr']}")
print(f"NDCG@10: {eval_result['ndcgAt10']}")
print(f"Precision@5: {eval_result['precisionAt5']}")
```

### Label Accuracy Evaluator

For classification tasks:

```python
from sentence_transformers import evaluator as se
import numpy as np

# Prepare classification evaluation data
sentences = [
    "I love this product",
    "Terrible experience",
    "Amazing quality",
    "Waste of money",
]
labels = np.array([0, 1, 0, 1])  # 0=positive, 1=negative

# Create evaluator
evaluator = se.LabelAccuracyEvaluator(
    sentences=sentences,
    labels=labels,
    batch_size=32,
)

# Evaluate
eval_result = evaluator(model)
print(f"Accuracy: {eval_result['accuracy']}")
```

### Pair Classification Evaluator

For binary pair classification:

```python
from sentence_transformers import evaluator as se
import numpy as np

# Prepare pair classification data
sentences1 = [
    "How do I reset my password?",
    "What is the capital of France?",
]
sentences2 = [
    "Can I recover my account?",
    "Where is Paris located?",
]
labels = np.array([1, 0])  # 1=similar/duplicate, 0=not similar

# Create evaluator
evaluator = se.PairClassificationEvaluator(
    sentences1=sentences1,
    sentences2=sentences2,
    labels=labels,
    batch_size=32,
)

# Evaluate
eval_result = evaluator(model)
print(f"Accuracy: {eval_result['accuracy']}")
```

## Evaluation Metrics

### Similarity Metrics

- **Cosine Similarity**: Measures angle between vectors (0 to 1 after normalization)
- **Pearson Correlation**: Linear correlation between predicted and actual scores
- **Spearman Correlation**: Rank correlation (more robust to outliers)

### Information Retrieval Metrics

- **MRR** (Mean Reciprocal Rank): Average of 1/rank of first relevant doc
- **NDCG@k** (Normalized Discounted Cumulative Gain): Quality of top-k results
- **Precision@k**: Fraction of relevant docs in top-k
- **Recall@k**: Fraction of all relevant docs found in top-k

### Clustering Metrics

- **V-measure**: Homogeneity and completeness of clusters
- **Adjusted Rand Index**: Agreement between predicted and true clusters
- **Adjusted Mutual Information**: Shared information between clusterings

## Leaderboard Submission

Submit your model to MTEB leaderboard:

```python
import mteb

# Run full evaluation
results = mteb.run(
    mteb_model,
    tasks=mteb.get_tasks(),  # All tasks
    output_folder="./mteb-results",
)

# Generate leaderboard submission
mteb.create_leaderboard_submission(
    results,
    model_name="my-custom-model",
    output_path="./leaderboard-submission.json",
)

# Submit via GitHub PR to mteb/leaderboard repository
```

## Parallel Evaluation

Speed up evaluation with parallel processing:

```python
import mteb
from concurrent.futures import ProcessPoolExecutor

def evaluate_task(task):
    return mteb.run(mteb_model, tasks=[task])

# Get tasks to evaluate
tasks = mteb.get_tasks(task_types=["Retrieval"])

# Run in parallel (use with caution - memory intensive!)
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(evaluate_task, tasks))
```

## Custom Task Definition

Create your own evaluation task:

```python
import mteb
from mteb.abstasks.AbsTask import AbsTask
from mteb.abstasks.TaskMetadata import TaskMetadata

class MyCustomTask(AbsTask):
    metadata = TaskMetadata(
        name="MyCustomTask",
        description="My custom evaluation task",
        reference="https://example.com",
        dataset={
            "path": "my-dataset",
            "revision": "abc123",
        },
        modalities=["text"],
        types=["Classification"],
        languages=["eng"],
    )
    
    def __init__(self):
        super().__init__()
        
        # Load dataset
        self.dataset = load_dataset("my-dataset")
        
        # Prepare evaluation data
        self.sentences = self.dataset["test"]["text"]
        self.labels = self.dataset["test"]["label"]
    
    def evaluate(self, model, **kwargs):
        # Implement custom evaluation logic
        embeddings = model.encode(self.sentences)
        
        # Compute metrics
        accuracy = compute_accuracy(embeddings, self.labels)
        
        return {
            "MyCustomTask": {
                "accuracy": accuracy,
                "main_score": accuracy,
            }
        }

# Use custom task
custom_task = MyCustomTask()
results = mteb.run(mteb_model, tasks=[custom_task])
```

## Best Practices

1. **Use held-out test sets**: Never evaluate on training data
2. **Multiple runs**: Average over multiple seeds for robustness
3. **Compare to baselines**: Evaluate against established models
4. **Task-specific metrics**: Use appropriate metrics for each task type
5. **Statistical significance**: Run significance tests for comparisons
6. **Report confidence intervals**: Show variance across runs

## Troubleshooting

### Issue: Out of memory during evaluation

**Solution**: Reduce batch size or evaluate tasks sequentially

### Issue: Evaluation very slow

**Solution**: 
- Use smaller models for quick testing
- Evaluate subset of tasks first
- Enable GPU if available

### Issue: Metrics seem wrong

**Solution**: 
- Verify data format matches task requirements
- Check that labels are in correct range
- Ensure model is in eval mode (`model.eval()`)
