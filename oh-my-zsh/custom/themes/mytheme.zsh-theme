# ~/.local/share/chezmoi/dot_oh-my-zsh/custom/themes/dot_custom.zsh-theme.tmpl
#!/usr/bin/env zsh
# Custom theme with colors from colors.toml

setopt prompt_subst
autoload -U colors && colors
autoload -U add-zsh-hook

# ======================
# Функция для чтения цветов из colors.toml
# ======================
load_colors_from_toml() {
    local colors_file="$HOME/.config/colors.toml"
    
    if [[ -f "$colors_file" ]]; then
        # Парсим normal секцию
        local normal_black=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'black' | sed 's/.*= "\(.*\)"/\1/')
        local normal_red=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'red' | sed 's/.*= "\(.*\)"/\1/')
        local normal_green=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'green' | sed 's/.*= "\(.*\)"/\1/')
        local normal_yellow=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'yellow' | sed 's/.*= "\(.*\)"/\1/')
        local normal_blue=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'blue' | sed 's/.*= "\(.*\)"/\1/')
        local normal_magenta=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'magenta' | sed 's/.*= "\(.*\)"/\1/')
        local normal_cyan=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'cyan' | sed 's/.*= "\(.*\)"/\1/')
        local normal_white=$(grep -A1 '\[colors.normal\]' "$colors_file" | grep 'white' | sed 's/.*= "\(.*\)"/\1/')
        
        # Парсим bright секцию
        local bright_black=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'black' | sed 's/.*= "\(.*\)"/\1/')
        local bright_red=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'red' | sed 's/.*= "\(.*\)"/\1/')
        local bright_green=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'green' | sed 's/.*= "\(.*\)"/\1/')
        local bright_yellow=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'yellow' | sed 's/.*= "\(.*\)"/\1/')
        local bright_blue=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'blue' | sed 's/.*= "\(.*\)"/\1/')
        local bright_magenta=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'magenta' | sed 's/.*= "\(.*\)"/\1/')
        local bright_cyan=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'cyan' | sed 's/.*= "\(.*\)"/\1/')
        local bright_white=$(grep -A1 '\[colors.bright\]' "$colors_file" | grep 'white' | sed 's/.*= "\(.*\)"/\1/')
        
        # Создаем ассоциативный массив цветов
        typeset -gA COLORS
        COLORS=(
            [black]="$normal_black"
            [red]="$normal_red"
            [green]="$normal_green"
            [yellow]="$normal_yellow"
            [blue]="$normal_blue"
            [magenta]="$normal_magenta"
            [cyan]="$normal_cyan"
            [white]="$normal_white"
            [bright_black]="$bright_black"
            [bright_red]="$bright_red"
            [bright_green]="$bright_green"
            [bright_yellow]="$bright_yellow"
            [bright_blue]="$bright_blue"
            [bright_magenta]="$bright_magenta"
            [bright_cyan]="$bright_cyan"
            [bright_white]="$bright_white"
        )
        
        # Конвертируем hex в формат Zsh (если нужно)
        for color in ${(k)COLORS}; do
            if [[ ${COLORS[$color]} =~ ^#[0-9A-Fa-f]{6}$ ]]; then
                # Конвертируем hex в RGB для Zsh (опционально)
                local r=$((16#${COLORS[$color]:1:2}))
                local g=$((16#${COLORS[$color]:3:2}))
                local b=$((16#${COLORS[$color]:5:2}))
                # Zsh может работать с 256 цветами, используем ближайший
                COLORS[$color]=$((16 + (r * 5 / 255) * 36 + (g * 5 / 255) * 6 + (b * 5 / 255)))
            fi
        done
    fi
}

# Загружаем цвета
load_colors_from_toml

# ======================
# Настройки темы (можно переопределить через переменные окружения)
# ======================
local user_color="${CUSTOM_THEME_USER_COLOR:-green}"
local host_color="${CUSTOM_THEME_HOST_COLOR:-blue}"
local dir_color="${CUSTOM_THEME_DIR_COLOR:-cyan}"
local git_branch_color="${CUSTOM_THEME_GIT_BRANCH_COLOR:-magenta}"
local git_status_color="${CUSTOM_THEME_GIT_STATUS_COLOR:-red}"
local prompt_symbol="${CUSTOM_THEME_PROMPT_SYMBOL:-❯}"
local prompt_symbol_color="${CUSTOM_THEME_PROMPT_SYMBOL_COLOR:-yellow}"
local show_time="${CUSTOM_THEME_SHOW_TIME:-true}"
local show_git="${CUSTOM_THEME_SHOW_GIT:-true}"
local show_path_short="${CUSTOM_THEME_SHOW_PATH_SHORT:-false}"

# ======================
# Git функции
# ======================
git_branch() {
    git symbolic-ref --short HEAD 2>/dev/null
}

git_status() {
    local branch=$(git_branch)
    [[ -z "$branch" ]] && return
    
    local status=$(git status --porcelain 2>/dev/null)
    if [[ -n "$status" ]]; then
        echo "%F{$git_status_color}●%f"
    else
        echo "%F{green}✓%f"
    fi
}

git_info() {
    [[ "$show_git" != "true" ]] && return
    local branch=$(git_branch)
    [[ -z "$branch" ]] && return
    
    echo " %F{$git_branch_color}($branch)%f $(git_status)"
}

# ======================
# Путь с сокращением
# ======================
get_path() {
    if [[ "$show_path_short" == "true" ]]; then
        # Показываем только последние 2 директории
        echo "%2~"
    else
        echo "%~"
    fi
}

# ======================
# Правая часть (время, код возврата)
# ======================
exit_code() {
    local code=$?
    [[ $code -eq 0 ]] && return
    echo "%F{$git_status_color} ↵${code}%f"
}

right_prompt() {
    local right=""
    
    # Время
    if [[ "$show_time" == "true" ]]; then
        right+="%F{cyan}[%D{%H:%M:%S}]%f"
    fi
    
    # Код возврата
    local code=$(exit_code)
    if [[ -n "$code" ]]; then
        [[ -n "$right" ]] && right+=" "
        right+="$code"
    fi
    
    echo "$right"
}

# ======================
# Хуки для измерения времени выполнения
# ======================
timer=0
preexec() {
    timer=$(date +%s%3N)
}

precmd() {
    local elapsed=0
    if [[ $timer -gt 0 ]]; then
        local now=$(date +%s%3N)
        elapsed=$((now - timer))
        timer=0
    fi
    
    # Показываем время выполнения если > 1 секунды
    if [[ $elapsed -gt 1000 ]]; then
        local seconds=$((elapsed / 1000))
        local milliseconds=$((elapsed % 1000))
        RPROMPT="%F{yellow}⏱ ${seconds}.${milliseconds}s%f $(right_prompt)"
    else
        RPROMPT="$(right_prompt)"
    fi
}

# ======================
# Основной PROMPT (две строки)
# ======================
PROMPT='%F{$user_color}%n%f@%F{$host_color}%m%f:%F{$dir_color}$(get_path)%f$(git_info)
%F{$prompt_symbol_color}$prompt_symbol%f '

# ======================
# Альтернативный PROMPT (одна строка) - раскомментировать если нужно
# ======================
# PROMPT='%F{$user_color}%n%f@%F{$host_color}%m%f:%F{$dir_color}$(get_path)%f$(git_info) %F{$prompt_symbol_color}$prompt_symbol%f '

# ======================
# PS2 для многострочных команд
# ======================
PS2='%F{cyan}→%f '

# ======================
# Информация о виртуальном окружении (если нужно)
# ======================
if type virtualenv_info > /dev/null 2>&1; then
    VIRTUAL_ENV_DISABLE_PROMPT=1
    plugins=(virtualenv)
fi

