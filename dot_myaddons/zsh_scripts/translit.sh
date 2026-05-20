function transliterate-command-line() {
    local mapping=(
        "й q" "ц w" "у e" "к r" "е t" "н y" "г u" "ш i" "щ o" "з p" "х [" "ъ ]"
        "ф a" "ы s" "в d" "а f" "п g" "р h" "о j" "л k" "д l" "ж ;" "э '"
        "я z" "ч x" "с c" "м v" "и b" "т n" "ь m" "б ," "ю ." "ё \`"
        "Й Q" "Ц W" "У E" "К R" "Е T" "Н Y" "Г U" "Ш I" "Щ O" "З P" "Х {" "Ъ }"
        "Ф A" "Ы S" "В D" "А F" "П G" "Р H" "О J" "Л K" "Д L" "Ж :" "Э \""
        "Я Z" "Ч X" "С C" "М V" "И B" "Т N" "Ь M" "Б <" "Ю >" "Ё ~"
    )

    local result="$BUFFER"
    local in_quotes=0
    local quote_char=""
    local output=""

    # Проходим по каждому символу в строке
    for (( i=0; i<${#result}; i++ )); do
        local char="${result:$i:1}"

        # Проверяем кавычки
        if [[ "$char" == "\"" || "$char" == "'" ]]; then
            if [[ $in_quotes -eq 0 ]]; then
                # Начало кавычек
                in_quotes=1
                quote_char="$char"
            elif [[ "$char" == "$quote_char" ]]; then
                # Конец кавычек (только если совпадает тип кавычек)
                in_quotes=0
                quote_char=""
            fi
        fi

        if [[ $in_quotes -eq 0 ]]; then
            # Вне кавычек - преобразуем
            local converted=0
            for pair in "${mapping[@]}"; do
                local ru="${pair%% *}"
                local en="${pair##* }"
                if [[ "$char" == "$ru" ]]; then
                    output+="$en"
                    converted=1
                    break
                fi
            done

            if [[ $converted -eq 0 ]]; then
                output+="$char"
            fi
        else
            # Внутри кавычек - оставляем как есть
            output+="$char"
        fi
    done

    BUFFER="$output"
    CURSOR=${#BUFFER}
}

# Привязываем к нажатию Enter
function accept-line-with-translit() {
    transliterate-command-line
    zle .accept-line
}

zle -N accept-line-with-translit
bindkey '^M' accept-line-with-translit
bindkey '^J' accept-line-with-translit