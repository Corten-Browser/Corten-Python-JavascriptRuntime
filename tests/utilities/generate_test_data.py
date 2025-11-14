"""
Test data generator for JavaScript runtime smoke tests.

Generates sample JavaScript files for testing the CLI and runtime engine.
Used by Phase 6 smoke tests to verify the complete system works end-to-end.
"""

from pathlib import Path
from typing import Dict, List


class TestDataGenerator:
    """Generates JavaScript test files for smoke testing."""

    def __init__(self, output_dir: Path):
        """
        Initialize test data generator.

        Args:
            output_dir: Directory where test files will be created
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> Dict[str, Path]:
        """
        Generate all test data files.

        Returns:
            Dictionary mapping test name to file path
        """
        files = {}

        files['simple_expression'] = self.generate_simple_expression()
        files['variable_declaration'] = self.generate_variable_declaration()
        files['function_declaration'] = self.generate_function_declaration()
        files['function_call'] = self.generate_function_call()
        files['control_flow'] = self.generate_control_flow()
        files['arithmetic'] = self.generate_arithmetic()
        files['complex_program'] = self.generate_complex_program()

        return files

    def generate_simple_expression(self) -> Path:
        """Generate file with simple expression."""
        content = "42"
        return self._write_file('simple_expression.js', content)

    def generate_variable_declaration(self) -> Path:
        """Generate file with variable declarations."""
        content = """// Variable declarations
var x = 10;
var y = 20;
var z = 30;
"""
        return self._write_file('variable_declaration.js', content)

    def generate_function_declaration(self) -> Path:
        """Generate file with function declarations."""
        content = """// Function declarations
function add(a, b) {
    return a + b;
}

function multiply(x, y) {
    return x * y;
}

function greet(name) {
    return name;
}
"""
        return self._write_file('function_declaration.js', content)

    def generate_function_call(self) -> Path:
        """Generate file with function calls."""
        content = """// Function definition and call
function double(n) {
    return n * 2;
}

double(21)
"""
        return self._write_file('function_call.js', content)

    def generate_control_flow(self) -> Path:
        """Generate file with control flow statements."""
        content = """// Control flow
var x = 10;

if (x) {
    var y = 20;
}

while (0) {
    var z = 30;
}
"""
        return self._write_file('control_flow.js', content)

    def generate_arithmetic(self) -> Path:
        """Generate file with arithmetic operations."""
        content = """// Arithmetic operations
var a = 10 + 20;
var b = 50 - 30;
var c = 6 * 7;
var d = 100 / 2;
"""
        return self._write_file('arithmetic.js', content)

    def generate_complex_program(self) -> Path:
        """Generate file with complex program."""
        content = """// Complex program
var x = 10;
var y = 20;

function add(a, b) {
    return a + b;
}

function multiply(a, b) {
    return a * b;
}

var sum = add(x, y);
var product = multiply(x, y);

if (sum) {
    var z = 100;
}
"""
        return self._write_file('complex_program.js', content)

    def _write_file(self, filename: str, content: str) -> Path:
        """
        Write content to file.

        Args:
            filename: Name of file to create
            content: JavaScript content to write

        Returns:
            Path to created file
        """
        filepath = self.output_dir / filename
        filepath.write_text(content)
        return filepath


def generate_test_files(output_dir: str = None) -> Dict[str, Path]:
    """
    Convenience function to generate all test files.

    Args:
        output_dir: Directory for test files (default: ./test_data)

    Returns:
        Dictionary mapping test name to file path
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / 'test_data'

    generator = TestDataGenerator(output_dir)
    return generator.generate_all()


if __name__ == '__main__':
    # Generate test data when run directly
    import sys

    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = './test_data'

    print(f"Generating test data in: {output_dir}")
    files = generate_test_files(output_dir)

    print(f"\nGenerated {len(files)} test files:")
    for name, path in files.items():
        print(f"  {name}: {path}")
