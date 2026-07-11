#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
from pathlib import Path

# ---------- Configuration ----------
# Максимальный размер файла (в байтах), который будет прочитан
MAX_FILE_SIZE = 1_000_000  # 1 МБ

IGNORE_DIRS = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "build",
    "dist",
    ".idea",
    ".vscode",
    "target",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    ".eggs",
    ".gradle",
    ".next",
    "out",
    ".output",
    ".serverless",
    ".terraform",
    ".parcel-cache",
    ".webpack",
    ".sass-cache",
    ".vite",
    ".yarn",
    ".pnpm-store",
    ".bun",
    "_build",
    "deps",
    ".gleam",
    "_gleam_build",
    ".mix",
    ".cargo",
    ".rustup",
    ".stack-work",
    ".hie-bios",
    ".cabal-sandbox",
    ".cabal",
    ".stack",
    ".nix",
    ".direnv",
    ".env",
    ".virtualenv",
    ".pyenv",
    ".pip",
    ".pypoetry",
    ".conda",
    ".julia",
    ".Rproj.user",
    ".rstudio",
    ".kotlin",
    ".clj-kondo",
    ".lsp",
    ".cljr",
    ".cpcache",
    ".shadow-cljs",
    ".figx",
    ".nrepl",
    ".boot",
    ".lein",
    ".m2",
    ".sbt",
    ".eclipse",
    ".project",
    ".classpath",
    ".settings",
    ".metadata",
    ".DS_Store",
    ".Trashes",
    ".fseventsd",
    ".TemporaryItems",
    ".Trash",
    ".localized",
    ".apdisk",
    ".AppleDouble",
    ".LSOverride",
    ".DocumentRevisions-V100",
    ".PKInstallSandboxManager",
    ".com.apple.timemachine.supported",
    ".com.apple.timemachine.donotpresent",
    ".vol",
    ".cddb",
    ".cpan",
    ".cpcpan",
    ".perl",
    ".go",
    ".gopath",
    ".godoc",
    ".glide",
    ".dep",
    ".vendor",
    ".mod",
    ".sum",
    ".work",
    ".bin",
    ".pkg",
    ".npm",
    ".nvm",
    ".deno",
    ".node",
    ".asdf",
    ".sdkman",
    ".jabba",
    ".coursier",
    ".ivy2",
    ".netbeans",
    ".clion",
    ".pycharm",
    ".intellij",
    ".rubymine",
    ".webstorm",
    ".phpstorm",
    ".goland",
    ".appcode",
    ".datagrip",
    ".rider",
    ".android",
    ".androidstudio",
    ".xcode",
    ".swiftpm",
    ".lldb",
    ".gdb",
    ".clang",
    ".cmake",
    ".ninja",
    ".conan",
    ".vcpkg",
    ".bazel",
    ".pants",
    ".please",
    ".mage",
    ".task",
    ".just",
    ".make",
]

TEXT_EXTS = {
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".hh", ".hxx",
    ".py", ".pyx", ".pyi",
    ".sh", ".bash", ".zsh", ".fish", ".ksh", ".dash",
    ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".html", ".htm", ".xhtml",
    ".css", ".scss", ".sass", ".less", ".styl",
    ".yaml", ".yml", ".toml", ".ini",
    ".md", ".markdown", ".rst", ".tex", ".latex", ".ltx",
    ".lua", ".rb", ".go", ".rs", ".swift", ".kt", ".kts", ".java",
    ".sql", ".psql", ".r", ".m", ".mm", ".pl", ".pm", ".t", ".pod",
    ".php", ".phtml", ".phps", ".asp", ".aspx", ".jsp",
    ".scala", ".sc", ".clj", ".cljs", ".edn", ".erl", ".hrl",
    ".ex", ".exs", ".el", ".lisp", ".cl", ".rkt", ".ss",
    ".dart", ".nim", ".cr", ".zig", ".v", ".vsh", ".fs", ".fsx",
    ".f", ".f90", ".f95", ".f03", ".for", ".ada", ".adb", ".ads",
    ".d", ".di", ".mli", ".ml", ".hs", ".lhs",
    ".asm", ".s", ".S", ".nasm",
    ".cfg", ".conf", ".config", ".cnf",
    ".vim", ".vimrc", ".gvimrc", ".nvimrc",
    ".zshrc", ".bashrc", ".bash_profile", ".profile", ".bash_logout",
    ".gitignore", ".gitattributes", ".gitconfig", ".gitmodules",
    ".dockerfile", "Dockerfile", ".containerfile",
    "Makefile", "makefile", ".mk", ".mak", ".cmake", "CMakeLists.txt",
    ".gradle", ".gradle.kts", ".sbt",
    ".vue", ".svelte", ".astro",
    ".graphql", ".gql",
    ".ejs", ".hbs", ".mustache",
    ".twig", ".jinja", ".jinja2",
    ".ipynb", ".julia", ".jl",
    ".qmd", ".rmd", ".Rnw",
    ".stan", ".bugs", ".jags",
    ".tf", ".tfvars", ".hcl",
    ".sls",
    ".pp",
    ".erb",
    ".ps1", ".psm1", ".psd1",
    ".j2",
    ".txt", ".text",
    ".nfo", ".readme", "README", "CHANGELOG", "LICENSE", "CONTRIBUTING",
    ".adoc", ".asciidoc",
    ".org",
    ".wiki",
    ".rtf",
    ".csv", ".tsv", ".psv",
    ".ics",
    ".desktop",
    ".service", ".timer", ".socket", ".target",
    ".cron", ".tab", "crontab",
    ".sed", ".awk",
    ".regex",
    ".prolog", ".pl", ".p",
    ".env",
    "Procfile",
    "Gemfile", "Gemfile.lock",
    "Rakefile",
    "Cargo.toml", "Cargo.lock",
    "go.mod", "go.sum",
    "requirements.txt", "Pipfile", "Pipfile.lock", "pyproject.toml", "setup.py", "setup.cfg",
    ".pre-commit-config.yaml",
    ".eslintrc", ".prettierrc", ".babelrc",
    ".patch", ".diff",
    ".sig", ".asc",
    ".gcode",
    ".scad",
    ".led",
}

AP_HOME = Path("/opt/goinfre") / os.environ.get("USER", "") / "ap"

def ensure_ap():
    if not AP_HOME.exists():
        print(f"📦 AP not found at {AP_HOME}, cloning...")
        subprocess.run(["git", "clone", "https://github.com/unxed/ap.git", str(AP_HOME)], check=True)
        print("✅ AP cloned successfully")
    if not (AP_HOME / "implementation" / "ap.py").is_file():
        print(f"❌ Error: {AP_HOME / 'implementation' / 'ap.py'} not found")
        return False
    return True

def get_clipboard_write_cmd():
    if shutil.which("pbcopy"):
        return "pbcopy"
    elif shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard"]
    elif shutil.which("clip.exe"):
        return "clip.exe"
    return None

def should_ignore_dir(name, ignore_dirs):
    for pattern in ignore_dirs:
        if pattern.endswith('*'):
            if name.startswith(pattern[:-1]):
                return True
        elif pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        else:
            if name == pattern:
                return True
    return False

def get_tree_output(ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = IGNORE_DIRS
    output = []
    def walk(dir_path, prefix=""):
        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            output.append(prefix + "└── [permission denied]")
            return
        filtered = []
        for name in entries:
            full_path = os.path.join(dir_path, name)
            if os.path.isdir(full_path) and not os.path.islink(full_path):
                if should_ignore_dir(name, ignore_dirs):
                    continue
            filtered.append(name)
        for i, name in enumerate(filtered):
            path = os.path.join(dir_path, name)
            is_last = (i == len(filtered) - 1)
            connector = "└── " if is_last else "├── "
            output.append(prefix + connector + name)
            if os.path.isdir(path) and not os.path.islink(path):
                new_prefix = prefix + ("    " if is_last else "│   ")
                walk(path, new_prefix)
    output.append(".")
    walk(".")
    return "\n".join(output) + "\n"

def collect_code_files(root_dir, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = IGNORE_DIRS
    result_lines = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d, ignore_dirs)]
        for fname in filenames:
            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, root_dir)
            ext = os.path.splitext(fname)[1].lower()
            base = fname
            # Пропускаем слишком большие файлы
            try:
                if os.path.getsize(full_path) > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            if base in TEXT_EXTS or ext in TEXT_EXTS or any(base.startswith(p) for p in ['Dockerfile', 'Makefile', 'Gemfile']):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except (UnicodeDecodeError, PermissionError, OSError):
                    continue
                result_lines.append(f"=== {rel_path} ===")
                result_lines.append(content)
                result_lines.append("")
                result_lines.append("")
    return "\n".join(result_lines)

def main():
    if not ensure_ap():
        sys.exit(1)
    ap_md = AP_HOME / "ap.md"
    if not ap_md.is_file():
        print(f"❌ Error: {ap_md} not found")
        sys.exit(1)

    # Собираем все данные в один большой буфер
    output_parts = []
    output_parts.append("# INSTRUCTIONS FOR AI\n")
    output_parts.append("#\n")
    output_parts.append("# === PROJECT STRUCTURE ===\n")
    output_parts.append("#\n")
    output_parts.append(get_tree_output())
    output_parts.append("\n")
    output_parts.append("# === END OF PROJECT STRUCTURE ===\n")
    output_parts.append("#\n")
    output_parts.append("# Now wait. Do nothing else.\n")
    output_parts.append("# Do not explain anything.\n")
    output_parts.append("# Do not add any comments or extra text.\n")
    output_parts.append("# Just wait for my next message.\n")
    output_parts.append("#\n")
    output_parts.append("# Below is the ap format specification and the current code.\n")
    output_parts.append("# After I tell you what to change, generate TWO things: the AP patch file (inside ```ap``` block) and a bash code block with git commands (git add, git commit -m \"...\", optionally git push).\n")
    output_parts.append("# Do not output anything else besides these two blocks.\n")
    output_parts.append("# If I write something to analyze, the analysis should not contain a patch.\n")
    output_parts.append("# The AP patch must be inside a ```ap``` block, and the git commands inside a ```bash``` block after the patch.\n")
    output_parts.append("# ```ap\n")
    output_parts.append("# *patch*\n")
    output_parts.append("# ```\n")
    output_parts.append("# === AP FORMAT SPECIFICATION ===\n")
    output_parts.append("#\n")
    output_parts.append(ap_md.read_text())
    output_parts.append("\n\n=== CURRENT CODE (with line numbers) ===\n\n")
    output_parts.append(collect_code_files("."))
    output_parts.append("\n\n# === GIT COMMANDS ===\n")
    output_parts.append("#\n")
    output_parts.append("# After applying the patch, you MUST provide TWO things:\n")
    output_parts.append("# 1. The AP patch inside ```ap``` block.\n")
    output_parts.append("# 2. A bash code block with git commands (git add, git commit, optionally git push).\n")
    output_parts.append("#\n")
    output_parts.append("# Example:\n")
    output_parts.append("```bash\n")
    output_parts.append("git add .\n")
    output_parts.append('git commit -m "feat(scope): description"\n')
    output_parts.append("git push\n")
    output_parts.append("```\n")
    output_parts.append("#\n")
    output_parts.append("# Replace <type>, <scope>, and <description> according to Conventional Commits.\n")
    output_parts.append("#\n")
    output_parts.append("\n\n# === WAITING FOR TASK ===\n")
    output_parts.append("#\n")
    output_parts.append("# I have analyzed the project structure and code.\n")
    output_parts.append("# I am ready to generate AP patches.\n")
    output_parts.append("# Just tell me what to change.\n")
    output_parts.append("# If I write something to analyze, the analysis should not contain a patch.\n")
    output_parts.append("# The response MUST contain TWO blocks:\n")
    output_parts.append("# 1. The AP patch inside ```ap``` block.\n")
    output_parts.append("# 2. A bash code block with git commands (git add, git commit, optionally git push).\n")
    output_parts.append("# The patch must be located inside a block of code like:\n")
    output_parts.append("# ```ap\n")
    output_parts.append("# *patch*\n")
    output_parts.append("# ```\n")
    output_parts.append("# The bash block should follow immediately after the patch.\n")
    output_parts.append("# === END ===\n")

    full_data = "".join(output_parts).encode("utf-8")

    clip_cmd = get_clipboard_write_cmd()
    if clip_cmd is None:
        print("❌ No clipboard command found")
        sys.exit(1)

    # Передаём данные напрямую в процесс буфера обмена без временного файла
    proc = subprocess.Popen(
        clip_cmd if isinstance(clip_cmd, str) else clip_cmd,
        stdin=subprocess.PIPE
    )
    proc.communicate(input=full_data)
    if proc.returncode != 0:
        print("❌ Failed to copy to clipboard")
        sys.exit(1)
    print("✅ Copied to clipboard: tree + instructions + ap.md + code contents")

if __name__ == "__main__":
    main()
