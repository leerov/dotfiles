#!/bin/bash

SCRIPT_NAME="sync_apps.sh"
LOG_DIR="$HOME"
LAST_HOST_FILE="$LOG_DIR/last_hostname"
CURRENT_HOST=$(hostname)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

need_sync() {
    local last_host=""

    if [ -f "$LAST_HOST_FILE" ]; then
        last_host=$(cat "$LAST_HOST_FILE" 2>/dev/null | head -1)

        if [ -f "$LAST_HOST_FILE" ]; then
            local file_age
            local current_time
            local one_day_seconds=86400

            if [[ "$OSTYPE" == "darwin"* ]]; then
                file_age=$(($(date +%s) - $(stat -f %m "$LAST_HOST_FILE" 2>/dev/null)))
            else
                file_age=$(($(date +%s) - $(stat -c %Y "$LAST_HOST_FILE" 2>/dev/null)))
            fi

            if [ "$file_age" -gt "$one_day_seconds" ]; then
                log_info "Файл $LAST_HOST_FILE старше 1 дня (возраст: $((file_age / 3600)) часов)"
                return 0
            fi
        fi
    fi

    if [ "$CURRENT_HOST" != "$last_host" ]; then
        log_info "Hostname изменился: было '$last_host', стало '$CURRENT_HOST'"
        return 0
    fi

    return 1
}

sync_applications() {
    local goinfre_base="/opt/goinfre"
    local home_apps="$HOME/Applications"

    if [ ! -d "$goinfre_base" ]; then
        return 1
    fi

    if [ ! -d "$home_apps" ]; then
        mkdir -p "$home_apps"
        log_info "Создана директория $home_apps"
    fi

    local added_count=0
    local removed_count=0
    local skipped_count=0

    for user_dir in "$goinfre_base"/*; do
        if [ -d "$user_dir" ] && [ -r "$user_dir" ]; then
            local user_apps_dir="$user_dir/Applications"
            if [ -d "$user_apps_dir" ] && [ -r "$user_apps_dir" ]; then
                for app in "$user_apps_dir"/*; do
                    if [ -e "$app" ] || [ -L "$app" ]; then
                        local app_name=$(basename "$app")
                        local home_link="$home_apps/$app_name"

                        if [ -L "$home_link" ]; then
                            local current_target=$(readlink "$home_link")
                            if [ "$current_target" != "$app" ]; then
                                rm -f "$home_link"
                                ln -s "$app" "$home_link"
                                ((added_count++))
                                log_info "Обновлена ссылка: $home_link -> $app"
                            else
                                ((skipped_count++))
                            fi
                        elif [ -e "$home_link" ]; then
                            ((skipped_count++))
                        else
                            ln -s "$app" "$home_link" 2>/dev/null
                            if [ $? -eq 0 ]; then
                                ((added_count++))
                                log_info "Создана ссылка: $home_link -> $app"
                            else
                                log_warning "Не удалось создать ссылку для $app_name"
                            fi
                        fi
                    fi
                done
            fi
        fi
    done

    if [ -d "$home_apps" ]; then
        for link in "$home_apps"/*; do
            if [ -L "$link" ]; then
                if [ ! -e "$link" ]; then
                    rm -f "$link"
                    ((removed_count++))
                    log_info "Удалена мёртвая ссылка: $link"
                fi
            fi
        done
    fi

    log_success "Синхронизация завершена: добавлено $added_count, удалено $removed_count, пропущено $skipped_count"
    return 0
}

write_last_hostname() {
    echo "$CURRENT_HOST" > "$LAST_HOST_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        log_info "Сохранён текущий hostname: $CURRENT_HOST"
    else
        log_warning "Не удалось сохранить hostname в $LAST_HOST_FILE"
    fi
}

main() {
    if [ ! -d "/opt/goinfre" ]; then
        return 0
    fi

    if need_sync; then
        log_info "Запуск синхронизации (смена hostname или истекло время)..."
        sync_applications
        local sync_result=$?
        write_last_hostname
        if [ $sync_result -eq 0 ]; then
            log_success "Синхронизация успешно завершена"
        else
            log_error "Синхронизация завершена с ошибками"
            return 1
        fi
    else
        log_info "Синхронизация не требуется (hostname не изменился, файл не старше 1 дня)"
    fi
    return 0
}

main "$@"