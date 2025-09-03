from flask import Flask
from app.people_service import find_people

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}

@app.route('/people/find', methods=['GET'])
def find_people_endpoint():
    return find_people()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
