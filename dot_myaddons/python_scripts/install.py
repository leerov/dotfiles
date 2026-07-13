#!/usr/bin/env python3
"""
Установщик необходимых инструментов для окружения.
Устанавливает font-hack-nerd-font, Neovim (в ~/nvim-macos-x86_64 с симлинком ~/bin/nvim) и Starship (в ~/bin).
"""
import subprocess
import sys
import os
import shutil
import platform
import urllib.request
import tarfile
import tempfile
import stat
import glob

def run(cmd, check=True):
    print(f"⚙️  Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=check)
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
    brew_path = f"/opt/goinfre/{user}/homebrew/bin"
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
    Скачивает последнюю стабильную версию Neovim для macOS x86_64,
    распаковывает в ~/nvim-macos-x86_64 и создаёт симлинк ~/bin/nvim.
    """
    home = os.path.expanduser("~")
    target_dir = os.path.join(home, "nvim-macos-x86_64")
    bin_dir = os.path.join(home, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    # Если папка уже существует, не перезаписываем, но проверим ссылку
    if os.path.exists(target_dir):
        print(f"✅ Neovim directory already exists at {target_dir}")
        create_nvim_symlink(target_dir)
        return

    print("📦 Downloading Neovim...")
    url = "https://github.com/neovim/neovim/releases/download/stable/nvim-macos-x86_64.tar.gz"
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = tmp.name
        try:
            urllib.request.urlretrieve(url, tmp_path)
        except Exception as e:
            print(f"❌ Failed to download Neovim: {e}")
            return

        print("📦 Extracting Neovim...")
        try:
            with tarfile.open(tmp_path, "r:gz") as tar:
                tar.extractall(path=home)
            # После распаковки в home появится папка типа nvim-macos-x86_64 (или nvim-...)
            # Убедимся, что она называется именно так
            extracted = os.path.join(home, "nvim-macos-x86_64")
            if not os.path.exists(extracted):
                # Возможно, имя немного отличается (например, nvim-macos-arm64)
                dirs = glob.glob(os.path.join(home, "nvim-*"))
                if dirs:
                    # Берём первую найденную папку и переименовываем
                    old = dirs[0]
                    os.rename(old, extracted)
                    print(f"✅ Renamed {old} to {extracted}")
                else:
                    print("❌ Could not find extracted Neovim directory")
                    return
            else:
                print(f"✅ Neovim extracted to {extracted}")
            create_nvim_symlink(extracted)
        except Exception as e:
            print(f"❌ Failed to extract Neovim: {e}")
        finally:
            os.unlink(tmp_path)

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

    # 3. Neovim (в ~/nvim-macos-x86_64 + симлинк)
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
