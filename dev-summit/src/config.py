"""
Shared configuration module for the presentation application.
"""

import qrcode.constants

# Common QR code configuration
QR_CODE_CONFIG = {
    "version": 1,
    "error_correction": qrcode.constants.ERROR_CORRECT_L,
    "box_size": 10,
    "border": 4,
}
