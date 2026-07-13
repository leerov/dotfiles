# leerov dotfiles

Управляются с помощью [chezmoi](https://www.chezmoi.io/).

## Быстрая установка

Выполните одну команду:

```bash
cd && sh -c "$(curl -fsLS https://chezmoi.io/get)" && ~/bin/chezmoi init --apply https://github.com/leerov/dotfiles.git && python3 ~/.myaddons/python_scripts/install.py; source ~/.zshrc
```

