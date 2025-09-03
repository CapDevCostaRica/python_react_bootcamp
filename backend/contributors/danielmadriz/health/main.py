from flask import Flask
from controllers.people_controller import PeopleController

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}

@app.route('/people/find', methods=['GET'])
def find_people():
    return PeopleController.find_people()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
