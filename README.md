# leerov dotfiles

Управляются с помощью [chezmoi](https://www.chezmoi.io/).

## Быстрая установка

Выполните одну команду:

```bash
cd && sh -c "$(curl -fsLS https://chezmoi.io/get)" && ~/bin/chezmoi init --apply https://github.com/leerov/dotfiles.git && python3 ~/.myaddons/python_scripts/install.py && source ~/.zshrc
```

После завершения установки перезапустите оболочку (команда выше уже делает это).

## Установка (подробно)

```bash
chezmoi init --apply https://github.com/leerov/dotfiles.git
```

Или, если репозиторий уже склонирован:

```bash
chezmoi apply
```

## Структура проекта

- **`.chezmoiignore`** – файлы, игнорируемые chezmoi.
- **`dot_config/`** – конфигурации приложений:
  - `alacritty/` – терминал Alacritty.
  - `kitty/` – терминал Kitty.
  - `nvim/` – конфигурация Neovim (использует lazy.nvim).
  - `starship.toml` – конфигурация Starship prompt.
  - `empty_colors.toml` – общая цветовая палитра для терминалов.
- **`dot_myaddons/`** – пользовательские скрипты и алиасы:
  - `python_scripts/` – утилиты на Python:
    - `clean.py` – интерактивная очистка системы (TUI).
    - `client.py` / `server.py` – PTY-клиент и сервер для удалённых сессий.
    - `fj.py` – сборка проекта и отправка в буфер обмена для ИИ.
    - `jf.py` – применение AP-патчей из буфера обмена с копированием вывода.
    - `open_*.py` – открытие браузерных инструментов (code-server, vscode.dev, терминал в браузере).
    - `order.txt` – файл для генерации алиасов (см. `python_aliases.sh`).
    - `install.py` – автоматическая установка всех необходимых инструментов.
  - `zsh_scripts/` – скрипты и настройки для Zsh:
    - `alias.sh`, `colors.sh`, `path.sh` – базовые алиасы, цвета, пути.
    - `brew.sh` – управление Homebrew (установка/активация).
    - `chezmoi_edit.sh` – алиас `ce` для редактирования и применения изменений.
    - `python_aliases.sh` – генерация алиасов из `order.txt`.
    - `showcopy.sh` – утилита `sc` для копирования содержимого текстовых файлов.
    - `sync_apps.sh` – синхронизация приложений из `/opt/goinfre` в `~/Applications`.
    - `translit.sh` – транслитерация с русского на английский в командной строке.
    - `unlock.sh` – снятие quarantine и подпись приложений.
- **`dot_oh-my-zsh/`** – темы для Oh My Zsh.
- **`dot_tmux.conf`** – конфигурация tmux.
- **`dot_zshrc`** – основной `.zshrc`.
- **`dot_zshrc_theme`** – настройки отображения темы Zsh.

## Использование

После применения chezmoi все файлы будут скопированы в домашнюю директорию с удалением префикса `dot_`.

### Редактирование и применение изменений

Для редактирования файла конфигурации (например, `.zshrc`):

```bash
chezmoi edit ~/.zshrc
```

После сохранения изменений примените их:

```bash
chezmoi apply
```

В этом проекте доступен алиас `ce` (chezmoi_edit), который автоматически выполняет `chezmoi apply` после редактирования:

```bash
ce ~/.zshrc
```

### Алиасы и команды

- `v`, `vim`, `nano`, `code` – открывают Neovim.
- `ls`, `ll`, `la` – раскрашенные версии `ls`.
- `r` – перезагрузка `.zshrc`.
- `py`, `python`, `pip` – ссылки на Python 3.
- `sc` – копирование содержимого текстовых файлов в буфер обмена (с номерами строк или без).
- `jf` – применение AP-патча из буфера обмена (вывод также копируется в буфер).
- `fj` – сборка проекта для ИИ (структура + код + спецификация AP).
- `c` – запуск `clean.py` (очистка системы).
- `bt` – открывает терминал в браузере.
- `bc` – открывает vscode.dev.
- `server` / `client` – PTY-сервер и клиент.

## Neovim

Конфигурация Neovim находится в `dot_config/nvim/`. Используется менеджер плагинов **lazy.nvim**. Основные возможности:

- Тема: Gruvbox Material (hard background).
- Файловый менеджер: nvim-tree (привязан к `<leader>e`).
- Поиск: Telescope (`<leader>f` – поиск в файле, `<leader>sf` – grep по проекту, `<C-p>` – поиск файлов).
- Автодополнение: nvim-cmp + LSP (lua_ls, pyright).
- Работа с Git: gitsigns (`]c`/`[c` для переходов по ханкам).
- Автосохранение, автопары, подсветка синтаксиса Treesitter.
- Клавиша `<F12>` копирует весь файл в буфер обмена.

## Tmux

Конфигурация `dot_tmux.conf` включает:

- Плагины: tpm, tmux-gruvbox.
- Восстановление сессий через continuum.
- Мышь включена.

## Особенности для окружения 42 (Ecole 42)

Проект адаптирован под работу в среде 42:

- Homebrew устанавливается в `/opt/goinfre/$USER/homebrew`.
- Приложения из `/opt/goinfre/*/Applications` синхронизируются в `~/Applications` (скрипт `sync_apps.sh`).
- Пути и переменные настроены для goinfre.

## Контакты

Автор: [leerov](https://github.com/leerov)

---

Если у вас возникли вопросы или предложения, создавайте issue или pull request в репозитории.


здесь был леня
