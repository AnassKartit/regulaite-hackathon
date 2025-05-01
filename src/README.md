# Regulaite

Regulaite is an AI-powered regulatory compliance tool that helps organizations analyze and ensure compliance with various regulations.

## Features

- AI-powered compliance analysis
- Support for multiple regulatory frameworks
- Integration with Azure services
- Real-time scanning and monitoring

## Installation

```bash
pip install regulaite
```

## Usage

```python
from regulaite.orchestrator import Orchestrator

# Initialize orchestrator with repository
orchestrator = Orchestrator("your-repo")

# Run compliance scan
result = orchestrator.run()
```

## Azure Functions Integration

The package includes Azure Functions for:
- Repository scanning
- Law upload and processing
- Compliance reporting

## Requirements

- Python 3.9+
- Azure Functions Core Tools
- Azure OpenAI access
- Azure Cognitive Search

## Development

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Run tests: `python -m pytest tests/`

## License

MIT License