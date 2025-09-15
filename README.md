# Dev Summit Shift Left on Steroids

This repository contains the code and resources for the "Shift Left on Steroids" session at Dev Summit. The session focuses on enhancing software development practices by integrating advanced techniques and tools to improve code quality, security, and efficiency.

## Development Setup

This project uses [UV](https://github.com/astral-sh/uv) for fast Python package management and project management.

### Prerequisites

- Python 3.11 or higher
- UV (Astral's fast Python package manager)

### Installing UV

```bash
# Install UV
pip install uv
```

Or follow the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Development Workflow

1. **Clone the repository**
   ```bash
   git clone https://github.com/github-mat/dev-summit-shift-left-on-steroids.git
   cd dev-summit-shift-left-on-steroids/dev-summit
   ```

2. **Install dependencies**
   ```bash
   # Install all dependencies including development tools
   uv sync --dev
   ```

3. **Run tests**
   ```bash
   uv run pytest -v
   ```

4. **Run linting and formatting**
   ```bash
   # Check code formatting
   uv run black --config pyproject.toml --check src/
   
   # Check import sorting
   uv run isort --settings-file=pyproject.toml --check-only src/
   
   # Run linting
   uv run pylint --rcfile=pyproject.toml src/
   ```

5. **Start the development server**
   ```bash
   cd src
   uv run python app.py
   ```

6. **Generate static HTML**
   ```bash
   uv run python src/generate_static.py
   ```

### Dependencies

This project uses:
- **Production**: Flask, Markdown, WeasyPrint
- **Development**: Black, Pylint, isort, pytest

All dependencies are managed through `pyproject.toml` and locked in `uv.lock` for reproducible builds.

### Docker

The project includes a Dockerfile that uses UV for dependency management:

```bash
docker build -t dev-summit .
docker run -p 8080:8080 dev-summit
```

## Benefits of UV

- ⚡ **10-100x faster** dependency resolution and installation
- 🔒 **Better lock file management** with `uv.lock` for reproducible builds  
- 🛠️ **Unified tooling** for dependency management, virtual environments, and project management
- 📦 **Modern Python packaging** standards with proper `pyproject.toml` integration