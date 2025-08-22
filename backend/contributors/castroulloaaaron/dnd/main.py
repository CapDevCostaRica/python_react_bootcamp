from flask import Flask

from backend.contributors.castroulloaaaron.dnd.service import Service

app = Flask(__name__)
service = Service()


@app.route('/monsters', methods=['POST'])
def get():
    service.get({})
    return {'status': 'ok'}


@app.route('/', methods=['POST'])
def get_monsters():
    service.list({})
    return {'status': 'ok'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
