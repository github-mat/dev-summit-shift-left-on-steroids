"""
Tests for PDF caching functionality.
"""

import os
import tempfile
import time
from unittest.mock import patch

import pytest

from app import (
    PDF_CACHE_FILE,
    PDF_CACHE_META_FILE,
    _get_content_hash,
    _is_pdf_cache_valid,
    _load_pdf_cache,
    _save_pdf_cache,
)


@pytest.fixture
def temp_cache_files():
    """Create temporary cache files for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_file = os.path.join(temp_dir, ".pdf_cache.pdf")
        meta_file = os.path.join(temp_dir, ".pdf_cache_meta.txt")

        with (
            patch("app.PDF_CACHE_FILE", cache_file),
            patch("app.PDF_CACHE_META_FILE", meta_file),
        ):
            yield cache_file, meta_file


def test_get_content_hash_consistency():
    """Test that content hash is consistent for the same content"""
    hash1 = _get_content_hash()
    hash2 = _get_content_hash()
    assert hash1 == hash2
    assert isinstance(hash1, str)
    assert len(hash1) == 32  # MD5 hash length


def test_pdf_cache_invalid_when_files_missing(temp_cache_files):
    """Test that cache is invalid when files are missing"""
    cache_file, meta_file = temp_cache_files
    assert not _is_pdf_cache_valid()


def test_pdf_cache_save_and_load(temp_cache_files):
    """Test saving and loading PDF cache"""
    cache_file, meta_file = temp_cache_files
    test_pdf_data = b"fake pdf content"

    # Save cache
    _save_pdf_cache(test_pdf_data)

    # Check files exist
    assert os.path.exists(cache_file)
    assert os.path.exists(meta_file)

    # Load cache
    loaded_data = _load_pdf_cache()
    assert loaded_data == test_pdf_data


def test_pdf_cache_validation(temp_cache_files):
    """Test cache validation logic"""
    cache_file, meta_file = temp_cache_files
    test_pdf_data = b"fake pdf content"

    # Save cache
    _save_pdf_cache(test_pdf_data)

    # Cache should be valid immediately after saving
    assert _is_pdf_cache_valid()

    # Manually write wrong hash to meta file
    with open(meta_file, "w", encoding="utf-8") as f:
        f.write("wrong_hash")

    # Cache should be invalid now
    assert not _is_pdf_cache_valid()


def test_pdf_cache_invalidates_on_content_change(temp_cache_files):
    """Test that cache invalidates when content changes"""
    cache_file, meta_file = temp_cache_files
    test_pdf_data = b"fake pdf content"

    # Save cache
    _save_pdf_cache(test_pdf_data)
    assert _is_pdf_cache_valid()

    # Simulate content change by modifying the hash stored in meta file
    current_hash = _get_content_hash()
    fake_old_hash = "different_hash_" + current_hash[13:]

    with open(meta_file, "w", encoding="utf-8") as f:
        f.write(fake_old_hash)

    # Cache should now be invalid
    assert not _is_pdf_cache_valid()
