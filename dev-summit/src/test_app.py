import os
import tempfile

import pytest

from app import app, generate_qr_code, get_slide_files


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

        files = get_slide_files()
        assert files == []

        app_module.SLIDES_DIR = original_dir


def test_get_slide_files_with_content(temp_slides):
    """Test get_slide_files with actual slide files."""
    files = get_slide_files()
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


def test_generate_qr_code():
    """Test QR code generation."""
    test_url = "http://localhost:8080/export/pdf"
    qr_data_url = generate_qr_code(test_url)

    # Check that it returns a valid data URL
    assert qr_data_url.startswith("data:image/png;base64,")
    assert len(qr_data_url) > 50  # Should be a substantial base64 string


def test_qr_code_cache():
    """Test QR code caching."""
    test_url = "http://test.example.com/test"

    # First call
    qr_data_url1 = generate_qr_code(test_url)

    # Second call should return the same cached result
    qr_data_url2 = generate_qr_code(test_url)

    assert qr_data_url1 == qr_data_url2


def test_qr_code_on_final_slide(client, temp_slides):
    """Test that QR code appears only on the final slide."""
    # Test first slide (should not have QR code)
    response = client.get("/slide/1")
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'class="qr-code-container"' not in content

    # Test final slide (should have QR code)
    response = client.get("/slide/2")  # Last slide in our test data
    assert response.status_code == 200
    content = response.get_data(as_text=True)
    assert 'class="qr-code-container"' in content
    assert "Scan to download slides" in content
    assert "data:image/png;base64," in content


def test_pdf_cache(client, temp_slides):
    """Test PDF export caching."""
    # First request
    response1 = client.get("/export/pdf")
    assert response1.status_code == 200

    # Second request should use cached version
    response2 = client.get("/export/pdf")
    assert response2.status_code == 200
    assert response1.data == response2.data
