alias dockle='docker run --rm -v /var/run/docker.sock:/var/run/docker.sock goodwithtech/dockle'
alias v="nvim"
alias vim="nvim"
alias nano="nvim"
alias code="nvim"
alias ls='ls -G'
alias ll="ls -laG"
alias la="ls -aG"
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias man='man -P "less -R"'
alias r='source ~/.zshrc'
alias py='python3'
alias python='python'
alias pip='pip3'

if ! command -v pbcopy &>/dev/null; then
    alias pbcopy='xclip -selection clipboard'
    alias pbpaste='xclip -selection clipboard -o'
fi
