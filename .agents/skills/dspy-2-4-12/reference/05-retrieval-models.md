# Retrieval Models

## Contents
- Overview
- Configuring a Retrieval Model
- Using dspy.Retrieve
- Built-in Retrieval Clients
- Custom Pythonic RM Client
- DSPythonic RM Client (Inheriting from dspy.Retrieve)
- Using Custom RM Models

## Overview

DSPy supports retrieval through the `dspy.Retrieve` module, which processes queries and outputs relevant passages from retrieval corpuses. The Retrieve module ties in with DSPy-supported Retrieval Model (RM) clients — retrieval servers or vector stores that users can utilize for information retrieval tasks.

The **input** to an RM is either a single query string or a list of query strings. The **output** is the top-k passages per query.

## Configuring a Retrieval Model

Configure a retrieval model via `dspy.configure`:

```python
colbertv2_wiki17_abstracts = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(rm=colbertv2_wiki17_abstracts)
```

## Using dspy.Retrieve

Instantiate with a user-defined `k` for number of passages to return:

```python
retriever = dspy.Retrieve(k=3)

query = 'When was the first FIFA World Cup held?'
topK_passages = retriever(query).passages

for idx, passage in enumerate(topK_passages):
    print(f'{idx+1}]', passage)
```

Retrieve can handle a single query or a list of queries, accumulating scores for each passage and returning results sorted by cumulative scores. If a reranker is configured, it re-scores retrieved passages based on relevance to the query.

## Built-in Retrieval Clients

DSPy provides several retrieval model clients:

- **`dspy.ColBERTv2`** — ColBERTv2 retrieval server
- **`dspy.AzureCognitiveSearch`** — Azure Cognitive Search
- **`dspy.PineconeRM`** — Pinecone vector database
- **`dspy.WeaviateRM`** — Weaviate vector database
- **`dspy.QdrantRM`** — Qdrant vector database
- **`dspy.MilvusRM`** — Milvus vector database
- **`dspy.ChromaRM`** — ChromaDB

## Custom Pythonic RM Client

The simplest approach: a callable class that takes queries and returns passages:

```python
from typing import List, Union

class PythonicRMClient:
    def __init__(self, url: str, port: int = None):
        self.url = f"{url}:{port}" if port else url

    def __call__(self, query: str, k: int) -> List[str]:
        import requests
        params = {"query": query, "k": k}
        response = requests.get(self.url, params=params)
        return response.json()["retrieved_passages"]
```

Use directly in a pipeline:

```python
class MyPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.rm = PythonicRMClient(url="http://localhost", port=3000)

    def forward(self, question):
        passages = self.rm(question, k=3)
        # use passages...
```

## DSPythonic RM Client (Inheriting from dspy.Retrieve)

For deeper DSPy integration, inherit from `dspy.Retrieve` and implement `forward`:

```python
import dspy
from typing import Optional

class DSPythonicRMClient(dspy.Retrieve):
    def __init__(self, url: str, port: int = None, k: int = 3):
        super().__init__(k=k)
        self.url = f"{url}:{port}" if port else url

    def forward(self, query_or_queries: str, k: Optional[int] = None) -> dspy.Prediction:
        import requests
        params = {"query": query_or_queries, "k": k if k else self.k}
        response = requests.get(self.url, params=params)
        passages = response.json()["retrieved_passages"]
        return dspy.Prediction(passages=passages)
```

This returns `dspy.Prediction(passages=...)`, the standard output format for all RM modules.

## Using Custom RM Models

**Direct method:** Instantiate the custom RM in your module and call it directly in `forward`.

**Via dspy.Retrieve (recommended for experimentation):** Configure the RM globally so `dspy.Retrieve` uses it:

```python
import dspy

lm = dspy.OpenAI(model='gpt-3.5-turbo')
dspythonic_rm = DSPythonicRMClient(url="http://localhost", port=3000, k=3)

dspy.configure(lm=lm, rm=dspythonic_rm)
```

Now `dspy.Retrieve(k=N)` in any pipeline will use this RM. To switch RMs, just reconfigure via `dspy.configure(rm=new_rm)`.

Internally, `dspy.Retrieve` uses `dsp.retrieveEnsemble` from `dsp/primitives/search.py`. If no `rm` is initialized in `dsp.settings`, it raises an error.
