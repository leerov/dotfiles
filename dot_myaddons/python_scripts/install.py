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
import zipfile
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

def run_with_brew(cmd):
    """Выполняет команду в окружении с активированным Homebrew."""
    brew_script = os.path.expanduser("~/.myaddons/zsh_scripts/brew.sh")
    if not os.path.exists(brew_script):
        print("⚠️ brew.sh not found, skipping brew commands")
        return None
    full_cmd = f"source {brew_script} && brewActivate && {cmd}"
    return run(f"bash -c '{full_cmd}'", check=False)

def is_installed(cmd):
    return shutil.which(cmd) is not None

def brew_install(packages):
    if not packages:
        return
    packages_str = " ".join(packages)
    run_with_brew(f"brew install {packages_str}")

def brew_cask_install(packages):
    if not packages:
        return
    packages_str = " ".join(packages)
    run_with_brew(f"brew install --cask {packages_str}")

def install_pip_packages(packages):
    for pkg in packages:
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
    # Используем известный стабильный релиз (можно заменить на последний, но для надёжности фиксируем)
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
            # Переименовываем извлечённую папку (обычно она называется nvim-macos-x86_64)
            extracted = os.path.join(os.path.dirname(target_dir), "nvim-macos-x86_64")
            if not os.path.exists(extracted):
                # может быть другое имя, поищем
                import glob
                dirs = glob.glob(os.path.join(os.path.dirname(target_dir), "nvim-*"))
                if dirs:
                    os.rename(dirs[0], target_dir)
                else:
                    print("❌ Could not find extracted Neovim directory")
                    return
            else:
                os.rename(extracted, target_dir)  # если уже существует, но мы проверили выше
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
    # Определяем архитектуру (для macOS universal)
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
                # Ищем файл starship
                for member in tar.getmembers():
                    if member.name == "starship":
                        member.name = os.path.basename(member.name)
                        tar.extract(member, path=bin_dir)
                        break
            # Делаем исполняемым
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
        print("⚠️ npm not found, installing via brew...")
        brew_install(["node"])
    run("npm install -g code-server")

def main():
    if platform.system() != "Darwin":
        print("⚠️ This script is intended for macOS.")

    print("🚀 Starting installation of development tools...")

    # Сначала установим основные пакеты через brew (активируем brew через brew.sh)
    brew_packages = [
        "tmux", "git", "zsh",
        "fzf", "ripgrep", "lazygit",
        "lua-language-server", "pyright",
        "node", "python3"
    ]
    brew_install(brew_packages)
    brew_cask_install(["font-hack-nerd-font"])

    # Устанавливаем Python пакеты
    pip_packages = ["flask", "flask-sock"]
    install_pip_packages(pip_packages)

    # Скачиваем Neovim и Starship напрямую
    download_neovim()
    download_starship()

    setup_tpm()
    setup_ap()
    install_code_server()

    if not is_installed("chezmoi"):
        print("📦 Installing chezmoi...")
        run("brew install chezmoi")  # можно тоже через brew_install, но оставим так

    print("🔄 Applying dotfiles with chezmoi...")
    run("chezmoi apply", check=False)

    install_neovim_plugins()

    print("✅ Installation complete!")
    print("📝 Next steps:")
    print("  - Start tmux and press prefix+I to install TPM plugins.")
    print("  - Restart your shell or run 'source ~/.zshrc'.")
    print("  - If chezmoi apply failed, run it manually from the dotfiles repo.")

if __name__ == "__main__":
    main()