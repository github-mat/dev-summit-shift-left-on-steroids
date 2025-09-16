import base64
import io
import mimetypes
import os
import re
import time

import markdown
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

from utils import generate_qr_code, get_slide_files

app = Flask(__name__)
SLIDES_DIR = os.path.join(os.path.dirname(__file__), "slides")

# Simple in-memory cache for PDF export
PDF_CACHE = {}
PDF_CACHE_TIMEOUT = 300  # 5 minutes

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


@app.route("/qr-code/pdf-download")
def qr_code_pdf_download():
    """Generate QR code for PDF download with environment-aware URL."""
    # Get the base URL dynamically based on the request
    base_url = request.url_root.rstrip("/")
    pdf_url = f"{base_url}/export/pdf"

    # Generate QR code using shared utility
    img = generate_qr_code(pdf_url)

    # Convert to bytes
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return Response(
        img_io.getvalue(),
        mimetype="image/png",
        headers={"Cache-Control": "max-age=3600"},  # Cache for 1 hour
    )


@app.route("/")
def index():
    files = get_slide_files(SLIDES_DIR)
    if not files:
        return NO_SLIDES_FOUND_HTML
    return redirect(url_for("show_slide", slide_num=1))


@app.route("/slide/<int:slide_num>")
def show_slide(slide_num):
    files = get_slide_files(SLIDES_DIR)
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
    # Check cache first
    cache_key = "pdf_export"
    current_time = time.time()

    if cache_key in PDF_CACHE:
        cached_data, timestamp = PDF_CACHE[cache_key]
        if current_time - timestamp < PDF_CACHE_TIMEOUT:
            return Response(
                cached_data,
                mimetype="application/pdf",
                headers=HEADERS,
            )

    # Generate PDF if not cached or expired
    files = get_slide_files(SLIDES_DIR)
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

    # Cache the PDF
    PDF_CACHE[cache_key] = (pdf, current_time)

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

        html_content = re.sub(IMAGE_REGEX, replace_img, html_content)
        slide_html = '<div class="slide">'
        slide_html += f'<img src="{summit_logo}" alt="Summit Logo" class="summit-logo">'
        slide_html += f"<h2>Folie {idx} / {len(files)}</h2>{html_content}</div>"
        slides_html.append(slide_html)
    return slides_html


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)
