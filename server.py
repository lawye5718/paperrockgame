from flask import Flask, send_from_directory
import os
import threading
import webbrowser

app = Flask(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(PROJECT_ROOT, path)

def open_browser():
    webbrowser.open_new('http://localhost:8502/')

if __name__ == '__main__':
    # 在单独的线程中打开浏览器
    threading.Timer(1.25, open_browser).start()
    app.run(host='0.0.0.0', port=8502, debug=True)