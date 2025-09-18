# Dev Summit Shift Left on Steroids

This repository contains the code and resources for the "Shift Left on Steroids" session at Dev Summit. The session focuses on enhancing software development practices by integrating advanced techniques and tools to improve code quality, security, and efficiency.

## Development Setup

This project uses [UV](https://docs.astral.sh/uv/) for fast and reliable Python dependency management.

### Prerequisites

- Python 3.11 or higher
- [UV](https://docs.astral.sh/uv/getting-started/installation/) package manager

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/github-mat/dev-summit-shift-left-on-steroids.git
   cd dev-summit-shift-left-on-steroids/dev-summit
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Run the development server:
   ```bash
   cd src
   uv run python app.py
   ```

4. Open http://localhost:8080 in your browser

### Development Commands

- **Install dependencies:** `uv sync --extra dev`
- **Run application:** `uv run python app.py`
- **Generate static HTML:** `uv run python generate_static.py`
- **Run tests:** `uv run pytest src/`
- **Code formatting:** `uv run black --config pyproject.toml src/`
- **Import sorting:** `uv run isort --settings-file=pyproject.toml src/`
- **Linting:** `uv run pylint --rcfile=pyproject.toml src/`

### Project Structure

- `src/` - Main application code
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions for reproducible builds
- `Dockerfile` - Container configuration

### Benefits of UV

- **10-100x faster** dependency resolution and installation
- **Reproducible builds** with lock file management
- **Unified tooling** for dependency management and virtual environments
- **Modern Python packaging** standards