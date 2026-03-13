# HuggingFace Spaces Deployment Guide

This guide documents the attempted deployment of the AI Code Documentation Generator to HuggingFace Spaces during Session 4.

**Status:** ⚠️ Deployment unsuccessful due to infrastructure limitations with large models on free tier.

**Purpose of this guide:** Document what was attempted, what challenges were encountered, and lessons learned for future deployment efforts.

---

## Overview

**Goal:** Deploy the documentation generator to HuggingFace Spaces with ZeroGPU for free GPU access.

**Outcome:** Multiple build and runtime errors due to:
- Model size (13GB) too large for free tier reliability
- ZeroGPU timeout limitations
- Gradio/Python version compatibility issues
- 3-6 minute generation times unsuitable for web deployment
- Smaller models produced unacceptable quality output

**Result:** Pivoted to Kaggle demo with comprehensive setup guide instead.

---

## Prerequisites

- HuggingFace account (free): https://huggingface.co/join
- GitHub repository with project code
- Basic understanding of Gradio and Spaces

---

## Step-by-Step Deployment Process

### Step 1: Create HuggingFace Space

1. Go to https://huggingface.co/new-space
2. Fill in details:
   - **Space name:** `ai-code-doc-generator` (or your preferred name)
   - **License:** MIT
   - **Select SDK:** Gradio
   - **Space hardware:** CPU basic (free)
   - **Visibility:** Public
3. Click **"Create Space"**

**Result:** Empty Space created at `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

---

### Step 2: Create Required Files

HuggingFace Spaces expects these files in your repository:

#### **File 1: README.md** (Space configuration)
```markdown
---
title: AI Code Documentation Generator
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
python_version: 3.11
pinned: false
license: mit
---

# AI Code Documentation Generator

Generate documentation for Python functions using CodeLlama-7B.

**Note:** Generation takes 3-5 minutes due to model size (13GB).
```

**Important settings:**
- `sdk_version: 4.44.0` - Gradio version (compatibility issues with 5.x)
- `python_version: 3.11` - Python 3.13 has compatibility issues
- `app_file: app.py` - Main application file

---

#### **File 2: requirements.txt**
```txt
transformers>=4.35.0
torch>=2.0.0
accelerate>=0.24.0
huggingface-hub<0.26.0
```

**Note:** `huggingface-hub<0.26.0` needed for Gradio 4.44 compatibility.

---

#### **File 3: app.py** (Main application)
```python
import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sys

# Add src to path
sys.path.insert(0, './src')
from analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
MODEL_NAME = "codellama/CodeLlama-7b-Instruct-hf"

# Global variables for model
tokenizer = None
model = None

def load_model():
    # Load model once and keep in memory
    global tokenizer, model
    if model is None:
        print("Loading model...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="auto"
        )
        print("Model loaded!")
    return tokenizer, model

def generate_documentation(code_input):
    # Generate documentation
    
    if not code_input or code_input.strip() == "":
        return "Please enter code", "Waiting..."
    
    try:
        tok, mdl = load_model()
        
        result = analyzer.parse_code(code_input)
        if not result['success'] or len(result['functions']) == 0:
            return "No functions found", "Error"
        
        func = result['functions'][0]
        
        prompt = f"Generate Google-style docstring for: {func['source']}"

        inputs = tok(prompt, return_tensors="pt").to(mdl.device)
        outputs = mdl.generate(**inputs, max_new_tokens=250, temperature=0.7)
        
        docstring = tok.decode(outputs[0], skip_special_tokens=True)
        
        return f"def {func['name']}(...): {docstring}", "Done"
        
    except Exception as e:
        return f"Error: {str(e)}", "Failed"

# Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# AI Code Documentation")
    
    with gr.Row():
        with gr.Column():
            code_in = gr.Code(label="Input", language="python")
            btn = gr.Button("Generate")
        with gr.Column():
            code_out = gr.Code(label="Output", language="python")
            status = gr.Markdown("")
    
    btn.click(generate_documentation, inputs=[code_in], outputs=[code_out, status])

demo.launch()
```

---

## Challenges Encountered During Deployment

### Issue 1: Python/Gradio Version Compatibility

**Error:** ImportError with huggingface_hub

**Solution:** Use `sdk_version: 4.44.0` and pin `huggingface-hub<0.26.0`

### Issue 2: Python 3.13 Compatibility

**Error:** Missing audioop modules

**Solution:** Use `python_version: 3.11`

### Issue 3: Model Loading Timeout

**Cause:** 13GB model takes too long to download

**Result:** Startup timeouts on free tier

### Issue 4: Slow Generation Times

**Problem:** 3-6 minutes per function unsuitable for web UI

### Issue 5: Smaller Model Testing

**Attempted:** CodeGen-350M and similar

**Result:** ❌ Quality unacceptable
- Incomplete documentation
- Missing Args/Returns sections
- Poor code understanding

**Conclusion:** CodeLlama-7B minimum for quality

---

## Why Deployment Failed

### Root Cause: Model Too Large for Free Tier

- 13GB model unsuitable for free hosting
- Generation time (3-6 min) too slow
- Smaller models produce poor quality output

### Real Requirements

- Persistent GPU (Modal, Replicate)
- Cost: $0.50-$1/hour
- OR: Kaggle demo as proof

---

## Lessons Learned

1. Model size matters for deployment
2. Can't compromise quality for convenience
3. Free tier has real limitations
4. Test deployment early
5. Document failures honestly

---

## Alternative Options

### Option 1: Smaller Models - NOT RECOMMENDED

**Tested:** CodeGen-350M

**Result:** Quality too poor (incomplete/incorrect output)

### Option 2: Paid GPU Hosting

**Cost:** $20-50/month

**Platforms:** Modal, Replicate, AWS

### Option 3: Kaggle Demo (Chosen)

**Cost:** $0

**Works reliably**

---

## Conclusion

**Attempted:** HF Spaces deployment

**Learned:** Infrastructure constraints, quality tradeoffs

**Chose:** Kaggle demo with setup guide

---

*Session 4 deployment documentation - learning from failures is valuable.*
