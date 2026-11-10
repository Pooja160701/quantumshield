# Development

Install Python 3.11+, then:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
uvicorn quantumshield.api.main:app --reload
pytest
ruff check .
```

Add regression tests for algorithm behavior and edge cases. Never use Python random for real cryptographic randomness. Use a vetted provider or OS CSPRNG. Document whether outputs are educational, benchmark measurements, provider capability, or validated property. Do not place secret material in logs, fixtures or screenshots.
