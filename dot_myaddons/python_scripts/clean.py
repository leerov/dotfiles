#!/usr/bin/env python3

import os
import subprocess
import shutil
import curses
import time
import threading
from pathlib import Path
import glob
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any, Set
from dataclasses import dataclass
from enum import Enum
import re
from collections import deque
import sys


class Color:
    """ANSI color codes (для совместимости)"""
    BLUE = '\033[0;34m'
    RESET = '\033[0;39m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    YELLOW = '\033[0;33m'
    BOLD = '\033[1m'
    NORMAL = '\033[0m'


@dataclass
class DiskUsage:
    """Disk usage information"""
    total: str
    used: str
    available: str


@dataclass
class FileInfo:
    """File information for sorting and display"""
    size: int
    path: Path
    
    @property
    def size_human(self) -> str:
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"


class Spinner:
    """Анимированный спиннер"""
    def __init__(self):
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.idx = 0
    
    def next(self) -> str:
        self.idx = (self.idx + 1) % len(self.frames)
        return self.frames[self.idx]


class ProgressBar:
    """Анимированный прогресс бар"""
    def __init__(self, width: int = 40):
        self.width = width
        self.progress = 0
        self.cached_render = ""
    
    def update(self, progress: float):
        self.progress = min(1.0, max(0.0, progress))
    
    def render(self) -> str:
        filled = int(self.width * self.progress)
        bar = '█' * filled + '░' * (self.width - filled)
        new_render = f"[{bar}] {int(self.progress * 100)}%"
        if new_render != self.cached_render:
            self.cached_render = new_render
        return self.cached_render


class SystemCleaner:
    """Main class for system cleanup operations"""
    
    SCRIPT_DIR = Path.home() / "leerov-tools"
    
    CACHE_PATHS = {
        "slack": [
            "Library/Application Support/Slack/Code Cache/",
            "Library/Application Support/Slack/Cache/",
            "Library/Application Support/Slack/Service Worker/CacheStorage/",
        ],
        "system": [
            "Library/Caches/*",
            "Library/42_cache/",
            "Library/Caches/CloudKit",
            "Library/Caches/com.apple.*",
            "Library/Caches/storeassetd",
            "Library/Caches/com.google.*",
        ],
        "browsers": [
            "Library/Application Support/Firefox/Profiles/*/storage",
            "Library/Application Support/Firefox/Profiles/*/cache*",
            "Library/Application Support/Google/Chrome/Default/Service Worker/CacheStorage/*",
            "Library/Application Support/Google/Chrome/Crashpad/completed/*",
            "Library/Application Support/Google/Chrome/Default/Cache/*",
            "Library/Safari/*",
            "Library/Containers/com.apple.Safari/Data/Library/Caches/*",
        ],
        "development": [
            ".kube/cache/*",
            "Library/Developer/Xcode/DerivedData/*",
            "Library/Developer/Xcode/iOS DeviceSupport/*",
            "Library/Application Support/Code/User/workspaceStorage",
            "Library/Application Support/Code/Cache*",
            "Library/Application Support/Code/Crashpad/completed",
            "Library/Caches/com.microsoft.VSCode*",
            "Library/Caches/org.swift.swiftpm/*",
            ".cargo/registry/cache/*",
            ".cargo/registry/src/*",
            ".cargo/git/db/*",
            ".npm/_cacache/*",
            ".npm/_logs/*",
        ],
        "multimedia": [
            "Library/Application Support/Spotify/PersistentCache",
            "Library/Application Support/Spotify/Data/*",
            "Library/Containers/com.apple.Music/Data/Library/Caches/*",
        ],
        "docker": [
            "Library/Containers/com.docker.docker/Data/vms/*",
            ".docker/cli-plugins/docker-scout",
            ".docker/cli-plugins/docker-agent",
            ".docker/cli-plugins/docker-buildx",
            ".docker/cli-plugins/docker-offload",
            ".docker/buildx/*",
            ".docker/contexts/*",
        ],
        "messengers": [
            "Library/Group Containers/*.ru.keepcoder.Telegram/stable/account-*/postbox/media/*",
            "Library/Group Containers/*.ru.keepcoder.Telegram/stable/account-*/postbox/temp/*",
            "Library/Group Containers/*.ru.keepcoder.Telegram/stable/account-*/postbox/cache/*",
        ],
        "spotlight": [
            "Library/Metadata/CoreSpotlight/*",
            "Library/Caches/com.apple.helpd/*",
            "Library/Caches/com.apple.spotlight/*",
        ],
        "python": [
            "Library/Python/*/lib/python/site-packages/nodejs_wheel/bin/node",
            "Library/Python/*/lib/python/site-packages/__pycache__/*",
            ".local/lib/python*/site-packages/__pycache__/*",
        ],
        "media_analysis": [
            "Library/Containers/com.apple.mediaanalysisd/Data/Library/Caches/*",
            "Library/Containers/com.apple.photoanalysisd/Data/Library/Caches/*",
        ],
        "system_logs": [
            "Library/Logs/*.log",
            "Library/Logs/*/*.log",
            ".npm/_logs/*",
            ".cargo/registry/index/*",
        ],
        "trash": [
            ".Trash/*",
            ".local/share/Trash/*",
        ],
        "temp": [
            "Library/Caches/TemporaryItems/*",
            "Library/Caches/com.apple.WebKit/*",
            ".cache/*",
            ".local/share/containers/*",
            ".wget-hsts",
            ".mysql_history",
            ".python_history",
            ".bash_history",
            ".zsh_history",
        ],
        "misc": [
            "leerov-tools/*.out",
            "Desktop/*.log",
            "Desktop/*.tmp",
            "Desktop/*.swp",
            "Desktop/*~",
            ".npm",
            ".nvm",
            ".node-gyp",
            ".yarn/cache/*",
            ".yarn/lock/*",
        ],
    }
    
    PROTECTED_PATTERNS = [
        ".docker/cli-plugins/docker$",
        ".docker/cli-plugins/docker-compose$",
        ".docker/cli-plugins/docker-credential",
        ".npmrc$",
        ".bashrc$",
        ".zshrc$",
        ".gitconfig$",
    ]
    
    SKIP_PATHS = [
        "Library/Application Support/Google/Chrome/Default/Extensions",
        "Library/Application Support/Firefox/Profiles/*/extensions",
        "Library/Application Support/Spotify/Apps",
        "Library/Containers/com.apple.mail",
        "Library/Messages",
    ]
    
    def __init__(self):
        self.home = Path.home()
        self.protected_patterns = [re.compile(p) for p in self.PROTECTED_PATTERNS]
        self.skip_paths = []
        for p in self.SKIP_PATHS:
            if '*' in p:
                self.skip_paths.append(p)
            else:
                self.skip_paths.append(str(self.home / p))
        self.spinner = Spinner()
        self.progress_bar = ProgressBar()
        self.cleaned_count = 0
        self.total_items = 0
        self.current_phase = "Initializing..."
        self.running = True
        self.log_messages = deque(maxlen=10)
        self.cache = {}
    
    @staticmethod
    def run_command(cmd: str) -> str:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.SubprocessError, OSError):
            return ""
    
    def get_disk_usage(self, path: Path) -> Optional[DiskUsage]:
        output = self.run_command(f"df -h {path} 2>/dev/null | tail -1")
        if output:
            parts = output.split()
            if len(parts) >= 4:
                return DiskUsage(parts[1], parts[2], parts[3])
        return None
    
    def is_skip_path(self, path: Path) -> bool:
        path_str = str(path)
        for skip in self.skip_paths:
            if '*' in skip:
                try:
                    if glob.fnmatch.fnmatch(path_str, skip):
                        return True
                except:
                    pass
            else:
                if skip in path_str:
                    return True
        return False
    
    def is_protected(self, path: Path) -> bool:
        path_str = str(path)
        for pattern in self.protected_patterns:
            if pattern.search(path_str):
                return True
        return False
    
    def get_largest_files(self, directory: Path, limit: int = 10) -> List[FileInfo]:
        files = []
        try:
            for filepath in directory.rglob('*'):
                if self.is_skip_path(filepath) or self.is_protected(filepath):
                    continue
                if filepath.is_file():
                    try:
                        size = filepath.stat().st_size
                        files.append(FileInfo(size, filepath))
                    except (OSError, PermissionError):
                        continue
            files.sort(key=lambda x: x.size, reverse=True)
            return files[:limit]
        except (OSError, PermissionError):
            return []
    
    def expand_glob_pattern(self, pattern: str) -> List[Path]:
        try:
            full_pattern = str(self.home / pattern)
            expanded = glob.glob(full_pattern, recursive=True)
            return [Path(p) for p in expanded if os.path.exists(p)]
        except (OSError, PermissionError):
            return []
    
    def clean_path(self, path_pattern: str) -> int:
        cleaned = 0
        
        if not path_pattern.startswith('/'):
            path_pattern = str(self.home / path_pattern)
        
        if '*' in path_pattern or '?' in path_pattern:
            try:
                for item in glob.glob(path_pattern, recursive=True):
                    if os.path.exists(item):
                        path_obj = Path(item)
                        if self.is_protected(path_obj) or self.is_skip_path(path_obj):
                            continue
                        try:
                            if os.path.isdir(item):
                                shutil.rmtree(item, ignore_errors=True)
                            else:
                                os.remove(item)
                            cleaned += 1
                        except (OSError, PermissionError):
                            pass
            except (OSError, PermissionError):
                pass
        else:
            if os.path.exists(path_pattern) or os.path.islink(path_pattern):
                path_obj = Path(path_pattern)
                if self.is_protected(path_obj) or self.is_skip_path(path_obj):
                    return cleaned
                try:
                    if os.path.isdir(path_pattern):
                        shutil.rmtree(path_pattern, ignore_errors=True)
                    else:
                        os.remove(path_pattern)
                    cleaned += 1
                except (OSError, PermissionError):
                    pass
        
        return cleaned
    
    def cleanup_paths(self, callback=None) -> int:
        total_cleaned = 0
        total_categories = len(self.CACHE_PATHS)
        
        for idx, (category, patterns) in enumerate(self.CACHE_PATHS.items()):
            self.current_phase = f"Cleaning {category}..."
            if callback:
                callback(idx / total_categories, f"Cleaning {category}...")
            
            for pattern in patterns:
                expanded_paths = self.expand_glob_pattern(pattern)
                if expanded_paths:
                    for path in expanded_paths:
                        total_cleaned += self.clean_path(str(path))
                else:
                    total_cleaned += self.clean_path(pattern)
        
        self.current_phase = "Cleaning old downloads..."
        total_cleaned += self.clean_old_downloads()
        
        self.current_phase = "Cleaning additional caches..."
        total_cleaned += self.clean_additional_caches()
        
        self.current_phase = "Cleaning Docker cache..."
        total_cleaned += self.clean_docker_build_cache()
        
        if callback:
            callback(1.0, "Cleanup complete!")
        
        return total_cleaned
    
    def clean_old_downloads(self) -> int:
        cleaned = 0
        downloads_dir = self.home / "Downloads"
        
        if downloads_dir.exists():
            patterns = ["*.dmg", "*.zip", "*.pkg", "*.tar.gz", "*.tgz", "*.rar", "*.7z"]
            for pattern in patterns:
                for filepath in downloads_dir.glob(pattern):
                    try:
                        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                        if datetime.now() - mtime > timedelta(days=30):
                            filepath.unlink()
                            cleaned += 1
                    except (OSError, PermissionError):
                        pass
        
        return cleaned
    
    def clean_additional_caches(self) -> int:
        cleaned = 0
        
        try:
            for pycache in self.home.rglob("__pycache__"):
                if pycache.is_dir() and not self.is_skip_path(pycache):
                    shutil.rmtree(pycache, ignore_errors=True)
                    cleaned += 1
        except (OSError, PermissionError):
            pass
        
        try:
            for ds_store in self.home.rglob(".DS_Store"):
                if ds_store.is_file() and not self.is_skip_path(ds_store):
                    ds_store.unlink()
                    cleaned += 1
        except (OSError, PermissionError):
            pass
        
        return cleaned
    
    def clean_docker_build_cache(self) -> int:
        cleaned = 0
        try:
            docker_version = self.run_command("docker version --format '{{.Server.Version}}'")
            if docker_version:
                self.run_command("docker builder prune -f")
                cleaned += 1
        except (subprocess.SubprocessError, OSError):
            pass
        
        return cleaned

    def get_file_list_for_display(self) -> List[str]:
        files = self.get_largest_files(self.home, 10)
        return [f"{f.size_human:>8}  {f.path}" for f in files]


class UIState:
    """Класс для хранения состояния UI с кэшированием"""
    def __init__(self):
        self.title = "🧹 System Cleaner v2.0"
        self.disk_usage = None
        self.usage_percent = 0
        self.phase = "Loading..."
        self.progress = 0.0
        self.cleaned_count = 0
        self.files_list = ["⏳ Scanning files..."]
        self.log_messages = []
        self.spinner_frame = 0
        self.dirty = True
        self.last_update = 0
        self.scanning = True
        
    def mark_dirty(self):
        self.dirty = True


def draw_ui(stdscr):
    """Основная функция отрисовки интерфейса с инкрементальным обновлением"""
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(50)  # 20 FPS
    
    # Инициализация цветов
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    cleaner = SystemCleaner()
    spinner = Spinner()
    state = UIState()
    
    # Получаем начальные данные синхронно (быстро)
    state.disk_usage = cleaner.get_disk_usage(cleaner.home) or cleaner.get_disk_usage(Path("/"))
    state.dirty = True
    
    # Запускаем фоновый поток для сканирования файлов
    def scan_files():
        state.phase = "Scanning files..."
        state.mark_dirty()
        files = cleaner.get_largest_files(cleaner.home, 10)
        if files:
            state.files_list = [f"{f.size_human:>8}  {f.path}" for f in files]
        else:
            state.files_list = ["No large files found"]
        state.scanning = False
        state.phase = "Ready"
        state.mark_dirty()
    
    scan_thread = threading.Thread(target=scan_files, daemon=True)
    scan_thread.start()
    
    cleaning = False
    cleanup_thread = None
    
    # Кэш для строк
    line_cache = {}
    
    def update_line(y, x, text, attr=0, force=False):
        """Обновить строку только если она изменилась"""
        key = (y, x)
        if force or key not in line_cache or line_cache[key] != (text, attr):
            try:
                stdscr.addstr(y, x, text, attr)
                line_cache[key] = (text, attr)
                return True
            except:
                pass
        return False
    
    start_time = time.time()
    
    while True:
        try:
            height, width = stdscr.getmaxyx()
            
            # Обновляем анимацию спиннера
            spinner_char = spinner.next()
            
            # Обновляем данные дискового пространства раз в 5 секунд
            current_time = time.time()
            if not cleaning and current_time - state.last_update > 5.0:
                state.disk_usage = cleaner.get_disk_usage(cleaner.home) or cleaner.get_disk_usage(Path("/"))
                state.last_update = current_time
                state.dirty = True
            
            # Заголовок
            x_center = (width - len(state.title)) // 2
            update_line(0, x_center, state.title, curses.color_pair(1) | curses.A_BOLD)
            
            # Разделительная линия
            update_line(1, 0, "╔" + "═" * (width - 2) + "╗", curses.color_pair(6))
            
            # Disk usage section
            update_line(2, 2, "💾 Disk Usage", curses.color_pair(2) | curses.A_BOLD)
            
            if state.disk_usage:
                usage_str = f"Total: {state.disk_usage.total}  Used: {state.disk_usage.used}  Available: {state.disk_usage.available}"
                update_line(3, 4, usage_str, 0)
                
                try:
                    total_gb = float(state.disk_usage.total.replace('Gi', ''))
                    used_gb = float(state.disk_usage.used.replace('Gi', ''))
                    state.usage_percent = (used_gb / total_gb) if total_gb > 0 else 0
                    
                    bar_width = min(60, width - 12)
                    filled = int(bar_width * state.usage_percent)
                    color = curses.color_pair(4) if state.usage_percent > 0.8 else curses.color_pair(3) if state.usage_percent > 0.6 else curses.color_pair(2)
                    
                    bar = '█' * filled + '░' * (bar_width - filled)
                    bar_text = f"[{bar}] {int(state.usage_percent * 100)}%"
                    update_line(4, 4, bar_text, color)
                except:
                    pass
            
            # Progress section
            update_line(6, 2, "⚡ Progress", curses.color_pair(7) | curses.A_BOLD)
            
            # Анимированный спиннер и фаза
            phase_text = f"{spinner_char} {state.phase}"
            update_line(7, 4, phase_text, 0)
            
            # Прогресс бар
            progress_bar = ProgressBar(min(50, width - 16))
            progress_bar.update(state.progress)
            bar_text = progress_bar.render()
            update_line(8, 4, bar_text, 0)
            
            # Statistics
            stats_text = f"📊 Items cleaned: {state.cleaned_count}"
            update_line(10, 2, stats_text, curses.color_pair(6))
            
            files_text = f"📁 Files scanned: {len(state.files_list) if not state.scanning else 'Scanning...'}"
            update_line(11, 2, files_text, curses.color_pair(6))
            
            # Top files section
            update_line(13, 2, "📋 Top 10 Largest Files", curses.color_pair(3) | curses.A_BOLD)
            
            # Show top files with инкрементальным обновлением
            max_y = height - 6
            display_list = state.files_list[:min(10, max_y - 15)]
            for i, file_info in enumerate(display_list):
                try:
                    display_info = file_info
                    if len(display_info) > width - 8:
                        display_info = display_info[:width - 11] + "..."
                    update_line(14 + i, 4, display_info, 0)
                except:
                    pass
            
            # Clear remaining file lines
            start_y = 14 + len(display_list)
            for i in range(start_y, min(14 + 10, height - 5)):
                update_line(i, 4, " " * (width - 8), 0)
            
            # Log messages
            log_start_y = min(14 + len(display_list), height - 5)
            if log_start_y < height - 5:
                update_line(log_start_y, 2, "📝 Recent Activity:", curses.color_pair(5))
                
                log_y = log_start_y + 1
                for i, msg in enumerate(cleaner.log_messages):
                    if log_y + i < height - 2:
                        try:
                            display_msg = msg
                            if len(display_msg) > width - 8:
                                display_msg = display_msg[:width - 11] + "..."
                            update_line(log_y + i, 4, display_msg, 0)
                        except:
                            pass
                
                # Clear remaining log lines
                for i in range(len(cleaner.log_messages), height - log_y - 3):
                    if log_y + i < height - 2:
                        update_line(log_y + i, 4, " " * (width - 8), 0)
            
            # Footer
            footer_text = "Press 'c' - Clean  |  'r' - Refresh  |  'q' - Quit"
            update_line(height - 2, 2, footer_text, curses.color_pair(6))
            
            # Нижняя граница
            update_line(height - 1, 0, "╚" + "═" * (width - 2) + "╝", curses.color_pair(6))
            
            # Обновляем экран только если были изменения
            if state.dirty or line_cache:
                stdscr.refresh()
                state.dirty = False
            
            # Обработка клавиш
            key = stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                if cleaning and cleanup_thread and cleanup_thread.is_alive():
                    cleaner.running = False
                    cleanup_thread.join(timeout=2)
                break
            
            elif key == ord('c') or key == ord('C'):
                if not cleaning:
                    cleaning = True
                    state.phase = "Starting cleanup..."
                    cleaner.log_messages.append("🚀 Starting cleanup process...")
                    
                    def cleanup_worker():
                        nonlocal state, cleaning
                        def update_progress(p, msg):
                            state.progress = p
                            state.phase = msg
                            state.dirty = True
                            if msg and "Cleaning" in msg:
                                cleaner.log_messages.append(f"🔄 {msg}")
                        
                        total = cleaner.cleanup_paths(update_progress)
                        state.cleaned_count = total
                        cleaner.log_messages.append(f"✅ Cleaned {total} items!")
                        state.phase = "Cleanup complete!"
                        state.dirty = True
                        cleaning = False
                    
                    cleanup_thread = threading.Thread(target=cleanup_worker)
                    cleanup_thread.daemon = True
                    cleanup_thread.start()
            
            elif key == ord('r') or key == ord('R'):
                if not cleaning:
                    state.phase = "Refreshing..."
                    cleaner.log_messages.append("🔄 Refreshing data...")
                    # Запускаем пересканирование в фоне
                    def refresh_files():
                        files = cleaner.get_largest_files(cleaner.home, 10)
                        if files:
                            state.files_list = [f"{f.size_human:>8}  {f.path}" for f in files]
                        else:
                            state.files_list = ["No large files found"]
                        state.phase = "Ready"
                        state.dirty = True
                    threading.Thread(target=refresh_files, daemon=True).start()
                    state.dirty = True
                    state.last_update = time.time()
            
            elif key == -1:
                # Просто обновляем спиннер
                state.dirty = True
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            try:
                stdscr.addstr(height - 3, 2, f"Error: {str(e)}")
                stdscr.refresh()
                time.sleep(1)
            except:
                break


def main():
    """Entry point"""
    try:
        curses.wrapper(draw_ui)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
