import os

from flask import (
    Flask,
    render_template,
    render_template_string,
    abort,
    redirect,
    url_for,
    send_from_directory,
)
import markdown


app = Flask(__name__)
SLIDES_DIR = os.path.join(os.path.dirname(__file__), "slides")


@app.route("/slide/images/<path:filename>")
def slide_images(filename):
    # Liefert Bilder aus slides/images/ aus
    return send_from_directory(os.path.join(SLIDES_DIR, "images"), filename)


# Route für Videos
@app.route("/slide/videos/<path:filename>")
def slide_videos(filename):
    # Liefert Videos aus slides/videos/ aus
    return send_from_directory(os.path.join(SLIDES_DIR, "videos"), filename)





import re

def get_slide_files():
    
    files = [f for f in os.listdir(SLIDES_DIR) if f.endswith(".md")]
    def extract_number(filename):
        match = re.match(r"(\d+)", os.path.splitext(filename)[0])
        return int(match.group(1)) if match else 0
    files = sorted(files, key=extract_number)
    return files


@app.route("/")
def index():
    files = get_slide_files()
    if not files:
        return "<h2>Keine Folien gefunden. Lege Markdown-Dateien im slides/-Verzeichnis an.</h2>"
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


# PDF Export Endpoint (Querformat, Bilder eingebettet)
from flask import Response
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

@app.route("/export/pdf")
def export_pdf():
    if not WEASYPRINT_AVAILABLE:
        return "WeasyPrint ist nicht installiert. Bitte 'weasyprint' in requirements.txt aufnehmen.", 500
    import base64, mimetypes
    files = get_slide_files()
    slides_html = []
    images_dir = os.path.abspath(os.path.join(SLIDES_DIR, "images"))

    def img_to_data_url(img_path):
        if not os.path.exists(img_path):
            return ''
        mime, _ = mimetypes.guess_type(img_path)
        with open(img_path, 'rb') as img_f:
            b64 = base64.b64encode(img_f.read()).decode('utf-8')
        return f'data:{mime};base64,{b64}'

    # Regex für verschiedene Bildpfade: /slide/images/foo.png, images/foo.png, ./images/foo.png
    img_regex = r'src=["\"](\/slide\/images\/|\.\/images\/|images\/)([^"\"]+)["\"]'

    # PDF-optimiertes CSS (kein position: fixed, keine Viewport-Größen)
    pdf_css = '''
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
    '''

    # Logos als Base64 einbetten
    def logo_data_url(filename):
        path = os.path.join(images_dir, filename)
        if not os.path.exists(path):
            return ''
        mime, _ = mimetypes.guess_type(path)
        with open(path, 'rb') as img_f:
            b64 = base64.b64encode(img_f.read()).decode('utf-8')
        return f'data:{mime};base64,{b64}'

    materna_logo = logo_data_url('materna-logo.png')
    summit_logo = logo_data_url('summit-logo.svg')

    slides_html = []
    for idx, filename in enumerate(files, 1):
        with open(os.path.join(SLIDES_DIR, filename), encoding="utf-8") as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=["extra"])

        def replace_img(match):
            img_file = match.group(2)
            img_path = os.path.join(images_dir, img_file)
            data_url = img_to_data_url(img_path)
            if data_url:
                return f'src="{data_url}"'
            else:
                return match.group(0)

        html_content = re.sub(
            img_regex,
            replace_img,
            html_content
        )
        slide_html = f'<div class="slide">'
        slide_html += f'<img src="{summit_logo}" alt="Summit Logo" class="summit-logo">'
        slide_html += f'<h2>Folie {idx} / {len(files)}</h2>{html_content}</div>'
        slides_html.append(slide_html)

    pdf_html = f'''<!DOCTYPE html>
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
</html>'''
    pdf = HTML(string=pdf_html).write_pdf()
    return Response(pdf, mimetype='application/pdf', headers={
        'Content-Disposition': 'attachment; filename=devsummit_praesentation.pdf'
    })


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)
