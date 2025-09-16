import os
import tempfile

import pytest

from app import app
from utils import get_slide_files


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_slides():
    """Create temporary slides for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test slide files
        test_slides = {
            "01_first.md": "# First Slide\n\nTest content",
            "02_second.md": "# Second Slide\n\nMore content",
        }

        for filename, content in test_slides.items():
            with open(os.path.join(temp_dir, filename), "w", encoding="utf-8") as f:
                f.write(content)

        # Mock the SLIDES_DIR
        original_slides_dir = app.config.get("SLIDES_DIR")
        import app as app_module

        original_dir = app_module.SLIDES_DIR
        app_module.SLIDES_DIR = temp_dir

        yield temp_dir

        # Restore original
        app_module.SLIDES_DIR = original_dir


def test_get_slide_files_empty():
    """Test get_slide_files with empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        import app as app_module

        original_dir = app_module.SLIDES_DIR
        app_module.SLIDES_DIR = temp_dir

        files = get_slide_files(temp_dir)
        assert files == []

        app_module.SLIDES_DIR = original_dir


def test_get_slide_files_with_content(temp_slides):
    """Test get_slide_files with actual slide files."""
    files = get_slide_files(temp_slides)
    assert len(files) == 2
    assert files == ["01_first.md", "02_second.md"]


def test_index_redirect(client, temp_slides):
    """Test that index redirects to first slide."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/slide/1" in response.location


def test_index_no_slides(client):
    """Test index when no slides exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        import app as app_module

        original_dir = app_module.SLIDES_DIR
        app_module.SLIDES_DIR = temp_dir

        response = client.get("/")
        assert response.status_code == 200
        assert "Keine Folien gefunden" in response.get_data(as_text=True)

        app_module.SLIDES_DIR = original_dir


def test_show_slide_valid(client, temp_slides):
    """Test showing a valid slide."""
    response = client.get("/slide/1")
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert "First Slide" in content


def test_show_slide_invalid(client, temp_slides):
    """Test showing invalid slide numbers."""
    response = client.get("/slide/999")
    assert response.status_code == 404

    response = client.get("/slide/0")
    assert response.status_code == 404


def test_pdf_export(client, temp_slides):
    """Test PDF export functionality."""
    response = client.get("/export/pdf")
    assert response.status_code == 200
    assert response.content_type == "application/pdf"


def test_qr_code_pdf_download(client):
    """Test QR code generation for PDF download."""
    response = client.get("/qr-code/pdf-download")
    assert response.status_code == 200
    assert response.content_type == "image/png"
    assert "Cache-Control" in response.headers
    assert "max-age=3600" in response.headers["Cache-Control"]


def test_pdf_export_caching(client, temp_slides):
    """Test that PDF export is cached properly."""
    # First request should generate PDF
    response1 = client.get("/export/pdf")
    assert response1.status_code == 200

    # Second request should use cached version
    response2 = client.get("/export/pdf")
    assert response2.status_code == 200
    assert response2.content_type == "application/pdf"

    # Content should be identical (cached)
    assert response1.data == response2.data


def test_final_slide_contains_qr_code(client):
    """Test that the final slide contains QR code reference."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test speaker slide with QR code
        test_slide = """# Speaker

| Name 1 | Name 2 |
|--------|--------|
| Test 1 | Test 2 |

<div style="text-align: center; margin-top: 2em;">
    <h3>Scan to download slides</h3>
    <img src="/qr-code/pdf-download" alt="QR Code for slide download">
</div>"""

        with open(os.path.join(temp_dir, "01_speaker.md"), "w", encoding="utf-8") as f:
            f.write(test_slide)

        import app as app_module

        original_dir = app_module.SLIDES_DIR
        app_module.SLIDES_DIR = temp_dir

        response = client.get("/slide/1")
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert "/qr-code/pdf-download" in content
        assert "Scan to download slides" in content

        app_module.SLIDES_DIR = original_dir
