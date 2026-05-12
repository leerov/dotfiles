autoload -Uz add-zsh-hook
autoload -Uz colors
autoload -Uz zle

colors
zmodload zsh/terminfo

setopt prompt_subst

# ============================================================
# Цвета
# ============================================================

for color in RED GREEN YELLOW BLUE MAGENTA CYAN WHITE BLACK; do
  typeset -g COLOR_BOLD_$color="%{$terminfo[bold]$fg[${(L)color}]%}"
  typeset -g COLOR_LIGHT_$color="%{$fg[${(L)color}]%}"
done

typeset -g COLOR_RESET="%{$reset_color%}"

typeset -g PROMPT_FRAME_COLOR="$COLOR_BOLD_CYAN"
typeset -g PROMPT_BRACKET_COLOR="$COLOR_BOLD_BLACK"
typeset -g PROMPT_PATH_COLOR="$COLOR_BOLD_GREEN"
typeset -g PROMPT_TIME_COLOR="$COLOR_BOLD_YELLOW"
typeset -g PROMPT_INNER_DECOR_COLOR="$COLOR_BOLD_BLUE"
typeset -g PROMPT_GIT_COLOR="$COLOR_LIGHT_BLUE"
typeset -g PROMPT_PS2_COLOR="$COLOR_LIGHT_GREEN"
typeset -g PROMPT_RESET_COLOR="$COLOR_RESET"

# ============================================================
# Git prompt
# ============================================================

ZSH_THEME_GIT_PROMPT_PREFIX=" on %{$fg[green]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_DIRTY=""
ZSH_THEME_GIT_PROMPT_CLEAN=""

ZSH_THEME_GIT_PROMPT_ADDED="%{$fg[green]%}✚"
ZSH_THEME_GIT_PROMPT_MODIFIED="%{$fg[blue]%}✹"
ZSH_THEME_GIT_PROMPT_DELETED="%{$fg[red]%}✖"
ZSH_THEME_GIT_PROMPT_RENAMED="%{$fg[magenta]%}➜"
ZSH_THEME_GIT_PROMPT_UNMERGED="%{$fg[yellow]%}═"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%{$fg[cyan]%}✭"

# ============================================================
# UTF-8 рамки
# ============================================================

if [[ "${langinfo[CODESET]}" = UTF-8 ]]; then
  PR_HBAR="─"
  PR_ULCORNER="┌"
  PR_LLCORNER="└"
  PR_LRCORNER="┘"
  PR_URCORNER="┐"
else
  PR_HBAR="-"
  PR_ULCORNER="+"
  PR_LLCORNER="+"
  PR_LRCORNER="+"
  PR_URCORNER="+"
fi

# ============================================================
# Заголовок терминала
# ============================================================

case "$TERM" in
  xterm*|screen*|tmux*)
    typeset -g PR_TITLEBAR=$'%{\e]0;%n@%m:%~\a%}'
    ;;
  *)
    typeset -g PR_TITLEBAR=""
    ;;
esac

# ============================================================
# Время / статус
# ============================================================

typeset -g current_time='%D{%H:%M:%S}'
typeset -g current_date='%D{%a,%b%d}'
typeset -g return_code='%(?..%{$fg[red]%}%? ↵%{$reset_color%})'

# ============================================================
# Хуки
# ============================================================

function theme_precmd() {
  current_time='%D{%H:%M:%S}'
  current_date='%D{%a,%b%d}'
}

function theme_preexec() {
  if [[ "$TERM" = screen* ]]; then
    local CMD=${1[(wr)^(*=*|sudo|-*)]}
    print -Pn "\ek$CMD\e\\"
  fi
}

add-zsh-hook precmd theme_precmd
add-zsh-hook preexec theme_preexec

# ============================================================
# Обычный transient prompt
# ============================================================

typeset -g PROMPT=' %{$fg[cyan]%}❯%{$reset_color%} '
typeset -g RPROMPT=''

# ============================================================
# Красивый prompt во время ввода
# ============================================================

function transient_prompt() {
  PROMPT='${PR_TITLEBAR}\
${PROMPT_FRAME_COLOR}${PR_ULCORNER}${PR_HBAR}\
${PROMPT_BRACKET_COLOR}(\
${PROMPT_PATH_COLOR}%~\
${PROMPT_BRACKET_COLOR})%=\
${PROMPT_BRACKET_COLOR}(\
${PROMPT_FRAME_COLOR}%(!.%SROOT%s.%n)\
${PROMPT_BRACKET_COLOR}@\
${PROMPT_PATH_COLOR}%m:%l\
${PROMPT_BRACKET_COLOR})\
${PROMPT_FRAME_COLOR}${PR_HBAR}${PR_URCORNER}

${PROMPT_FRAME_COLOR}${PR_LLCORNER}\
${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}(\
${PROMPT_TIME_COLOR}${current_time}\
${PROMPT_GIT_COLOR}$(git_prompt_info)$(git_prompt_status)\
${PROMPT_INNER_DECOR_COLOR})%=\
(${PROMPT_TIME_COLOR}${current_date}\
${PROMPT_INNER_DECOR_COLOR})\
${PROMPT_FRAME_COLOR}${PR_HBAR}${PR_LRCORNER}
 %{$fg[cyan]%}❯%{$reset_color%} '
}

# ============================================================
# zle hooks
# ============================================================

function zle-line-init() {
  transient_prompt
  zle reset-prompt
}

function zle-line-finish() {
  PROMPT=' %{$fg[cyan]%}❯%{$reset_color%} '
  RPROMPT=''
  zle reset-prompt
}

zle -N zle-line-init
zle -N zle-line-finish

# ============================================================
# Secondary prompt
# ============================================================

PS2='${PROMPT_FRAME_COLOR}${PR_HBAR}\
${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}(\
${PROMPT_PS2_COLOR}%_\
${PROMPT_INNER_DECOR_COLOR})\
${PR_HBAR}${PROMPT_FRAME_COLOR}${PR_HBAR}\
${PROMPT_RESET_COLOR} '
