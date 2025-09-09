import os
import tempfile
from generate_static import (
    get_slide_files, 
    get_html_content, 
    prepare_page,
    PREV_NAV_TEMPLATE,
    NEXT_NAV_TEMPLATE
)


def test_get_slide_files_sorting():
    """Test that slide files are sorted correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create files in mixed order
        test_files = ["10_slide.md", "2_slide.md", "1_slide.md"]
        for filename in test_files:
            with open(os.path.join(temp_dir, filename), "w") as f:
                f.write("test")
        
        import generate_static as gen_module
        original_dir = gen_module.SLIDES_DIR
        gen_module.SLIDES_DIR = temp_dir
        
        files = get_slide_files()
        assert files == ["1_slide.md", "2_slide.md", "10_slide.md"]
        
        gen_module.SLIDES_DIR = original_dir


def test_get_html_content():
    """Test markdown to HTML conversion."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_md = "# Test Title\n\nThis is a test with /slide/images/test.png"
        test_file = os.path.join(temp_dir, "test.md")
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_md)
        
        import generate_static as gen_module
        original_dir = gen_module.SLIDES_DIR
        gen_module.SLIDES_DIR = temp_dir
        
        html = get_html_content("test.md")
        assert "<h1>Test Title</h1>" in html
        assert "images/test.png" in html  # Should convert Flask paths
        assert "/slide/images/" not in html
        
        gen_module.SLIDES_DIR = original_dir


def test_prepare_page_first_slide():
    """Test page preparation for first slide."""
    template = f"""
    <html>
    <body>
        <div>{{{{ content|safe }}}}</div>
        <p>Slide {{{{ slide_num }}}} of {{{{ total_slides }}}}</p>
        <nav>
            {PREV_NAV_TEMPLATE}
            {NEXT_NAV_TEMPLATE}
        </nav>
    </body>
    </html>
    """
    
    html_content = "<h1>First Slide</h1>"
    result = prepare_page(template, html_content, 1, 3)
    
    assert "<h1>First Slide</h1>" in result
    assert "Slide 1 of 3" in result
    assert "disabled" in result  # Previous should be disabled
    assert "slide2.html" in result  # Next should link to slide2


def test_prepare_page_last_slide():
    """Test page preparation for last slide."""
    template = f"""
    <html>
    <body>
        <div>{{{{ content|safe }}}}</div>
        <p>Slide {{{{ slide_num }}}} of {{{{ total_slides }}}}</p>
        <nav>
            {PREV_NAV_TEMPLATE}
            {NEXT_NAV_TEMPLATE}
        </nav>
    </body>
    </html>
    """
    
    html_content = "<h1>Last Slide</h1>"
    result = prepare_page(template, html_content, 3, 3)
    
    assert "<h1>Last Slide</h1>" in result
    assert "Slide 3 of 3" in result
    assert "slide2.html" in result  # Previous should link to slide2
    assert "disabled" in result  # Next should be disabled
