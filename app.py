from flask import Flask, request, render_template, redirect
import boto3
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash
import logging

# Configurar o logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Configurar o cliente DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('MyApplicationData')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    # Capturar dados do formulário
    username = request.form['username']
    password = request.form['password']
    hashed_password = generate_password_hash(password)
    
    # Gerar um UUID único para cada nova entrada
    user_id = str(uuid.uuid4())
    
    # Obter a data e hora atuais
    created_at = datetime.utcnow().isoformat()

    # Inserir os dados na tabela DynamoDB
    try:
        response = table.put_item(
           Item={
                'Id': user_id,
                'Username': username,
                'Password': hashed_password,
                'created_at': created_at
            }
        )
        return redirect('/')
    except Exception as e:
        logging.error(f"Erro ao inserir dados: {str(e)}")
        return redirect('/')

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
