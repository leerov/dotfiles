# python_aliases.sh - Генерация алиасов для Python скриптов
#
# Порядок подключения: загружается после остальных zsh-скриптов.
# Читает файл ~/.myaddons/python_scripts/order.txt
# Формат строки: <alias_name> <script_file.py>
# Пример строки: client client.py
# Результат: alias client="python3 ~/.myaddons/python_scripts/client.py"

PYTHON_SCRIPTS_DIR="$HOME/.myaddons/python_scripts"
ORDER_FILE="$PYTHON_SCRIPTS_DIR/order.txt"

if [ -f "$ORDER_FILE" ]; then
    while IFS= read -r line; do
        # Убираем пробелы в начале и конце
        line=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        # Пропускаем пустые строки и комментарии
        if [ -z "$line" ] || [ "${line:0:1}" = "#" ]; then
            continue
        fi
        # Извлекаем имя алиаса и имя файла (первое и второе слово)
        alias_name=$(echo "$line" | awk '{print $1}')
        script_file=$(echo "$line" | awk '{print $2}')
        if [ -n "$alias_name" ] && [ -n "$script_file" ]; then
            alias "$alias_name"="python3 $PYTHON_SCRIPTS_DIR/$script_file"
        fi
    done < "$ORDER_FILE"
fi