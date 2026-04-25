# Custom Processors and Variants

## Processor Variants

Processor variants allow you to integrate external tools or custom implementations into the Stanza pipeline while maintaining compatibility with existing processors.

### What Are Processor Variants?

Variants are alternative implementations of existing processor functionality. They're useful when:
- You want to use spaCy's tokenizer instead of Stanza's
- You have a custom lemmatizer for a specific domain
- You need to integrate with external NLP services

### Registering a Variant

Use the `@register_processor_variant` decorator:

```python
from stanza.pipeline.processor import ProcessorVariant, register_processor_variant

@register_processor_variant('tokenize', 'spacy')
class SpacyTokenizer(ProcessorVariant):
    """Use spaCy for tokenization instead of Stanza's tokenizer."""
    
    def __init__(self, config):
        import spacy
        self.nlp = spacy.load('en_core_web_sm')
    
    def process(self, text):
        """Tokenize text using spaCy."""
        doc = self.nlp(text)
        # Return tokens as expected by Stanza
        return [token.text for token in doc]
```

### Using a Variant

Once registered, use it via the `processors` parameter:

```python
import stanza

# Import the variant first to trigger registration
from my_custom_module import SpacyTokenizer  # Contains the decorator

nlp = stanza.Pipeline(
    'en',
    processors={'tokenize': 'spacy', 'pos': 'default'}
)

doc = nlp("Hello world!")
```

### Override Mode

For variants that completely replace a processor:

```python
@register_processor_variant('lemma', 'cool')
class CoolLemmatizer(ProcessorVariant):
    """Replace all lemmas with 'cool' (example only!)."""
    
    OVERRIDE = True  # This replaces the entire LemmaProcessor
    
    def __init__(self, lang):
        pass
    
    def process(self, document):
        for sentence in document.sentences:
            for word in sentence.words:
                word.lemma = "cool"
        
        return document
```

Usage:
```python
nlp = stanza.Pipeline('en', processors={'lemma': 'cool'})
doc = nlp("The cats were running.")
print(doc.sentences[0].words[1].lemma)  # 'cool'
```

## Creating Custom Processors

Create entirely new processors for custom annotation tasks.

### Basic Processor Structure

```python
from stanza.pipeline.processor import Processor, register_processor

@register_processor('lowercase')
class LowercaseProcessor(Processor):
    """Processor that lowercases all text."""
    
    # Declare dependencies and outputs
    _requires = set(['tokenize'])  # Needs tokenization first
    _provides = set(['lowercase'])  # Provides 'lowercase' annotation
    
    def __init__(self, device, config, pipeline):
        """Initialize the processor."""
        self.device = device
        self.config = config
        self.pipeline = pipeline
    
    def _set_up_model(self, *args):
        """Load models if needed (can be empty for simple processors)."""
        pass
    
    def process(self, doc):
        """Process a document and return it."""
        # Lowercase all text
        doc.text = doc.text.lower()
        
        for sent in doc.sentences:
            sent.text = sent.text.lower()
            
            for token in sent.tokens:
                token.text = token.text.lower()
            
            for word in sent.words:
                word.text = word.text.lower()
        
        return doc
```

### Using Custom Processors

```python
# Import to register the processor
from my_module import LowercaseProcessor

nlp = stanza.Pipeline('en', processors='tokenize,lowercase')
doc = nlp("HELLO WORLD")
print(doc.text)  # 'hello world'
```

### Advanced: Model-Based Processor

Create a processor that loads and uses a neural model:

```python
import torch
from stanza.pipeline.processor import Processor, register_processor

@register_processor('custom_tagger')
class CustomTaggerProcessor(Processor):
    """Custom tagger using a PyTorch model."""
    
    _requires = set(['tokenize'])
    _provides = set(['custom_tag'])
    
    def __init__(self, device, config, pipeline):
        self.device = device
        self.config = config
        
        # Load custom model
        model_path = config.get('model_path', 'default_model.pt')
        self.model = CustomTaggerModel.load(model_path).to(device)
        self.model.eval()
    
    def process(self, doc):
        """Apply custom tagging to document."""
        with torch.no_grad():
            for sent in doc.sentences:
                # Extract features
                tokens = [token.text for token in sent.tokens]
                
                # Run model
                tags = self.model.predict(tokens)
                
                # Attach tags to tokens
                for token, tag in zip(sent.tokens, tags):
                    token.misc = f"custom_tag={tag}"
        
        return doc
```

Usage:
```python
nlp = stanza.Pipeline(
    'en',
    processors='tokenize,custom_tagger',
    custom_tagger_model_path='./my_custom_model.pt'
)
```

## Pre-trained Model Integration

Integrate models from other frameworks:

### spaCy Integration

```python
from stanza.pipeline.processor import ProcessorVariant, register_processor_variant
import spacy

@register_processor_variant('ner', 'spacy')
class SpacyNER(ProcessorVariant):
    """Use spaCy's NER instead of Stanza's."""
    
    def __init__(self, config):
        self.nlp = spacy.load('en_core_web_sm')
    
    def process(self, document):
        """Run spaCy NER and convert to Stanza format."""
        for sent in document.sentences:
            spacy_doc = self.nlp(sent.text)
            
            for ent in spacy_doc.ents:
                # Create Stanza Span for entity
                from stanza.models.common.doc import Span
                span = Span(
                    doc=document,
                    text=ent.text,
                    type=ent.label_,
                    start_char=ent.start_char,
                    end_char=ent.end_char
                )
                sent.entities.append(span)
                document.entities.append(span)
        
        return document
```

### NLTK Integration

```python
from stanza.pipeline.processor import ProcessorVariant, register_processor_variant
import nltk

@register_processor_variant('pos', 'nltk')
class NLTKPOSTagger(ProcessorVariant):
    """Use NLTK's POS tagger."""
    
    def __init__(self, config):
        self.tagger = nltk.pos_tag
    
    def process(self, document):
        for sent in document.sentences:
            tokens = [token.text for token in sent.tokens]
            tagged = self.tagger(tokens)
            
            for token, (word, pos) in zip(sent.tokens, tagged):
                # Map NLTK POS to Universal POS if needed
                word.upos = map_to_upos(pos)
        
        return document
```

## Adding Custom Annotations

Extend Stanza data objects with custom properties:

```python
from stanza.models.common.doc import Document, Sentence, Word, Token

# Add property to Word class
Word.add_property(
    'sentiment_score',
    default=0.0,
    getter=lambda self: getattr(self, '_sentiment_score', 0.0),
    setter=lambda self, value: setattr(self, '_sentiment_score', value)
)

# Now you can set and get sentiment scores on words
for word in doc.sentences[0].words:
    word.sentiment_score = calculate_sentiment(word.text)
    print(word.text, word.sentiment_score)
```

## Example: Domain-Specific Processor

Create a processor for biomedical entity recognition:

```python
from stanza.pipeline.processor import Processor, register_processor

@register_processor('biomed_ner')
class BiomedNERProcessor(Processor):
    """Recognize biomedical entities (genes, proteins, diseases)."""
    
    _requires = set(['tokenize'])
    _provides = set(['biomed_entity'])
    
    def __init__(self, device, config, pipeline):
        # Load biomedical dictionary or model
        self.entity_dict = load_biomedical_entities()
        self.model = BiomedicalNERModel().to(device)
    
    def process(self, doc):
        """Annotate biomedical entities."""
        for sent in doc.sentences:
            # Use dictionary-based matching or neural model
            entities = self.find_entities(sent.text)
            
            for entity_text, entity_type in entities:
                from stanza.models.common.doc import Span
                span = Span(
                    doc=doc,
                    text=entity_text,
                    type=entity_type,  # 'GENE', 'PROTEIN', 'DISEASE'
                    start_char=sent.text.find(entity_text),
                    end_char=sent.text.find(entity_text) + len(entity_text)
                )
                sent.entities.append(span)
        
        return doc
```

## Testing Custom Processors

Write tests for your custom processors:

```python
import stanza
from my_module import LowercaseProcessor

def test_lowercase_processor():
    nlp = stanza.Pipeline('en', processors='tokenize,lowercase')
    doc = nlp("HELLO World")
    
    assert doc.text == "hello world"
    assert doc.sentences[0].words[0].text == "hello"
    assert doc.sentences[0].words[1].text == "world"

def test_variant_registration():
    from stanza.pipeline.registry import PROCESSOR_VARIANTS
    
    # Check if variant is registered
    assert 'spacy' in PROCESSOR_VARIANTS['tokenize']
```

## Performance Considerations

### Lazy Loading

Load models only when needed:

```python
class EfficientProcessor(Processor):
    def __init__(self, device, config, pipeline):
        self.device = device
        self._model = None
    
    @property
    def model(self):
        if self._model is None:
            self._model = load_model().to(self.device)
        return self._model
```

### Batch Processing

Process multiple sentences together:

```python
def process(self, doc):
    # Collect all sentences
    all_tokens = [[t.text for t in sent.tokens] for sent in doc.sentences]
    
    # Batch process
    all_tags = self.model.predict_batch(all_tokens)
    
    # Distribute results
    for sent, tags in zip(doc.sentences, all_tags):
        for token, tag in zip(sent.tokens, tags):
            token.misc = tag
    
    return doc
```

## Debugging Tips

### Enable Logging

```python
nlp = stanza.Pipeline('en', processors='tokenize,custom_processor', logging_level='DEBUG')
```

### Add Debug Output

```python
def process(self, doc):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Processing document with {len(doc.sentences)} sentences")
    
    for i, sent in enumerate(doc.sentences):
        logger.debug(f"Sentence {i}: {sent.text}")
    
    return doc
```

### Type Checking

Add type hints for better IDE support:

```python
from typing import List
from stanza.models.common.doc import Document

def process(self, doc: Document) -> Document:
    """Process document and return annotated version."""
    # Implementation...
    return doc
```
