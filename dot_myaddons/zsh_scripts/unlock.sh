unlock() {
    if [ -z "$1" ]; then
        echo "❌ Ошибка: укажите путь к .app"
        echo "Пример: unlock /Applications/Telegram.app"
        return 1
    fi
    
    local app_path="$1"
    
    if [ ! -d "$app_path" ]; then
        echo "❌ Ошибка: '$app_path' не найден"
        return 1
    fi
    
    echo "🔓 Снимаю quarantine с: $app_path"
    sudo xattr -d com.apple.quarantine "$app_path" 2>/dev/null || echo "   ⚠️  quarantine не найден (скорее всего уже снят)"
    
    echo "✍️  Подписываю ad-hoc: $app_path"
    codesign --force --deep -s - "$app_path"
    
    if [ $? -eq 0 ]; then
        echo "✅ Готово! Приложение можно запускать"
    else
        echo "❌ Ошибка при подписи"
        return 1
    fi
}
