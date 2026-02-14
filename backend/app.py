from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Register API blueprint
from backend.api.routes import api
app.register_blueprint(api)

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok', 'message': 'Backend is running'}

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port)
