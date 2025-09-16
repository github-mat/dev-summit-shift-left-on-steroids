import base64
import hashlib
import mimetypes
import os
import re
from io import BytesIO

import markdown
import qrcode
from flask import (
    Flask,
    Response,
    abort,
    redirect,
    render_template_string,
    request,
    send_from_directory,
    url_for,
)
from weasyprint import HTML

from config import QR_CODE_CONFIG

app = Flask(__name__)
SLIDES_DIR = os.path.join(os.path.dirname(__file__), "slides")

# PDF Cache configuration
PDF_CACHE_FILE = os.path.join(os.path.dirname(__file__), ".pdf_cache.pdf")
PDF_CACHE_META_FILE = os.path.join(os.path.dirname(__file__), ".pdf_cache_meta.txt")

IMAGE_REGEX = r'src=["\"](\/slide\/images\/|\.\/images\/|images\/)([^"\"]+)["\"]'

HEADERS = {
    "Content-Disposition": "attachment; filename=devsummit_praesentation.pdf",
}
NO_SLIDES_FOUND_HTML = """
    <h2>
        Keine Folien gefunden. Lege Markdown-Dateien im slides/-Verzeichnis an.
    </h2>
    """


@app.route("/slide/images/<path:filename>")
def slide_images(filename):
    # Liefert Bilder aus slides/images/ aus
    return send_from_directory(os.path.join(SLIDES_DIR, "images"), filename)


# Route für Videos
@app.route("/slide/videos/<path:filename>")
def slide_videos(filename):
    # Liefert Videos aus slides/videos/ aus
    return send_from_directory(os.path.join(SLIDES_DIR, "videos"), filename)


@app.route("/qr-code.png")
def qr_code():
    # Generate QR code that points to the PDF export URL
    base_url = request.url_root.rstrip("/")
    pdf_url = f"{base_url}/export/pdf"

    # Create QR code
    qr = qrcode.QRCode(**QR_CODE_CONFIG)
    qr.add_data(pdf_url)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return Response(img_io.getvalue(), mimetype="image/png")


def get_slide_files():

    files = [f for f in os.listdir(SLIDES_DIR) if f.endswith(".md")]

    def extract_number(filename):
        match = re.match(r"(\d+)", os.path.splitext(filename)[0])
        return int(match.group(1)) if match else 0

    files = sorted(files, key=extract_number)
    return files


def _get_content_hash():
    """Generate a hash of all content that affects PDF generation"""
    hasher = hashlib.md5()

    # Hash all slide files
    files = get_slide_files()
    for filename in files:
        file_path = os.path.join(SLIDES_DIR, filename)
        if os.path.exists(file_path):
            hasher.update(filename.encode("utf-8"))
            hasher.update(str(os.path.getmtime(file_path)).encode("utf-8"))

    # Hash template file
    template_path = os.path.join(os.path.dirname(__file__), "template.html")
    if os.path.exists(template_path):
        hasher.update(str(os.path.getmtime(template_path)).encode("utf-8"))

    # Hash all images
    images_dir = os.path.join(SLIDES_DIR, "images")
    if os.path.exists(images_dir):
        for root, _, files in os.walk(images_dir):
            for file in sorted(files):  # Sort for consistent hashing
                file_path = os.path.join(root, file)
                hasher.update(file.encode("utf-8"))
                hasher.update(str(os.path.getmtime(file_path)).encode("utf-8"))

    return hasher.hexdigest()


def _is_pdf_cache_valid():
    """Check if PDF cache is still valid"""
    if not os.path.exists(PDF_CACHE_FILE) or not os.path.exists(PDF_CACHE_META_FILE):
        return False

    try:
        with open(PDF_CACHE_META_FILE, "r", encoding="utf-8") as f:
            cached_hash = f.read().strip()

        current_hash = _get_content_hash()
        return cached_hash == current_hash
    except (OSError, IOError):
        return False


def _save_pdf_cache(pdf_data):
    """Save PDF to cache with metadata"""
    try:
        # Save PDF content
        with open(PDF_CACHE_FILE, "wb") as f:
            f.write(pdf_data)

        # Save content hash
        with open(PDF_CACHE_META_FILE, "w", encoding="utf-8") as f:
            f.write(_get_content_hash())
    except (OSError, IOError):
        # If caching fails, continue without cache
        pass


def _load_pdf_cache():
    """Load PDF from cache"""
    try:
        with open(PDF_CACHE_FILE, "rb") as f:
            return f.read()
    except (OSError, IOError):
        return None


@app.route("/")
def index():
    files = get_slide_files()
    if not files:
        return NO_SLIDES_FOUND_HTML
    return redirect(url_for("show_slide", slide_num=1))


@app.route("/slide/<int:slide_num>")
def show_slide(slide_num):
    files = get_slide_files()
    total = len(files)
    if slide_num < 1 or slide_num > total:
        abort(404)
    filename = files[slide_num - 1]
    with open(os.path.join(SLIDES_DIR, filename), encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=["extra"])
    prev_slide = slide_num - 1 if slide_num > 1 else None
    next_slide = slide_num + 1 if slide_num < total else None
    # Template-Pfad relativ zu src
    template_path = os.path.join(os.path.dirname(__file__), "template.html")
    with open(template_path, encoding="utf-8") as tpl:
        template_content = tpl.read()
    return render_template_string(
        template_content,
        content=html_content,
        slide_num=slide_num,
        total_slides=total,
        prev_slide=prev_slide,
        next_slide=next_slide,
    )


@app.route("/export/pdf")
def export_pdf():
    # Check if we have a valid cached PDF
    if _is_pdf_cache_valid():
        cached_pdf = _load_pdf_cache()
        if cached_pdf:
            return Response(
                cached_pdf,
                mimetype="application/pdf",
                headers=HEADERS,
            )

    # Generate new PDF if cache is invalid or missing
    files = get_slide_files()
    slides_html = []
    images_dir = os.path.abspath(os.path.join(SLIDES_DIR, "images"))

    # PDF-optimiertes CSS (kein position: fixed, keine Viewport-Größen)
    pdf_css = """
    @page { size: A4 landscape; margin: 1cm; }
    body { font-family: sans-serif; background: #fff; color: #222; }
    .slide {
        width: 100%;
        min-height: 15cm;
        margin: 0 0 1cm 0;
        background: #fff;
        padding: 2em 2em 1em 2em;
        border-radius: 10px;
        box-shadow: 0 0 20px #ccc8;
        display: block;
        position: relative;
        page-break-after: always;
    }
    h2 { margin-top: 0; }
    img { max-width: 90%; height: auto; margin: 1em 0; }
    .materna-logo {
        position: fixed;
        right: 2em;
        bottom: 2em;
        width: 100px;
        max-width: 15vw;
        max-height: 12vh;
        height: auto;
        z-index: 101;
        /* Für PDF: auf jeder Seite anzeigen */
        display: block;
    }
    .summit-logo {
        position: absolute;
        top: 2em;
        right: 2em;
        width: 100px;
        max-width: 15vw;
        max-height: 12vh;
        height: auto;
        z-index: 100;
    }
    ul, ol { margin-top: 1em; margin-bottom: 1em; }
    li { margin-bottom: 0.7em; }
    """

    # Logos als Base64 einbetten
    def logo_data_url(filename):
        path = os.path.join(images_dir, filename)
        if not os.path.exists(path):
            return ""
        mime, _ = mimetypes.guess_type(path)
        with open(path, "rb") as img_f:
            b64 = base64.b64encode(img_f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    materna_logo = logo_data_url("materna-logo.png")
    summit_logo = logo_data_url("summit-logo.svg")

    slides_html = _prepare_slides(files, images_dir, summit_logo)

    pdf_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>DevSummit 2025 PDF Export</title>
    <style>{pdf_css}</style>
</head>
<body>
    <img src="{materna_logo}" alt="Materna Logo" class="materna-logo">
    {''.join(slides_html)}
</body>
</html>"""
    pdf = HTML(string=pdf_html).write_pdf()

    # Cache the generated PDF
    _save_pdf_cache(pdf)

    return Response(
        pdf,
        mimetype="application/pdf",
        headers=HEADERS,
    )


def _img_to_data_url(img_path):
    if not os.path.exists(img_path):
        return ""
    mime, _ = mimetypes.guess_type(img_path)
    with open(img_path, "rb") as img_f:
        b64 = base64.b64encode(img_f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _prepare_slides(files: list[str], images_dir: str, summit_logo: str):
    slides_html = []
    for idx, filename in enumerate(files, 1):
        with open(os.path.join(SLIDES_DIR, filename), encoding="utf-8") as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=["extra"])

        def replace_img(match):
            img_file = match.group(2)
            img_path = os.path.join(images_dir, img_file)
            data_url = _img_to_data_url(img_path)
            return f'src="{data_url}"'

        # Replace regular images
        html_content = re.sub(IMAGE_REGEX, replace_img, html_content)

        # Replace QR code URL with generated data URL for PDF
        qr_data_url = _generate_qr_code_data_url()
        html_content = html_content.replace(
            'src="/qr-code.png"', f'src="{qr_data_url}"'
        )

        slide_html = '<div class="slide">'
        slide_html += f'<img src="{summit_logo}" alt="Summit Logo" class="summit-logo">'
        slide_html += f"<h2>Folie {idx} / {len(files)}</h2>{html_content}</div>"
        slides_html.append(slide_html)
    return slides_html


def _generate_qr_code_data_url():
    """Generate QR code as data URL for PDF export"""
    # For PDF export, use a generic URL since the PDF will be saved/shared
    pdf_url = "https://your-presentation-url.com/export/pdf"

    # Create QR code
    qr = qrcode.QRCode(**QR_CODE_CONFIG)
    qr.add_data(pdf_url)
    qr.make(fit=True)

    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to data URL
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    b64 = base64.b64encode(img_io.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)
