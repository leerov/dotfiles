#!/usr/bin/env python3
"""
Установщик необходимых инструментов для окружения.
Устанавливает font-hack-nerd-font, Neovim и Starship.
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
    """Скачивает последнюю стабильную версию Neovim для macOS и распаковывает в ~/nvim-macos-x86_64,
    затем создаёт симлинк ~/bin/nvim."""
    target_dir = os.path.expanduser("~/nvim-macos-x86_64")
    if os.path.exists(target_dir):
        print(f"✅ Neovim already exists at {target_dir}")
        # Всё равно создадим ссылку (на случай, если её нет)
        create_nvim_symlink(target_dir)
        return

    print("📦 Downloading Neovim...")
    url = "https://github.com/neovim/neovim/releases/download/stable/nvim-macos-x86_64.tar.gz"
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        try:
            urllib.request.urlretrieve(url, tmp.name)
        except Exception as e:
            print(f"❌ Failed to download Neovim: {e}")
            return

        print("📦 Extracting Neovim...")
        try:
            with tarfile.open(tmp.name, "r:gz") as tar:
                tar.extractall(path=os.path.dirname(target_dir))
            # Переименовываем извлечённую папку
            extracted = os.path.join(os.path.dirname(target_dir), "nvim-macos-x86_64")
            if not os.path.exists(extracted):
                import glob
                dirs = glob.glob(os.path.join(os.path.dirname(target_dir), "nvim-*"))
                if dirs:
                    os.rename(dirs[0], target_dir)
                else:
                    print("❌ Could not find extracted Neovim directory")
                    return
            else:
                os.rename(extracted, target_dir)
            print(f"✅ Neovim extracted to {target_dir}")
            create_nvim_symlink(target_dir)
        except Exception as e:
            print(f"❌ Failed to extract Neovim: {e}")
        finally:
            os.unlink(tmp.name)

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

    # Проверяем, установлен ли уже starship (но для надёжности переустановим)
    print("🚀 Installing Starship via official installer...")
    cmd = f"curl -sS https://starship.rs/install.sh | sh -s -- --bin-dir {bin_dir} -y"
    run(cmd, check=True)
    print("✅ Starship installed")

def main():
    if platform.system() != "Darwin":
        print("⚠️ This script is intended for macOS.")

    print("🚀 Starting installation of Font Hack Nerd Font, Neovim, and Starship...")

    # 1. Убедиться, что Homebrew установлен и активирован
    if not ensure_brew():
        print("❌ Cannot proceed without Homebrew")
        sys.exit(1)

    # 2. Установка шрифта через brew cask
    brew_cask_install(["font-hack-nerd-font"])

    # 3. Скачивание Neovim
    download_neovim()

    # 4. Установка Starship
    install_starship()

    print("✅ Installation complete!")
    print("📝 Next steps:")
    print("  - Restart your shell or run 'source ~/.zshrc'.")
    print("  - You may need to set up your terminal to use the font.")
    print("  - Check that 'nvim' and 'starship' are in your PATH (e.g., ~/bin).")

if __name__ == "__main__":
    main()
