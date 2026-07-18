# ============================================================
#  Профиль PowerShell, аналогичный .zshrc из dotfiles leerov
# ============================================================

# ---- Пути ----
$env:MYADDONS = "$HOME\.myaddons"
$env:PYTHON_SCRIPTS = "$env:MYADDONS\python_scripts"

# ---- Добавляем скрипты в PATH (для удобного вызова) ----
if ($env:PATH -notlike "*$env:PYTHON_SCRIPTS*") {
    $env:PATH += ";$env:PYTHON_SCRIPTS"
}

# ---- Алиасы (функции) для основных скриптов ----
function fj { python "$env:PYTHON_SCRIPTS\fj.py" $args }
function jf { python "$env:PYTHON_SCRIPTS\jf.py" $args }
function clean { python "$env:PYTHON_SCRIPTS\clean.py" $args }
function client { python "$env:PYTHON_SCRIPTS\client.py" $args }
function server { python "$env:PYTHON_SCRIPTS\server.py" $args }
function sc { python "$env:PYTHON_SCRIPTS\showcopy.py" $args }

# Открытие браузерных инструментов
function bt { python "$env:PYTHON_SCRIPTS\open_terminal_browser.py" $args }
function bc { python "$env:PYTHON_SCRIPTS\open_vscode_dev.py" $args }
function bcs { python "$env:PYTHON_SCRIPTS\open_code_server.py" $args }

# ---- Дополнительные алиасы из .zshrc ----
function v { nvim $args }
function vim { nvim $args }
function nano { nvim $args }
function code { nvim $args }   # если хотите, чтобы code открывал Neovim

# ls с цветами (используем встроенную Get-ChildItem с настройками)
function ls { Get-ChildItem -Color $args }
function ll { Get-ChildItem -Color -Long $args }
function la { Get-ChildItem -Color -Force $args }

# Перезагрузка профиля
function r { . $PROFILE }

# Редактирование профиля (открываем в Neovim)
function edit-profile { nvim $PROFILE }

# ---- Настройка приглашения (prompt) ----
# Можно использовать starship, если установлен
if (Get-Command starship -ErrorAction SilentlyContinue) {
    function prompt { starship prompt }
} else {
    # Простой вариант: показывает текущую папку
    function prompt { "PS $($executionContext.SessionState.Path.CurrentLocation)> " }
}

# ---- Дополнительные настройки окружения ----
# Включаем автоматическое завершение для Python
Set-PSReadLineOption -EditMode Emacs
Set-PSReadLineOption -PredictionSource History

# ---- Сообщение о загрузке (опционально) ----
Write-Host "🔧 Профиль PowerShell загружен (аналогичен .zshrc)" -ForegroundColor Green
