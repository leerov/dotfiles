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

# ---- Генерация алиасов (функций) из order.txt ----
$orderFile = "$env:PYTHON_SCRIPTS\order.txt"
if (Test-Path $orderFile) {
    Get-Content $orderFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $parts = $line -split '\s+'
            if ($parts.Count -ge 2) {
                $aliasName = $parts[0]
                $scriptFile = $parts[1]
                $scriptPath = "$env:PYTHON_SCRIPTS\$scriptFile"
                Set-Item -Path "function:\$aliasName" -Value "python `"$scriptPath`" `$args"
            }
        }
    }
}

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
