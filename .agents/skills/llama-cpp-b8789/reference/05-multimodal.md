# Multimodal Support for llama.cpp b8789

## Overview

llama.cpp supports multimodal models that can process images and audio in addition to text. This is enabled via the `libmtmd` library and available in:
- `llama-mtmd-cli` - Command-line multimodal tool
- `llama-server` - OpenAI-compatible API with `/chat/completions`

## Quick Start

### Vision Model (Gemma 3)

```bash
# Simple usage - automatic mmproj download
llama-server -hf ggml-org/gemma-3-4b-it-GGUF

# With CLI
llama-mtmd-cli -hf ggml-org/gemma-3-12b-it-GGUF
```

### Local Files

```bash
# Specify model and projector separately
llama-server -m gemma-3-4b-it-Q4_K_M.gguf \
  --mmproj mmproj-gemma-3-4b-it-Q4_K_M.gguf
```

### Disable GPU Offload for Projector

```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF --no-mmproj-offload
```

## Supported Multimodal Models

### Vision Models

#### Gemma 3 Series
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF
llama-server -hf ggml-org/gemma-3-12b-it-GGUF
llama-server -hf ggml-org/gemma-3-27b-it-GGUF
```

**Capabilities:** Image understanding, VQA, document analysis

#### Qwen2.5-VL
```bash
llama-server -hf ggml-org/Qwen2.5-VL-3B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-VL-7B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-VL-32B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2.5-VL-72B-Instruct-GGUF
```

**Capabilities:** High-resolution images, OCR, detailed visual reasoning

#### Qwen2-VL
```bash
llama-server -hf ggml-org/Qwen2-VL-2B-Instruct-GGUF
llama-server -hf ggml-org/Qwen2-VL-7B-Instruct-GGUF
```

#### InternVL 2.5/3
```bash
llama-server -hf ggml-org/InternVL2_5-1B-GGUF
llama-server -hf ggml-org/InternVL2_5-4B-GGUF
llama-server -hf ggml-org/InternVL3-1B-Instruct-GGUF
llama-server -hf ggml-org/InternVL3-8B-Instruct-GGUF
llama-server -hf ggml-org/InternVL3-14B-Instruct-GGUF
```

**Capabilities:** Advanced OCR, document understanding

#### SmolVLM
```bash
llama-server -hf ggml-org/SmolVLM-Instruct-GGUF
llama-server -hf ggml-org/SmolVLM2-2.2B-Instruct-GGUF
llama-server -hf ggml-org/SmolVLM2-500M-Video-Instruct-GGUF
```

**Capabilities:** Lightweight vision, video understanding (SmolVLM2)

#### Other Vision Models
```bash
# Pixtral 12B
llama-server -hf ggml-org/pixtral-12b-GGUF

# Llama 4 Scout (vision-enabled)
llama-server -hf ggml-org/Llama-4-Scout-17B-16E-Instruct-GGUF

# Moondream2
llama-server -hf ggml-org/moondream2-20250414-GGUF
```

### Audio Models

#### Ultravox
```bash
llama-server -hf ggml-org/ultravox-v0_5-llama-3_2-1b-GGUF
llama-server -hf ggml-org/ultravox-v0_5-llama-3_1-8b-GGUF
```

**Capabilities:** Speech-to-text, audio understanding

#### Voxtral (Mistral)
```bash
llama-server -hf ggml-org/Voxtral-Mini-3B-2507-GGUF
```

**Capabilities:** Audio input processing

#### Qwen3-ASR
```bash
llama-server -hf ggml-org/Qwen3-ASR-0.6B-GGUF
llama-server -hf ggml-org/Qwen3-ASR-1.7B-GGUF
```

**Capabilities:** Automatic speech recognition

### Multimodal (Vision + Audio)

#### Qwen2.5-Omni
```bash
llama-server -hf ggml-org/Qwen2.5-Omni-3B-GGUF
llama-server -hf ggml-org/Qwen2.5-Omni-7B-GGUF
```

**Capabilities:** Simultaneous vision and audio input

#### Qwen3-Omni
```bash
llama-server -hf ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF
llama-server -hf ggml-org/Qwen3-Omni-30B-A3B-Thinking-GGUF
```

**Capabilities:** Advanced multimodal reasoning

#### Gemma 4
```bash
llama-server -hf ggml-org/gemma-4-E2B-it-GGUF
llama-server -hf ggml-org/gemma-4-E4B-it-GGUF
llama-server -hf ggml-org/gemma-4-26B-A4B-it-GGUF
llama-server -hf ggml-org/gemma-4-31B-it-GGUF
```

**Capabilities:** Audio and vision in single model

## API Usage

### Image Input via API

**Base64-encoded image:**
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma-3-4b",
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgo..."
          }
        },
        {
          "type": "text",
          "text": "What is in this image?"
        }
      ]
    }],
    "max_tokens": 512
  }'
```

**File path:**
```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "file:///path/to/image.png"
          }
        },
        {
          "type": "text",
          "text": "Describe this image"
        }
      ]
    }]
  }'
```

**Multiple images:**
```bash
curl http://localhost:8080/v1/chat/completions \
  -d '{
    "messages": [{
      "role": "user",
      "content": [
        {"type": "image_url", "image_url": {"url": "file:///image1.png"}},
        {"type": "image_url", "image_url": {"url": "file:///image2.png"}},
        {"type": "text", "text": "Compare these images"}
      ]
    }]
  }'
```

### Audio Input via API

**Base64-encoded audio:**
```bash
curl http://localhost:8080/v1/chat/completions \
  -d '{
    "messages": [{
      "role": "user",
      "content": [
        {
          "type": "input_audio",
          "input_audio": {
            "data": "UklGRiQAAABXQVZFZm10IBIAAAA...",
            "format": "wav"
          }
        },
        {
          "type": "text",
          "text": "Transcribe this audio"
        }
      ]
    }]
  }'
```

**Supported formats:** WAV, MP3, FLAC, M4A (depending on model)

## Command-Line Usage

### llama-mtmd-cli

**Interactive mode with image:**
```bash
llama-mtmd-cli -hf ggml-org/gemma-3-4b-it-GGUF \
  --image /path/to/image.png
```

**Single prompt:**
```bash
llama-mtmd-cli -hf ggml-org/Qwen2.5-VL-7B-Instruct-GGUF \
  -m "What is shown in this image?" \
  --image /path/to/diagram.png
```

**Audio input:**
```bash
llama-mtmd-cli -hf ggml-org/ultravox-v0_5-llama-3_1-8b-GGUF \
  --audio /path/to/audio.wav
```

**Multiple inputs:**
```bash
llama-mtmd-cli -hf ggml-org/Qwen2.5-Omni-7B-GGUF \
  --image /path/to/chart.png \
  --audio /path/to/explanation.wav \
  -m "Explain this chart with the audio context"
```

## OCR Models

Specialized models for document and text extraction:

### PaddleOCR-VL

See https://github.com/ggml-org/llama.cpp/pull/18825

**Usage:**
```bash
llama-server -hf <paddle-ocr-model> \
  --chat-template paddle-ocr
```

### GLM-OCR

See https://github.com/ggml-org/llama.cpp/pull/19677

**Usage:**
```bash
llama-server -hf <glm-ocr-model> \
  --chat-template glm-ocr
```

### Deepseek-OCR

See https://github.com/ggml-org/llama.cpp/pull/17400

**Usage:**
```bash
llama-server -hf <deepseek-ocr-model> \
  --chat-template deepseek-ocr
```

### HunyuanOCR

See https://github.com/ggml-org/llama.cpp/pull/21395

## Configuration Options

### Image Resolution

**Set minimum/maximum tokens per image:**
```bash
llama-server -hf ggml-org/Qwen2.5-VL-7B-Instruct-GGUF \
  --image-min-tokens 256 \
  --image-max-tokens 1024
```

Dynamic resolution models adjust token count based on image complexity.

### Multimodal Projector Control

**Disable automatic mmproj download:**
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF --no-mmproj
```

**Use custom mmproj file:**
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF \
  --mmproj /path/to/custom-mmproj.gguf
```

**Disable GPU offload for projector:**
```bash
llama-server --no-mmproj-offload
```

### Media Path (Server)

Allow loading local media files:
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF \
  --media-path /path/to/media/directory
```

Then use relative URLs: `file://image.png`

## Performance Tips

### GPU Offloading

**Offload projector to GPU (default):**
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF --mmproj-offload
```

Projector can consume significant VRAM. Disable if VRAM is limited:
```bash
llama-server --no-mmproj-offload
```

### Context Size

Vision models may need larger context:
```bash
llama-server -hf ggml-org/Qwen2.5-VL-7B-Instruct-GGUF \
  -c 8192
```

Images can consume 256-2048+ tokens depending on resolution and model.

### Batch Processing

For multiple images, use parallel slots:
```bash
llama-server -hf ggml-org/gemma-3-4b-it-GGUF \
  --parallel 4
```

## Troubleshooting

### "Cannot load mmproj"

**Cause:** Projector file not found or corrupted

**Solutions:**
1. Use `-hf` for automatic download
2. Download mmproj manually from same Hugging Face repo
3. Check file integrity: `llama-cli -m mmproj.gguf --check-tensors`

### VRAM exhaustion with images

**Solutions:**
- Reduce image resolution before processing
- Disable projector offload: `--no-mmproj-offload`
- Use smaller model (e.g., SmolVLM instead of Qwen2.5-VL-72B)
- Reduce context size

### "Audio quality is poor"

**Note:** Audio support is experimental in b8789

**Solutions:**
- Use WAV format at 16kHz or higher
- Try different audio models (Ultravox vs Qwen3-ASR)
- Pre-process audio to remove noise
- Keep audio clips short (< 30 seconds)

### Image not recognized

**Causes:**
- Unsupported image format (use PNG, JPG, WEBP)
- Corrupted image file
- Model doesn't support vision (check model capabilities)

**Solutions:**
```bash
# Verify model has mmproj capability
llama-cli -m model.gguf --verbose

# Check if mmproj is loaded
llama-server -hf ggml-org/gemma-3-4b-it-GGUF 2>&1 | grep -i mmproj
```

## Model Selection Guide

| Task | Recommended Model | VRAM Required |
|------|------------------|---------------|
| General VQA (lightweight) | SmolVLM-Instruct | ~4 GB |
| General VQA (quality) | Gemma 3 4B | ~6 GB |
| High-res images | Qwen2.5-VL-7B | ~8 GB |
| OCR documents | InternVL3-8B | ~10 GB |
| Video understanding | SmolVLM2-500M-Video | ~4 GB |
| Audio transcription | Ultravox 1B | ~4 GB |
| Vision + Audio | Qwen2.5-Omni-3B | ~6 GB |
| Maximum quality | Qwen2.5-VL-72B | ~48 GB |

## Finding More Models

**Hugging Face search:**
- Multimodal GGUFs: https://huggingface.co/collections/ggml-org/multimodal-ggufs-68244e01ff1f39e5bebeeedc
- Vision models: https://huggingface.co/models?pipeline_tag=image-text-to-text&sort=trending&search=gguf

**Check model card:** Look for "multimodal", "vision", or "mmproj" in description.
