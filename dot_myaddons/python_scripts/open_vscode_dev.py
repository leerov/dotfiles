#!/usr/bin/env python3
"""
Открывает заданный URL в браузере.
Использование: python open_url.py [URL]
Если URL не указан, открывается https://vscode.dev
"""

import sys
import webbrowser

def main():
    # Берём первый аргумент командной строки, если он есть
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://vscode.dev'
    
    # Открываем в браузере по умолчанию
    webbrowser.open(url)
    print(f"✅ Открыто: {url}")

if __name__ == "__main__":
    main()
