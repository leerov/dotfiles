#!/usr/bin/env python3
import os
import pty
import threading
import webbrowser
import time
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

try:
    from flask import Flask, render_template_string
except ImportError:
    install('flask')
    from flask import Flask, render_template_string

try:
    from flask_sock import Sock
except ImportError:
    install('flask-sock')
    from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm/css/xterm.css" />
    <script src="https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"></script>
    <!-- Подключаем аддон для автоматического подгона размера -->
    <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
    <style>
        html, body {
            height: 100%;
            width: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #1e1e1e;
        }
        #terminal {
            height: 100%;
            width: 100%;
            padding: 0;
            box-sizing: border-box;
        }
        /* Принудительное растяжение всех внутренних элементов xterm */
        .xterm,
        .xterm-viewport,
        .xterm-screen {
            width: 100% !important;
            height: 100% !important;
        }
        .xterm {
            font-family: 'Hack Nerd Font Mono', 'Hack Nerd Font', 'Hack', monospace;
        }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <script>
        const term = new Terminal({
            fontFamily: "'Hack Nerd Font Mono', 'Hack Nerd Font', 'Hack', monospace"
        });

        // Используем FitAddon для подгонки размеров
        const fitAddon = new FitAddon.FitAddon();
        term.loadAddon(fitAddon);

        // Открываем терминал в контейнере
        term.open(document.getElementById('terminal'));

        // Подгоняем сразу и при изменении размера окна
        fitAddon.fit();
        window.addEventListener('resize', () => fitAddon.fit());

        // WebSocket
        const ws = new WebSocket('ws://' + location.host + '/ws');
        term.onData(data => ws.send(data));
        ws.onmessage = ev => term.write(ev.data);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@sock.route('/ws')
def ws(ws):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('/bin/zsh', ['/bin/zsh'])
    else:
        def reader():
            try:
                while True:
                    data = os.read(fd, 1024)
                    if not data:
                        break
                    ws.send(data.decode('utf-8', errors='ignore'))
            except Exception:
                pass

        def writer():
            try:
                while True:
                    msg = ws.receive()
                    if msg is None:
                        break
                    os.write(fd, msg.encode())
            except Exception:
                pass

        t1 = threading.Thread(target=reader, daemon=True)
        t2 = threading.Thread(target=writer, daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        os.close(fd)

def open_browser():
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
