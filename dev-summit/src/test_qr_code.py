"""Tests for QR code functionality."""

import pytest

from app import generate_qr_code_data_url


def test_qr_code_generation():
    """Test that QR code generation works."""
    test_url = "https://example.com/export/pdf"
    qr_data_url = generate_qr_code_data_url(test_url)

    # Check that a data URL is returned
    assert qr_data_url.startswith("data:image/png;base64,")

    # Check that it contains base64 data
    assert len(qr_data_url) > 50  # Should be longer than just the prefix


def test_qr_code_different_urls():
    """Test that different URLs generate different QR codes."""
    url1 = "https://example.com/pdf1"
    url2 = "https://example.com/pdf2"

    qr1 = generate_qr_code_data_url(url1)
    qr2 = generate_qr_code_data_url(url2)

    # Different URLs should generate different QR codes
    assert qr1 != qr2


def test_qr_code_empty_url():
    """Test QR code generation with empty URL."""
    qr_data_url = generate_qr_code_data_url("")

    # Should still generate a valid data URL
    assert qr_data_url.startswith("data:image/png;base64,")
