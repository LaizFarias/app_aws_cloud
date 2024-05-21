from flask import Flask, request, jsonify, render_template_string
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import uuid

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = 'MyApplicationData'
table = dynamodb.Table(table_name)

@app.before_request
def verify_headers():
    if not request.headers.get('Host'):
        abort(400)

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form['text']
    unique_id = str(uuid.uuid4())  # Gerar um UUID único
    response = table.put_item(
        Item={
            'id': unique_id,
            'text': data
        }
    )
    return jsonify(response), 200

@app.route('/form')
def form():
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Submit Data</title>
    </head>
    <body>
        <form action="/submit" method="POST">
            <label for="text">Enter Text:</label>
            <input type="text" id="text" name="text" required>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(form_html)

@app.route('/show')
def show():
    response = table.scan()
    items = response.get('Items', [])
    
    items_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Show Data</title>
    </head>
    <body>
        <h1>Stored Data</h1>
        <ul>
    """
    for item in items:
        items_html += f"<li>ID: {item['id']} - Text: {item['text']}</li>"
    
    items_html += """
        </ul>
    </body>
    </html>
    """
    return render_template_string(items_html)

if __name__ == '_main_':
    app.run(host='0.0.0.0', port=5000)
