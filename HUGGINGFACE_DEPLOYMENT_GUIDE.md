# HuggingFace Spaces Deployment Guide

This guide documents how to deploy the AI Code Documentation Generator from Kaggle to HuggingFace Spaces, including the challenges encountered during Session 4.

**Status:** ⚠️ Deployment unsuccessful due to infrastructure limitations with large models on free tier.

**Purpose:** Provide complete deployment instructions from Kaggle + document challenges and lessons learned.

---

## Overview

**Goal:** Deploy the documentation generator from Kaggle to HuggingFace Spaces with ZeroGPU for free GPU access.

**Outcome:** Multiple build and runtime errors due to:
- Model size (13GB) too large for free tier reliability
- ZeroGPU timeout limitations
- Gradio/Python version compatibility issues
- 3-6 minute generation times unsuitable for web deployment
- Smaller models produced unacceptable quality output

**Result:** Pivoted to Kaggle demo with comprehensive setup guide instead.

**What this guide provides:**
- Complete deployment steps from Kaggle to HuggingFace
- All errors encountered and attempted solutions
- Why deployment failed
- Lessons learned

---

## Prerequisites

### Before You Start

1. **HuggingFace Account** (free)
   - Sign up: https://huggingface.co/join
   - Verify your email

2. **HuggingFace Access Token**
   - Go to: https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: "Spaces Deployment"
   - Type: Write
   - Click "Generate"
   - **Copy and save the token** (starts with `hf_...`)

3. **Working Kaggle Environment**
   - GPU enabled (T4 x2)
   - Project files already in Kaggle (from Kaggle demo guide)

4. **GitHub Repository**
   - Your code in GitHub (from Sessions 1-2)

---

## Part 1: Create HuggingFace Space

### Step 1: Create Empty Space on HuggingFace Website

1. Go to https://huggingface.co/new-space
2. Fill in the form:
   - **Owner:** Your username
   - **Space name:** `ai-code-doc-generator` (or your choice)
   - **License:** MIT
   - **Select SDK:** Gradio
   - **Space hardware:** CPU basic (free)
   - **Visibility:** Public
3. **Click "Create Space"**

**Important:** Leave the Space empty for now - don't add any files through the web interface yet.

**Result:** You'll have an empty Space at:
`https://huggingface.co/spaces/YOUR_USERNAME/ai-code-doc-generator`

---

## Part 2: Prepare Files in Kaggle

### Step 2: Set Up Kaggle Notebook for Deployment

**Run this in a NEW Kaggle cell:**
```python
# Cell 1: Setup for HuggingFace deployment
import os

# Create deployment directory
!mkdir -p /kaggle/working/hf-deployment
%cd /kaggle/working/hf-deployment

print("✅ Deployment directory created")
```

---

### Step 3: Create HuggingFace Space Configuration Files

**Cell 2: Create README.md (Space configuration)**
```python
# Cell 2: Create Space README with metadata

readme_content = """---
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

**⏱️ Note:** Generation takes 3-5 minutes due to model size (13GB) and free GPU limitations.

## How to Use

1. Paste your Python function in the input box
2. Click "Generate Documentation"
3. Wait 3-5 minutes for generation
4. Copy the documented code

## Tech Stack

- Model: CodeLlama-7B-Instruct (13GB)
- Framework: Gradio 4.44
- Backend: PyTorch, Transformers

## Limitations

- Free tier deployment
- Long generation times (3-5 minutes)
- Single function at a time

[View on GitHub](https://github.com/YOUR_USERNAME/ai-code-doc-generator)
"""

with open('README.md', 'w') as f:
    f.write(readme_content)

print("✅ README.md created")
```

---

**Cell 3: Create requirements.txt**
```python
# Cell 3: Create requirements file

requirements = """transformers>=4.35.0
torch>=2.0.0
accelerate>=0.24.0
huggingface-hub<0.26.0
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements)

print("✅ requirements.txt created")
```

---

**Cell 4: Create app.py (main application)**

**Note:** The app.py code is provided below. Copy this entire cell into Kaggle:
```python
# Cell 4: Create main application file

# Write app.py content to file
with open('app.py', 'w') as f:
    f.write("""import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sys
import ast

# Simple analyzer inline
class CodeAnalyzer:
    def parse_code(self, code_string):
        try:
            tree = ast.parse(code_string)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    source = ast.get_source_segment(code_string, node)
                    
                    functions.append({
                        'name': node.name,
                        'args': args,
                        'source': source if source else code_string
                    })
            
            return {'success': True, 'functions': functions, 'error': None}
        except Exception as e:
            return {'success': False, 'functions': [], 'error': str(e)}

analyzer = CodeAnalyzer()
MODEL_NAME = "codellama/CodeLlama-7b-Instruct-hf"

tokenizer = None
model = None

def load_model():
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
    if not code_input or code_input.strip() == "":
        return "Please enter code", "Waiting"
    
    try:
        result = analyzer.parse_code(code_input)
        if not result['success'] or len(result['functions']) == 0:
            return "No functions found", "Error"
        
        func = result['functions'][0]
        
        # Build prompt
        prompt = "Generate Google-style docstring for: " + func['source'] + " Docstring:"
        
        tok, mdl = load_model()
        inputs = tok(prompt, return_tensors="pt").to(mdl.device)
        outputs = mdl.generate(**inputs, max_new_tokens=300, temperature=0.7, pad_token_id=tok.eos_token_id)
        
        result_text = tok.decode(outputs[0], skip_special_tokens=True)
        docstring = result_text.split("Docstring:")[-1].strip()
        
        documented = f"def {func['name']}({', '.join(func['args'])}):\n    " + '"""' + f"\n{docstring}\n    " + '"""' + f"\n{func['source'].split(':', 1)[1] if ':' in func['source'] else ''}"
        
        return documented, "Done"
    except Exception as e:
        return f"Error: {str(e)}", "Failed"

examples = [
    ["def fibonacci(n):\n    if n <= 1: return n\n    a, b = 0, 1\n    for _ in range(n-1): a, b = b, a+b\n    return b"],
    ["def merge(l1, l2):\n    r = []\n    i = j = 0\n    while i < len(l1) and j < len(l2):\n        if l1[i] < l2[j]: r.append(l1[i]); i += 1\n        else: r.append(l2[j]); j += 1\n    return r + l1[i:] + l2[j:]"]
]

with gr.Blocks(title="AI Code Docs") as demo:
    gr.Markdown("# 🤖 AI Code Documentation\n\nGenerate docs with CodeLlama-7B\n\n⏱️ Takes 3-5 minutes")
    
    with gr.Row():
        with gr.Column():
            code_in = gr.Code(label="Input", language="python", lines=12)
            btn = gr.Button("Generate", variant="primary")
        with gr.Column():
            code_out = gr.Code(label="Output", language="python", lines=12)
            status = gr.Markdown("")
    
    gr.Examples(examples=examples, inputs=[code_in])
    
    btn.click(generate_documentation, inputs=[code_in], outputs=[code_out, status])

demo.launch()
""")

print("✅ app.py created")
import os
print(f"File size: {os.path.getsize('app.py')} bytes")
```

---

### Step 4: Verify Files
```python
# Cell 5: Verify files

print("📂 Files created:")
!ls -lah
print("\n✅ Ready for deployment!")
```

---

## Part 3: Deploy to HuggingFace from Kaggle

### Step 5: Clone HuggingFace Space
```python
# Cell 6: Clone HF Space

HF_USERNAME = "your_username"  # Replace
HF_TOKEN = "hf_xxxxx"  # Replace
SPACE_NAME = "ai-code-doc-generator"

!git clone https://{HF_USERNAME}:{HF_TOKEN}@huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME} hf-space
%cd hf-space

print("✅ Space cloned")
```

---

### Step 6: Copy Files
```python
# Cell 7: Copy files

!cp /kaggle/working/hf-deployment/README.md .
!cp /kaggle/working/hf-deployment/requirements.txt .
!cp /kaggle/working/hf-deployment/app.py .

print("✅ Files copied")
!ls -la
```

---

### Step 7: Push to HuggingFace
```python
# Cell 8: Deploy

!git add .
!git commit -m "Deploy from Kaggle"
!git push

print("\n✅ DEPLOYED!")
print(f"\nSpace: https://huggingface.co/spaces/{HF_USERNAME}/{SPACE_NAME}")
print("\nWait 5-10 min for build, then check Logs tab")
```

---

## Challenges Encountered

### Issue 1: Version Compatibility
- **Error:** ImportError with huggingface_hub
- **Fix:** Use Gradio 4.44.0, pin huggingface-hub<0.26.0

### Issue 2: Python 3.13
- **Error:** Missing audioop
- **Fix:** Use Python 3.11

### Issue 3: Model Size
- **Problem:** 13GB too large for free tier
- **Result:** Timeouts, slow generation

### Issue 4: Smaller Models
- **Tested:** CodeGen-350M
- **Result:** Quality unacceptable (incomplete docs)

---

## Why It Failed

- 13GB model too large
- 3-6 min generation too slow
- Smaller models = poor quality
- Can't compromise quality

**Solution:** Kaggle demo instead

---

## Lessons Learned

1. Model size matters for deployment
2. Can't compromise quality for convenience
3. Free tiers have real limits
4. Test deployment early
5. Document failures

---

## Alternatives

1. **Smaller models:** Quality too poor
2. **Paid GPU:** $20-50/month (Modal, Replicate)
3. **Kaggle demo:** Free, works well (chosen)

---

## Conclusion

**Deployment steps work**, but 13GB model impractical on free tier.

**Better:** [Kaggle Demo Guide](KAGGLE_DEMO_GUIDE.md)

---

*Complete deployment process documented, including why it's impractical for production on free tier.*
