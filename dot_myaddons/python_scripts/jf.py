#!/usr/bin/env python3
import os
import subprocess
import tempfile
import sys
import shutil
from pathlib import Path

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

def get_clipboard_read_cmd():
    if shutil.which("pbpaste"):
        return "pbpaste"
    elif shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard", "-o"]
    elif shutil.which("powershell"):
        return ["powershell", "-command", "Get-Clipboard"]
    return None
def get_clipboard_write_cmd():
    if shutil.which("pbcopy"):
        return "pbcopy"
    elif shutil.which("xclip"):
        return ["xclip", "-selection", "clipboard"]
    elif shutil.which("clip.exe"):
        return "clip.exe"
    return None

def main():
    if not ensure_ap():
        sys.exit(1)
    clip_cmd = get_clipboard_read_cmd()
    if clip_cmd is None:
        print("❌ No clipboard command found")
        sys.exit(1)
    try:
        proc = subprocess.run(clip_cmd if isinstance(clip_cmd, str) else clip_cmd, capture_output=True, check=True)
        patch_content = proc.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to read clipboard: {e}")
        sys.exit(1)
    if not patch_content:
        print("❌ Clipboard is empty.")
        sys.exit(1)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".ap")
    tmpfile.write(patch_content)
    tmpfile.close()
    ap_py = AP_HOME / "implementation" / "ap.py"
    try:
        result = subprocess.run(
            ["python3", str(ap_py), tmpfile.name] + sys.argv[1:],
            capture_output=True,
            text=True
        )
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        output = result.stdout + result.stderr
        if output:
            write_cmd = get_clipboard_write_cmd()
            if write_cmd:
                proc_write = subprocess.Popen(
                    write_cmd if isinstance(write_cmd, str) else write_cmd,
                    stdin=subprocess.PIPE
                )
                proc_write.communicate(input=output.encode())
                if proc_write.returncode != 0:
                    print("⚠️ Warning: Failed to copy output to clipboard")
            else:
                print("⚠️ Warning: No clipboard write command found")
        else:
            print("ℹ️ No output from ap.py")
    finally:
        os.unlink(tmpfile.name)
        failed = Path("afailed.ap")
        if failed.exists():
            failed.unlink()

if __name__ == "__main__":
    main()