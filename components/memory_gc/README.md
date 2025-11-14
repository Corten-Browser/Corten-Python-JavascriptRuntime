# memory_gc

**Type**: core
**Level**: 1
**Tech Stack**: Python 3.11+
**Version**: 0.1.0

## Responsibility

Memory allocation and mark-and-sweep GC

## Dependencies

shared_types, value_system

## Structure

```
├── src/           # Source code
├── tests/         # Tests (unit, integration)
├── CLAUDE.md      # Component-specific instructions for Claude Code
└── README.md      # This file
```

## Setup

```bash
# Install dependencies (from project root)
pip install -e .

# Install dev dependencies
pip install pytest pytest-cov pylint black
```

## Usage

```python
# Example usage will be added after implementation
from components.memory_gc import ...
```

## Development

### Run Tests
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
# Lint
pylint src/ tests/

# Format
black src/ tests/

# Complexity check
radon cc src/ -a
```

## API

See `../../contracts/memory_gc.yaml` for complete API specification.

## Architecture

Phase 1 (Foundation) component implementing core JavaScript runtime functionality.
Follows TDD methodology with 80%+ test coverage requirement.
