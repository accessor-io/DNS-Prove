# Development Guide

## Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/accessor-io/DNS-Prove.git
cd DNS-Prove
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev,docs]"
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=dns_prove
```

## Code Style

We use:
- flake8 for linting
- black for code formatting
- isort for import sorting

Format code:
```bash
black dns_prove tests
isort dns_prove tests
```

Check style:
```bash
flake8 dns_prove tests
```

## Building Documentation

Build HTML documentation:
```bash
cd docs
make html
```

## Making a Release

1. Update version in setup.py and __init__.py
2. Update CHANGELOG.md
3. Create a release commit:
```bash
git add .
git commit -m "Release v1.2.0"
git tag v1.2.0
git push origin main --tags
``` 