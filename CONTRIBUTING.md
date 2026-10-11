# Contributing to CryptoMAKA Lab

Thank you for contributing to CryptoMAKA Lab.

## Development Setup

1. **Python Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Run Tests & Linting:**
   ```bash
   pytest tests/ -v
   ruff check .
   ```

3. **Frontend Development:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Guidelines

- **Code Quality:** Ensure all code adheres to PEP 8, typed Pydantic models, and passes Ruff linter checks.
- **Academic Integrity:**
  - Do not alter the published Ju-Park protocol equations without documenting the normalization rationale in `docs/protocol.md`.
  - Maintain the clear separation between the published paper, normalized reconstruction, ECC counterpart, and proposed extensions.
  - Never hard-code academic claims or benchmark results as live measurements.
