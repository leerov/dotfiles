#!/usr/bin/env python3

import os
import subprocess
import shutil
from pathlib import Path
import glob
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum


class Color:
    """ANSI color codes"""
    BLUE = '\033[0;34m'
    RESET = '\033[0;39m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    YELLOW = '\033[0;33m'
    BOLD = '\033[1m'
    NORMAL = '\033[0m'


class SizeThreshold(Enum):
    """Size thresholds for color coding"""
    GB = 1024 ** 3
    MB_100 = 100 * 1024 ** 2
    MB_1 = 1024 ** 2


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
        """Get human readable file size"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    @property
    def color(self) -> str:
        """Get color based on file size"""
        if self.size > SizeThreshold.GB.value:
            return Color.RED
        if self.size > SizeThreshold.MB_100.value:
            return Color.YELLOW
        if self.size > SizeThreshold.MB_1.value:
            return Color.GREEN
        return Color.CYAN


class SystemCleaner:
    """Main class for system cleanup operations"""
    
    SCRIPT_DIR = Path.home() / "leerov-tools"
    
    # Cache path definitions organized by category
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
            "Library/Caches/com.apple.akd",
            "Library/Caches/com.apple.ap.adprivacyd",
            "Library/Caches/com.apple.appstore",
            "Library/Caches/com.apple.appstoreagent",
            "Library/Caches/com.apple.cache_delete",
            "Library/Caches/com.apple.commerce",
            "Library/Caches/com.apple.iCloudHelper",
            "Library/Caches/com.apple.imfoundation.IMRemoteURLConnectionAgent",
            "Library/Caches/com.apple.keyboardservicesd",
            "Library/Caches/com.apple.nbagent",
            "Library/Caches/com.apple.nsservicescache.plist",
            "Library/Caches/com.apple.nsurlsessiond",
            "Library/Caches/storeassetd",
            "Library/Caches/com.apple.touristd",
            "Library/Caches/com.apple.tiswitcher.cache",
            "Library/Caches/com.apple.preferencepanes.usercache",
            "Library/Caches/com.apple.preferencepanes.searchindexcache",
            "Library/Caches/com.apple.parsecd",
            "Library/42_cache",
        ],
        "browsers": [
            "Library/Application Support/Firefox/Profiles/*/storage",
            "Library/Application Support/Google/Chrome/Default/Service Worker/CacheStorage/*",
            "Library/Application Support/Google/Chrome/Crashpad/completed/*",
            "Library/Safari/*",
            "Library/Containers/com.apple.Safari/Data/Library/Caches/*",
        ],
        "development": [
            ".kube/cache/*",
            "Library/Developer/Xcode/DerivedData/*",
            "Library/Application Support/Code/User/workspaceStorage",
            "Library/Application Support/Code/CacheData",
            "Library/Application Support/Code/Cache",
            "Library/Application Support/Code/Crashpad/completed",
            "Library/Application Support/Code/CachedData",
            "Library/Application Support/Code/CachedExtension",
            "Library/Application Support/Code/CachedExtensions",
            "Library/Application Support/Code/CachedExtensionVSIXs",
            "Library/Application Support/Code/Code Cache",
            "Library/Application Support/Code/CachedData/*",
            "Library/Application Support/Code/Crashpad/completed/*",
            "Library/Application Support/Code/User/workspaceStorage/*",
            "Library/Caches/com.microsoft.VSCode.ShipIt",
            "Library/Caches/com.microsoft.VSCode",
        ],
        "multimedia": [
            "Library/Application Support/Spotify/PersistentCache",
        ],
        "google": [
            "Library/Caches/com.google.SoftwareUpdate",
            "Library/Caches/com.google.Keystone",
        ],
        "docker": [
            "Library/Containers/com.docker.docker/Data/vms/*",
        ],
        "trash": [
            ".Trash/*",
        ],
        "misc": [
            "leerov-tools/*.out",
            "Desktop/*.log",
            "Desktop/*.tmp",
            ".npm",
            ".nvm",
        ],
    }
    
    # File patterns for analysis
    FILE_PATTERNS = {
        "video": ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.wmv", "*.flv"],
        "archives": ["*.dmg", "*.iso", "*.zip", "*.rar", "*.7z", "*.tar.gz", "*.pkg"],
        "development": ["*.node_modules", "*.docker", "*.vdi", "*.vmdk", "*.qcow2"],
    }
    
    def __init__(self):
        """Initialize the cleaner with home directory"""
        self.home = Path.home()
    
    @staticmethod
    def run_command(cmd: str) -> str:
        """Run a shell command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.SubprocessError, OSError):
            return ""
    
    def get_disk_usage(self, path: Path) -> Optional[DiskUsage]:
        """Get disk usage for a path"""
        output = self.run_command(f"df -h {path} 2>/dev/null | tail -1")
        if output:
            parts = output.split()
            if len(parts) >= 4:
                return DiskUsage(parts[1], parts[2], parts[3])
        return None
    
    def show_disk_space(self, phase: str) -> None:
        """Display disk space information"""
        print(f"{Color.PURPLE}|----|{phase}|----|")
        print(f"{Color.PURPLE}|{Color.BLUE}Size  {Color.PURPLE}|  {Color.RED}Used  {Color.PURPLE}|  {Color.GREEN}Avail {Color.PURPLE}|{Color.RESET}")
        
        # Try home directory first, fallback to root
        usage = self.get_disk_usage(self.home) or self.get_disk_usage(Path("/"))
        
        if usage:
            print(f"{Color.PURPLE}|{Color.BLUE}{usage.total} {Color.PURPLE}=  {Color.RED}{usage.used} {Color.PURPLE}+  {Color.GREEN}{usage.available} {Color.PURPLE}|{Color.RESET}")
        else:
            print(f"{Color.RED}Unable to get disk space info{Color.RESET}")
    
    def get_largest_files(self, directory: Path, limit: int = 10) -> List[FileInfo]:
        """Get largest files in directory"""
        files = []
        try:
            for filepath in directory.rglob('*'):
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
    
    def find_files_by_pattern(self, directory: Path, patterns: List[str], min_size_mb: int = 100, limit: int = 3) -> List[FileInfo]:
        """Find files matching patterns with minimum size"""
        result = []
        try:
            for pattern in patterns:
                for filepath in directory.rglob(pattern):
                    if filepath.is_file():
                        try:
                            size = filepath.stat().st_size
                            if size > min_size_mb * 1024 ** 2:
                                result.append(FileInfo(size, filepath))
                        except (OSError, PermissionError):
                            continue
            result.sort(key=lambda x: x.size, reverse=True)
            return result[:limit]
        except (OSError, PermissionError):
            return []
    
    def show_largest_files_full(self, directory: Optional[Path] = None) -> None:
        """Show top 10 largest files and analysis"""
        directory = directory or self.home
        
        print(f"{Color.PURPLE}|----| Top 10 Largest Files |----|{Color.RESET}")
        print(f"{Color.CYAN}Searching in: {directory}{Color.RESET}\n")
        
        # Count total files
        try:
            file_count = sum(1 for _ in directory.rglob('*') if _.is_file())
            print(f"{Color.YELLOW}📁 Total files scanned: {file_count}{Color.RESET}\n")
        except (OSError, PermissionError):
            print(f"{Color.YELLOW}📁 Total files scanned: (unable to count){Color.RESET}\n")
        
        # Show top 10 largest files
        top_files = self.get_largest_files(directory)
        if top_files:
            print(f"{'Size':<8}  Full Path")
            print("--------  ------------------------------------------------------------")
            for file_info in top_files:
                print(f"{Color.PURPLE}{file_info.size_human:>8}{Color.RESET}  {file_info.color}{file_info.path}{Color.RESET}")
        
        print(f"\n{Color.PURPLE}|----| File Type Analysis |----|{Color.RESET}\n")
        print(f"{Color.BOLD}📊 Largest files by type:{Color.NORMAL}\n")
        
        # Analyze by file types
        for category, patterns in self.FILE_PATTERNS.items():
            display_name = {
                "video": "🎬 Video files (>100MB)",
                "archives": "🗃️  Archives & Disk Images (>100MB)",
                "development": "💻 Development files (>50MB)",
            }.get(category, category.title())
            
            min_size = 50 if category == "development" else 100
            files = self.find_files_by_pattern(directory, patterns, min_size)
            
            print(f"{Color.BLUE}{display_name}:{Color.RESET}")
            if files:
                for file_info in files[:3]:
                    print(f"  {file_info.size_human:<7} {file_info.path}")
            else:
                print("  None found")
            print()
        
        # Show largest directories
        print(f"{Color.PURPLE}|----| Largest Directories |----|{Color.RESET}\n")
        print(f"{Color.BOLD}📁 Top 5 Largest Directories:{Color.NORMAL}\n")
        
        self.show_largest_directories(directory)
    
    def show_largest_directories(self, directory: Path) -> None:
        """Show largest directories"""
        dirs = []
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    try:
                        output = self.run_command(f"du -sh {item} 2>/dev/null")
                        if output:
                            size_str, _ = output.split('\t', 1)
                            size_num = self.parse_size_for_sorting(size_str)
                            dirs.append((size_num, size_str, item))
                    except ValueError:
                        continue
            
            dirs.sort(key=lambda x: x[0], reverse=True)
            for size_num, size_str, item in dirs[:5]:
                color = self.get_size_color(size_str)
                print(f"{Color.PURPLE}{size_str:>8}{Color.RESET}  {color}{item}{Color.RESET}")
        except (OSError, PermissionError) as e:
            print(f"  Unable to scan directories: {e}")
    
    @staticmethod
    def parse_size_for_sorting(size_str: str) -> float:
        """Parse size string for sorting"""
        if size_str.endswith('G'):
            return float(size_str[:-1]) * 1024
        if size_str.endswith('M'):
            return float(size_str[:-1])
        if size_str.endswith('K'):
            return float(size_str[:-1]) / 1024
        try:
            return float(size_str) / 1024 / 1024
        except ValueError:
            return 0
    
    @staticmethod
    def get_size_color(size_str: str) -> str:
        """Get color based on size string"""
        if size_str.endswith('G'):
            return Color.RED
        if size_str.endswith('M'):
            return Color.YELLOW
        return Color.GREEN
    
    def cleanup_paths(self) -> int:
        """Clean up cache paths"""
        cleaned_count = 0
        
        # Clean all cache paths
        cleaned_count += self.clean_cache_paths()
        
        # Clean old downloads
        cleaned_count += self.clean_old_downloads()
        
        # Clean additional caches
        cleaned_count += self.clean_additional_caches()
        
        return cleaned_count
    
    def clean_cache_paths(self) -> int:
        """Clean all configured cache paths"""
        cleaned = 0
        
        for category, paths in self.CACHE_PATHS.items():
            for path_pattern in paths:
                path = self.home / path_pattern
                cleaned += self.clean_path(str(path))
        
        return cleaned
    
    def clean_path(self, path_pattern: str) -> int:
        """Clean a single path or glob pattern"""
        cleaned = 0
        
        if '*' in path_pattern:
            try:
                for item in glob.glob(path_pattern, recursive=True):
                    if os.path.exists(item):
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
                try:
                    if os.path.isdir(path_pattern):
                        shutil.rmtree(path_pattern, ignore_errors=True)
                    else:
                        os.remove(path_pattern)
                    cleaned += 1
                except (OSError, PermissionError):
                    pass
        
        return cleaned
    
    def clean_old_downloads(self) -> int:
        """Clean old files in Downloads directory"""
        cleaned = 0
        downloads_dir = self.home / "Downloads"
        
        if downloads_dir.exists():
            for pattern in ["*.dmg", "*.zip", "*.pkg"]:
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
        """Clean additional cache directories"""
        cleaned = 0
        app_support = self.home / "Library/Application Support"
        
        if app_support.exists():
            try:
                for item in app_support.rglob("*cache*"):
                    if item.is_dir():
                        try:
                            shutil.rmtree(item, ignore_errors=True)
                            cleaned += 1
                        except (OSError, PermissionError):
                            pass
            except (OSError, PermissionError):
                pass
        
        return cleaned
    
    def run(self) -> None:
        """Main execution method"""
        self.show_disk_space("Before cleanup")
        
        cleaned_count = self.cleanup_paths()
        
        print()
        print(f"{Color.PURPLE}Cleaned {cleaned_count} items")
        print()
        
        self.show_disk_space("After cleanup")
        print(f"{Color.PURPLE}|----|Cleanup ended|----|{Color.RESET}")
        
        self.show_largest_files_full()


def main() -> None:
    """Entry point"""
    cleaner = SystemCleaner()
    cleaner.run()


if __name__ == "__main__":
    main()
