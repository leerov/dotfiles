#!/usr/bin/env python3
import socket
import sys
import os
import tty
import termios
import select
import struct
import signal
import threading
import time
import json
from datetime import datetime

class ServerDiscovery:
    def __init__(self, announce_port=8888):
        self.announce_port = announce_port
        self.servers = {}  # ip -> server_info
        self.running = True
        
    def listen_for_servers(self):
        """Слушает UDP broadcast от серверов"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.announce_port))
        sock.settimeout(1)
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                try:
                    server_info = json.loads(data.decode())
                    server_info['last_seen'] = time.time()
                    server_info['address'] = addr[0]
                    
                    # Пытаемся получить hostname, если его нет
                    if 'name' not in server_info:
                        try:
                            server_info['name'] = socket.gethostbyaddr(addr[0])[0]
                        except:
                            server_info['name'] = addr[0]
                    
                    self.servers[addr[0]] = server_info
                except:
                    pass
            except socket.timeout:
                # Удаляем старые записи (не обновлялись > 15 сек)
                current_time = time.time()
                expired = [ip for ip, info in self.servers.items() 
                          if current_time - info.get('last_seen', 0) > 15]
                for ip in expired:
                    del self.servers[ip]
            except Exception as e:
                print(f"[-] Ошибка discovery: {e}")
        
        sock.close()
    
    def print_servers(self):
        """Выводит список обнаруженных серверов"""
        if not self.servers:
            print("\n[!] Серверы не найдены")
            return
        
        print("\n" + "="*80)
        print(f"{'#':<3} {'Имя сервера':<30} {'IP адрес':<15} {'Порт':<8} {'Последний раз':<12}")
        print("-"*80)
        
        for idx, (ip, info) in enumerate(self.servers.items(), 1):
            name = info.get('name', 'Unknown')
            if len(name) > 30:
                name = name[:27] + '...'
                
            last_seen = datetime.fromtimestamp(info.get('last_seen', 0))
            time_str = last_seen.strftime("%H:%M:%S")
            
            print(f"{idx:<3} {name:<30} {ip:<15} "
                  f"{info.get('port', 8080):<8} {time_str:<12}")
        print("="*80)
    
    def stop(self):
        self.running = False

def get_terminal_size():
    """Возвращает (rows, cols) текущего терминала"""
    import fcntl
    try:
        h, w, _, _ = struct.unpack('HHHH',
            fcntl.ioctl(0, termios.TIOCGWINSZ,
                        struct.pack('HHHH', 0, 0, 0, 0)))
        return h, w
    except:
        return 24, 80

def restore_term(orig):
    """Восстанавливает исходные настройки терминала"""
    if orig is not None:
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, orig)
        except:
            pass

def connect_to_server(host, port):
    """Подключается к серверу и запускает сессию"""
    orig_termios = None
    try:
        orig_termios = termios.tcgetattr(sys.stdin.fileno())
    except:
        pass
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Пытаемся получить hostname
        try:
            hostname = socket.gethostbyaddr(host)[0]
            print(f"[*] Подключение к {hostname} ({host}:{port})...")
        except:
            print(f"[*] Подключение к {host}:{port}...")
        
        sock.connect((host, port))
    except Exception as e:
        print(f"[-] Ошибка подключения: {e}")
        return False
    
    # Отправляем размер терминала
    rows, cols = get_terminal_size()
    print(f"[+] Подключено! Размер терминала: {rows}x{cols}")
    sock.sendall(struct.pack("II", rows, cols))
    
    # Переводим терминал в raw-режим
    try:
        tty.setraw(sys.stdin.fileno())
    except:
        pass
    
    # Обработчик изменения размера окна
    def sigwinch_handler(signum, frame):
        rows, cols = get_terminal_size()
        print(f"\r\n[ Размер терминала изменился на {rows}x{cols} ]\r\n", end='', flush=True)
    
    signal.signal(signal.SIGWINCH, sigwinch_handler)
    
    try:
        while True:
            rlist, _, _ = select.select([sys.stdin.fileno(), sock], [], [])
            if sys.stdin.fileno() in rlist:
                try:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if not data:
                        break
                    sock.sendall(data)
                except:
                    break
            if sock in rlist:
                try:
                    data = sock.recv(1024)
                    if not data:
                        print("\r\n[ Соединение закрыто сервером ]\r\n")
                        break
                    sys.stdout.buffer.write(data)
                    sys.stdout.buffer.flush()
                except:
                    break
    except (ConnectionResetError, BrokenPipeError):
        print("\r\n[ Соединение разорвано ]\r\n")
    except KeyboardInterrupt:
        pass
    finally:
        restore_term(orig_termios)
        sock.close()
    
    return True

def print_header():
    """Выводит заголовок программы"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              PTY Клиент с обнаружением серверов           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

def main():
    discovery = ServerDiscovery()
    listener_thread = threading.Thread(target=discovery.listen_for_servers, daemon=True)
    listener_thread.start()
    
    try:
        while True:
            print_header()
            discovery.print_servers()
            
            print("\nДействия:")
            print("  ├─ 1..N - Подключиться к серверу по номеру")
            print("  ├─ m - Ввести IP вручную")
            print("  ├─ r - Обновить список")
            print("  └─ q - Выход")
            
            try:
                choice = input("\nВыбор: ").strip().lower()
            except KeyboardInterrupt:
                break
            
            if choice == 'q':
                break
            elif choice == 'm':
                print("\n--- Ручной ввод ---")
                host = input("Введите IP или hostname: ").strip()
                if not host:
                    continue
                    
                port_input = input("Введите порт (Enter для 8080): ").strip()
                port = int(port_input) if port_input else 8080
                
                connect_to_server(host, port)
                input("\nНажмите Enter для продолжения...")
            elif choice == 'r':
                continue
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(discovery.servers):
                    servers_list = list(discovery.servers.items())
                    ip, info = servers_list[idx]
                    port = info.get('port', 8080)
                    name = info.get('name', ip)
                    
                    print(f"\n--- Подключение к {name} ({ip}:{port}) ---")
                    connect_to_server(ip, port)
                    input("\nНажмите Enter для продолжения...")
            
    except KeyboardInterrupt:
        print("\n[!] Выход")
    finally:
        discovery.stop()

if __name__ == "__main__":
    main()
