from flask import Flask, jsonify
import os
import random
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))
from database import get_session
from models import MotivationalPhrase

app = Flask(__name__)

@app.route('/')
def get_motivation():
    session = get_session()
    phrases = session.query(MotivationalPhrase).all()
    session.close()
    if not phrases:
        return jsonify({'error': 'No motivational phrases found.'}), 404
    phrase = random.choice(phrases).phrase
    return jsonify({'phrase': phrase})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
