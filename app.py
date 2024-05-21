from flask import Flask, request, redirect, render_template, jsonify
import boto3
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

app = Flask(__name__)

# Configurar a conexão com o DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('MyApplicationData')

@app.route('/')
def index():
    try:
        # Recuperar todos os registros da tabela DynamoDB
        response = table.scan()
        items = response.get('Items', [])

        for item in items:
            if 'created_at' not in item:
                item['created_at'] = '1970-01-01T00:00:00.000000'  
        items.sort(key=lambda x: x['created_at'], reverse=True)

        return render_template('index.html', posts=items)
    except ClientError as e:
        return f"Erro ao acessar DynamoDB: {e.response['Error']['Message']}", 500

@app.route('/health')
def health():
    return "OK", 200

@app.route('/calculate_imc', methods=['POST'])
def calculate_imc():
    name = request.form['name']
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    imc = weight / (height ** 2)

    # Determinar o status do IMC
    if imc < 18.5:
        status = "Abaixo do peso"
    elif 18.5 <= imc < 24.9:
        status = "Peso normal"
    elif 25 <= imc < 29.9:
        status = "Sobrepeso"
    else:
        status = "Obesidade"

    # Salvar no DynamoDB
    item = {
        'Id': str(uuid.uuid4()),
        'Name': name,
        'Weight': weight,
        'Height': height,
        'IMC': imc,
        'Status': status,
        'created_at': datetime.utcnow().isoformat()
    }
    try:
        table.put_item(Item=item)
    except ClientError as e:
        return f"Erro ao acessar DynamoDB: {e.response['Error']['Message']}", 500

    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
