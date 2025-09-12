from flask import Flask, jsonify
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({'status': "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
