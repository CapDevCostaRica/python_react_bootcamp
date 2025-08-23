from flask import Flask, jsonify, request

from dnd.service import Service

app = Flask(__name__)
service = Service()


@app.route('/monsters', methods=['POST'])
def get():
    data, code = service.get(request.get_json(silent=True) or {})
    return jsonify(data), code


@app.route('/', methods=['POST'])
def get_monsters():
    data, code = service.list(request.get_json(silent=True) or {})
    return jsonify(data), code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
