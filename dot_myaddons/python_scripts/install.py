#!/usr/bin/env python3
"""
Установщик необходимых инструментов для окружения.
Устанавливает только font-hack-nerd-font, Neovim и Starship.
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

    # После установки добавляем путь к brew в PATH
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
    """Скачивает последнюю стабильную версию Neovim для macOS и распаковывает в ~/nvim-macos-x86_64"""
    target_dir = os.path.expanduser("~/nvim-macos-x86_64")
    if os.path.exists(target_dir):
        print(f"✅ Neovim already exists at {target_dir}")
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
        except Exception as e:
            print(f"❌ Failed to extract Neovim: {e}")
        finally:
            os.unlink(tmp.name)

def download_starship():
    """Скачивает бинарник Starship и помещает в ~/bin/starship (перезаписывает, если уже существует)"""
    bin_dir = os.path.expanduser("~/bin")
    os.makedirs(bin_dir, exist_ok=True)
    target = os.path.join(bin_dir, "starship")

    # Если файл существует, удаляем его для принудительной перезаписи
    if os.path.exists(target):
        print(f"🔄 Starship already exists, will re-download (overwrite)")
        try:
            os.remove(target)
        except Exception as e:
            print(f"⚠️ Could not remove old starship: {e}")
            return

    print("📦 Downloading Starship...")
    url = "https://github.com/starship/starship/releases/latest/download/starship-x86_64-apple-darwin.tar.gz"
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        try:
            urllib.request.urlretrieve(url, tmp.name)
        except Exception as e:
            print(f"❌ Failed to download Starship: {e}")
            return

        print("📦 Extracting Starship...")
        try:
            with tarfile.open(tmp.name, "r:gz") as tar:
                for member in tar.getmembers():
                    if member.name == "starship":
                        member.name = os.path.basename(member.name)
                        tar.extract(member, path=bin_dir)
                        break
            os.chmod(target, os.stat(target).st_mode | stat.S_IEXEC)
            print(f"✅ Starship installed to {target}")
        except Exception as e:
            print(f"❌ Failed to extract Starship: {e}")
        finally:
            os.unlink(tmp.name)

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

    # 3. Скачивание Neovim и Starship напрямую
    download_neovim()
    download_starship()

    print("✅ Installation complete!")
    print("📝 Next steps:")
    print("  - Restart your shell or run 'source ~/.zshrc'.")
    print("  - You may need to set up your terminal to use the font.")

if __name__ == "__main__":
    main()