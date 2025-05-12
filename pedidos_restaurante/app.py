from flask import Flask, request, jsonify  # type: ignore
import requests # type: ignore

app = Flask(__name__)

POCKETBASE_URL = "http://localhost:8090/api/collections"

@app.route('/pedidos', methods=['POST'])
def crear_pedido():
    data = request.json
    response = requests.post(f"{POCKETBASE_URL}/pedidos/records", json=data)
    return jsonify(response.json()), response.status_code

@app.route('/pedidos/pendientes', methods=['GET'])
def obtener_pedidos_pendientes():
    response = requests.get(f"{POCKETBASE_URL}/pedidos/records", params={"filter": 'estado="Pendiente"'})
    return jsonify(response.json()), response.status_code

@app.route('/pedidos/<id>', methods=['PATCH'])
def actualizar_estado_pedido(id):
    data = request.json
    response = requests.patch(f"{POCKETBASE_URL}/pedidos/records/{id}", json=data)
    return jsonify(response.json()), response.status_code

@app.route('/pedidos/historial', methods=['GET'])
def obtener_historial_pedidos():
    response = requests.get(f"{POCKETBASE_URL}/pedidos/records", params={"filter": 'estado="Entregado"'})
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
