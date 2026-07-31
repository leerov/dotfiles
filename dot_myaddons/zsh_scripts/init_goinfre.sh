#!/usr/bin/env bash
# init_goinfre.sh - Инициализация структуры goinfre при старте терминала

USER_NAME=$(whoami)
GOINFRE_PATH="/opt/goinfre/$USER_NAME"

if [ -d "$GOINFRE_PATH" ]; then
    # Создаем папку private, если её нет
    if [ ! -d "$GOINFRE_PATH/private" ]; then
        mkdir -p "$GOINFRE_PATH/private" 2>/dev/null
    fi

    # Устанавливаем права только для владельца (rwx------)
    chmod 700 "$GOINFRE_PATH/private" 2>/dev/null

    # Гарантируем, что корневая папка пользователя в goinfre доступна для чтения и выполнения всем
    # Это необходимо, чтобы путь ~/goinfre/private/bin мог быть прочитан системой
    chmod 755 "$GOINFRE_PATH" 2>/dev/null
fi