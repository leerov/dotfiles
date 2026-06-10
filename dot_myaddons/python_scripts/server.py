#!/usr/bin/env python3
import os
import pty
import socket
import select
import sys
import struct
import fcntl
import termios
import signal
import threading
import time
import json

class PTYServer:
    def __init__(self, host='0.0.0.0', port=8080, announce_port=8888):
        self.host = host
        self.port = port
        self.announce_port = announce_port
        self.server_name = socket.gethostname()
        self.running = True
        
    def announce_presence(self):
        """Периодически рассылает UDP broadcast о своем существовании"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1)
        
        # Формируем информацию о сервере
        server_info = {
            'name': self.server_name,
            'host': self.get_local_ip(),
            'port': self.port,
            'time': time.time()
        }
        
        data = json.dumps(server_info).encode()
        
        while self.running:
            try:
                sock.sendto(data, ('<broadcast>', self.announce_port))
                time.sleep(5)  # Каждые 5 секунд
            except Exception as e:
                print(f"[-] Ошибка announce: {e}")
                time.sleep(10)
        
        sock.close()
    
    def get_local_ip(self):
        """Получает локальный IP адрес"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def set_winsize(self, fd, rows, cols):
        """Устанавливает размер окна для PTY"""
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
    
    def handle_connection(self, conn, addr):
        print(f"[+] Подключение от {addr}")
        
        # Получаем размер терминала
        try:
            winsize_data = conn.recv(8)
            if len(winsize_data) < 8:
                print("[-] Не получен размер терминала")
                conn.close()
                return
            rows, cols = struct.unpack("II", winsize_data)
            print(f"[*] Размер терминала: {rows}x{cols}")
        except Exception as e:
            print(f"[-] Ошибка получения размера: {e}")
            conn.close()
            return
        
        # Создаём PTY
        try:
            pid, fd = pty.fork()
        except Exception as e:
            print(f"[-] pty.fork error: {e}")
            conn.close()
            return
        
        if pid == 0:
            # Дочерний процесс
            shell = os.environ.get('SHELL', '/bin/bash')
            # Для macOS
            if not os.path.exists(shell):
                shell = '/bin/zsh' if os.path.exists('/bin/zsh') else '/bin/bash'
            os.execvp(shell, [shell, '-i'])
            sys.exit(1)
        else:
            # Родительский процесс
            self.set_winsize(fd, rows, cols)
            
            try:
                while True:
                    rlist, _, _ = select.select([conn, fd], [], [])
                    if conn in rlist:
                        data = conn.recv(1024)
                        if not data:
                            print("[*] Соединение закрыто клиентом")
                            break
                        os.write(fd, data)
                    if fd in rlist:
                        data = os.read(fd, 1024)
                        if not data:
                            print("[*] PTY закрыт")
                            break
                        conn.sendall(data)
            except (ConnectionResetError, BrokenPipeError):
                print("[*] Соединение разорвано")
            except Exception as e:
                print(f"[-] Ошибка: {e}")
            finally:
                try:
                    os.close(fd)
                    os.kill(pid, signal.SIGTERM)
                except:
                    pass
                conn.close()
                print(f"[-] Отключение от {addr}")
    
    def start(self):
        """Запускает сервер"""
        # Запускаем поток для announce
        announce_thread = threading.Thread(target=self.announce_presence, daemon=True)
        announce_thread.start()
        
        # Основной TCP сервер
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"[*] Сервер запущен на {self.host}:{self.port}")
        print(f"[*] Announce порт: {self.announce_port}")
        print(f"[*] Имя сервера: {self.server_name}")
        
        try:
            while self.running:
                conn, addr = server.accept()
                # Обрабатываем каждое подключение в отдельном потоке
                client_thread = threading.Thread(
                    target=self.handle_connection, 
                    args=(conn, addr),
                    daemon=True
                )
                client_thread.start()
        except KeyboardInterrupt:
            print("\n[!] Сервер остановлен")
        finally:
            self.running = False
            server.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='PTY Server')
    parser.add_argument('port', type=int, nargs='?', default=8080, help='Port to listen on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--announce-port', type=int, default=8888, help='UDP announce port')
    
    args = parser.parse_args()
    
    server = PTYServer(
        host=args.host,
        port=args.port,
        announce_port=args.announce_port
    )
    server.start()
