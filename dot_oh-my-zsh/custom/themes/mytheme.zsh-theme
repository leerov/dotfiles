# === Кэш для заполнителя и длины пути ===
typeset -g _cached_fillbar=""
typeset -g _cached_pwdlen=""

# ============================================================
# Переименованные переменные цветов
# (значения вычисляются так же, как раньше, но имена стали
#  смысловыми и показывают, за какой элемент промпта отвечает цвет)
# ============================================================
autoload zsh/terminfo

# --- общие цветовые переменные (bold / light) ---
for color in RED GREEN YELLOW BLUE MAGENTA CYAN WHITE GREY; do
  typeset -g COLOR_BOLD_$color="%{$terminfo[bold]$fg[${(L)color}]%}"
  typeset -g COLOR_LIGHT_$color="%{$fg[${(L)color}]%}"
done
typeset -g COLOR_RESET="%{$terminfo[sgr0]%}"

# --- семантические переменные (по элементам промпта) ---
typeset -g PROMPT_FRAME_COLOR="$COLOR_BOLD_CYAN"          # рамка (углы, горизонтальные линии)
typeset -g PROMPT_BRACKET_COLOR="$COLOR_BOLD_GREY"        # скобки вокруг пути и user@host
typeset -g PROMPT_PATH_COLOR="$COLOR_BOLD_GREEN"          # текущий путь (%~)
typeset -g PROMPT_TIME_COLOR="$COLOR_BOLD_YELLOW"         # время / дата
typeset -g PROMPT_INNER_DECOR_COLOR="$COLOR_BOLD_BLUE"    # внутренние линии и скобки времени/даты
typeset -g PROMPT_GIT_COLOR="$COLOR_LIGHT_BLUE"           # информация git
typeset -g PROMPT_PS2_COLOR="$COLOR_LIGHT_GREEN"          # текст продолжения (PS2)
typeset -g PROMPT_RESET_COLOR="$COLOR_RESET"               # сброс цвета

# ============================================================
# Обработчик изменения размеров терминала (SIGWINCH)
# ============================================================
function _update_prompt_on_resize() {
  local TERMWIDTH=$(( COLUMNS - ${ZLE_RPROMPT_INDENT:-1} ))

  local promptsize=${#${(%):---(%n@%m:%l)---()--}}
  local rubypromptsize=${#${(%)$(ruby_prompt_info)}}
  local pwdsize=${#${(%):-%~}}
  local venvpromptsize=$((${#$(virtualenv_prompt_info)}))
  local condapromptsize=$((${#$(conda_prompt_info)}))

  # Усечение пути при необходимости
  if (( promptsize + rubypromptsize + pwdsize + venvpromptsize + condapromptsize > TERMWIDTH )); then
    _cached_pwdlen=$(( TERMWIDTH - promptsize ))
  else
    _cached_pwdlen=""
  fi

  # Фактическая длина пути в промпте (с учётом '...' при усечении)
  local actual_pwdsize
  if [[ -n "$_cached_pwdlen" ]]; then
    actual_pwdsize=$(( _cached_pwdlen + 3 ))   # 3 символа '...'
  else
    actual_pwdsize=$pwdsize
  fi

  # Заполнение пробелами
  local fill_size=$(( TERMWIDTH - (promptsize + rubypromptsize + actual_pwdsize + venvpromptsize + condapromptsize) ))
  _cached_fillbar="\${(l:${fill_size}:: :)}"

  # Мгновенное обновление строки приглашения
  zle reset-prompt 2>/dev/null
}

# Назначаем ловушку на изменение размера
trap '_update_prompt_on_resize' WINCH

# Первоначальный расчёт
_update_prompt_on_resize

# ============================================================
# theme_precmd — только подставляет кэшированные значения
# ============================================================
function theme_precmd {
  PR_FILLBAR="$_cached_fillbar"
  PR_PWDLEN="$_cached_pwdlen"
}

function theme_preexec {
  setopt local_options extended_glob
  if [[ "$TERM" = "screen" ]]; then
    local CMD=${1[(wr)^(*=*|sudo|-*)]}
    echo -n "\ek$CMD\e\\"
  fi
}

autoload -U add-zsh-hook
add-zsh-hook precmd  theme_precmd
add-zsh-hook preexec theme_preexec

# Включаем подстановки в промпте
setopt prompt_subst

# Настройки git prompt
ZSH_THEME_GIT_PROMPT_PREFIX=" on %{$fg[green]%}"
ZSH_THEME_GIT_PROMPT_SUFFIX="%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_DIRTY=""
ZSH_THEME_GIT_PROMPT_CLEAN=""

ZSH_THEME_GIT_PROMPT_ADDED="%{$fg[green]%} %{%G✚%}"
ZSH_THEME_GIT_PROMPT_MODIFIED="%{$fg[blue]%} %{%G✹%}"
ZSH_THEME_GIT_PROMPT_DELETED="%{$fg[red]%} %{%G✖%}"
ZSH_THEME_GIT_PROMPT_RENAMED="%{$fg[magenta]%} %{%G➜%}"
ZSH_THEME_GIT_PROMPT_UNMERGED="%{$fg[yellow]%} %{%G═%}"
ZSH_THEME_GIT_PROMPT_UNTRACKED="%{$fg[cyan]%} %{%G✭%}"

# Символы рамки
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

# Заголовок терминала
case $TERM in
  xterm*)
    PR_TITLEBAR=$'%{\e]0;%(!.-=*[ROOT]*=- | .)%n@%m:%~ | ${COLUMNS}x${LINES} | %y\a%}'
    ;;
  screen)
    PR_TITLEBAR=$'%{\e_screen \005 (\005t) | %(!.-=[ROOT]=- | .)%n@%m:%~ | ${COLUMNS}x${LINES} | %y\e\\%}'
    ;;
  *)
    PR_TITLEBAR=""
    ;;
esac

if [[ "$TERM" = "screen" ]]; then
  PR_STITLE=$'%{\ekzsh\e\\%}'
else
  PR_STITLE=""
fi
typeset -g current_time='%D{%H:%M:%S}'
# Основной промпт (с новыми именами цветов)
PROMPT='${PR_SET_CHARSET}${PR_STITLE}${(e)PR_TITLEBAR}\
${PROMPT_FRAME_COLOR}${PR_ULCORNER}${PR_HBAR}${PROMPT_BRACKET_COLOR}(\
${PROMPT_PATH_COLOR}%${PR_PWDLEN}<...<%~%<<\
${PROMPT_BRACKET_COLOR})$(virtualenv_prompt_info)$(ruby_prompt_info)$(conda_prompt_info)${PROMPT_FRAME_COLOR} ${(e)PR_FILLBAR} ${PROMPT_BRACKET_COLOR}(\
${PROMPT_FRAME_COLOR}%(!.%SROOT%s.%n)${PROMPT_BRACKET_COLOR}@${PROMPT_PATH_COLOR}%m:%l\
${PROMPT_BRACKET_COLOR})${PROMPT_FRAME_COLOR}${PR_HBAR}${PR_URCORNER}\

${PROMPT_FRAME_COLOR}${PR_LLCORNER}${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}(\
${PROMPT_TIME_COLOR}$current_time\
${PROMPT_GIT_COLOR}%{$reset_color%}$(git_prompt_info)$(git_prompt_status)${PROMPT_INNER_DECOR_COLOR})${PROMPT_FRAME_COLOR}${PR_HBAR}\
${PR_HBAR}\
>${PROMPT_RESET_COLOR} '

# Правый промпт (код возврата + дата)
return_code="%(?..%{$fg[red]%}%? ↵ %{$reset_color%})"
RPROMPT=' $return_code${PROMPT_FRAME_COLOR}${PR_HBAR}${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}\
(${PROMPT_TIME_COLOR}%D{%a,%b%d}${PROMPT_INNER_DECOR_COLOR})${PR_HBAR}${PROMPT_FRAME_COLOR}${PR_LRCORNER}${PROMPT_RESET_COLOR}'

PS2='${PROMPT_FRAME_COLOR}${PR_HBAR}\
${PROMPT_INNER_DECOR_COLOR}${PR_HBAR}(\
${PROMPT_PS2_COLOR}%_${PROMPT_INNER_DECOR_COLOR})${PR_HBAR}\
${PROMPT_FRAME_COLOR}${PR_HBAR}${PROMPT_RESET_COLOR} '
