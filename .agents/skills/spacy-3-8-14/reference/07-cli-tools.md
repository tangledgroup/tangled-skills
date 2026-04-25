# Command-Line Interface Tools

This guide covers spaCy's command-line tools for model management, training, evaluation, and system utilities.

## Overview of CLI Commands

spaCy provides a comprehensive CLI accessible via `python -m spacy`:

```bash
# Show all available commands
python -m spacy --help

# Show help for specific command
python -m spacy download --help
python -m spacy train --help
```

## Model Management

### Downloading Models

```bash
# Download English models (small, medium, large)
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python -m spacy download en_core_web_lg

# Download transformer-based model
python -m spacy download en_core_web_trf

# Download models for other languages
python -m spacy download de_core_news_sm  # German
python -m spacy download fr_core_news_sm  # French
python -m spacy download es_core_news_sm  # Spanish
python -m spacy download ja_core_news_sm  # Japanese
python -m spacy download zh_core_web_sm   # Chinese

# Download to custom location
python -m spacy download en_core_web_sm --download-dir ./models

# Force re-download
python -m spacy download en_core_web_sm --force
```

### Listing Installed Models

```bash
# Show all installed models
python -m spacy validate

# Output includes:
# - Model name and version
# - Compatibility with current spaCy version
# - Language code
# - Pipeline components
```

### Validating Models

```bash
# Check model compatibility
python -m spacy validate

# Validate specific model
python -m spacy validate ./path/to/model

# Check all models in directory
python -m spacy validate --models-dir ./models
```

Validation checks:
- spaCy version compatibility
- Model metadata integrity
- Pipeline component registration
- Vector table consistency

### Creating Blank Models

```bash
# Create a blank model for any language
python -m spacy init blank en ./blank_en

# Create with specific components
python -m spacy init blank en ./blank_en --pipes ner,textcat

# Create from existing model (copy structure)
python -m spacy init blank en_core_web_sm ./custom_model
```

## Training Commands

### Initializing Training Configuration

```bash
# Create config from blank model
python -m spacy init config default_config.cfg

# Create config from existing model
python -m spacy init config en_core_web_sm my_config.cfg

# Create with specific pipeline
python -m spacy init config --pipeline ner,textcat my_config.cfg
```

### Training Models

```bash
# Basic training
python -m spacy train config.cfg \
    --paths.train train.json \
    --paths.dev dev.json \
    --output output

# Training with GPU
python -m spacy train config.cfg \
    --paths.train train.json \
    --gpu-id 0

# Resume training from checkpoint
python -m spacy train config.cfg \
    --paths.train train.json \
    --init-nlp output/model-best

# Training with specific epochs
python -m spacy train config.cfg \
    --paths.train train.json \
    --epochs 20

# Dry run (validate config without training)
python -m spacy train config.cfg --dry-run
```

### Training Data Formats

```bash
# Convert documents to training format
python -m spacy init lookups en ./lookups

# Create training data from annotations
python -m spacy annotate "text here" \
    --output train.jsonl \
    --format jsonl
```

## Evaluation and Scoring

### Evaluating Models

```bash
# Evaluate model on test data
python -m spacy evaluate ./my_model ./test.json

# Evaluate with specific components
python -m spacy evaluate ./my_model ./test.json --stats ner,textcat

# Output to file
python -m spacy evaluate ./my_model ./test.json --output results.json
```

### Comparing Models

```bash
# Compare multiple models on same data
python -m spacy compare \
    ./model_v1 ./model_v2 ./model_v3 \
    --data ./test.json \
    --output comparison.json
```

## Project Management

### Creating Projects

```bash
# Initialize a new spaCy project
python -m spacy init project my_project

# Create from template
python -m spacy init project \
    https://github.com/explosion/projects \
    --name my_training_project \
    ./my_project
```

### Running Projects

```bash
# Execute project workflow
python -m spacy project run ./path/to/project

# Run specific step
python -m spacy project run ./path/to/project --step train

# Run with GPU
python -m spacy project run ./path/to/project --gpu 0

# Run in background (Docker)
python -m spacy project run ./path/to/project --docker
```

## Visualization Tools

### displaCy Visualization

```bash
# Visualize NER entities
python -m spacy visualize ner ./my_model "John works at Google in New York"

# Visualize dependency parsing
python -m spacy visualize parse ./my_model "The quick brown fox jumps over the lazy dog"

# Save visualization to HTML
python -m spacy visualize ner ./my_model "Text here" --output entities.html

# Customize colors
python -m spacy visualize ner ./my_model "Text here" \
    --colors '{"PERSON": "#ff0000", "ORG": "#00ff00"}'
```

### Interactive Visualization

```bash
# Start interactive visualization server
python -m spacy serve ./my_model --port 5000

# Then access at http://localhost:5000
```

## Language and Tokenization

### Listing Languages

```bash
# Show all supported languages
python -m spacy info languages

# Show language details
python -m spacy info languages en
```

### Tokenization Utilities

```bash
# Tokenize text
echo "Hello, world!" | python -m spacy tokenize en

# Show token details
echo "Hello, world!" | python -m spacy annotate en \
    --show pos,lemma,morph

# Compare tokenizers
python -m spacy info tokenizer en "Sample text here"
```

## Model Conversion and Migration

### Converting Models

```bash
# Convert v2 model to v3 format
python -m spacy migrate ./v2_model ./v3_model

# Convert training data format
python -m spacy convert train_v2.json train_v3.json
```

### Migrating from v2.x

```bash
# Migrate trained model
python -m spacy migrate \
    ./path/to/v2/model \
    ./path/to/v3/model

# Migrate configuration
python -m spacy migrate-config \
    old_config.cfg \
    new_config.cfg
```

## System Information

### Checking Installation

```bash
# Show spaCy version and system info
python -m spacy info

# Show detailed system information
python -m spacy info --system

# Check GPU availability
python -m spacy info --gpu
```

### Environment Variables

```bash
# Set custom model location
export SPACY_MODEL_DIR=./models
python -m spacy download en_core_web_sm

# Disable progress bars
export SPACY_DISABLE_PROGRESS_BAR=1
python -m spacy train config.cfg

# Set log level
export SPACY_LOG_LEVEL=DEBUG
python -m spacy train config.cfg
```

## Advanced CLI Usage

### Using Custom Factories

```bash
# Register custom component
python -c "
from spacy.language import Language
from spacy.tokens import Doc

@Language.component('my_component')
def my_component(doc):
    return doc

nlp = spacy.blank('en')
nlp.add_pipe('my_component')
nlp.to_disk('./custom_model')
"

# Use custom model
python -m spacy validate ./custom_model
```

### Batch Processing with CLI

```bash
# Process file with specific model
python -m spacy annotate input.txt \
    --model en_core_web_sm \
    --output output.jsonl

# Process multiple files
for file in *.txt; do
    python -m spacy annotate "$file" \
        --model en_core_web_sm \
        --output "outputs/${file%.txt}.jsonl"
done
```

### Profiling and Debugging

```bash
# Profile model performance
python -m spacy profile ./my_model --text "Sample text" --iterations 100

# Debug mode with verbose output
python -m spacy train config.cfg --verbose

# Profile memory usage
python -c "
import tracemalloc
import spacy

tracemalloc.start()
nlp = spacy.load('en_core_web_sm')
docs = list(nlp.pipe(['Sample text'] * 1000))
current, peak = tracemalloc.get_traced_memory()
print(f'Current: {current / 1024**2:.1f}MB; Peak: {peak / 1024**2:.1f}MB')
tracemalloc.stop()
"
```

## Common CLI Workflows

### Quick Setup and Training

```bash
# 1. Create project structure
python -m spacy init project \
    https://github.com/explosion/projects \
    --name training_ner \
    ./my_project

cd ./my_project

# 2. Prepare data (edit config.yaml)

# 3. Initialize configuration
python -m spacy init config config.cfg

# 4. Train model
python -m spacy train config.cfg \
    --paths.train data/train.json \
    --paths.dev data/dev.json \
    --output output

# 5. Evaluate
python -m spacy evaluate output/model-best data/test.json

# 6. Package for distribution
cd output/model-best
python setup.py sdist bdist_wheel
```

### Production Deployment Pipeline

```bash
# 1. Train final model
python -m spacy train config.cfg \
    --paths.train all_training_data.json \
    --epochs 50 \
    --output production_model

# 2. Validate
python -m spacy validate production_model/model-best

# 3. Evaluate on held-out test set
python -m spacy evaluate production_model/model-best final_test.json \
    --output evaluation_results.json

# 4. Create distribution package
cd production_model/model-best
pip install build
python -m build --wheel

# 5. Install in production environment
pip install dist/*.whl

# 6. Verify installation
python -m spacy validate
```

## Troubleshooting CLI Issues

### Model Download Failures

```bash
# Check network connectivity
python -m spacy info

# Try direct pip installation
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# Use mirror or alternative source
python -m spacy download en_core_web_sm --url https://alternative-url.com/model.tar.gz
```

### Training Configuration Errors

```bash
# Validate config before training
python -m spacy train config.cfg --dry-run

# Check for common issues
python -c "
import spacy
nlp = spacy.load_config('config.cfg')
print('Config loaded successfully')
print('Pipeline:', nlp.pipe_names)
"

# Debug specific component
python -m spacy train config.cfg --verbose --paths.train small_sample.json
```

### Permission and Path Issues

```bash
# Use absolute paths
python -m spacy train /full/path/to/config.cfg \
    --paths.train /full/path/to/train.json \
    --output /full/path/to/output

# Check file permissions
ls -la config.cfg train.json

# Run with appropriate permissions (avoid sudo if possible)
python -m spacy train config.cfg --output ./output
```

## References

- [CLI Documentation](https://spacy.io/api/cli)
- [Training Guide](https://spacy.io/usage/training)
- [Project Templates](https://github.com/explosion/projects)
- [Model Management](https://spacy.io/usage/models)
- [Visualization Tools](https://spacy.io/usage/visualizers)
