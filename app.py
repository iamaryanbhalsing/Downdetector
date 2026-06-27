from flask import Flask, render_template, request, jsonify
import requests
import threading
import time
import os
from datetime import datetime

app = Flask(__name__)

websites = ["google.com", "github.com", "microsoft.com", "aws.amazon.com"]
status_data = {}

def check_website(url):
    try:
        full_url = url if url.startswith(('http://', 'https://')) else f"https://{url}"
        r = requests.get(full_url, timeout=8, headers={'User-Agent': 'Downdetector'})
        return "UP" if r.status_code == 200 else "DOWN"
    except:
        return "DOWN"

def background_monitor():
    global status_data
    while True:
        for url in list(websites):  # Use copy to avoid issues
            status = check_website(url)
            status_data[url] = {
                "status": status,
                "last_check": datetime.now().strftime("%H:%M:%S")
            }
        time.sleep(6)  # Faster update

@app.route('/')
def index():
    return render_template('index.html', websites=websites, status_data=status_data)

@app.route('/history')
def history():
    return jsonify({
        "websites": websites,
        "status_data": status_data
    })

@app.route('/add_site', methods=['POST'])
def add_site():
    url = request.form.get('url', '').strip()
    if url and url not in websites:
        websites.append(url)
        status_data[url] = {
            "status": "Checking...",
            "last_check": datetime.now().strftime("%H:%M:%S")
        }
    return jsonify({"success": True})

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    print("🚀 Starting Downdetector...")
    threading.Thread(target=background_monitor, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)