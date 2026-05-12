# ================================================
# mytheme.zsh-theme — с Transient Prompt
# ================================================

# === Кэш для заполнителя и длины пути ===
typeset -g _cached_fillbar=""
typeset -g _cached_pwdlen=""

autoload zsh/terminfo

# --- общие цветовые переменные ---
for color in RED GREEN YELLOW BLUE MAGENTA CYAN WHITE GREY; do
  typeset -g COLOR_BOLD_$color="%{$terminfo[bold]$fg[${(L)color}]%}"
  typeset -g COLOR_LIGHT_$color="%{$fg[${(L)color}]%}"
done
typeset -g COLOR_RESET="%{$terminfo[sgr0]%}"

# --- семантические переменные ---
typeset -g PROMPT_FRAME_COLOR="$COLOR_BOLD_CYAN"
typeset -g PROMPT_BRACKET_COLOR="$COLOR_BOLD_GREY"
typeset -g PROMPT_PATH_COLOR="$COLOR_BOLD_GREEN"
typeset -g PROMPT_TIME_COLOR="$COLOR_BOLD_YELLOW"
typeset -g PROMPT_INNER_DECOR_COLOR="$COLOR_BOLD_BLUE"
typeset -g PROMPT_GIT_COLOR="$COLOR_LIGHT_BLUE"
typeset -g PROMPT_PS2_COLOR="$COLOR_LIGHT_GREEN"
typeset -g PROMPT_RESET_COLOR="$COLOR_RESET"

# ============================================================
# Обработчик изменения размеров терминала
# ============================================================
function _update_prompt_on_resize() {
  local TERMWIDTH=$(( COLUMNS - ${ZLE_RPROMPT_INDENT:-1} ))

  local promptsize=${#${(%):---(%n@%m:%l)---()--}}
  local pwdsize=${#${(%):-%~}}
  local rubypromptsize=0
  local venvpromptsize=0
  local condapromptsize=0

  # Безопасные вызовы
  (( $+functions[ruby_prompt_info] )) && rubypromptsize=${#${(%)$(ruby_prompt_info)}}
  (( $+functions[virtualenv_prompt_info] )) && venvpromptsize=${#${(%)$(virtualenv_prompt_info)}}
  (( $+functions[conda_prompt_info] )) && condapromptsize=${#${(%)$(conda_prompt_info)}}

  if (( promptsize + rubypromptsize + pwdsize + venvpromptsize + condapromptsize > TERMWIDTH )); then
    _cached_pwdlen=$(( TERMWIDTH - promptsize ))
  else
    _cached_pwdlen=""
  fi

  local actual_pwdsize
  if [[ -n "$_cached_pwdlen" ]]; then
    actual_pwdsize=$(( _cached_pwdlen + 3 ))
  else
    actual_pwdsize=$pwdsize
  fi

  local fill_size=$(( TERMWIDTH - (promptsize + rubypromptsize + actual_pwdsize + venvpromptsize + condapromptsize) ))
  _cached_fillbar="\${(l:${fill_size}:: :)}"

  zle reset-prompt 2>/dev/null
}

trap '_update_prompt_on_resize' WINCH
_update_prompt_on_resize

# ============================================================
# Хуки
# ============================================================
function theme_precmd {
  PR_FILLBAR="$_cached_fillbar"
  PR_PWDLEN="$_cached_pwdlen"
}

function theme_preexec {
  if [[ "$TERM" = "screen" ]]; then
    local CMD=${1[(wr)^(*=*|sudo|-*)]}
    echo -n "\ek$CMD\e\\"
  fi
}

autoload -U add-zsh-hook
add-zsh-hook precmd  theme_precmd
add-zsh-hook preexec theme_preexec

setopt prompt_subst

# ============================================================
# Git
# ============================================================
ZSH_THEME_GIT_PROMPT_PREFIX=" on %{$fg[green]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_ADDED="%{$fg[green]%} %{%G✚%}"
ZSH_THEME_GIT_PROMPT_MODIFIED="%{$fg[blue]%} %{%G✹%}"
ZSH_THEME_GIT_PROMPT_DELETED="%{$fg[red]%} %{%G✖%}"
ZSH_THEME_GIT_PROMPT_RENAMED="%{$fg[magenta]%} %{%G➜%}"
ZSH_THEME_GIT_PROMPT_UNMERGED="%{$fg[yellow]%} %{%G═%}"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%{$fg[cyan]%} %{%G✭%}"

# Безопасные git функции
git_prompt_info()    { (( $+functions[git_prompt_info] ))    && command git_prompt_info    || echo "" }
git_prompt_status()  { (( $+functions[git_prompt_status] ))  && command git_prompt_status  || echo "" }

# ============================================================
# Рамка и заголовок
# ============================================================
if [[ "${langinfo[CODESET]}" = UTF-8 ]]; then
  PR_SET_CHARSET=""
  PR_HBAR="─"
  PR_ULCORNER="┌"
  PR_LLCORNER="└"
  PR_LRCORNER="┘"
  PR_URCORNER="┐"
else
  typeset -g -A altchar
  set -A altchar ${(s..)terminfo[acsc]}
  PR_SET_CHARSET="%{$terminfo[enacs]%}"
  PR_SHIFT_IN="%{$terminfo[smacs]%}"
  PR_SHIFT_OUT="%{$terminfo[rmacs]%}"
  PR_HBAR="${PR_SHIFT_IN}${altchar[q]:--}${PR_SHIFT_OUT}"
  PR_ULCORNER="${PR_SHIFT_IN}${altchar[l]:--}${PR_SHIFT_OUT}"
  PR_LLCORNER="${PR_SHIFT_IN}${altchar[m]:--}${PR_SHIFT_OUT}"
  PR_LRCORNER="${PR_SHIFT_IN}${altchar[j]:--}${PR_SHIFT_OUT}"
  PR_URCORNER="${PR_SHIFT_IN}${altchar[k]:--}${PR_SHIFT_OUT}"
fi

case $TERM in
  xterm*) PR_TITLEBAR=$'%{\e]0;%(!.-=*[ROOT]*=- | .)%n@%m:%~ | ${COLUMNS}x${LINES} | %y\a%}' ;;
  screen) PR_TITLEBAR=$'%{\e_screen \005 (\005t) | %(!.-=[ROOT]=- | .)%n@%m:%~ | ${COLUMNS}x${LINES} | %y\e\\%}' ;;
  *)      PR_TITLEBAR="" ;;
esac

[[ "$TERM" = "screen" ]] && PR_STITLE=$'%{\ekzsh\e\\%}' || PR_STITLE=""

typeset -g current_time='%D{%H:%M:%S}'
typeset -g return_code="%(?..%{$fg[red]%}%? ↵ %{$reset_color%})"

# ============================================================
# TRANSIENT PROMPT
# ============================================================

# Постоянный минимальный промпт после выполнения команды
typeset -g PROMPT=' %{$fg[cyan]%}❯%{$reset_color%} '
typeset -g RPROMPT=''

# Полноценный красивый промпт (только во время ввода)
function transient_prompt() {
  local venv="$( (( $+functions[virtualenv_prompt_info] )) && virtualenv_prompt_info || echo '' )"
  local ruby="$( (( $+functions[ruby_prompt_info] )) && ruby_prompt_info || echo '' )"
  local conda="$( (( $+functions[conda_prompt_info] )) && conda_prompt_info || echo '' )"

  PROMPT='${PR_SET_CHARSET}${PR_STITLE}${(e)PR_TITLEBAR}\
${PROMPT_FRAME_COLOR}${PR_ULCORNER}${PR_HBAR}${PROMPT_BRACKET_COLOR}(\
${PROMPT_PATH_COLOR}%${PR_PWDLEN}<...<%~%<<\
${PROMPT_BRACKET_COLOR})${venv}${ruby}${conda}${PROMPT_FRAME_COLOR} ${(e)PR_FILLBAR} ${PROMPT_BRACKET_COLOR}(\
${PROMPT_FRAME_COLOR}%(!.%SROOT%s.%n)${PROMPT_BRACKET_COLOR}@${PROMPT_PATH_COLOR}%m:%l\
${PROMPT_BRACKET_COLOR})${PROMPT_FRAME_COLOR}${PR_HBAR}${PR_URCORNER}\

${PROMPT_FRAME_COLOR}${PR_LLCORNER}${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}(\
${PROMPT_TIME_COLOR}$current_time\
${PROMPT_GIT_COLOR}$(git_prompt_info)$(git_prompt_status)${PROMPT_INNER_DECOR_COLOR})${PROMPT_FRAME_COLOR}${PR_HBAR}${PR_HBAR}\
>${PROMPT_RESET_COLOR} '

  RPROMPT=' $return_code${PROMPT_FRAME_COLOR}${PR_HBAR}${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}\
(${PROMPT_TIME_COLOR}%D{%a,%b%d}${PROMPT_INNER_DECOR_COLOR})${PR_HBAR}${PROMPT_FRAME_COLOR}${PR_LRCORNER}${PROMPT_RESET_COLOR}'
}

# Регистрация transient
zle -N zle-line-init
zle -N zle-line-finish

function zle-line-init() {
  transient_prompt
  zle reset-prompt
}

function zle-line-finish() {
  PROMPT=' %{$fg[cyan]%}❯%{$reset_color%} '
  RPROMPT=''
  zle reset-prompt
}

# PS2
PS2='${PROMPT_FRAME_COLOR}${PR_HBAR}${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}(\
${PROMPT_PS2_COLOR}%_${PROMPT_INNER_DECOR_COLOR})${PR_HBAR}${PROMPT_FRAME_COLOR}${PR_HBAR}${PROMPT_RESET_COLOR} '
