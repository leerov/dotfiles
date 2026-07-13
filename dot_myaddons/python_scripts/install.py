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

def brew_install(packages):
    if not packages:
        return
    packages_str = " ".join(packages)
    run(f"brew install {packages_str}")

def brew_cask_install(packages):
    if not packages:
        return
    packages_str = " ".join(packages)
    run(f"brew install --cask {packages_str}")

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

    brew_packages = [
        "neovim", "tmux", "git", "zsh", "starship",
        "fzf", "ripgrep", "lazygit",
        "lua-language-server", "pyright",
        "node", "python3"
    ]
    brew_install(brew_packages)

    brew_cask_install(["font-hack-nerd-font"])

    pip_packages = ["flask", "flask-sock"]
    install_pip_packages(pip_packages)

    setup_tpm()

    setup_ap()

    install_code_server()

    if not is_installed("chezmoi"):
        print("📦 Installing chezmoi...")
        run("brew install chezmoi")

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