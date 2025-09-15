"""Tests for QR code functionality"""

import pytest

from app import app


@pytest.fixture
def client():
    """Create test client for Flask app"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_qr_code_endpoint(client):
    """Test that QR code endpoint returns PNG image"""
    response = client.get("/qr-code.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert len(response.data) > 0


def test_final_slide_contains_qr_code(client):
    """Test that final slide contains QR code"""
    response = client.get("/slide/18")
    assert response.status_code == 200
    assert b'src="/qr-code.png"' in response.data
    assert b"Scan to download slides" in response.data
