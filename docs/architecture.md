# Architecture

## System Overview

The AI Code Documentation Generator follows a multi-stage pipeline architecture:

**Pipeline Stages:**

1. **Input** → Python Code
2. **Code Analyzer** → Extract structure using AST
3. **Context Builder** → Gather metadata and context
4. **LLM Generator** → Generate documentation with CodeLlama
5. **Post-Processor** → Format and validate output
6. **Output** → Documented Code

---

## Component Details

### 1. Code Analyzer
**Purpose:** Parse Python code and extract structural information

**Responsibilities:**
- Parse code using Python's AST (Abstract Syntax Tree)
- Identify functions, classes, and methods
- Extract existing documentation if present
- Calculate complexity metrics (cyclomatic complexity)
- Identify dependencies and imports

**Key Features:**
- Language-aware parsing (not just regex)
- Handles edge cases (nested functions, decorators)
- Extracts type hints when available

---

### 2. Context Builder
**Purpose:** Prepare rich context for the LLM

**Responsibilities:**
- Build complete function signatures
- Gather parameter information and types
- Find related functions and dependencies
- Extract inline comments and existing docs
- Identify the function's role in the codebase

**Output:**
- Structured context object ready for LLM prompt

---

### 3. LLM Generator
**Purpose:** Generate documentation using CodeLlama

**Responsibilities:**
- Use CodeLlama-7B-Instruct model
- Apply custom prompt templates
- Support multiple documentation styles (Google/NumPy/Sphinx)
- Stream generation for better UX
- Tune temperature for consistency vs creativity

**Key Decisions:**
- Temperature: 0.7 (balanced)
- Max tokens: 300 (sufficient for most docstrings)
- Top-p sampling: 0.9 (diverse but coherent)

---

### 4. Post-Processor
**Purpose:** Validate and format generated documentation

**Responsibilities:**
- Validate docstring completeness
- Format according to style guide
- Generate usage examples
- Add type hints if missing
- Ensure consistent formatting

**Quality Checks:**
- Has description? ✓
- Has Args section? ✓
- Has Returns section? ✓
- Has examples? ✓
- Proper indentation? ✓

---

## Design Decisions

### Why CodeLlama over GPT?

**Advantages:**
- ✅ Open-source, no API costs
- ✅ Specialized for code understanding
- ✅ Can run on free Colab tier (T4 GPU)
- ✅ Full control over deployment
- ✅ No rate limits or quotas
- ✅ Privacy - code never leaves our infrastructure

**Trade-offs:**
- ❌ Slightly lower quality than GPT-4
- ❌ Slower inference than API calls
- ❌ Requires GPU for reasonable speed

**Verdict:** For a portfolio project, the benefits outweigh the drawbacks.

---

### Why AST Parsing?

**Advantages:**
- ✅ Accurate code structure understanding
- ✅ Language-aware (not just text processing)
- ✅ Can extract type hints and decorators
- ✅ Foundation for future features (refactoring suggestions)
- ✅ Handles complex Python syntax correctly

**Alternative Considered:** Regex-based parsing
- Rejected because it's fragile and error-prone

---

### Why Multi-Stage Pipeline?

**Advantages:**
- ✅ Separation of concerns (easier to debug)
- ✅ Can test each component independently
- ✅ Can swap components (e.g., try different models)
- ✅ Better error handling and recovery
- ✅ Easier to add features incrementally

**Trade-offs:**
- ❌ Slightly more complex architecture
- ❌ More code to maintain

**Verdict:** Worth it for maintainability and extensibility.

---

## Technology Stack

**Core Technologies:**
- **Language:** Python 3.10+
- **LLM:** CodeLlama-7B-Instruct (Hugging Face)
- **Code Analysis:** Python AST module
- **Deep Learning:** PyTorch, Transformers
- **UI:** Gradio (for web interface)
- **Deployment:** Hugging Face Spaces

**Development Tools:**
- **IDE:** Google Colab (free GPU)
- **Version Control:** Git/GitHub
- **Documentation:** Markdown

---

## Performance Considerations

**Current Benchmarks:**
- Model loading: ~30 seconds (first time only)
- Doc generation: ~5-10 seconds per function
- Memory usage: ~7GB GPU RAM (CodeLlama-7B)

**Optimization Opportunities:**
- Cache loaded model between requests
- Batch process multiple functions
- Use quantization (int8) for faster inference
- Implement prompt caching

---

## Future Enhancements

**Phase 2 (Next Sessions):**
1. Add evaluation metrics
2. Support multiple documentation styles
3. Build quality scoring system
4. Add web interface with Gradio

**Phase 3 (Advanced Features):**
1. Batch processing for entire projects
2. Code quality analysis beyond docs
3. Integration with CI/CD pipelines
4. Custom model fine-tuning

**Phase 4 (Production Features):**
1. API endpoint for programmatic access
2. GitHub App integration
3. VSCode extension
4. Performance monitoring dashboard

---

## Project Structure
```
ai-code-doc-generator/
├── src/
│   ├── analyzer.py      # Code parsing and analysis
│   ├── generator.py     # LLM-based doc generation
│   └── __init__.py      # Package initialization
├── tests/
│   └── __init__.py      # Test suite (to be added)
├── notebooks/
│   └── development.ipynb # Colab development notebook
├── examples/
│   └── sample_code/     # Example code for testing
├── docs/
│   ├── architecture.md  # This file
│   └── session-notes.md # Development log
├── README.md            # Project overview
└── requirements.txt     # Dependencies
```

---

## Development Workflow

1. **Analysis:** Parse code with analyzer.py
2. **Generation:** Generate docs with generator.py
3. **Validation:** Check quality and completeness
4. **Iteration:** Refine prompts based on results
5. **Deployment:** Package for Hugging Face Spaces

---

**Last Updated:** Session 1
**Status:** Architecture defined, core modules implemented
**Next Steps:** Add evaluation framework and web interface
