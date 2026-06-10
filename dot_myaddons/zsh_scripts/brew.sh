#!/bin/bash
# lib/brew-functions.sh - Функции для управления Homebrew

USER_NAME=$(whoami)
GOINFRE_PATH="/opt/goinfre/$USER_NAME"
BREW_PATH="$GOINFRE_PATH/homebrew"

# Функция активации Homebrew
function brewActivate {
    if [ -d "$BREW_PATH" ]; then
        # 1. Активируем Homebrew
        eval "$("$BREW_PATH/bin/brew" shellenv)"
        
        # 2. Настраиваем пути для Cask
        export HOMEBREW_CASK_OPTS="--appdir=$GOINFRE_PATH/Applications --fontdir=$GOINFRE_PATH/Library/Fonts"
        
        # 3. Настраиваем кеш в goinfre
        export HOMEBREW_CACHE="$BREW_PATH/cache"
        
        # 4. Оптимизации для 42
        export HOMEBREW_NO_ANALYTICS=1
        export HOMEBREW_NO_AUTO_UPDATE=1
        
        # 5. Создаем необходимые директории
        mkdir -p "$GOINFRE_PATH/Applications" 2>/dev/null
        mkdir -p "$GOINFRE_PATH/Library/Fonts" 2>/dev/null
        mkdir -p "$HOMEBREW_CACHE" 2>/dev/null
        
        # 6. Создаем симлинки для совместимости
        if [ ! -L ~/Applications ] && [ ! -d ~/Applications ]; then
            ln -sf "$GOINFRE_PATH/Applications" ~/Applications 2>/dev/null
        fi
        
        if [ ! -L ~/Library/Fonts ] && [ ! -d ~/Library/Fonts ]; then
            ln -sf "$GOINFRE_PATH/Library/Fonts" ~/Library/Fonts 2>/dev/null
        fi
        
        # 7. Исправляем права для zsh автодополнения
        chmod -R go-w "$(brew --prefix)/share/zsh" 2>/dev/null || true
        
        echo "✅ Homebrew активирован"
        echo "📦 Cask приложения: $GOINFRE_PATH/Applications"
        echo "🗄️  Кеш brew: $HOMEBREW_CACHE"
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
    cd "$GOINFRE_PATH"
    git clone https://github.com/Homebrew/brew homebrew
    eval "$("$BREW_PATH/bin/brew" shellenv)"
    brew update --force --quiet
    chmod -R go-w "$(brew --prefix)/share/zsh"
    brew install lcov
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
    cd "$GOINFRE_PATH"
    
    # Оптимальный вариант: неглубокое клонирование
    git clone --depth=1 https://github.com/Homebrew/brew homebrew
    
    eval "$("$BREW_PATH/bin/brew" shellenv)"
    brew update --force --quiet
    chmod -R go-w "$(brew --prefix)/share/zsh"
    
    # Тестируем функциональность
    if brew --version > /dev/null 2>&1; then
        echo "✓ Homebrew успешно установлен и готов к работе"
        echo "✓ Доступны: brew install, brew search, brew update и другие команды"
    else
        echo "❌ Что-то пошло не так"
        return 1
    fi
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
