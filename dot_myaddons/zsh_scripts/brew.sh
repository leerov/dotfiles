#!/usr/bin/env bash
# lib/brew-functions.sh - Функции для управления Homebrew

USER_NAME=$(whoami)
if [ -d "/opt/goinfre/$USER_NAME" ]; then
    GOINFRE_PATH="/opt/goinfre/$USER_NAME"
    BREW_PATH="$GOINFRE_PATH/homebrew"

    # Глобальные настройки для goinfre (Ecole 42)
    export HOMEBREW_CASK_OPTS="--appdir=$GOINFRE_PATH/Applications --fontdir=$GOINFRE_PATH/Library/Fonts"
    export HOMEBREW_CACHE="$BREW_PATH/cache"
    export HOMEBREW_NO_ANALYTICS=1
    export HOMEBREW_NO_AUTO_UPDATE=1

    # Создаем необходимые директории сразу при загрузке скрипта
    mkdir -p "$GOINFRE_PATH/Applications" 2>/dev/null
    mkdir -p "$GOINFRE_PATH/Library/Fonts" 2>/dev/null
    mkdir -p "$HOMEBREW_CACHE" 2>/dev/null

    # Создаем симлинки для совместимости
    if [ ! -L ~/Applications ] && [ ! -d ~/Applications ]; then
        ln -sf "$GOINFRE_PATH/Applications" ~/Applications 2>/dev/null
    fi
    if [ ! -L ~/Library/Fonts ] && [ ! -d ~/Library/Fonts ]; then
        ln -sf "$GOINFRE_PATH/Library/Fonts" ~/Library/Fonts 2>/dev/null
    fi
else
    if [[ "$(uname -m)" == "arm64" ]]; then
        BREW_PATH="/opt/homebrew"
    else
        BREW_PATH="/usr/local"
    fi
    export HOMEBREW_NO_ANALYTICS=1
    export HOMEBREW_NO_AUTO_UPDATE=1
fi

# Функция активации Homebrew
function brewActivate {
    if [ -d "$BREW_PATH" ]; then
        eval "$("$BREW_PATH/bin/brew" shellenv)"
        chmod -R go-w "$(brew --prefix)/share/zsh" 2>/dev/null || true
        echo "✅ Homebrew активирован"
        if [ -n "$GOINFRE_PATH" ]; then
            echo "📦 Cask приложения: $GOINFRE_PATH/Applications"
            echo "🗄️  Кеш brew: $HOMEBREW_CACHE"
        fi
        return 0
    else
        echo "❌ Homebrew не найден по пути: $BREW_PATH"
        echo "💡 Используйте команду: brew-setup"
        return 1
    fi
}

# Функция установки Homebrew
function brewInstall {
    if [ -d "$BREW_PATH" ]; then
        echo "Homebrew уже установлен"
        brewActivate
        return 0
    fi
    
    echo "Установка Homebrew..."
    local START_DIR="$(pwd)"
    if [ -n "$GOINFRE_PATH" ]; then
        cd "$GOINFRE_PATH" || return 1
    else
        cd "/tmp" || return 1
    fi
    git clone https://github.com/Homebrew/brew homebrew
    eval "$("$BREW_PATH/bin/brew" shellenv)"
    # Используем command brew, чтобы обойти функцию-обёртку
    command brew update --force --quiet
    chmod -R go-w "$(brew --prefix)/share/zsh"
    command brew install lcov
    cd "$START_DIR"
    brewActivate
    echo "Homebrew успешно установлен"
}

# Функция удаления Homebrew
function brewUninstall {
    if [ -d "$BREW_PATH" ]; then
        echo "Удаление Homebrew..."
        rm -rf "$BREW_PATH"
        echo "Homebrew удален"
    else
        echo "Homebrew не установлен в $BREW_PATH"
    fi
}

# Основная функция установки/активации
function brewSetup {
    if [ -d "$BREW_PATH" ]; then
        eval "$("$BREW_PATH/bin/brew" shellenv)"
        chmod -R go-w "$(brew --prefix)/share/zsh"
        echo "✓ Homebrew активирован"
        return 0
    fi
    
    echo "Быстрая установка Homebrew..."
    local START_DIR="$(pwd)"
    if [ -n "$GOINFRE_PATH" ]; then
        cd "$GOINFRE_PATH" || return 1
    else
        cd "/tmp" || return 1
    fi
    # Оптимальный вариант: неглубокое клонирование
    git clone --depth=1 https://github.com/Homebrew/brew homebrew
    
    eval "$("$BREW_PATH/bin/brew" shellenv)"
    # Используем command brew, чтобы обойти функцию-обёртку
    command brew update --force --quiet
    chmod -R go-w "$(brew --prefix)/share/zsh"
    
    # Тестируем функциональность
    if command brew --version > /dev/null 2>&1; then
        brewActivate
        echo "✓ Homebrew успешно установлен и готов к работе"
        echo "✓ Доступны: brew install, brew search, brew update и другие команды"
    else
        echo "❌ Что-то пошло не так"
        cd "$START_DIR"
        return 1
    fi
    cd "$START_DIR"
}

# Функция переустановки
function brewReinstall {
    brewUninstall
    brewInstall
}

# Добавляем brew в PATH если он есть
if [[ ":$PATH:" != *":$BREW_PATH/bin:"* ]] && [ -d "$BREW_PATH/bin" ]; then
    export PATH="$BREW_PATH/bin:$PATH"
fi

# Обертка для автоматической установки при вызове brew
brew() {
    if [ ! -f "$BREW_PATH/bin/brew" ]; then
        echo "🍺 Homebrew не установлен. Автоматически запускаю brewSetup..."
        brewSetup
    fi
    if [[ ":$PATH:" != *":$BREW_PATH/bin:"* ]]; then
        eval "$("$BREW_PATH/bin/brew" shellenv)" 2>/dev/null
    fi
    command brew "$@"
}
