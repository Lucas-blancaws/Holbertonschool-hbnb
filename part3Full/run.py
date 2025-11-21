from app import create_app
from flask import Flask
from flask_cors import CORS
import config

app = create_app(config.DevelopmentConfig)

# Configuration CORS complète
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

if __name__ == '__main__':
    app.run(debug=True)