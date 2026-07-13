# Мои dotfiles

Управляются с помощью [chezmoi](https://www.chezmoi.io/).

## Быстрая установка

Выполните одну команду:

```bash
sh -c "$(curl -fsLS https://chezmoi.io/get)" && chezmoi init --apply https://github.com/leerov/dotfiles.git && python3 ~/.myaddons/python_scripts/install.py
```

После завершения установки перезапустите оболочку.

---

Подробная документация доступна в [README.full.md](README.full.md) (если есть) или в репозитории.