#!/usr/bin/env python3
import os
import pty
import select
import threading
import webbrowser
import time

from flask import Flask, render_template_string
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm/css/xterm.css" />
    <script src="https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"></script>
    <style>
        body { margin: 0; padding: 10px; background: #1e1e1e; }
        /* Основной шрифт – Hack Nerd Font Mono, запасные – Hack, monospace */
        .xterm { font-family: 'Hack Nerd Font Mono', 'Hack Nerd Font', 'Hack', monospace; }
    </style>
</head>
<body>
    <div id="terminal"></div>
    <script>
        const term = new Terminal({
            // Передаём те же варианты в порядке предпочтения
            fontFamily: "'Hack Nerd Font Mono', 'Hack Nerd Font', 'Hack', monospace"
        });
        term.open(document.getElementById('terminal'));
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
    # Создаём псевдотерминал и запускаем /bin/zsh
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('/bin/zsh', ['/bin/zsh'])
    else:
        try:
            while True:
                r, _, _ = select.select([fd], [], [], 0.1)
                if fd in r:
                    data = os.read(fd, 1024)
                    if data:
                        ws.send(data.decode('utf-8', errors='ignore'))
                msg = ws.receive()
                if msg is not None:
                    os.write(fd, msg.encode())
        except:
            pass
        finally:
            os.close(fd)

def open_browser():
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
