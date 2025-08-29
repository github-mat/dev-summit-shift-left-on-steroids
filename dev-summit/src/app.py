import os

from flask import (
    Flask,
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


TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>DevSummit 2025</title>
    <style>
        .materna-logo {
            position: fixed;
            right: 2vw;
            bottom: 9vh;
            width: 120px;
            max-width: 15vw;
            max-height: 12vh;
            height: auto;
            z-index: 101;
            pointer-events: none;
        }
        .summit-logo {
            position: fixed;
            top: 2vh;
            right: 2vw;
            width: 120px;
            max-width: 15vw;
            max-height: 12vh;
            height: auto;
            z-index: 100;
            pointer-events: none;
        }
        .summit-logo {
            position: fixed;
            top: 2vh;
            right: 2vw;
            width: 120px;
            height: auto;
            z-index: 100;
        }
        html, body { height: 100%; margin: 0; padding: 0; }
    body { font-family: sans-serif; margin: 0; background: #fff; color: #222; height: 100vh; }
        .slide {
            width: 95vw;
            height: 85vh;
            margin: 2.5vh auto 0 auto;
            background: #fff;
            padding: 3vw 3vw 2vw 3vw;
            border-radius: 10px;
            box-shadow: 0 0 20px #ccc8;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            overflow: auto;
        }
        .footer {
            width: 100vw;
            margin: 0;
            height: 7vh;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: fixed;
            left: 0;
            bottom: 0;
            background: #787777;
            color: #222;
            padding: 0 2vw;
            box-sizing: border-box;
            z-index: 10;
        }
        .footer-title {
            color: #fff;
            font-size: 1.1em;
            letter-spacing: 1px;
            flex: 1;
            text-align: left;
        }
        .footer-right {
            flex: 1;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            color: #fff;
        }
        .nav {
            display: flex;
            align-items: center;
            gap: 1.5em;
        }
        .nav a {
            color: #fff;
            margin: 0 0.5em;
            text-decoration: none;
            font-size: 1.2em;
            transition: color 0.2s;
        }
        .nav a.disabled {
            color: #666 !important;
            pointer-events: none;
            cursor: default;
            text-decoration: none;
        }
        .nav a:not(.disabled):hover { text-decoration: underline; }
        ul, ol {
            margin-top: 1em;
            margin-bottom: 1em;
        }
        li {
            margin-bottom: 0.7em;
        }
    </style>
</head>
<body>
    <img src="/slide/images/materna-logo.png" alt="Materna Logo" class="materna-logo">
    <img src="/slide/images/summit-logo.svg" alt="Summit Logo" class="summit-logo">
    <div class="slide">
        {{ content|safe }}
    </div>
    <div class="footer">
        <div class="footer-title">©Materna</div>
        <div class="footer-right">
            <div class="nav">
                {% if prev_slide %}
                    <a href="{{ url_for('show_slide', slide_num=prev_slide) }}">&laquo; Zurück</a>
                {% else %}
                    <a class="disabled">&laquo; Zurück</a>
                {% endif %}
                <span>Folie {{ slide_num }} / {{ total_slides }}</span>
                {% if next_slide %}
                    <a href="{{ url_for('show_slide', slide_num=next_slide) }}">Weiter &raquo;</a>
                {% else %}
                    <a class="disabled">Weiter &raquo;</a>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""


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
    return render_template_string(
        TEMPLATE,
        content=html_content,
        slide_num=slide_num,
        total_slides=total,
        prev_slide=prev_slide,
        next_slide=next_slide,
    )


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)
