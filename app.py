from flask import Flask, request, render_template, jsonify
import boto3
import uuid
from botocore.exceptions import ClientError
import logging
from werkzeug.security import generate_password_hash

# Configurar o logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Configurar a conexão com o DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('MyApplicationData')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return "OK", 200

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Salvar no DynamoDB
        item = {
            'Id': str(uuid.uuid4()),
            'Username': username,
            'Password': hashed_password,
            'created_at': datetime.utcnow().isoformat()
        }

        logging.debug(f"Inserting item into DynamoDB: {item}")
        table.put_item(Item=item)

        return jsonify({
            'Username': username,
            'Message': 'Registration successful'
        })
    except ClientError as e:
        logging.error(f"Error inserting item into DynamoDB: {e.response['Error']['Message']}")
        return jsonify({'error': f"Erro ao acessar DynamoDB: {e.response['Error']['Message']}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f"Erro inesperado: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
