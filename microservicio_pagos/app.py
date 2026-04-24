from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/api/v2/comprar', methods=['POST'])
def realizar_compra():
    data = request.get_json(silent=True) or {}

    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad', 1)

    if not producto_id:
        return jsonify({'error': 'Falta el ID del producto'}), 400

    return jsonify(
        {
            'mensaje': 'Compra procesada exitosamente por el Microservicio Flask (v2)',
            'producto_id': producto_id,
            'cantidad': cantidad,
            'status': 'Aprobado',
        }
    ), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
