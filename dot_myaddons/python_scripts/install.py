#!/usr/bin/env python3
"""
Установщик необходимых инструментов для окружения.
Запускайте из корня проекта dotfiles.
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

def run(cmd, check=True, capture=False):
    print(f"⚙️  Running: {cmd}")
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if capture:
            return None
        sys.exit(1)

def is_installed(cmd):
    return shutil.which(cmd) is not None

def ensure_brew():
    """Убеждается, что Homebrew установлен и активирован."""
    # Сначала попробуем найти brew в стандартных местах
    if is_installed("brew"):
        print("✅ Homebrew already installed")
        return True

    brew_script = os.path.expanduser("~/.myaddons/zsh_scripts/brew.sh")
    if not os.path.exists(brew_script):
        print("❌ brew.sh not found. Please ensure dotfiles are applied correctly.")
        return False

    print("🍺 Installing/activating Homebrew via brew.sh...")
    # Вызываем brewSetup, который установит brew при необходимости
    result = run(f"bash -c 'source {brew_script} && brewSetup'", check=False)

    # После установки добавляем путь к brew в PATH
    user = os.environ.get("USER", "")
    brew_path = f"/opt/goinfre/{user}/homebrew/bin"
    if os.path.exists(brew_path):
        os.environ["PATH"] = brew_path + ":" + os.environ.get("PATH", "")

    # Проверяем снова
    if is_installed("brew"):
        print("✅ Homebrew is ready")
        return True
    else:
        print("❌ Failed to set up Homebrew")
        return False

def brew_install(packages):
    if not packages:
        return
    # Фильтруем уже установленные пакеты
    to_install = []
    for pkg in packages:
        if not is_installed(pkg):
            to_install.append(pkg)
        else:
            print(f"✅ {pkg} already installed")
    if not to_install:
        return
    packages_str = " ".join(to_install)
    # После ensure_brew, brew должен быть в PATH
    run(f"brew install {packages_str}")

def brew_cask_install(packages):
    if not packages:
        return
    to_install = []
    for pkg in packages:
        # Для cask сложно проверить наличие, просто пробуем установить
        to_install.append(pkg)
    if not to_install:
        return
    packages_str = " ".join(to_install)
    run(f"brew install --cask {packages_str}")

def install_pip_packages(packages):
    for pkg in packages:
        if is_installed(f"pip3 show {pkg}"):
            print(f"✅ {pkg} already installed")
            continue
        run(f"pip3 install {pkg}")

def clone_repo(repo_url, dest):
    if os.path.exists(dest):
        print(f"✅ {dest} already exists")
        return
    run(f"git clone {repo_url} {dest}")

def setup_tpm():
    tpm_dir = os.path.expanduser("~/.tmux/plugins/tpm")
    clone_repo("https://github.com/tmux-plugins/tpm", tpm_dir)

def install_neovim_plugins():
    if not is_installed("nvim"):
        print("⚠️ Neovim not installed, skipping plugin installation")
        return
    print("📦 Installing Neovim plugins...")
    run("nvim --headless +Lazy sync +qa", check=False)

def setup_ap():
    user = os.environ.get("USER", "")
    ap_path = f"/opt/goinfre/{user}/ap"
    if not os.path.exists("/opt/goinfre"):
        ap_path = os.path.expanduser("~/ap")
    if os.path.exists(ap_path):
        print(f"✅ AP already exists at {ap_path}")
        return
    print(f"📦 Cloning AP to {ap_path}...")
    run(f"git clone https://github.com/unxed/ap.git {ap_path}")

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
    """Скачивает бинарник Starship и помещает в ~/bin/starship"""
    bin_dir = os.path.expanduser("~/bin")
    os.makedirs(bin_dir, exist_ok=True)
    target = os.path.join(bin_dir, "starship")
    if os.path.exists(target):
        print(f"✅ Starship already exists at {target}")
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
        except Exception as e:
            print(f"❌ Failed to extract Starship: {e}")
        finally:
            os.unlink(tmp.name)

def install_code_server():
    if is_installed("code-server"):
        print("✅ code-server already installed")
        return
    if not is_installed("npm"):
        print("⚠️ npm not found, installing node via brew...")
        brew_install(["node"])
    run("npm install -g code-server")

def main():
    if platform.system() != "Darwin":
        print("⚠️ This script is intended for macOS.")

    print("🚀 Starting installation of development tools...")

    # 1. Убедиться, что Homebrew установлен и активирован
    if not ensure_brew():
        print("❌ Cannot proceed without Homebrew")
        sys.exit(1)

    # 2. Установка пакетов через brew
    brew_packages = [
        "tmux", "git", "zsh", "fzf", "ripgrep", "lazygit",
        "lua-language-server", "pyright", "node", "python3"
    ]
    brew_install(brew_packages)
    brew_cask_install(["font-hack-nerd-font"])

    # 3. Python пакеты
    pip_packages = ["flask", "flask-sock"]
    install_pip_packages(pip_packages)

    # 4. Скачивание Neovim и Starship напрямую
    download_neovim()
    download_starship()

    # 5. Дополнительные инструменты
    setup_tpm()
    setup_ap()
    install_code_server()

    # 6. Установка chezmoi (если ещё нет)
    if not is_installed("chezmoi"):
        print("📦 Installing chezmoi...")
        brew_install(["chezmoi"])

    # 7. Применение dotfiles
    print("🔄 Applying dotfiles with chezmoi...")
    run("chezmoi apply", check=False)

    # 8. Установка плагинов Neovim
    install_neovim_plugins()

    print("✅ Installation complete!")
    print("📝 Next steps:")
    print("  - Start tmux and press prefix+I to install TPM plugins.")
    print("  - Restart your shell or run 'source ~/.zshrc'.")
    print("  - If chezmoi apply failed, run it manually from the dotfiles repo.")

if __name__ == "__main__":
    main()