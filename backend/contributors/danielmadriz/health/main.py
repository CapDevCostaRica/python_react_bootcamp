from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}

@app.route('/people/find', methods=['GET'])
def find_people():
    return jsonify({
        'message': 'Not implemented',
        'result_count': 0,
        'names': []
    }), 501

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
