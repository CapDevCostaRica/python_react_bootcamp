from flask import Flask
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


from seeds import seed_database

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    print("Seeding database...")
    seed_database()
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=4000)