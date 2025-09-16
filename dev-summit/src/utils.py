"""Shared utility functions for the presentation application."""

import os
import re

import qrcode


def get_slide_files(slides_dir):
    """Get sorted list of markdown slide files."""
    files = [f for f in os.listdir(slides_dir) if f.endswith(".md")]

    def extract_number(filename):
        match = re.match(r"(\d+)", os.path.splitext(filename)[0])
        return int(match.group(1)) if match else 0

    files = sorted(files, key=extract_number)
    return files


def generate_qr_code(url):
    """Generate a QR code image for the given URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image
    return qr.make_image(fill_color="black", back_color="white")
