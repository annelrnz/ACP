# launcher.py
import threading
import time
import webbrowser
import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app import app
    from main import ProfessorApp
    from database import init_db
    import tkinter as tk
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📁 Current directory:", current_dir)
    print("📁 Files in directory:", os.listdir(current_dir))
    input("Press Enter to exit...")
    sys.exit(1)

def run_flask():
    """Run Flask web server"""
    print("🚀 Starting Flask web server...")
    try:
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"❌ Flask error: {e}")

def run_tkinter():
    """Run Tkinter desktop app"""
    print("🎯 Starting Tkinter desktop app...")
    try:
        root = tk.Tk()
        gui_app = ProfessorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"❌ Tkinter error: {e}")

if __name__ == "__main__":
    # Initialize database first
    print("📊 Initializing database...")
    init_db()
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Open browser automatically
    print("🌐 Opening web browser...")
    webbrowser.open('http://localhost:5000')
    
    # Start Tkinter (this will block until Tkinter closes)
    run_tkinter()