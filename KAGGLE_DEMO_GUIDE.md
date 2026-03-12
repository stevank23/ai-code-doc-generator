# How to Run the Demo in Kaggle

This guide shows you how to run the AI Code Documentation Generator demo in Kaggle.

## Prerequisites

- Free Kaggle account (sign up at https://kaggle.com)
- No installation required - everything runs in the browser

## Step-by-Step Instructions

### 1. Create New Kaggle Notebook

1. Go to https://kaggle.com/code
2. Click **"New Notebook"** button
3. You'll see a blank notebook

### 2. Enable GPU

1. On the right side panel, click **"Settings"** (or look for Accelerator dropdown)
2. Under **"Accelerator"**, select **"GPU T4 x2"**
3. Click **"Save"** (if needed)
4. You should see "GPU T4 x2" confirmed in settings

**Important:** Without GPU, the model won't work. Make sure you see "GPU T4 x2" selected.

### 3. Setup and Clone Repository

Copy and paste this into **Cell 1**:
```python
# Cell 1: Setup and clone repository
!git config --global user.email "temp@example.com"
!git config --global user.name "Kaggle User"

!git clone https://github.com/stevank23/ai-code-doc-generator.git
%cd ai-code-doc-generator

print("✅ Repository cloned!")
```

Run the cell (Shift + Enter). You should see "✅ Repository cloned!"

### 4. Install Dependencies

Copy and paste this into **Cell 2**:
```python
# Cell 2: Install dependencies
!pip install -q transformers torch accelerate gradio

print("✅ Dependencies installed!")
```

Run the cell. This takes about 1 minute.

### 5. Import Libraries and Setup

Copy and paste this into **Cell 3**:
```python
# Cell 3: Import libraries
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import gradio as gr
import sys

# Add src to path
sys.path.insert(0, '/kaggle/working/ai-code-doc-generator/src')

from analyzer import CodeAnalyzer

print(f"✅ Libraries imported!")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

Run the cell. You should see:
- ✅ Libraries imported!
- CUDA available: True
- GPU: Tesla T4

**If CUDA is False, go back to Step 2 and enable GPU!**

### 6. Load the Model

Copy and paste this into **Cell 4**:
```python
# Cell 4: Load CodeLlama model
print("Loading CodeLlama-7B model...")
print("⏳ This will take 5-10 minutes (downloading ~13GB)...")
print("Please be patient - this is normal!")

MODEL_NAME = "codellama/CodeLlama-7b-Instruct-hf"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    low_cpu_mem_usage=True
)

print("✅ Model loaded successfully!")
print(f"Model device: {next(model.parameters()).device}")
```

Run the cell. **This takes 5-10 minutes the first time.** You'll see progress bars downloading the model.

### 7. Create Analyzer

Copy and paste this into **Cell 5**:
```python
# Cell 5: Initialize analyzer
analyzer = CodeAnalyzer()

print("✅ Analyzer ready!")
```

Run the cell. Should be instant.

### 8. Define Generation Function

Copy and paste this into **Cell 6**:
```python
# Cell 6: Documentation generator function
def generate_documentation(code_input):
    if not code_input or code_input.strip() == "":
        return "⚠️ Please enter some Python code", "⚠️ Waiting for input..."
    
    try:
        result = analyzer.parse_code(code_input)
        
        if not result['success']:
            return f"❌ Error: {result['error']}", "❌ Parsing failed"
        
        if len(result['functions']) == 0:
            return "⚠️ No functions found", "⚠️ No functions detected"
        
        func = result['functions'][0]
        
        prompt = f"""You are a Python documentation expert. Write in English only.

Generate a Google-style docstring for this function:

Function: {func['name']}
Parameters: {', '.join(func['args'])}

Code:
{func['source']}

Requirements:
- One-line summary
- Args section with types
- Returns section
- Usage example

Docstring:"""

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        result_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        docstring = result_text.split("Docstring:")[-1].strip()
        
        documented_code = f'''def {func['name']}({', '.join(func['args'])}):
    """
{docstring}
    """
{func['source'].split(':', 1)[1] if ':' in func['source'] else ''}'''
        
        return documented_code, "✅ Generated!"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Error: {str(e)}", "❌ Failed"

print("✅ Generation function ready!")
```

Run the cell.

### 9. Create and Launch Gradio Interface

Copy and paste this into **Cell 7**:
```python
# Cell 7: Create Gradio interface
examples = [
    ["""def calculate_fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b"""],
    
    ["""def merge_sorted_lists(list1, list2):
    result = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] < list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    result.extend(list1[i:])
    result.extend(list2[j:])
    return result"""],
]

with gr.Blocks(title="AI Code Documentation Generator") as demo:
    gr.Markdown("""
    # 🤖 AI Code Documentation Generator
    
    Generate documentation using CodeLlama-7B
    
    ⏱️ **Note:** Each generation takes 3-5 minutes
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📥 Input")
            code_input = gr.Code(
                label="Your Python Code",
                language="python",
                lines=12,
                value="def your_function(args):\\n    pass"
            )
            generate_btn = gr.Button("🚀 Generate", variant="primary")
        
        with gr.Column():
            gr.Markdown("### 📤 Output")
            code_output = gr.Code(
                label="Documented Code",
                language="python",
                lines=12
            )
            status = gr.Markdown("")
    
    gr.Examples(examples=examples, inputs=[code_input])
    
    generate_btn.click(
        fn=generate_documentation,
        inputs=[code_input],
        outputs=[code_output, status]
    )

demo.launch(share=True, debug=True)

print("✅ Interface launched!")
print("📱 Look for the public URL above")
```

Run the cell. You should see a Gradio interface appear with a public URL.

### 10. Use the Interface

1. **Try an example:** Click on one of the example functions
2. **Click "Generate"**
3. **Wait 3-5 minutes** (this is normal)
4. **See the result** appear in the Output box

## Troubleshooting

### "CUDA available: False"
**Fix:** Enable GPU in Settings → Accelerator → GPU T4 x2

### "Model not found" or download errors
**Fix:** Check internet connection, run Cell 4 again

### Generation takes forever
**Fix:** Normal for first generation. Wait 5-10 minutes. If stuck after 15 min, restart runtime.

### "No functions found"
**Fix:** Make sure your code has a function (starts with `def`)

## Expected Performance

- **First run:** ~10 minutes (model download)
- **Each generation:** 3-5 minutes
- **Quality:** 85%+ completeness

## Tips

- **GPU quota:** Free Kaggle accounts get 30 hours/week
- **Share URL:** Gradio public URL works for 72 hours
- **Restart if needed:** Runtime → Restart Session

---

**Questions?** Open an issue: https://github.com/stevank23/ai-code-doc-generator/issues
