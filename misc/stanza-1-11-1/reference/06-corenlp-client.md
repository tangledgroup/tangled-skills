# CoreNLP Client

## Overview

Stanza includes an official Python wrapper for the Java Stanford CoreNLP software. It launches a CoreNLP server as a background process and sends annotation requests to it. The response is parsed into Stanza Document protobuf objects, allowing you to use CoreNLP's full functionality from native Python code.

## Setup

1. Download Stanford CoreNLP and language models from https://stanfordnlp.github.io/CoreNLP/
2. Place model JARs in the distribution folder
3. Set the `CORENLP_HOME` environment variable:

```bash
export CORENLP_HOME=/path/to/stanford-corenlp-4.5.3
```

## Basic Usage

```python
from stanza.server import CoreNLPClient

# Start client — launches Java server in background
with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse'],
                   timeout=30000,
                   memory='4G',
                   be_quiet=True) as client:
    # Annotate text
    ann = client.annotate('Barack Obama was born in Hawaii.')

    # Access annotations
    for sentence in ann.sentences:
        for token in sentence.tokens:
            print(f"{token.word}: pos={token.pos} ner={token.ner}")
```

## Available CoreNLP Annotators

CoreNLP provides additional annotators beyond the neural pipeline:
- `tokenize`, `ssplit` — Tokenization and sentence splitting
- `pos` — Part-of-speech tagging
- `lemma` — Lemmatization
- `ner` — Named entity recognition
- `parse` — Constituency parsing (full parse tree)
- `depparse` — Dependency parsing
- `coref` — Coreference resolution
- `openie` — Open information extraction
- `sentiment` — Sentiment analysis
- `quote` — Quotation detection
- `entitylink` — Entity linking to Wikipedia/Wikidata

## Semgrex

Semgrex is a pattern matching language for searching dependency graphs. Accessible through the CoreNLP client:

```python
from stanza.server import CoreNLPClient

with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'depparse'],
                   be_quiet=True) as client:
    ann = client.annotate('The cat sat on the mat.')

    # Search for nouns that are subjects of verbs
    matches = client.semgrex(ann, pattern='{word:/cat|dog/} < {upostag:VERB}')
    for match in matches.matches:
        print(match)
```

Semgrex pattern syntax supports:
- `{property:value}` — Match tokens by property (word, upostag, lemma, etc.)
- `<` — Child relation (dependent of)
- `>` — Parent relation (head of)
- `.` — Rightward adjacency
- ``  — Leftward adjacency
- `..` / `..` — Any distance right/left
- Named nodes with `=name` for referencing

## Ssurgeon

Ssurgeon edits dependency trees based on Semgrex search patterns:

```python
from stanza.server import CoreNLPClient

with CoreNLPClient(annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'depparse'],
                   be_quiet=True) as client:
    ann = client.annotate('The cat sat on the mat.')

    # Edit: change lemma of matched nodes
    result = client.ssurgeon(ann,
        semgrex='{word:cat}=target',
        edits='editNode -node target -lemma feline')
```

Common Ssurgeon edits:
- `editNode -node <name> -lemma <lemma>` — Change lemma
- `editNode -node <name> -upostag <tag>` — Change POS tag
- `combineMWT -node <name1> -node <name2>` — Combine nodes into MWT

## Tsurgeon

Tsurgeon is the constituency parse tree equivalent of Ssurgeon, for editing phrase structure trees.

## Advanced Client Options

```python
client = CoreNLPClient(
    annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'depparse', 'coref'],
    properties={
        'ner.model': 'models/maven_ner/model',  # Custom NER model
        'parse.model': 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz',
    },
    timeout=60000,
    memory='8G',
    output_format='json',  # 'json', 'conllu', 'serialized'
)
```

Output formats:
- `json` — JSON representation of annotations
- `conllu` — CoNLL-U format for dependency parses
- `serialized` — Binary serialized annotation object
