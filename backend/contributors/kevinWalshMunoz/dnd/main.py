import os
import sys

# Add project root and framework to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../framework')))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)