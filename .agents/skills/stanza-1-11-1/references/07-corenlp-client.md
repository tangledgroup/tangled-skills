# Stanford CoreNLP Client

Stanza provides a Python interface to the Java Stanford CoreNLP toolkit, enabling access to advanced features like coreference resolution, constituency parsing (for more languages), and semantic role labeling.

## Setup

### Install Stanford CoreNLP

1. Download CoreNLP from [Stanford NLP website](https://stanfordnlp.github.io/CoreNLP/)
2. Extract the distribution:
```bash
cd /path/to/download
unzip stanford-corenlp-4.5.3.jar  # Or latest version
```

3. Download language models:
```bash
cd stanford-corenlp-4.5.3
./sh getModels.sh  # Downloads English models
# Or for other languages:
./sh getModels.sh --lang fr
```

### Set Environment Variable

```bash
export CORENLP_HOME=/path/to/stanford-corenlp-4.5.3
```

Add to `~/.bashrc` for persistence:
```bash
echo 'export CORENLP_HOME=/path/to/stanford-corenlp-4.5.3' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

```python
import os
print(os.environ.get('CORENLP_HOME'))  # Should print path
```

## Basic Usage

### Start CoreNLP Server

```python
from stanza.server import CoreNLPClient

# Start server with default annotators
with CoreNLPClient() as client:
    doc = client.annotate("Barack Obama was born in Hawaii.")
    print(doc.sentences[0].words)
```

### Specify Annotators

Choose which annotators to run:

```python
with CoreNLPClient(annotators='tokenize,ssplit,pos,lemma,ner') as client:
    doc = client.annotate("The cat sat on the mat.")
    
    for word in doc.sentences[0].words:
        print(f"{word.text}: {word.pos} -> {word.lemma}")
```

Available annotators: tokenize, ssplit, pos, lemma, parse, coref, ner, openie, sentiment, dcoref, constituency, basicdependencies, enhanceddependencies

### Coreference Resolution

CoreNLP excels at coreference resolution:

```python
with CoreNLPClient(annotators='tokenize,ssplit,pos,ner,dcoref') as client:
    text = "Stephen was in the kitchen. He was cooking dinner for his wife."
    doc = client.annotate(text)
    
    # Access coreference chains
    for coref in doc.corefs:
        for chain in coref.chains:
            mentions = [mention.text for mention in chain.mentions]
            print(f"Coreference chain: {mentions}")
            # Output: Coreference chain: ['Stephen', 'He', 'his']
```

### Constituency Parsing

```python
with CoreNLPClient(annotators='tokenize,ssplit,pos,constituency') as client:
    doc = client.annotate("The quick brown fox jumps over the lazy dog.")
    
    tree = doc.sentences[0].constituency_parsers[0]
    print(tree)
    # Output: (ROOT (S (NP (DT The) (JJ quick) (JJ brown) (NN fox)) ...))
```

## Advanced Configuration

### Custom Properties

Pass custom properties to CoreNLP server:

```python
properties = {
    'ssplit.analyzeSentenceLength': False,
    'ner.applyDefaultPatterns': True,
    'parse.maxDependenciesDepth': 10
}

with CoreNLPClient(properties=properties) as client:
    doc = client.annotate("Hello world.")
```

### Server Options

```python
with CoreNLPClient(
    annotators='tokenize,ssplit,pos,lemma,ner',
    timeout=30000,           # Timeout in milliseconds
    memory='4G',             # Memory allocation for Java process
    properties={},           # Custom properties
    server_timeout=60000,    # Server startup timeout
    port=9000,              # Custom port
    cache_results=True       # Cache annotation results
) as client:
    doc = client.annotate("Hello world.")
```

### Pre-started Server

Connect to an existing CoreNLP server:

```python
# Start server manually (in terminal)
java -cp stanford-corenlp-4.5.3.jar edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
    -port 9000 -timeout 15000

# Connect from Python
client = CoreNLPClient(port=9000, start_server=False)
doc = client.annotate("Hello world.")
client.close()
```

## Semantic Role Labeling (OpenIE)

Extract semantic triples from text:

```python
with CoreNLPClient(annotators='tokenize,ssplit,pos,openie') as client:
    doc = client.annotate("Barack Obama was born in Hawaii in 1961.")
    
    for sentence in doc.sentences:
        for relation in sentence.openie_relations:
            print(f"{relation.subject} | {relation.relation} | {relation.object}")
            # Output:
            # Barack Obama | was born | Hawaii
            # Barack Obama | was born in | 1961
```

## Named Entity Recognition

CoreNLP NER with additional entity types:

```python
with CoreNLPClient(annotators='tokenize,ssplit,pos,ner') as client:
    doc = client.annotate("Google was founded in 1998 by Larry Page and Sergey Brin.")
    
    for entity in doc.entities:
        print(f"{entity.type}: {entity.text}")
    # Output includes: ORGANIZATION, DATE, PERSON
```

Entity types: PERSON, LOCATION, FACILITY, ORGANIZATION, PRODUCT, GPE, MONEY, PERCENT, DATE, TIME, ORDINAL, CARDINAL

## Regex Matching with Semgrex and Ssurgeon

### Semgrex (Semantic Regex)

Search dependency graphs with pattern matching:

```python
from stanza.server import CoreNLPClient

with CoreNLPClient(annotators='tokenize,ssplit,pos,depparse') as client:
    doc = client.annotate("The quick brown fox jumps over the lazy dog.")
    
    # Find all nouns that are subjects
    pattern = 'nsubj(ROOT, {WORD}/NOUN)'
    matches = doc.semgrex(pattern)
    
    for match in matches:
        print(match)
```

### Ssurgeon

Manipulate dependency graphs:

```python
# Extract specific dependencies
pattern = 'nmod:{WORD}/NOUN'
matches = doc.ssrg(pattern)

for match in matches:
    print(match)
```

### Tsurgeon (Constituency Surgeon)

Extract from constituency trees:

```python
with CoreNLPClient(annotators='tokenize,ssplit,pos,constituency') as client:
    doc = client.annotate("The quick brown fox jumps.")
    
    # Extract noun phrases
    pattern = 'NP'
    matches = doc.tsrg(pattern)
    
    for match in matches:
        print(match)
```

## Batch Processing

Process multiple documents efficiently:

```python
with CoreNLPClient(annotators='tokenize,ssplit,pos,ner') as client:
    texts = [
        "Barack Obama was born in Hawaii.",
        "Albert Einstein won the Nobel Prize.",
        "Marie Curie discovered radium."
    ]
    
    # Process all at once
    docs = client.annotate(texts)
    
    for doc in docs:
        print(f"Text: {doc.text}")
        for entity in doc.entities:
            print(f"  {entity.type}: {entity.text}")
```

## Error Handling

### Connection Errors

```python
from stanza.server import CoreNLPClient

try:
    with CoreNLPClient() as client:
        doc = client.annotate("Hello world.")
except RuntimeError as e:
    print(f"CoreNLP server error: {e}")
    # Check CORENLP_HOME, Java installation, port availability
```

### Timeout Errors

Increase timeout for long documents:

```python
with CoreNLPClient(timeout=60000) as client:  # 60 second timeout
    doc = client.annotate(very_long_text)
```

### Memory Issues

Allocate more memory:

```python
with CoreNLPClient(memory='8G') as client:  # 8GB heap
    doc = client.annotate(large_document)
```

## Performance Tips

### Reuse Client Instance

Don't restart server for each document:

```python
# Good: Reuse client
with CoreNLPClient() as client:
    for text in texts:
        doc = client.annotate(text)

# Bad: Restart server repeatedly
for text in texts:
    with CoreNLPClient() as client:
        doc = client.annotate(text)  # Slow!
```

### Select Minimal Annotators

Only run needed annotators:

```python
# Fast: Only what you need
with CoreNLPClient(annotators='tokenize,ssplit,pos') as client:
    pass

# Slow: All annotators
with CoreNLPClient(annotators='*') as client:
    pass
```

### Parallel Processing

Use multiple clients for parallel processing:

```python
from concurrent.futures import ThreadPoolExecutor

def annotate_text(text):
    with CoreNLPClient(start_server=False, port=9000) as client:
        return client.annotate(text)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(annotate_text, texts))
```

## Comparison: Neural Pipeline vs CoreNLP Client

| Feature | Neural Pipeline | CoreNLP Client |
|---------|----------------|----------------|
| Setup | Simple (pip install) | Requires Java, CoreNLP download |
| Speed | Fast (native Python/PyTorch) | Slower (server-client overhead) |
| Languages | 80+ (neural models) | 20+ (varies by annotator) |
| Coreference | Not available | Excellent (dcoref) |
| Constituency | Limited languages | All supported languages |
| OpenIE | Not available | Available |
| GPU Support | Yes | No (Java-based) |
| Custom Training | Easy | Complex (requires Java) |

### When to Use Each

**Use Neural Pipeline when:**
- You need fast, GPU-accelerated processing
- Working with 80+ languages via UD
- Training custom models on your data
- Need tokenization, POS, lemmatization, dependency parsing, NER

**Use CoreNLP Client when:**
- You need coreference resolution
- Need semantic role labeling (OpenIE)
- Require constituency parsing for non-neural languages
- Need specific Java-based annotators
- Working with legacy Stanford NLP tools

## Migration from Neural Pipeline

Switching from neural pipeline to CoreNLP:

```python
# Neural pipeline
import stanza
nlp = stanza.Pipeline('en')
doc = nlp("Hello world")

# Equivalent CoreNLP client
from stanza.server import CoreNLPClient
with CoreNLPClient(annotators='tokenize,ssplit,pos,lemma,ner') as client:
    doc = client.annotate("Hello world")

# Data objects are similar but not identical
print(doc.sentences[0].words[0].text)  # Works for both
```
