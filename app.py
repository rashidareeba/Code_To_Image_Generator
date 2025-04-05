from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import uuid
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['IMAGES_FOLDER'] = 'generated_images'

# Create images directory if not exists
if not os.path.exists(app.config['IMAGES_FOLDER']):
    os.makedirs(app.config['IMAGES_FOLDER'])

def highlight_code(code, language):
    """Syntax highlighting using Pygments"""
    try:
        lexer = get_lexer_by_name(language)
        formatter = HtmlFormatter(style="monokai", cssclass="codehilite")
        return highlight(code, lexer, formatter), formatter.get_style_defs()
    except:
        lexer = get_lexer_by_name('text')
        formatter = HtmlFormatter(style="monokai", cssclass="codehilite")
        return highlight(code, lexer, formatter), formatter.get_style_defs()

def generate_screenshot(html_content, output_path):
    """Generate PNG using Playwright"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_content)
            page.screenshot(path=output_path, full_page=True, type='png')
            browser.close()
    except Exception as e:
        print("Playwright error:", e)


@app.route('/')
def index():
    session.clear()  # Clear previous sessions
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    code = request.form['code']
    language = request.form['language']
    
    # Generate highlighted code
    highlighted_code, css = highlight_code(code, language)
    
    # Create HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            {css}
            body {{ 
                margin: 20px;
                background: #1e1e1e;
                padding: 20px;
            }}
            .codehilite {{
                padding: 20px;
                border-radius: 5px;
                font-size: 14px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        {highlighted_code}
    </body>
    </html>
    """
    
    # Generate unique filename
    filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(app.config['IMAGES_FOLDER'], filename)
    
    # Generate and save image
    generate_screenshot(html_template, output_path)
    
    # Store in session for possible reuse
    session['last_image'] = filename
    
    return jsonify({
        'image_url': f'/images/{filename}',
        'download_url': f'/download/{filename}'
    })

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename)

@app.route('/download/<filename>')
def download_image(filename):
    return send_from_directory(
        app.config['IMAGES_FOLDER'],
        filename,
        as_attachment=True,
        download_name=f"code-snippet-{filename}"
    )

if __name__ == '__main__':
    app.run(debug=True)