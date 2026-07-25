#!/bin/bash
# repeat.sh - Функция для повторного выполнения команды по нажатию Enter

repeat_on_enter() {
    local cmd="$*"
    while read -r; do
        eval "$cmd"
    done
}

# Алиас для быстрого доступа
alias repeat='repeat_on_enter'