from flask import Flask, jsonify
import os
import random
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

from database import get_session
from models import AndresnbozaMonster

app = Flask(__name__)

@app.route('/')
def get_random_monster():
    session = get_session()
    monsters = session.query(AndresnbozaMonster).all()
    session.close()
    if not monsters:
        return jsonify({'error': 'No andresnboza dnd monsters found.'}), 404
    monster = random.choice(monsters).name
    return jsonify({'monster': monster})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
