# Biomedical and Clinical Models

Stanza provides specialized models for biomedical and clinical text analysis, trained on domain-specific corpora like PubMed abstracts, biomedical literature, and clinical notes.

## Overview

Biomedical models offer improved performance on:
- **Syntactic analysis**: Tokenization, POS tagging, lemmatization, dependency parsing for biomedical text
- **Named entity recognition**: Genes, proteins, diseases, chemicals, species, and other biomedical entities

### Available Packages

| Package | Description | Language |
|---------|-------------|----------|
| `biomed` | Biomedical literature models (PubMed) | English |
| `clinical` | Clinical notes models (MIMIC-III) | English |
| `biomed_pos` | POS tagger for biomedical text | English |
| `biomed_depparse` | Dependency parser for biomedical text | English |
| `clinical_ner` | NER for clinical notes | English |

## Installation and Download

### Download Biomedical Models

```python
import stanza

# Download biomedical package
stanza.download('en', package='biomed')

# Download clinical package
stanza.download('en', package='clinical')

# Download specific component
stanza.download('en', package='biomed', processors='ner')
```

### Model Locations

Biomedical models are stored in:
```
~/stanza_resources/en/
├── biomed/
│   ├── tokenize/
│   ├── pos/
│   ├── lemma/
│   ├── depparse/
│   └── ner/
└── clinical/
    └── ner/
```

## Usage Examples

### Biomedical Pipeline

```python
import stanza

# Initialize biomedical pipeline
nlp = stanza.Pipeline('en', package='biomed')

# Process biomedical text
text = "The protein p53 is a tumor suppressor that regulates cell cycle."
doc = nlp(text)

# Access annotations
for word in doc.sentences[0].words:
    print(f"{word.text}: {word.upos} -> {word.lemma}")

# Named entities
for entity in doc.entities:
    print(f"{entity.type}: {entity.text}")
# Output might include: PROTEIN: p53, DISEASE: tumor
```

### Clinical Pipeline

```python
# Initialize clinical pipeline
nlp = stanza.Pipeline('en', package='clinical')

# Process clinical note
text = "Patient presents with chest pain and shortness of breath. History of hypertension."
doc = nlp(text)

# Extract clinical entities
for entity in doc.entities:
    print(f"{entity.type}: {entity.text}")
# Output might include: SYMPTOM: chest pain, HISTORY: hypertension
```

### Component-Specific Usage

Use only specific biomedical processors:

```python
# Biomedical NER only
nlp = stanza.Pipeline(
    'en',
    processors='tokenize,mwt,ner',
    package='biomed'
)

# Biomedical syntax analysis only
nlp = stanza.Pipeline(
    'en',
    processors='tokenize,mwt,pos,lemma,depparse',
    package='biomed'
)
```

## Entity Types

### Biomedical Entities

| Type | Description | Examples |
|------|-------------|----------|
| `GENE` | Gene names | BRCA1, TP53, EGFR |
| `PROTEIN` | Protein names | p53, insulin, hemoglobin |
| `DISEASE` | Diseases and disorders | cancer, diabetes, Alzheimer's |
| `CHEMICAL` | Chemical compounds | aspirin, glucose, ATP |
| `SPECIES` | Organism species | Homo sapiens, Mus musculus |
| `CELL_TYPE` | Cell types | T cell, neuron, fibroblast |

### Clinical Entities

| Type | Description | Examples |
|------|-------------|----------|
| `SYMPTOM` | Symptoms | chest pain, fever, fatigue |
| `DIAGNOSIS` | Diagnoses | pneumonia, myocardial infarction |
| `TREATMENT` | Treatments | chemotherapy, surgery |
| `MEDICATION` | Medications | ibuprofen, metformin |
| `TEST` | Medical tests | CT scan, blood test |
| `HISTORY` | Patient history | family history of cancer |

## Performance Comparison

Biomedical models outperform general-domain models on biomedical text:

| Task | General Model | Biomedical Model | Improvement |
|------|---------------|------------------|-------------|
| Tokenization F1 | 96.2 | 98.1 | +1.9 |
| POS Accuracy | 94.5 | 96.8 | +2.3 |
| Dependency LAS | 82.3 | 85.7 | +3.4 |
| NER F1 (GENE) | 72.4 | 84.6 | +12.2 |

## Training Custom Biomedical Models

### Prepare Biomedical Data

Convert biomedical corpora to CoNLL-U format:

```bash
# Example: Convert PubMed annotations
python scripts/convert_biomed_to_conllu.py \
    --input pubmed_annotations.xml \
    --output biomed_train.conllu
```

### Train Biomedical POS Tagger

```bash
python -m stanza.utils.training.run_pos biomed_corpus \
    --train_file data/biomed_train.conllu \
    --eval_file data/biomed_dev.conllu \
    --batch_size 512 \
    --hidden_dim 256 \
    --pretrain_path saved_models/pos/biomed.pretrain.pt \
    --save_dir saved_models/pos/biomed_custom
```

### Train Biomedical NER

```bash
python -m stanza.utils.training.run_ner biomed_ner \
    --train_file data/biomed_ner_train.json \
    --eval_file data/biomed_ner_dev.json \
    --batch_size 64 \
    --hidden_dim 256 \
    --pretrain_path saved_models/pos/biomed.pretrain.pt
```

## Domain Adaptation

Fine-tune general models on biomedical text:

```bash
# Start from English EWT model, fine-tune on biomedical corpus
python -m stanza.utils.training.run_pos UD_English-EWT \
    --fine_tune \
    --model_path saved_models/pos/en_ewt.pt \
    --train_file data/biomed_train.conllu \
    --iter 50  # Fewer iterations for fine-tuning
```

## Common Biomedical Corpora

### Available Datasets

| Corpus | Description | Size |
|--------|-------------|------|
| **PubMed** | Biomedical abstracts | ~30M articles |
| **PMC** | Full-text biomedical articles | ~6M articles |
| **MIMIC-III** | Clinical notes | ~170K notes |
| **i2b2** | Clinical NLP challenges | Various |
| **BC5CDR** | Chemical-disease relations | 1,503 documents |
| **JNLPBA** | Gene mention corpus | 940 articles |

### Data Formats

Most biomedical corpora use custom formats. Convert to CoNLL-U:

```python
from stanza.io import ConllUDocument

# Read custom format
def parse_biomed_annotation(file_path):
    """Parse biomedical annotation file."""
    sentences = []
    for line in open(file_path):
        # Extract tokens, POS tags, entities
        # ...
        pass
    
    return ConllUDocument(sentences)
```

## Integration with Other Tools

### BioBERT Integration

Combine Stanza with BioBERT for enhanced performance:

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import stanza

# Use Stanza for tokenization and syntax
stanza_nlp = stanza.Pipeline('en', package='biomed', processors='tokenize,pos')

# Use BioBERT for specialized NER
biobert_tokenizer = AutoTokenizer.from_pretrained('dmis-lab/biobert-base-uncased')
biobert_model = AutoModelForTokenClassification.from_pretrained('dmis-lab/biobert-nfbase')

def hybrid_ner(text):
    # Stanza for syntax
    stanza_doc = stanza_nlp(text)
    
    # BioBERT for NER
    encoded = biobert_tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        predictions = biobert_model(**encoded)
    
    # Combine results
    return stanza_doc, predictions
```

### spaCy Biomedical Models

Use Stanza alongside spaCy's biomedical models:

```python
import stanza
import spacy

# Stanza for multilingual support
stanza_nlp = stanza.Pipeline('en', package='biomed')

# spaCy for fast inference
spacy_nlp = spacy.load("en_ner_bionlp13cg_md")

def compare_results(text):
    stanza_doc = stanza_nlp(text)
    spacy_doc = spacy_nlp(text)
    
    print("Stanza entities:")
    for entity in stanza_doc.entities:
        print(f"  {entity.type}: {entity.text}")
    
    print("spaCy entities:")
    for ent in spacy_doc.ents:
        print(f"  {ent.label_}: {ent.text}")
```

## Troubleshooting

### Model Not Found

```python
# Ensure biomedical package is downloaded
stanza.download('en', package='biomed')

# Verify installation
import os
print(os.listdir('~/stanza_resources/en/'))
# Should include 'biomed' directory
```

### Poor Entity Recognition

- Check if text matches training domain (PubMed vs clinical notes)
- Use appropriate package (`biomed` for literature, `clinical` for notes)
- Consider fine-tuning on domain-specific data

### Memory Issues

Biomedical models can be larger. Increase memory:

```python
nlp = stanza.Pipeline(
    'en',
    package='biomed',
    pos_batch_size=256,  # Reduce batch size
    depparse_batch_size=32
)
```

## Citation

If you use biomedical models in your research:

```bibtex
@article{zhang2021biomedical,
    author = {Zhang, Yuhao and Zhang, Yuhui and Qi, Peng and Manning, Christopher D and Langlotz, Curtis P},
    title = {Biomedical and clinical English model packages for the Stanza Python NLP library},
    journal = {Journal of the American Medical Informatics Association},
    year = {2021},
    month = {06},
    issn = {1527-974X}
}
```

## Resources

- **Biomedical models paper**: https://arxiv.org/abs/2007.14640
- **Online demo**: https://stanfordnlp.github.io/stanza/biomed.html
- **MIMIC-III dataset**: https://mimic.physionet.org/
- **BC5CDR corpus**: http://www.nactem.ac.uk/tpldata/BC5CDR/
