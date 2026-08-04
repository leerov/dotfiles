alias dockle='docker run --rm -v /var/run/docker.sock:/var/run/docker.sock goodwithtech/dockle'
if command -v nvim &>/dev/null; then
alias v="nvim"
alias vim="nvim"
alias nano="nvim"
alias code="nvim"
elif command -v vim &>/dev/null; then
alias v="vim"
alias nano="vim"
alias code="vim"
fi
alias ls='ls -G'
alias ll="ls -laG"
alias la="ls -aG"
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias man='man -P "less -R"'
alias r='source ~/.zshrc'
# Git aliases
alias g='git'
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gd='git diff'
alias gb='git branch'
alias gco='git checkout'
alias gm='git merge'
alias gr='git remote'
alias gf='git fetch'
alias gg='git log --oneline --graph --decorate'
alias gcm='git commit -m'
alias py='python3'
alias python='python'
alias pip='pip3'

if ! command -v pbcopy &>/dev/null; then
    alias pbcopy='xclip -selection clipboard'
    alias pbpaste='xclip -selection clipboard -o'
fi
