import os
import re
import shutil

import markdown

# Statisches HTML-Export-Skript für die Slides
# Nutzt das gleiche Template wie die Flask-App

SLIDES_DIR = os.path.join(os.path.dirname(__file__), "slides")
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.html")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../../", "docs")


PREV_NAV_TEMPLATE = """
    {% if prev_slide %}
    <a href="{{ url_for('show_slide', slide_num=prev_slide) }}">
        &laquo; Zurück
    </a>
    {% else %}
    <a class="disabled">&laquo; Zurück</a>
    {% endif %}"""

NEXT_NAV_TEMPLATE = """
    {% if next_slide %}
    <a href="{{ url_for('show_slide', slide_num=next_slide) }}">
        Weiter &raquo;
    </a>
    {% else %}
    <a class="disabled">Weiter &raquo;</a>
    {% endif %}"""


def render_static_html():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    copy_media()
    content_template = get_template_content()

    files = get_slide_files()
    total = len(files)
    for idx, filename in enumerate(files, 1):

        html_content = get_html_content(filename)
        page = prepare_page(content_template, html_content, idx, total)

        # store first slide as index.html
        if idx == 1:
            index_path = os.path.join(OUTPUT_DIR, "index.html")
            with open(index_path, "w", encoding="utf-8") as out:
                out.write(page)

        out_path = os.path.join(OUTPUT_DIR, f"slide{idx}.html")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(page)


def copy_media():
    for media in ["images", "videos"]:
        src = os.path.join(SLIDES_DIR, media)
        dst = os.path.join(OUTPUT_DIR, media)
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)


def get_template_content() -> str:
    with open(TEMPLATE_PATH, encoding="utf-8") as tpl:
        template_content = tpl.read()
    return template_content


def get_slide_files():
    files = [f for f in os.listdir(SLIDES_DIR) if f.endswith(".md")]

    def extract_number(filename):
        match = re.match(r"(\d+)", os.path.splitext(filename)[0])
        return int(match.group(1)) if match else 0

    files = sorted(files, key=extract_number)
    return files


def get_html_content(filename: str) -> str:
    with open(os.path.join(SLIDES_DIR, filename), encoding="utf-8") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=["extra"])

    html_content = html_content.replace("/slide/images/", "images/")
    html_content = html_content.replace("/slide/videos/", "videos/")
    return html_content


def prepare_page(content_template: str, html_content: str, idx: int, total: int) -> str:
    page = content_template
    page = page.replace("{{ content|safe }}", html_content)
    page = page.replace("{{ slide_num }}", str(idx))
    page = page.replace("{{ total_slides }}", str(total))

    prev_slide = idx - 1 if idx > 1 else None
    next_slide = idx + 1 if idx < total else None

    page = content_template
    page = page.replace("{{ content|safe }}", html_content)
    page = page.replace("{{ slide_num }}", str(idx))
    page = page.replace("{{ total_slides }}", str(total))

    # Navigation-Links (nur statisch, keine Flask-URL)
    if prev_slide:
        prev_link = f"slide{prev_slide}.html"
        page = page.replace(
            PREV_NAV_TEMPLATE,
            f'<a href="{prev_link}">&laquo; Zurück</a>',
        )
    else:
        page = page.replace(
            PREV_NAV_TEMPLATE,
            '<a class="disabled">&laquo; Zurück</a>',
        )
    if next_slide:
        next_link = f"slide{next_slide}.html"
        page = page.replace(
            NEXT_NAV_TEMPLATE,
            f'<a href="{next_link}">Weiter &raquo;</a>',
        )
    else:
        page = page.replace(
            NEXT_NAV_TEMPLATE,
            '<a class="disabled">Weiter &raquo;</a>',
        )
    return page


if __name__ == "__main__":
    render_static_html()
