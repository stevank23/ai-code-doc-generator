"""
Documentation Generator Module

Uses LLMs to generate high-quality documentation for Python code.
"""

from typing import Dict, Any, Optional


class DocGenerator:
    """Generates documentation using LLM models."""
    
    def __init__(self, model, tokenizer):
        """
        Initialize documentation generator.
        
        Args:
            model: Pre-loaded LLM model
            tokenizer: Tokenizer for the model
        """
        self.model = model
        self.tokenizer = tokenizer
        self.style = "google"  # Default style
    
    def generate_docstring(
        self, 
        function_code: str, 
        function_name: str,
        style: Optional[str] = None
    ) -> str:
        """
        Generate documentation for a Python function.
        
        Args:
            function_code: Source code of the function
            function_name: Name of the function
            style: Documentation style (google, numpy, sphinx)
            
        Returns:
            Generated docstring
        """
        doc_style = style or self.style
        prompt = self._build_prompt(function_code, function_name, doc_style)
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )
        
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        docstring = self._extract_docstring(result)
        
        return docstring
    
    def _build_prompt(self, code: str, name: str, style: str) -> str:
        """Build prompt for the LLM based on documentation style."""
        style_instructions = {
            'google': """Generate a Google-style docstring with:
1. Brief description
2. Args section with type hints
3. Returns section with type
4. Example usage""",
            'numpy': """Generate a NumPy-style docstring with:
1. Brief description
2. Parameters section
3. Returns section
4. Examples section""",
            'sphinx': """Generate a Sphinx-style docstring with:
1. Brief description
2. :param: for each parameter
3. :return: description
4. :rtype: return type"""
        }
        
        instruction = style_instructions.get(style, style_instructions['google'])
        
        prompt = f"""You are a Python documentation expert. {instruction}

Function name: {name}
Code:
{code}

Docstring:"""
        
        return prompt
    
    def _extract_docstring(self, generated_text: str) -> str:
        """Extract the docstring from generated text."""
        # Remove the prompt part if present
        if "Docstring:" in generated_text:
            docstring = generated_text.split("Docstring:")[-1].strip()
        else:
            docstring = generated_text.strip()
        
        return docstring
    
    def set_style(self, style: str):
        """Set the default documentation style."""
        valid_styles = ['google', 'numpy', 'sphinx']
        if style.lower() in valid_styles:
            self.style = style.lower()
        else:
            raise ValueError(f"Style must be one of {valid_styles}")


# Example usage
if __name__ == "__main__":
    # This would normally use a loaded model
    # For now, just showing the structure
    print("DocGenerator module loaded")
    print("Usage: generator = DocGenerator(model, tokenizer)")
