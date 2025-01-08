from flask import Flask, request, jsonify, render_template

import grpc
import service_pb2
import service_pb2_grpc
import uuid

app = Flask(__name__)

# Connessione al server gRPC in ascolto sulla porta 50051
channel = grpc.insecure_channel('servergrpc:50051')
user_stub = service_pb2_grpc.UserServiceStub(channel)
stock_stub = service_pb2_grpc.StockServiceStub(channel)

def validate_values(high_value, low_value):
    # Controllo che almeno uno tra high_value e low_value sia stato fornito
    if high_value is None and low_value is None:
        return False, "Errore: devi fornire almeno uno tra high_value e low_value."
    
    # Se entrambi sono forniti, controllo che high_value sia maggiore di low_value
    if high_value is not None and low_value is not None and high_value <= low_value:
        return False, "Errore: il valore massimo (high_value) deve essere maggiore del valore minimo (low_value)."
    
    return True, ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email')
    ticker = data.get('ticker')
    high_value = data.get('high_value', None)
    low_value = data.get('low_value', None)

    # Validazione dei valori
    valid, message = validate_values(high_value, low_value)
    if not valid:
        return jsonify({'success': False, 'message': message}), 200  # Success con messaggio di errore

    request_id = str(uuid.uuid4())

    user_request = service_pb2.UserRequest(
        email=email,
        ticker=ticker,
        high_value=high_value if high_value is not None else 0.0,
        low_value=low_value if low_value is not None else 0.0,
        request_id=request_id
    )
    response = user_stub.RegisterUser(user_request)
    return jsonify({
        'success': response.success,
        'message': response.message
    })

@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.json
    email = data.get('email')
    ticker = data.get('ticker')
    high_value = data.get('high_value', None)
    low_value = data.get('low_value', None)

    # Validazione dei valori
    valid, message = validate_values(high_value, low_value)
    if not valid:
        return jsonify({'success': False, 'message': message}), 200  # Success con messaggio di errore

    request_id = str(uuid.uuid4())

    user_request = service_pb2.UserRequest(
        email=email,
        ticker=ticker,
        high_value=high_value if high_value is not None else 0.0,
        low_value=low_value if low_value is not None else 0.0,
        request_id=request_id
    )
    response = user_stub.UpdateUser(user_request)
    return jsonify({
        'success': response.success,
        'message': response.message
    })

@app.route('/get_latest_stock_value', methods=['POST'])
def get_latest_stock_value():
    data = request.json
    email = data.get('email')

    stock_request = service_pb2.StockRequest(email=email)
    stock_response = stock_stub.GetLatestStockValue(stock_request)

    return jsonify({
        'ticker': stock_response.ticker,
        'value': stock_response.value,
        'timestamp': stock_response.timestamp
    })

@app.route('/get_average_stock_value', methods=['POST'])
def get_average_stock_value():
    data = request.json
    email = data.get('email')
    count = data.get('count')

    if not count or not isinstance(count, int) or count <= 0:
        return jsonify({'success': False, 'message': 'Il numero di valori per calcolare la media deve essere un numero intero positivo.'}), 200  # Success con messaggio di errore

    stock_average_request = service_pb2.StockAverageRequest(email=email, count=count)
    stock_average_response = stock_stub.GetAverageStockValue(stock_average_request)

    return jsonify({
        'average': stock_average_response.average
    })

@app.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.json
    email = data.get('email')

    request_id = str(uuid.uuid4())
    user_request = service_pb2.UserRequest(email=email, ticker="", request_id=request_id)
    response = user_stub.DeleteUser(user_request)

    return jsonify({
        'success': response.success,
        'message': response.message
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)




