"""
Code Analyzer Module

Parses Python code using AST to extract functions, classes, and their metadata.
"""

import ast
from typing import List, Dict, Any


class CodeAnalyzer:
    """Analyzes Python code structure and extracts documentation-relevant information."""
    
    def __init__(self):
        self.functions = []
        self.classes = []
    
    def parse_code(self, code: str) -> Dict[str, Any]:
        """
        Parse Python code and extract structure.
        
        Args:
            code: Python source code as string
            
        Returns:
            Dictionary containing parsed functions and classes
        """
        try:
            tree = ast.parse(code)
            self.functions = self._extract_functions(tree)
            self.classes = self._extract_classes(tree)
            
            return {
                'functions': self.functions,
                'classes': self.classes,
                'success': True
            }
        except SyntaxError as e:
            return {
                'functions': [],
                'classes': [],
                'success': False,
                'error': str(e)
            }
    
    def _extract_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract function definitions from AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'lineno': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'source': ast.unparse(node)
                }
                functions.append(func_info)
        return functions
    
    def _extract_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract class definitions from AST."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'lineno': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                }
                classes.append(class_info)
        return classes
    
    def get_function_signature(self, func_info: Dict[str, Any]) -> str:
        """Generate human-readable function signature."""
        args = ', '.join(func_info['args'])
        return f"def {func_info['name']}({args}):"


# Example usage
if __name__ == "__main__":
    analyzer = CodeAnalyzer()
    
    sample_code = """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count
"""
    
    result = analyzer.parse_code(sample_code)
    print(f"Found {len(result['functions'])} functions")
    for func in result['functions']:
        print(f"  - {func['name']}")
