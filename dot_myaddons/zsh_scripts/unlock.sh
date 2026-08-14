unlock() {
	if [ -z "$1" ]; then
		echo "❌ Ошибка: укажите путь к .app"
		echo "Пример: unlock /Applications/Telegram.app"
		return 1
	fi
	local app_path="${1%/}"
	if [ ! -d "$app_path" ]; then
		echo "❌ Ошибка: '$app_path' не найден"
		return 1
	fi
	echo "🔓 Снимаю quarantine с: $app_path"
	if xattr -r -d com.apple.quarantine "$app_path" 2>/dev/null || sudo xattr -r -d com.apple.quarantine "$app_path" 2>/dev/null; then
		echo "   ✅ quarantine снят"
	else
		echo "   ⚠️  quarantine не найден (скорее всего уже снят)"
	fi
	echo "✍️  Подписываю ad-hoc: $app_path"
	local out status
	out=$(codesign --force --deep -s - "$app_path" 2>&1)
	status=$?
	[ -n "$out" ] && echo "$out"
	if [ $status -ne 0 ] && echo "$out" | grep -q "unsealed contents"; then
		echo "🧹 В корне бандла лишние файлы (допустим только Contents) — удаляю и повторяю подпись:"
		find "$app_path" -maxdepth 1 -mindepth 1 ! -name "Contents" -print -exec rm -rf {} + 2>/dev/null | sed 's/^/   🗑  /'
		out=$(codesign --force --deep -s - "$app_path" 2>&1)
		status=$?
		[ -n "$out" ] && echo "$out"
	fi
	if [ $status -eq 0 ]; then
		echo "✅ Готово! Приложение можно запускать"
	else
		echo "❌ Ошибка при подписи"
		return 1
	fi
}
