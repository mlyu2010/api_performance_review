#!/usr/bin/env python3
"""
HTML Documentation Generator
============================

This script generates comprehensive HTML documentation from Python source files
in the Python_Api project. It extracts module docstrings, class docstrings,
method docstrings, and function docstrings to create a browsable documentation site.

Features:
- Extracts docstrings from all Python modules
- Generates individual HTML pages for each module
- Creates an index page with navigation
- Includes syntax highlighting for code examples
- Modern, responsive UI design
- Supports reStructuredText-style docstrings

Usage:
    python scripts/generate_docs.py

Output:
    Creates documentation in ./docs/html/ directory
"""

import os
import ast
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class DocstringExtractor:
    """Extracts docstrings and structure information from Python source files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules = []

    def scan_project(self, directory: Path = None) -> List[Dict]:
        """Scan project directory for Python files and extract documentation."""
        if directory is None:
            directory = self.project_root / "app"

        modules = []
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".venv" in str(py_file):
                continue

            relative_path = py_file.relative_to(self.project_root)
            module_info = self.extract_module_info(py_file, relative_path)
            if module_info:
                modules.append(module_info)

        self.modules = sorted(modules, key=lambda x: x['path'])
        return self.modules

    def extract_module_info(self, file_path: Path, relative_path: Path) -> Optional[Dict]:
        """Extract documentation information from a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)

            module_doc = ast.get_docstring(tree) or ""

            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self.extract_class_info(node)
                    if class_info:
                        classes.append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if self.is_top_level(node, tree):
                        func_info = self.extract_function_info(node)
                        if func_info:
                            functions.append(func_info)

            return {
                'name': file_path.stem,
                'path': str(relative_path),
                'full_path': str(file_path),
                'module_doc': module_doc,
                'classes': classes,
                'functions': functions
            }
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            return None

    def is_top_level(self, node: ast.FunctionDef, tree: ast.Module) -> bool:
        """Check if a function is defined at module level (not inside a class)."""
        for item in tree.body:
            if item == node:
                return True
        return False

    def extract_class_info(self, node: ast.ClassDef) -> Dict:
        """Extract documentation from a class node."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self.extract_function_info(item)
                if method_info:
                    methods.append(method_info)

        return {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'methods': methods,
            'bases': [self.get_base_name(base) for base in node.bases]
        }

    def extract_function_info(self, node: ast.FunctionDef) -> Dict:
        """Extract documentation from a function/method node."""
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'signature': self.get_signature(node)
        }

    def get_signature(self, node: ast.FunctionDef) -> str:
        """Generate function signature string."""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        return f"{node.name}({', '.join(args)})"

    def get_base_name(self, node) -> str:
        """Get the name of a base class."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return "object"


class HTMLDocGenerator:
    """Generates HTML documentation from extracted docstrings."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, modules: List[Dict]):
        """Generate complete HTML documentation."""
        print(f"Generating documentation in {self.output_dir}")

        # Generate CSS file
        self.generate_css()

        # Generate index page
        self.generate_index(modules)

        # Generate module pages
        for module in modules:
            self.generate_module_page(module)

        print(f"Documentation generated successfully!")
        print(f"Open {self.output_dir / 'index.html'} in your browser")

    def generate_css(self):
        """Generate CSS stylesheet for documentation."""
        css_content = """
/* Documentation Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 0;
    margin-bottom: 40px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}

header p {
    font-size: 1.2em;
    opacity: 0.9;
}

nav {
    background: white;
    padding: 20px;
    margin-bottom: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

nav a {
    color: #667eea;
    text-decoration: none;
    padding: 8px 16px;
    display: inline-block;
    border-radius: 4px;
    transition: background-color 0.3s;
}

nav a:hover {
    background-color: #f0f0f0;
}

.content {
    background: white;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h2 {
    color: #667eea;
    margin-top: 30px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #667eea;
}

h3 {
    color: #764ba2;
    margin-top: 25px;
    margin-bottom: 10px;
}

h4 {
    color: #555;
    margin-top: 20px;
    margin-bottom: 10px;
}

.module-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.module-card {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    transition: transform 0.2s, box-shadow 0.2s;
}

.module-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.module-card h3 {
    margin-top: 0;
}

.module-card a {
    color: #667eea;
    text-decoration: none;
    font-weight: bold;
}

.docstring {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 6px;
    margin: 15px 0;
    white-space: pre-wrap;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
    line-height: 1.5;
    border-left: 3px solid #667eea;
}

.signature {
    background: #2d2d2d;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    margin: 10px 0;
    overflow-x: auto;
}

.class-section, .function-section {
    margin: 30px 0;
    padding: 20px;
    background: #fafafa;
    border-radius: 8px;
}

.method {
    margin: 20px 0;
    padding: 15px;
    background: white;
    border-radius: 6px;
    border-left: 3px solid #764ba2;
}

footer {
    text-align: center;
    padding: 30px;
    color: #777;
    margin-top: 50px;
}

code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}

.timestamp {
    color: #999;
    font-size: 0.9em;
    margin-top: 20px;
}

a {
    color: #667eea;
}

.toc {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}

.toc ul {
    list-style: none;
    padding-left: 20px;
}

.toc li {
    margin: 8px 0;
}

.breadcrumb {
    color: #999;
    margin-bottom: 20px;
}

.breadcrumb a {
    color: #667eea;
    text-decoration: none;
}
"""
        css_path = self.output_dir / "style.css"
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)

    def generate_index(self, modules: List[Dict]):
        """Generate the main index page."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python_Api Documentation</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>Python_Api Documentation</h1>
            <p>Comprehensive REST API for managing agents, tasks, and task executions</p>
        </div>
    </header>

    <div class="container">
        <div class="content">
            <h2>Project Overview</h2>
            <p>
                A comprehensive REST API built with FastAPI and PostgreSQL for managing agents, 
                tasks, and task executions with JWT authentication.
            </p>

            <h2>Modules</h2>
            <div class="module-list">
"""

        # Group modules by directory
        modules_by_dir = {}
        for module in modules:
            dir_name = str(Path(module['path']).parent)
            if dir_name not in modules_by_dir:
                modules_by_dir[dir_name] = []
            modules_by_dir[dir_name].append(module)

        # Generate module cards
        for dir_name in sorted(modules_by_dir.keys()):
            for module in modules_by_dir[dir_name]:
                module_name = module['name']
                module_path = module['path']
                doc_preview = module['module_doc'][:150] + "..." if len(module['module_doc']) > 150 else module['module_doc']
                doc_preview = doc_preview.split('\n')[0]  # First line only

                html += f"""
                <div class="module-card">
                    <h3><a href="{module_name}.html">{module_name}</a></h3>
                    <p><code>{module_path}</code></p>
                    <p>{self.escape_html(doc_preview)}</p>
                </div>
"""

        html += f"""
            </div>

            <div class="timestamp">
                Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    </div>

    <footer>
        <p>Generated by Python_Api Documentation Generator</p>
    </footer>
</body>
</html>
"""

        index_path = self.output_dir / "index.html"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def generate_module_page(self, module: Dict):
        """Generate documentation page for a single module."""
        module_name = module['name']
        module_path = module['path']
        module_doc = module['module_doc']
        classes = module['classes']
        functions = module['functions']

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_name} - Python_Api Documentation</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>{module_name}</h1>
            <p><code>{module_path}</code></p>
        </div>
    </header>

    <div class="container">
        <nav>
            <a href="index.html">← Back to Index</a>
        </nav>

        <div class="content">
"""

        # Module docstring
        if module_doc:
            html += f"""
            <h2>Module Documentation</h2>
            <div class="docstring">{self.escape_html(module_doc)}</div>
"""

        # Table of contents
        if classes or functions:
            html += """
            <div class="toc">
                <h3>Contents</h3>
                <ul>
"""
            if classes:
                html += "<li><strong>Classes</strong><ul>"
                for cls in classes:
                    html += f'<li><a href="#{cls["name"]}">{cls["name"]}</a></li>'
                html += "</ul></li>"

            if functions:
                html += "<li><strong>Functions</strong><ul>"
                for func in functions:
                    html += f'<li><a href="#{func["name"]}">{func["name"]}</a></li>'
                html += "</ul></li>"

            html += """
                </ul>
            </div>
"""

        # Classes
        if classes:
            html += "<h2>Classes</h2>"
            for cls in classes:
                html += self.generate_class_section(cls)

        # Functions
        if functions:
            html += "<h2>Functions</h2>"
            for func in functions:
                html += self.generate_function_section(func)

        html += f"""
            <div class="timestamp">
                Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    </div>

    <footer>
        <p>Generated by Python_Api Documentation Generator</p>
    </footer>
</body>
</html>
"""

        output_path = self.output_dir / f"{module_name}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def generate_class_section(self, cls: Dict) -> str:
        """Generate HTML for a class section."""
        bases = cls['bases']
        base_str = f"({', '.join(bases)})" if bases else ""

        html = f"""
        <div class="class-section" id="{cls['name']}">
            <h3>class {cls['name']}{base_str}</h3>
"""

        if cls['docstring']:
            html += f"""
            <div class="docstring">{self.escape_html(cls['docstring'])}</div>
"""

        if cls['methods']:
            html += "<h4>Methods</h4>"
            for method in cls['methods']:
                html += f"""
            <div class="method" id="{cls['name']}.{method['name']}">
                <h4>{method['name']}</h4>
                <div class="signature">{self.escape_html(method['signature'])}</div>
"""
                if method['docstring']:
                    html += f"""
                <div class="docstring">{self.escape_html(method['docstring'])}</div>
"""
                html += """
            </div>
"""

        html += """
        </div>
"""
        return html

    def generate_function_section(self, func: Dict) -> str:
        """Generate HTML for a function section."""
        html = f"""
        <div class="function-section" id="{func['name']}">
            <h3>{func['name']}</h3>
            <div class="signature">{self.escape_html(func['signature'])}</div>
"""

        if func['docstring']:
            html += f"""
            <div class="docstring">{self.escape_html(func['docstring'])}</div>
"""

        html += """
        </div>
"""
        return html

    def escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def main():
    """Main entry point for documentation generator."""
    print("Python_Api Documentation Generator")
    print("=" * 50)

    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print(f"Project root: {project_root}")

    # Extract documentation
    print("\nExtracting documentation from source files...")
    extractor = DocstringExtractor(project_root)
    modules = extractor.scan_project()

    print(f"Found {len(modules)} modules")

    # Generate HTML
    output_dir = project_root / "docs" / "html"
    generator = HTMLDocGenerator(output_dir)
    generator.generate(modules)

    print("\n" + "=" * 50)
    print(f"Documentation generated successfully!")
    print(f"\nTo view the documentation:")
    print(f"  Open: {output_dir / 'index.html'}")
    print(f"  Or run: python -m http.server 8080 --directory {output_dir}")
    print(f"  Then visit: http://localhost:8080")


if __name__ == "__main__":
    main()
