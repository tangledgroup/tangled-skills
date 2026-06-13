# Processor Reference

## TokenizeProcessor (`tokenize`)

Segments raw text into sentences and tokens. Also predicts multi-word tokens (expanded by MWTProcessor).

**Options:**
- `tokenize_batch_size` (int, default 32): Max paragraphs per minibatch
- `tokenize_pretokenized` (bool, default False): Assume whitespace-tokenized, newline-split
- `tokenize_no_ssplit` (bool, default False): Disable sentence segmentation, use `\n\n` as boundary

```python
nlp = stanza.Pipeline('en', processors='tokenize')
doc = nlp("This is a test sentence. Another one.")
for sent in doc.sentences:
    for token in sent.tokens:
        print(f"id: {token.id}  text: {token.text}")
```

## MWTProcessor (`mwt`)

Expands multi-word tokens predicted by the tokenizer. For languages without MWTs (e.g., Chinese), this processor is not implemented.

No additional options beyond pipeline-level settings.

## POSProcessor (`pos`)

Labels words with Universal POS (UPOS), treebank-specific POS (XPOS), and Universal morphological features (UFeats).

**Options:**
- `pos_batch_size` (int, default 5000): Max words per minibatch. Must exceed longest sentence length.

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos')
doc = nlp("Barack Obama was born in Hawaii.")
for word in doc.sentences[0].words:
    print(f"{word.text}: upos={word.upos} xpos={word.xpos} feats={word.feats or '_'}")
# Barack: upos=PROPN xpos=NNP feats=Number=Sing
# was: upos=AUX xpos=VBD feats=Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin
```

## LemmaProcessor (`lemma`)

Recovers lemma forms for each word. Uses a seq2seq model ensembled with dictionary-based lemmatization.

**Options:**
- `lemma_use_identity` (bool, default False): Use identity lemmatizer (lemma = original form)
- `lemma_batch_size` (int, default 50): Max words per batch
- `lemma_ensemble_dict` (bool, default True): Ensemble seq2seq with dictionary
- `lemma_dict_only` (bool, default False): Use only dictionary-based lemmatizer
- `lemma_edit` (bool, default True): Use edit classifier for shortcut operations
- `lemma_beam_size` (int, default 1): Beam size for seq2seq decoding
- `lemma_pretagged` (bool, default False): Assume document is already tokenized and tagged
- `lemma_max_dec_len` (int, default 50): Max decoding character length

```python
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma')
doc = nlp("The dogs were running.")
for word in doc.sentences[0].words:
    print(f"{word.text} -> {word.lemma}")
# dogs -> dog
# were -> be
# running -> run
```

## DepparseProcessor (`depparse`)

Builds syntactic dependency trees following Universal Dependencies formalism.

**Options:**
- `depparse_batch_size` (int, default 5000): Max words per minibatch
- `depparse_pretagged` (bool, default False): Assume document is tokenized and pretagged
- `depparse_min_length_to_batch_separately` (int, default None): Isolate long sentences to avoid OOM

```python
nlp = stanza.Pipeline('fr', processors='tokenize,mwt,pos,lemma,depparse')
doc = nlp("Nous avons atteint la fin du sentier.")
for word in doc.sentences[0].words:
    head_text = doc.sentences[0].words[word.head - 1].text if word.head > 0 else "root"
    print(f"{word.text} -> {head_text} ({word.deprel})")
# Nous -> atteint (nsubj)
# atteint -> root (root)
# fin -> atteint (obj)
```

## NERProcessor (`ner`)

Recognizes named entity mention spans using BIOES tagging. Supports 23 languages.

**Options:**
- `ner_batch_size` (int, default 32): Max sentences per minibatch
- `ner_pretrain_path` (str): Path to custom pretrained word embeddings

```python
nlp = stanza.Pipeline('en', processors='tokenize,ner')
doc = nlp("Chris Manning teaches at Stanford University. He lives in the Bay Area.")
for ent in doc.ents:
    print(f"entity: {ent.text}  type: {ent.type}")
# entity: Chris Manning  type: PERSON
# entity: Stanford University  type: ORG
# entity: the Bay Area  type: LOC
```

Token-level BIOES tags:

```python
for sent in doc.sentences:
    for token in sent.tokens:
        if token.ner and token.ner != 'O':
            print(f"{token.text}: {token.ner}")
```

Multiple NER models can be used simultaneously:

```python
nlp = stanza.Pipeline('en', processors={'ner': ['ontonotes', 'ncbi_disease']})
```

## SentimentProcessor (`sentiment`)

Assigns per-sentence sentiment scores using a CNN classifier. Scores: 0 (negative), 1 (neutral), 2 (positive).

**Options:**
- `model_path` (str): Model file path
- `pretrain_path` (str): Word vectors path
- `batch_size` (int, default None): Chunk size for processing

```python
nlp = stanza.Pipeline('en', processors='tokenize,sentiment')
doc = nlp("I love this product!")
print(doc.sentences[0].sentiment)  # 2 (positive)
```

Available for English, Chinese, and German.

## ConstituencyProcessor (`constituency`)

Phrase structure parsing using a shift-reduce parser. Available for English, Chinese, Indonesian, Italian, Japanese, Vietnamese.

**Options:**
- `model_path` (str): Model file path
- `pretrain_path` (str): Word vectors path

```python
nlp = stanza.Pipeline('en', processors='tokenize,pos,constituency')
doc = nlp("This is a test")
print(doc.sentences[0].constituency)
# (ROOT (S (NP (DT This)) (VP (VBZ is) (NP (DT a) (NN test)))))
```

Use `package='default_accurate'` for BERT-enhanced models with higher accuracy.

## CorefProcessor (`coref`)

Word-level coreference resolution using Conjunction-Aware Word-level Coreference Resolution (CAW-coref). Available for English (GUM) and Hebrew (IAHLT). Uses transformer models (Electra-Large with PEFT).

```python
nlp = stanza.Pipeline('en', processors='tokenize,coref')
doc = nlp("John Bauer works at Stanford. He has been there 4 years.")
# Coref chains attached at Document level
# Word objects have coref_chains field with CorefAttachment objects
```

## LangidProcessor (`langid`)

Language identification using a character-level Bi-LSTM. Detects 80+ languages. Route texts to language-specific pipelines.

```python
from stanza.pipeline.core import Pipeline
stanza.download('multilingual')
nlp = Pipeline(lang="multilingual", processors="langid")
doc = nlp("Bonjour le monde")
print(doc.lang)  # 'fr'
```
