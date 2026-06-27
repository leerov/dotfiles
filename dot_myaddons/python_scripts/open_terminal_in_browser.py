#!/usr/bin/env python3
"""
Скрипт, который устанавливает pyxtermjs (если не установлен),
запускает терминал с /bin/zsh через pyxtermjs с шрифтом Hack
и через 2 секунды открывает браузер по адресу http://127.0.0.1:5000.
"""

import subprocess
import sys
import time
import webbrowser
import threading


def open_browser():
    """Открывает браузер через 2 секунды после запуска."""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')


def main():
    # Проверяем, установлен ли pyxtermjs
    try:
        subprocess.run([sys.executable, '-m', 'pyxtermjs', '--help'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        installed = True
    except subprocess.CalledProcessError:
        installed = False

    if not installed:
        print("pyxtermjs не найден, устанавливаю...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyxtermjs'])
        except subprocess.CalledProcessError as e:
            print(f"Ошибка установки: {e}")
            sys.exit(1)
        print("Установка завершена.")
    else:
        print("pyxtermjs уже установлен.")

    # Запускаем поток, который откроет браузер через 2 секунды
    threading.Thread(target=open_browser, daemon=True).start()

    # Запускаем сервер pyxtermjs с нужным шрифтом
    print("Запуск pyxtermjs... Остановите сервер с помощью Ctrl+C.")
    try:
        subprocess.run([
            sys.executable, '-m', 'pyxtermjs',
            '--command', '/bin/zsh',
            '--font-family', 'Hack'
        ], check=True)
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
        sys.exit(0)


if __name__ == "__main__":
    main()
