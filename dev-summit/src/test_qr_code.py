"""Tests for QR code functionality."""

import unittest

import app


class TestQRCodeFunctionality(unittest.TestCase):
    """Test QR code generation and display."""

    def setUp(self):
        """Set up test client."""
        self.app = app.app.test_client()

    def test_generate_qr_code(self):
        """Test QR code generation with proper request context."""
        with app.app.test_request_context("http://localhost:8080/"):
            qr_data = app.generate_qr_code()

            # Verify it returns a base64 data URL
            self.assertTrue(qr_data.startswith("data:image/png;base64,"))
            self.assertGreater(
                len(qr_data), 100
            )  # Should be a substantial base64 string

    def test_final_slide_has_qr_code(self):
        """Test that the final slide contains QR code data."""
        with app.app.test_request_context():
            response = self.app.get("/slide/18")

            # Should have 200 response
            self.assertEqual(response.status_code, 200)

            # Response should contain QR code data
            response_data = response.get_data(as_text=True)
            self.assertIn("data:image/png;base64,", response_data)
            self.assertIn("Scan to download slides", response_data)

    def test_non_final_slide_no_qr_code(self):
        """Test that non-final slides don't contain QR code."""
        with app.app.test_request_context():
            response = self.app.get("/slide/1")

            # Should have 200 response
            self.assertEqual(response.status_code, 200)

            # Response should NOT contain QR code data
            response_data = response.get_data(as_text=True)
            self.assertNotIn("data:image/png;base64,", response_data)
            self.assertNotIn("Scan to download slides", response_data)

    def test_pdf_caching(self):
        """Test that PDF export uses caching."""
        # Reset cache
        app.CACHED_PDF = None

        with app.app.test_request_context():
            # First request should generate PDF
            response1 = self.app.get("/export/pdf")
            self.assertEqual(response1.status_code, 200)
            self.assertEqual(response1.content_type, "application/pdf")

            # Cache should now be populated
            self.assertIsNotNone(app.CACHED_PDF)

            # Second request should use cache
            response2 = self.app.get("/export/pdf")
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response2.content_type, "application/pdf")

            # Both responses should have same content
            self.assertEqual(response1.data, response2.data)


if __name__ == "__main__":
    unittest.main()
