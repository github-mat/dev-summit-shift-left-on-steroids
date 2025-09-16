# Dev Summit Shift Left on Steroids

This repository contains a Python Flask web application that renders a presentation system for "Shift Left on Steroids" session at Dev Summit. The application displays Markdown slides in a web interface, supports PDF export, and generates static HTML files for deployment.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Initial Setup
- Install Python dependencies:
  - `cd dev-summit`
  - `pip install -r requirements.txt` -- takes ~13 seconds
  - `pip install -r requirements-dev.txt` -- takes ~6 seconds

### Development Workflow
- Run the Flask web application:
  - `cd dev-summit/src`
  - `python app.py`
  - Application runs on http://localhost:8080
  - NEVER CANCEL: Application starts immediately, no build step required
- Generate static HTML files:
  - `cd dev-summit/src`
  - `python generate_static.py` -- takes ~1 second
  - Static files are generated in `docs/` directory
  - Static files can be served with: `cd docs && python3 -m http.server 8081`

### Code Quality and Testing (REQUIRED before committing)
- Run all linting and formatting checks:
  - `cd dev-summit`
  - `black --config pyproject.toml --check src/`
  - `isort --settings-file=pyproject.toml --check-only src/`
  - `pylint --rcfile=pyproject.toml src/`
- Run tests:
  - `cd dev-summit`
  - `pytest src/`
- Fix formatting automatically:
  - `black --config pyproject.toml src/`
  - `isort --settings-file=pyproject.toml src/`

### Docker and Deployment
- Docker build: 
  - `cd dev-summit`
  - `docker build -t dev-summit .` -- FAILS due to SSL certificate issues in CI environment
  - Docker build works in production with proper SSL configuration
- Terraform deployment:
  - `cd terraform/deployment`
  - `terraform init`
  - `terraform plan`
  - `terraform apply`
  - Deploys to Google Cloud Run using workspace-based naming

## Validation

### Manual Testing Requirements
- ALWAYS test the Flask application after making changes by:
  1. Start the Flask app: `cd dev-summit/src && python app.py`
  2. Navigate to http://localhost:8080 in browser
  3. Verify the first slide loads with "Bug-Free by Design" title
  4. Test navigation: click "Weiter »" to go to slide 2
  5. Test PDF export: visit http://localhost:8080/export/pdf
  6. Verify static generation works: `cd dev-summit/src && python generate_static.py`
- ALWAYS run all linting and test commands before committing
- Test both web interface and static HTML generation for any slide content changes

### Expected Functionality
- The application displays 18 slides with navigation controls
- PDF export creates a complete presentation document
- Static HTML generation produces deployable files in `docs/` directory
- All code passes Black formatting, isort import sorting, and Pylint analysis
- All 11 tests pass consistently

## Repository Structure

### Key Directories and Files
- `dev-summit/src/` - Main application code
  - `app.py` - Flask web application with slide rendering and PDF export
  - `generate_static.py` - Static HTML generation script
  - `template.html` - HTML template for slide presentation
  - `slides/` - Markdown slide files (01_startfolie.md through 18_speaker.md)
  - `test_*.py` - Test files for application logic
- `dev-summit/` - Python project configuration
  - `requirements.txt` - Runtime dependencies (flask, markdown, weasyprint)
  - `requirements-dev.txt` - Development dependencies (black, pylint, isort, pytest)
  - `pyproject.toml` - Tool configuration for formatting and linting
  - `Dockerfile` - Container configuration for deployment
- `.github/workflows/` - CI/CD pipeline
  - `deploy.yaml` - Main deployment workflow with Docker build and Terraform apply
  - `destroy-pr-resources.yaml` - Cleanup workflow for PR environments
- `terraform/deployment/` - Infrastructure as Code for Google Cloud deployment
- `docs/` - Generated static HTML files for web hosting

### Slide System
- Slides are numbered Markdown files in `dev-summit/src/slides/`
- Images and media go in `dev-summit/src/slides/images/` and `dev-summit/src/slides/videos/`
- Navigation supports keyboard arrow keys and click navigation
- Templates include Materna and Summit logos automatically

## CI/CD Pipeline

### GitHub Actions Workflow
The deployment pipeline (`deploy.yaml`) runs on push to main and PR events:
1. **CI Phase**: Install dependencies, run Black, isort, and Pylint checks
2. **Static HTML Generation**: Generate and commit static files to `docs/` (main branch only)
3. **Docker Build**: Build and push container image to Google Artifact Registry
4. **Terraform Apply**: Deploy to Google Cloud Run with workspace-based environments

### Build Timeouts and Expectations
- Python dependency installation: ~20 seconds total
- Linting and formatting checks: ~5 seconds total  
- Test execution: ~3 seconds
- Docker build: ~2-5 minutes (when SSL certificates work)
- Static HTML generation: ~1 second
- NEVER CANCEL: All operations complete quickly, no long-running builds

### Environment Limitations
- Docker builds may fail in development due to SSL certificate issues
- This is normal and expected in CI environments
- Production builds work correctly with proper SSL configuration
- Local development should focus on Python Flask application testing

## Common Tasks

### Adding New Slides
1. Create numbered Markdown file in `dev-summit/src/slides/` (e.g., `19_new-slide.md`)
2. Add any images to `dev-summit/src/slides/images/`
3. Test with Flask app: `cd dev-summit/src && python app.py`
4. Regenerate static HTML: `python generate_static.py`
5. Run tests and linting before committing

### Debugging Issues
- Check Flask app logs when running `python app.py`
- Verify slide files are properly numbered and formatted
- Test PDF export separately with WeasyPrint dependencies
- Use browser developer tools to debug CSS and JavaScript issues
- Static HTML generation issues usually involve path resolution

### Development Tips
- Use `FLASK_DEBUG=true python app.py` for development mode with auto-reload
- Test both dynamic Flask routes and static HTML output
- PDF export requires proper system fonts and WeasyPrint dependencies
- Arrow key navigation only works when no input fields are focused
- Images should use relative paths: `images/filename.png` not absolute paths