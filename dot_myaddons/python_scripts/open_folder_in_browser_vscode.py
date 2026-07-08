#!/usr/bin/env python3
"""
Скрипт для открытия текущей папки в браузерной версии VS Code через code-server.
Это альтернатива vscode.dev для локальных папок.
"""

import subprocess
import sys
import time
import webbrowser
import shutil
import os
import threading


def open_browser_after_delay(delay=3):
    """Открывает браузер через заданную задержку."""
    time.sleep(delay)
    webbrowser.open('http://127.0.0.1:8080')


def install_code_server():
    """Устанавливает code-server через npm или скачивает бинарник."""
    if shutil.which('npm') is None:
        print("npm не найден. Установите Node.js и npm, затем выполните:")
        print("  npm install -g code-server")
        return False

    print("Устанавливаю code-server (глобально через npm)...")
    try:
        subprocess.check_call(['npm', 'install', '-g', 'code-server'])
        print("Установка завершена.")
        return True
    except subprocess.CalledProcessError:
        print("Ошибка установки. Установите code-server вручную: https://coder.com/docs/code-server/install")
        return False


def main():
    # Проверяем наличие code-server
    if shutil.which('code-server') is None:
        print("code-server не найден. Попытка установки...")
        if not install_code_server():
            sys.exit(1)

    # Проверяем, что порт 8080 свободен (опционально)
    # Запускаем браузер через пару секунд после старта сервера
    threading.Thread(target=open_browser_after_delay, daemon=True).start()

    # Запускаем code-server в текущей папке
    print(f"Запуск code-server для папки '{os.getcwd()}'")
    print("Сервер доступен по адресу http://127.0.0.1:8080")
    print("Остановите сервер нажатием Ctrl+C")
    try:
        subprocess.run(['code-server', '--auth', 'none', '--port', '8080', '.'], check=True)
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
