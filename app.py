from flask import Flask, request, jsonify, send_file
import boto3
import uuid

app = Flask(__name__)

# Configurar a conexão com o DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('ProjetoApplicationData')

@app.route('/')
def index():
    return send_file('index.html')

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
        'Status': status
    }
    table.put_item(Item=item)

    return jsonify(item)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
