#!/bin/bash

if [ -d /opt/goinfre ] && [ -w /opt/goinfre ]; then
    USER_NAME=$(whoami)
    GOINFRE_PATH="/opt/goinfre/$USER_NAME"
    BREW_PATH="$GOINFRE_PATH/homebrew"
    export HOMEBREW_CASK_OPTS="--appdir=$GOINFRE_PATH/Applications --fontdir=$GOINFRE_PATH/Library/Fonts"
    export HOMEBREW_CACHE="$BREW_PATH/cache"
else
    if [[ $(uname) == "Darwin" ]]; then
        if [[ $(uname -m) == "arm64" ]]; then
            BREW_PATH="/opt/homebrew"
        else
            BREW_PATH="/usr/local"
        fi
    else
        BREW_PATH="/home/linuxbrew/.linuxbrew"
    fi
    export HOMEBREW_CASK_OPTS=""
    export HOMEBREW_CACHE=""
fi

export HOMEBREW_NO_AUTO_UPDATE=1

brewActivate() {
    if [ -d "$BREW_PATH" ]; then
        eval "$("$BREW_PATH/bin/brew" shellenv)"
        if [ -n "$GOINFRE_PATH" ]; then
            mkdir -p "$GOINFRE_PATH/Applications" 2>/dev/null
            mkdir -p "$GOINFRE_PATH/Library/Fonts" 2>/dev/null
            mkdir -p "$HOMEBREW_CACHE" 2>/dev/null
            if [ ! -L ~/Applications ] && [ ! -d ~/Applications ]; then
                ln -sf "$GOINFRE_PATH/Applications" ~/Applications 2>/dev/null
            fi
            if [ ! -L ~/Library/Fonts ] && [ ! -d ~/Library/Fonts ]; then
                ln -sf "$GOINFRE_PATH/Library/Fonts" ~/Library/Fonts 2>/dev/null
            fi
        fi
        chmod -R go-w "$(brew --prefix)/share/zsh" 2>/dev/null || true
        return 0
    else
        return 1
    fi
}

brewSetup() {
    if [ -d "$BREW_PATH" ]; then
        eval "$("$BREW_PATH/bin/brew" shellenv)"
        chmod -R go-w "$(brew --prefix)/share/zsh" 2>/dev/null
        return 0
    fi

    mkdir -p "$(dirname "$BREW_PATH")"
    cd "$(dirname "$BREW_PATH")" || exit 1
    git clone --depth=1 https://github.com/Homebrew/brew "$(basename "$BREW_PATH")"
    eval "$("$BREW_PATH/bin/brew" shellenv)"
    brew update --force --quiet
    chmod -R go-w "$(brew --prefix)/share/zsh"

    if brew --version > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

if [[ ":$PATH:" != *":$BREW_PATH/bin:"* ]] && [ -d "$BREW_PATH/bin" ]; then
    export PATH="$BREW_PATH/bin:$PATH"
fi

(nohup brewSetup > /dev/null 2>&1 &)

if [ -d "$BREW_PATH" ]; then
    brewActivate
fi
