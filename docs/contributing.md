# Contributing

We love your input! We want to make contributing to DNS-Prove as easy and transparent as possible.

## Development Process

1. Fork the repo and create your branch from `main`
2. Install development dependencies: `pip install -e ".[dev,docs]"`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `flake8`
6. Submit a Pull Request

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dns_prove

# Run specific test
pytest tests/test_dnsprover.py -k test_name
```

## Building Documentation

```bash
cd docs
make html
``` 