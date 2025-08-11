from flask import Flask, render_template_string, request, send_file
import segno
import io
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>QR Generator with UTM</title>
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #fafafa;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
    }
    .container {
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        max-width: 420px;
        width: 100%;
        text-align: center;
    }
    .logo {
        max-width: 100px;
        margin-bottom: 20px;
    }
    h2 {
        color: #F66129;
        margin-bottom: 20px;
    }
    input, select, button {
        width: 100%;
        padding: 10px;
        margin-top: 8px;
        border-radius: 6px;
        border: 1px solid #ccc;
        font-size: 14px;
    }
    button {
        background-color: #F66129;
        border: none;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.2s ease-in-out;
    }
    button:hover {
        background-color: #e37a62;
    }
    .utm-fields {
        display: none;
        margin-top: 15px;
    }
</style>
<script>
    function toggleUTMFields() {
        const utmFields = document.getElementById('utm-fields');
        utmFields.style.display = document.getElementById('enable-utm').checked ? 'block' : 'none';
    }
</script>
</head>
<body>
<div class="container">
    <img src="https://www.onthefuze.com/hubfs/Logo-1.svg" class="logo" alt="Company Logo">
    <h2>QR Code Generator</h2>
    <form method="post">
        <input name="data" placeholder="Enter URL or text" required>
        
        <label style="display:block; margin-top:10px;">
            <input type="checkbox" id="enable-utm" name="enable_utm" onclick="toggleUTMFields()"> Add/Edit UTM Parameters
        </label>
        
        <div id="utm-fields" class="utm-fields">
            <input name="utm_source" placeholder="utm_source">
            <input name="utm_medium" placeholder="utm_medium">
            <input name="utm_campaign" placeholder="utm_campaign">
            <input name="utm_term" placeholder="utm_term">
            <input name="utm_content" placeholder="utm_content">
        </div>

        <select name="format">
            <option value="png">PNG</option>
            <option value="svg">SVG</option>
        </select>
        <button type="submit">Generate & Download</button>
    </form>
</div>
</body>
</html>
"""

def add_or_update_utm(url, utm_params):
    """Append or update UTM params in a URL."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # Update with new UTM params if provided
    for key, value in utm_params.items():
        if value:
            query[key] = [value]
    
    # Build new URL
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.get('data', '').strip()
        fmt = request.form.get('format', 'png')
        enable_utm = request.form.get('enable_utm')

        if not data:
            return "Error: No data provided", 400
        
        # If UTM is enabled, add/update params
        if enable_utm:
            utm_params = {
                'utm_source': request.form.get('utm_source', '').strip(),
                'utm_medium': request.form.get('utm_medium', '').strip(),
                'utm_campaign': request.form.get('utm_campaign', '').strip(),
                'utm_term': request.form.get('utm_term', '').strip(),
                'utm_content': request.form.get('utm_content', '').strip(),
            }
            data = add_or_update_utm(data, utm_params)
        
        # Generate QR
        qr = segno.make(data, error='m')
        bio = io.BytesIO()
        
        if fmt == 'png':
            qr.save(bio, kind='png', scale=8, border=4)
            bio.seek(0)
            return send_file(bio, as_attachment=True, download_name='qr.png', mimetype='image/png')
        elif fmt == 'svg':
            qr.save(bio, kind='svg', scale=8, border=4)
            bio.seek(0)
            return send_file(bio, as_attachment=True, download_name='qr.svg', mimetype='image/svg+xml')
        else:
            return "Error: Unsupported format", 400

    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
