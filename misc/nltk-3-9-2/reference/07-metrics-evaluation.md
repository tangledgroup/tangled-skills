# Metrics & Evaluation

## String Distance Metrics

### Edit Distance (Levenshtein)

Minimum number of single-character edits (insertions, deletions, substitutions) to transform one string into another:

```python
from nltk.metrics import edit_distance

distance = edit_distance('learning', 'leaning')
print(distance)  # 1

# With alignment
distance, alignment = edit_distance('learning', 'leaning', step_cost={'ins': 1, 'del': 1, 'sub': 1}, return_one=False)
```

### Jaro and Jaro-Winkler Similarity

Measures similarity between two strings (higher = more similar):

```python
from nltk.metrics import jaro_similarity, jaro_winkler_similarity

print(jaro_similarity('catherine', 'katharine'))
# 0.919...

print(jaro_winkler_similarity('catherine', 'katharine'))
# 0.944... (bonus for matching prefix)
```

### Other Distance Measures

```python
from nltk.metrics import binary_distance, jaccard_distance, fractional_presence, presence, interval_distance, masi_distance

# Binary distance — proportion of differing bits
print(binary_distance([1, 0, 1], [1, 1, 0]))  # 0.333

# Jaccard distance
print(jaccard_distance(set('abc'), set('bcd')))  # 0.667

# Fractional presence — fraction of positions where one is present
print(fractional_presence([1, 0, 1], [1, 1, 1]))
```

## Machine Translation Metrics

### BLEU Score

Bilingual Evaluation Understudy — the standard MT evaluation metric:

```python
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction

# Single sentence
references = [['This', 'is', 'a', 'test'], ['This', 'is', 'testing']]
hypothesis = ['This', 'is', 'a', 'test']

bleu = sentence_bleu(references, hypothesis)
print(bleu)  # 1.0 (perfect match with first reference)

# With smoothing for short sentences
smoothie = SmoothingFunction()
bleu_smooth = sentence_bleu(
    references, hypothesis,
    smoothing_function=smoothie.method1
)

# Corpus-level BLEU
references = [[['This', 'is', 'a', 'test']], [['Another', 'sentence']]]
hypotheses = [['This', 'is', 'a', 'test'], ['Another', 'sentenc']]

corpus_bleu_score = corpus_bleu(references, hypotheses)

# Multi-reference BLEU
multi_refs = [
    [['good', 'translation'], ['nice', 'translation']],
    [['bad', 'output'], ['poor', 'result']]
]
hypotheses = [['good', 'translation'], ['bad', 'output']]
bleu = corpus_bleu(multi_refs, hypotheses)
```

Smoothing functions: `method0` through `method7`.

### METEOR Score

Metric for Evaluation of Translation with Explicit Ordering — considers synonyms and stemming:

```python
from nltk.translate.meteor_score import meteor_score

reference = "The cat is on the mat"
hypothesis = "The cat sits on the mat"

# Requires pre-tokenized input (NLTK 3.6.6+)
score = meteor_score(
    [reference.split()],
    hypothesis.split()
)
print(score)
```

### chrF Score

Character n-gram F-score — effective for morphologically rich languages:

```python
from nltk.translate.chrf_score import corpus_chrf, sentence_chrf

score = sentence_chrf(['The cat sat'], 'The cat sit')
print(score)  # 0.87...
```

### GLEU Score

Geometric Mean of BLEU scores across n-gram orders:

```python
from nltk.translate.gleu_score import corpus_gleu, sentence_gleu

score = sentence_gleu([['The', 'cat', 'sat']], ['The', 'cat', 'sat'])
```

### RIBES Score

Rating index for machine translation based on sentence editing:

```python
from nltk.translate.ribes_score import corpus_ribes, sentence_ribes

score = sentence_ribes(['The', 'cat', 'sat'], ['The', 'cat', 'sat'])
```

### NIST Score

National Institute of Standards and Technology metric:

```python
from nltk.translate.nist_score import corpus_nist, sentence_nist

score = sentence_nist([['The', 'cat', 'sat']], ['The', 'cat', 'sat'])
```

### LEPOr Score

Length-Penalized Order score:

```python
from nltk.translate.lepor import corpus_lepor, sentence_lepor

score = sentence_lepor(['The', 'cat', 'sat'], ['The', 'cat', 'sat'])
```

### Alignment Error Rate

```python
from nltk.translate.metrics import alignment_error_rate

alignment1 = [(0, 0), (1, 1)]
alignment2 = [(0, 0), (1, 2)]
aer = alignment_error_rate(alignment1, alignment2)
```

## Classification Metrics

### Precision, Recall, F-Measure

```python
from nltk.metrics import precision, recall, f_measure

predicted = set(['cat', 'dog', 'bird'])
reference = set(['cat', 'dog', 'fish'])

print(precision(reference, predicted))    # 0.667
print(recall(reference, predicted))       # 0.667
print(f_measure(reference, predicted))    # 0.667
```

### Accuracy

```python
from nltk.metrics import accuracy

ref = ['a', 'b', 'c', 'd']
hyp = ['a', 'b', 'x', 'd']
print(accuracy(ref, hyp))  # 0.75
```

### Confusion Matrix

```python
from nltk.metrics import ConfusionMatrix

cm = ConfusionMatrix(
    ['cat', 'cat', 'dog', 'dog', 'bird'],
    ['cat', 'dog', 'dog', 'cat', 'bird']
)

cm.pretty_format()
# Shows misclassifications

print(cm.precision())
print(cm.recall())
print(cm.f_measure())
```

### Approximate Rand Index

Cluster comparison metric:

```python
from nltk.metrics import approxrand

cluster1 = ['A', 'A', 'B', 'B']
cluster2 = ['A', 'B', 'A', 'B']
print(approxrand(cluster1, cluster2))
```

## Inter-Annotator Agreement

### Kappa Statistics

```python
from nltk.metrics.agreement import AnnotationTask

at = AnnotationTask()
at.load_array([
    ('annotator1', 'item1', 'positive'),
    ('annotator1', 'item2', 'negative'),
    ('annotator2', 'item1', 'positive'),
    ('annotator2', 'item2', 'positive'),
])

print(at.kappa())           # Cohen's kappa
print(at.multi_kappa())     # Multi-rater kappa
print(at.pi())              # Scott's pi
print(at.alpha())           # Krippendorff's alpha
```

### Weighted Kappa

For ordinal categories:

```python
at.weighted_kappa()
```

## Association Measures

Find significant word collocations:

```python
from nltk.metrics import BigramAssocMeasures, NgramAssocMeasures
from nltk.collocations import BigramCollocationFinder

finder = BigramCollocationFinder.from_words(words)
finder.apply_freq_filter(3)  # minimum frequency

# Score bigrams by various measures
bigrams = finder.nbest(BigramAssocMeasures.pmi, 10)
bigrams = finder.nbest(BigramAssocMeasures.chi_sq, 10)
bigrams = finder.nbest(BigramAssocMeasures.likelihood_ratio, 10)
bigrams = finder.nbest(BigramAssocMeasures.dice, 10)
bigrams = finder.nbest(BigramAssocMeasures.fisher, 10)

# Score by frequency
bigrams = finder.score_ngrams(BigramAssocMeasures.raw_freq)
```

### N-gram Association

```python
trigrams = finder.nbest(NgramAssocMeasures.pmi, 10)
```

## Segmentation Metrics

For evaluating text segmentation:

```python
from nltk.metrics.segmentation import pk, windowdiff, ghd

# PK (PK error rate)
print(pk([0, 0, 1, 0], [0, 0, 0, 1]))

# Window Diff
print(windowdiff([0, 0, 1, 0], [0, 0, 0, 1]))

# Global Alignment Error
print(ghd([0, 0, 1, 0], [0, 0, 0, 1]))
```

## Spearman Correlation

```python
from nltk.metrics import spearman_correlation

scores1 = [1, 2, 3, 4, 5]
scores2 = [5, 4, 3, 2, 1]
print(spearman_correlation(scores1, scores2))  # -1.0
```

## Paice Similarity

Dictionary-based word similarity:

```python
from nltk.metrics import Paice

paice = Paice()
paice.update(word_list)  # build from dictionary
print(paice.similarity('car', 'automobile'))
```
