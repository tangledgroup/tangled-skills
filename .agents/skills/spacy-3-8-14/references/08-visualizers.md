# Visualizations with displaCy

This guide covers spaCy's visualization tool displaCy for creating interactive visualizations of NER entities, dependency parses, and entity links.

## Overview of displaCy

displaCy is spaCy's built-in visualization tool that creates interactive HTML visualizations for:
- Named Entity Recognition (NER)
- Dependency parsing
- Entity linking

### Basic Usage

```python
import spacy
from spacy.displacy import serve, render

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

# Render to HTML string
options = {"compact": True, "border": True}
html = render(doc, style="ent", options=options)

# Save to file
with open("entities.html", "w", encoding="utf-8") as f:
    f.write(html)

# Or serve interactively on localhost:5000
serve(doc, style="ent", port=5000)
```

## Named Entity Recognition Visualization

### Basic NER Visualization

```python
import spacy
from spacy.displacy import render

nlp = spacy.load("en_core_web_sm")
doc = nlp("John Smith works at Google in Mountain View, California.")

# Generate HTML visualization
html = render(doc, style="ent")

# Save to file
with open("ner_visualization.html", "w", encoding="utf-8") as f:
    f.write(html)

# Open in browser (requires webbrowser module)
import webbrowser
webbrowser.open("ner_visualization.html")
```

### Customizing Entity Colors

```python
from spacy.displacy import render

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple Inc. was founded by Steve Jobs in California.")

# Define custom colors for entity types
colors = {
    "ORG": "#ff6b6b",      # Red for organizations
    "PERSON": "#4ecdc4",   # Teal for people
    "GPE": "#95e1d3",      # Light green for locations
    "DATE": "#f38181"      # Pink for dates
}

options = {
    "colors": colors,
    "compact": False,
    "border": True,
    "bg": "#fff"
}

html = render(doc, style="ent", options=options)
```

### Entity Legend Customization

```python
# Customize entity labels and descriptions
entities = [
    {"label": "PERSON", "description": "People"},
    {"label": "ORG", "description": "Organizations"},
    {"label": "GPE", "description": "Countries, cities, states"},
    {"label": "PRODUCT", "description": "Products and services"}
]

options = {
    "ent_per_line": 4,  # Entities per row in legend
    "legend": entities,
    "color": "#fff"
}

html = render(doc, style="ent", options=options)
```

### Multiple Documents Visualization

```python
# Visualize multiple documents at once
docs = [
    nlp("John works at Google"),
    nlp("Apple was founded in 1976"),
    nlp("Paris is the capital of France")
]

html = render(docs, style="ent")
with open("multiple_entities.html", "w", encoding="utf-8") as f:
    f.write(html)
```

## Dependency Parsing Visualization

### Basic Dependency Tree

```python
import spacy
from spacy.displacy import render

nlp = spacy.load("en_core_web_sm")
doc = nlp("The quick brown fox jumps over the lazy dog.")

# Render dependency parse
html = render(doc, style="dep")

with open("dependency_tree.html", "w", encoding="utf-8") as f:
    f.write(html)
```

### Dependency Visualization Options

```python
options = {
    "compact": False,        # Show full tree (not compact)
    "color": "#fff",         # Background color
    "bg": "#f8f9fa",         # Page background
    "font": "Roboto",        # Font family
    "width": 800,            # Visualization width
    "height": 400,           # Visualization height
    "border_radius": 5,      # Border radius for nodes
    "align": "center"        # Text alignment
}

html = render(doc, style="dep", options=options)
```

### Multiple Sentences with Dependencies

```python
doc = nlp("The fox jumps. The dog sleeps.")

# Visualize all sentences
html = render(doc, style="dep")

# Or visualize specific sentence
sent = doc.sents[0]  # First sentence
html = render(sent, style="dep")
```

### Dependency with Entity Overlay

Combine dependency parsing with entity highlighting:

```python
from spacy.displacy import parse

nlp = spacy.load("en_core_web_sm")
doc = nlp("John works at Google in California.")

# Extract data for custom visualization
data = parse(doc, style="dep", options={"compact": True})

# Data includes tokens, dependencies, and entities
print(data["sentences"][0]["tokens"])
```

## Entity Linking Visualization

### Basic Entity Linking

```python
import spacy
from spacy.displacy import render

# Load model with entity linking
nlp = spacy.load("en_ner_trf_large")  # Or custom model with EL

doc = nlp("Barack Obama was president of the United States.")

# Render entity links
html = render(doc, style="span")

with open("entity_links.html", "w", encoding="utf-8") as f:
    f.write(html)
```

### Custom Entity Link Styles

```python
options = {
    "link_width": 2,        # Width of connection lines
    "link_color": "#3498db",  # Color of links
    "entity_color": "#2ecc71",  # Color of linked entities
    "compact": True,
    "border": True
}

html = render(doc, style="span", options=options)
```

## Interactive Serving

### Serving Visualizations

```python
from spacy.displacy import serve

nlp = spacy.load("en_core_web_sm")

# Single document
doc = nlp("Apple is looking at buying U.K. startup")
serve(doc, style="ent", port=5000)

# Multiple documents
docs = [
    nlp("Document 1 text here"),
    nlp("Document 2 text here")
]
serve(docs, style="ent", port=5000)

# With options
serve(doc, style="dep", port=5000, options={"compact": False})
```

### Batch Serving with Navigation

```python
from spacy.displacy import serve

nlp = spacy.load("en_core_web_sm")

texts = [
    "John Smith works at Google in Mountain View.",
    "Apple Inc. was founded by Steve Jobs.",
    "The Eiffel Tower is located in Paris, France."
]

docs = [nlp(text) for text in texts]

# Serve with navigation between documents
serve(
    docs,
    style="ent",
    port=5000,
    manual=True,  # Enable manual navigation
    options={"compact": True}
)
```

## Custom Visualizations

### Creating Custom Styles

You can create custom visualization styles by extending displaCy:

```python
from spacy.displacy import Renderer
from spacy.tokens import Doc, Span

class CustomRenderer(Renderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def ent(self, doc, **opts):
        """Custom entity rendering"""
        # Customize entity rendering logic
        return self.render(doc, style="ent", **opts)

# Use custom renderer
renderer = CustomRenderer()
html = renderer.render(doc, style="ent")
```

### Exporting to Different Formats

```python
from spacy.displacy import render

nlp = spacy.load("en_core_web_sm")
doc = nlp("Sample text for visualization")

# HTML (default)
html = render(doc, style="ent")

# SVG (requires additional processing)
svg = render(doc, style="dep", options={"to_svg": True})

# JSON data for custom rendering
from spacy.displacy import parse
data = parse(doc, style="ent")
import json
with open("entities.json", "w") as f:
    json.dump(data, f, indent=2)
```

## Integration with Web Applications

### Flask Integration

```python
from flask import Flask, render_template_string, request
import spacy
from spacy.displacy import render

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

@app.route('/visualize', methods=['POST'])
def visualize():
    text = request.json.get('text', '')
    style = request.json.get('style', 'ent')
    
    doc = nlp(text)
    html = render(doc, style=style)
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><title>spaCy Visualization</title></head>
        <body>{{ visualization | safe }}</body>
        </html>
    ''', visualization=html)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import spacy
from spacy.displacy import render

app = FastAPI()
nlp = spacy.load("en_core_web_sm")

class VisualizationRequest(BaseModel):
    text: str
    style: str = "ent"

@app.post("/visualize", response_class=HTMLResponse)
async def visualize(request: VisualizationRequest):
    doc = nlp(request.text)
    html = render(doc, style=request.style)
    return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head><title>Visualization</title></head>
        <body>{html}</body>
        </html>
    """)

# Run with: uvicorn main:app --port 8000
```

### Jupyter Notebook Integration

```python
from IPython.display import HTML, display
import spacy
from spacy.displacy import render

nlp = spacy.load("en_core_web_sm")
doc = nlp("John works at Google in California.")

# Display visualization inline
html = render(doc, style="ent")
display(HTML(html))

# Or use displaCy's built-in notebook support
from spacy.displacy import plot

plot(doc, style="ent", options={"compact": True})
```

## Advanced Customization

### Custom CSS Styling

```python
from spacy.displacy import render

nlp = spacy.load("en_core_web_sm")
doc = nlp("Sample text for custom styling")

# Get base HTML
base_html = render(doc, style="ent")

# Add custom CSS
custom_css = """
<style>
    .displace-entity {
        border-radius: 10px;
        padding: 5px 10px;
        margin: 2px;
        display: inline-block;
    }
    .displace-legend {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
    }
</style>
"""

# Combine and save
full_html = f"""
<!DOCTYPE html>
<html>
<head>{custom_css}</head>
<body>
{base_html}
</body>
</html>
"""

with open("custom_styled.html", "w", encoding="utf-8") as f:
    f.write(full_html)
```

### Responsive Visualizations

```python
# Make visualizations responsive for mobile
options = {
    "width": "100%",      # Full width on mobile
    "height": "auto",     # Auto height
    "compact": True,      # Compact view for small screens
    "font_size": "14px"   # Readable font size
}

html = render(doc, style="ent", options=options)
```

## Troubleshooting Visualizations

### HTML Not Rendering in Browser

```python
# Ensure proper encoding
with open("visualization.html", "w", encoding="utf-8") as f:
    f.write(html)

# Check for special characters
doc = nlp("Text with special chars: <>&\"'")
html = render(doc, style="ent")  # Should escape HTML entities
```

### Large Documents Causing Issues

```python
# Limit visualization to first N tokens
nlp = spacy.load("en_core_web_sm")
doc = nlp(very_long_text)

# Visualize only first sentence
sent = list(doc.sents)[0]
html = render(sent, style="ent")

# Or limit to specific span
span = doc[:100]  # First 100 tokens
html = render(span, style="dep")
```

### Missing Entity Types

```python
# Ensure all entity types have colors
colors = {
    "PERSON": "#ff6b6b",
    "ORG": "#4ecdc4",
    "GPE": "#95e1d3",
    # Add custom entity types here
    "CUSTOM_ENTITY": "#f38181"
}

options = {"colors": colors}
html = render(doc, style="ent", options=options)
```

## Programmatic Access to Visualization Data

### Extracting Visualization Data

```python
from spacy.displacy import parse

nlp = spacy.load("en_core_web_sm")
doc = nlp("John works at Google")

# Get structured data for entities
ent_data = parse(doc, style="ent")

# Access entity information
for sentence in ent_data["sentences"]:
    for token in sentence["tokens"]:
        print(token["text"], token["entity"])

# For dependencies
dep_data = parse(doc, style="dep")
for sentence in dep_data["sentences"]:
    for token in sentence["tokens"]:
        print(token["text"], token["tag"], token["deprel"])
```

### Custom Data Processing

```python
from spacy.displacy import parse
import json

nlp = spacy.load("en_core_web_sm")
doc = nlp("Sample text for data extraction")

# Get structured data
data = parse(doc, style="ent")

# Process and transform
entities = []
for sentence in data["sentences"]:
    current_entity = None
    for token in sentence["tokens"]:
        if token["entity"] and not token["entity"].startswith("B-"):
            if current_entity:
                entities.append(current_entity)
            current_entity = {
                "label": token["entity"][2:],  # Remove "I-" prefix
                "text": token["text"]
            }
        elif token["entity"] and token["entity"].startswith("B-"):
            if current_entity:
                entities.append(current_entity)
            current_entity = {
                "label": token["entity"][2:],  # Remove "B-" prefix
                "text": token["text"]
            }
        else:
            if current_entity:
                entities.append(current_entity)
                current_entity = None

# Save as JSON
with open("entities.json", "w") as f:
    json.dump(entities, f, indent=2)
```

## References

- [displaCy Documentation](https://spacy.io/usage/visualizers)
- [displaCy GitHub](https://github.com/explosion/displacy)
- [Visualization API](https://spacy.io/api/displacy)
- [Custom Visualization Guide](https://spacy.io/usage/visualizers#custom)
