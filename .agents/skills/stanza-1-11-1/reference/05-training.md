# Training Custom Models

## Overview

All neural modules in Stanza can be trained on custom annotated data. Training is done from source (not via the Pipeline interface).

**Data formats:**
- CoNLL-U format: Required for tokenizer, MWT expander, POS/morphological tagger, lemmatizer, and dependency parser
- BIOES format: Required for NER models

## Training from Source

```bash
git clone https://github.com/stanfordnlp/stanza.git
cd stanza
pip install -e .
```

Training scripts are located in `stanza/train/`. Each processor has its own training entry point.

## Training a UD Pipeline (Tokenize, POS, Lemma, Depparse)

For Universal Dependencies tasks, prepare data in CoNLL-U format:

```
# sent_id = sentence-1
# text = The cat sat on the mat .
1	The	the	DET	DT	Number=Sing	4	det	_	_
2	cat	cat	NOUN	NN	Number=Sing	3	nsubj	_	_
3	sat	sit	VERB	VBD	Tense=Past|VerbForm=Fin	0	root	_	_
4	on	on	ADP	IN	_	3	case	_	_
5	the	the	DET	DT	Number=Sing	6	det	_	_
6	mat	mat	NOUN	NN	Number=Sing	3	obl	_	_
7	.	.	PUNCT	.	_	3	punct	_	_
```

Train individual processors or the full pipeline using scripts in `stanza/train/`.

## Training NER

Prepare data in BIOES format (one token per line, tags prefixed with B-, I-, E-, S-, O-):

```
Chris	B-PER
Manning	I-PER
teaches	O
at	STANFORD
Stanford	B-ORG
University	E-ORG
.	O
```

## Word Vectors

Custom word vectors can be used during training. Stanza supports:
- Pretrained embeddings (fastText, GloVe)
- Character-level language models (CharLM) for better coverage of unseen words

## Adding a New Language

To add support for a new language:
1. Prepare annotated data in the appropriate format
2. Train each processor independently
3. Register the models with Stanza's resources system
4. Test with the Pipeline interface

## Evaluation

Each training script supports evaluation on held-out test data. Metrics vary by task:
- Tokenization: token accuracy, sentence boundary accuracy
- POS: UPOS F1, XPOS F1, all-tags accuracy
- Lemmatization: lemma accuracy
- Dependency parsing: UAS (Unlabeled Attachment Score), LAS (Labeled Attachment Score)
- NER: entity-level F1

## Biomedical Model Training

Biomedical models follow the same training process but use domain-specific annotated corpora. Training data includes biomedical literature and clinical notes with entity annotations for diseases, chemicals, and genes.
