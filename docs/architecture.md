# Architecture

## System Overview
┌─────────────┐
│   Input     │
│  (Python    │
│   Code)     │
└──────┬──────┘
│
▼
┌─────────────────────┐
│  Code Analyzer      │
│  - AST Parser       │
│  - Extract functions│
│  - Complexity check │
└──────┬──────────────┘
│
▼
┌─────────────────────┐
│  Context Builder    │
│  - Function context │
│  - Dependencies     │
│  - Type hints       │
└──────┬──────────────┘
│
▼
┌─────────────────────┐
│  LLM Generator      │
│  - CodeLlama-7B     │
│  - Prompt templates │
│  - Response parsing │
└──────┬──────────────┘
│
▼
┌─────────────────────┐
│  Post-Processor     │
│  - Format docstrings│
│  - Add examples     │
│  - Validate output  │
└──────┬──────────────┘
│
▼
┌─────────────┐
│   Output    │
│ (Documented │
│    Code)    │
└─────────────┘
## Component Details

### 1. Code Analyzer
- Parses Python code using AST
- Identifies functions, classes, methods
- Extracts existing documentation
- Calculates complexity metrics

### 2. Context Builder
- Gathers function signatures
- Identifies parameter types
- Finds dependencies and imports
- Builds context for LLM

### 3. LLM Generator
- Uses CodeLlama-7B-Instruct
- Custom prompt templates for different doc styles
- Streaming generation for better UX
- Temperature tuning for consistency

### 4. Post-Processor
- Validates generated docstrings
- Formats according to style guide (Google/NumPy)
- Adds usage examples
- Ensures completeness

## Design Decisions

**Why CodeLlama over GPT?**
- Open-source, no API costs
- Specialized for code understanding
- Can run on free Colab tier
- Full control over deployment

**Why AST parsing?**
- Accurate code structure understanding
- Language-aware (not just text)
- Enables type hint extraction
- Foundation for future features

**Why multi-stage pipeline?**
- Separation of concerns
- Easier testing and debugging
- Can swap components independently
- Better error handling
