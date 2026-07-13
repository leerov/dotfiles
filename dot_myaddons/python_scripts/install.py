#!/usr/bin/env python3
"""
Установщик необходимых инструментов для окружения.
Устанавливает font-hack-nerd-font, Neovim (в ~/nvim-{arch} с симлинком ~/bin/nvim) и Starship (в ~/bin).
"""
import subprocess
import sys
import os
import shutil
import platform

def run(cmd, check=True, cwd=None):
    print(f"⚙️  Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=check, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def is_installed(cmd):
    return shutil.which(cmd) is not None

def ensure_brew():
    """Убеждается, что Homebrew установлен и активирован."""
    if is_installed("brew"):
        print("✅ Homebrew already installed")
        return True

    brew_script = os.path.expanduser("~/.myaddons/zsh_scripts/brew.sh")
    if not os.path.exists(brew_script):
        print("❌ brew.sh not found. Please ensure dotfiles are applied correctly.")
        return False

    print("🍺 Installing/activating Homebrew via brew.sh...")
    run(f"bash -c 'source {brew_script} && brewSetup'", check=False)

    user = os.environ.get("USER", "")
    brew_p wqath = f"/opt/goinfre/{user}/homebrew/bin"
    if os.path.exists(brew_path):
        os.environ["PATH"] = brew_path + ":" + os.environ.get("PATH", "")

    if is_installed("brew"):
        print("✅ Homebrew is ready")
        return True
    else:
        print("❌ Failed to set up Homebrew")
        return False

def brew_cask_install(packages):
    if not packages:
        return
    packages_str = " ".join(packages)
    run(f"brew install --cask {packages_str}")

def download_neovim():
    """
    Скачивает последнюю стабильную версию Neovim для macOS (определяет архитектуру),
    распаковывает в ~/ и создаёт симлинк ~/bin/nvim.
    """
    home = os.path.expanduser("~")
    bin_dir = os.path.join(home, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    # Определяем архитектуру
    arch = platform.machine().lower()
    if arch in ("x86_64", "amd64"):
        nvim_arch = "x86_64"
    elif arch in ("arm64", "aarch64"):
        nvim_arch = "arm64"
    else:
        print(f"⚠️ Unknown architecture '{arch}', defaulting to x86_64")
        nvim_arch = "x86_64"

    target_dir = os.path.join(home, f"nvim-macos-{nvim_arch}")
    archive_name = f"nvim-macos-{nvim_arch}.tar.gz"
    url = f"https://github.com/neovim/neovim/releases/latest/download/{archive_name}"

    # Если папка уже существует, не перезаписываем, но проверим ссылку
    if os.path.exists(target_dir):
        print(f"✅ Neovim directory already exists at {target_dir}")
        create_nvim_symlink(target_dir)
        return

    print(f"📦 Downloading Neovim ({nvim_arch}) via curl...")
    # Скачиваем архив в домашнюю директорию
    run(f"curl -LO {url}", cwd=home, check=True)

    # Проверяем, что архив скачался
    archive_path = os.path.join(home, archive_name)
    if not os.path.exists(archive_path):
        print(f"❌ Failed to download {archive_name}")
        return

    print(f"📦 Extracting Neovim to {home}...")
    run(f"tar -xzf {archive_path} -C {home}", check=True)

    # Удаляем архив
    os.remove(archive_path)
    print(f"✅ Neovim extracted to {target_dir}")

    # Создаём симлинк
    create_nvim_symlink(target_dir)

def create_nvim_symlink(nvim_dir):
    """Создаёт символическую ссылку ~/bin/nvim -> nvim_dir/bin/nvim"""
    bin_dir = os.path.expanduser("~/bin")
    os.makedirs(bin_dir, exist_ok=True)
    link_path = os.path.join(bin_dir, "nvim")
    target = os.path.join(nvim_dir, "bin", "nvim")

    if not os.path.exists(target):
        print(f"⚠️ Neovim binary not found at {target}, skipping symlink")
        return

    # Удаляем старую ссылку/файл, если есть
    if os.path.exists(link_path) or os.path.islink(link_path):
        os.remove(link_path)

    os.symlink(target, link_path)
    print(f"🔗 Symlink created: {link_path} -> {target}")

def install_starship():
    """Устанавливает Starship через официальный установщик в ~/bin"""
    bin_dir = os.path.expanduser("~/bin")
    os.makedirs(bin_dir, exist_ok=True)

    print("🚀 Installing Starship via official installer...")
    cmd = f"curl -sS https://starship.rs/install.sh | sh -s -- --bin-dir {bin_dir} -y"
    run(cmd, check=True)
    print("✅ Starship installed")

def main():
    if platform.system() != "Darwin":
        print("⚠️ This script is intended for macOS.")

    print("🚀 Starting installation of Font Hack Nerd Font, Neovim, and Starship...")

    # 1. Homebrew
    if not ensure_brew():
        print("❌ Cannot proceed without Homebrew")
        sys.exit(1)

    # 2. Шрифт
    brew_cask_install(["font-hack-nerd-font"])

    # 3. Neovim (скачивание через curl, распаковка в ~, симлинк)
    download_neovim()

    # 4. Starship
    install_starship()

    print("✅ Installation complete!")
    print("📝 Next steps:")
    print("  - Restart your shell or run 'source ~/.zshrc'.")
    print("  - Make sure ~/bin is in your PATH (add 'export PATH=\"$HOME/bin:$PATH\"' if not).")
    print("  - Check that 'nvim' and 'starship' are available.")

if __name__ == "__main__":
    main()
