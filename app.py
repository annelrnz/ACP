# app.py
from flask import Flask
from routes import setup_routes

app = Flask(__name__)

# Setup all routes
setup_routes(app)

if __name__ == '__main__':
    print("🚀 Attendify Student Website running on http://localhost:5000")
    print("📱 Students can scan QR code to access this website")
    app.run(debug=True, host='0.0.0.0', port=5000)