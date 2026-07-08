#!/bin/bash
# lib/ap.zsh - AP (AI-friendly Patch) functions

export AP_HOME="/opt/goinfre/$(whoami)/ap"

# Function to ensure ap is installed
_ensure_ap() {
    if [[ ! -d "$AP_HOME" ]]; then
        echo "📦 AP not found at $AP_HOME, cloning..."
        git clone https://github.com/unxed/ap.git "$AP_HOME"
        if [[ $? -eq 0 ]]; then
            echo "✅ AP cloned successfully"
        else
            echo "❌ Failed to clone AP"
            return 1
        fi
    fi
    if [[ ! -f "$AP_HOME/implementation/ap.py" ]]; then
        echo "❌ Error: $AP_HOME/implementation/ap.py not found"
        return 1
    fi
    return 0
}

function fj() {
    _ensure_ap || return 1

    if [[ ! -f "$AP_HOME/ap.md" ]]; then
        echo "❌ Error: $AP_HOME/ap.md not found"
        return 1
    fi

    local tmpfile="/tmp/fj_combined.txt"

    cat > "$tmpfile" << 'EOF'
# INSTRUCTIONS FOR AI
#
# === PROJECT STRUCTURE ===
#
EOF

    tree >> "$tmpfile" 2>/dev/null

    cat >> "$tmpfile" << 'EOF'
#
# === END OF PROJECT STRUCTURE ===
#
# Now wait. Do nothing else.
# Do not explain anything.
# Do not add any comments or extra text.
# Just wait for my next message.
#
# Below is the ap format specification and the current code.
# After I tell you what to change, generate ONLY the ap patch file.
# Nothing else. Just the patch.
# If I write something to analyze, the analysis should not contain a patch.
# The patch must be located inside a block of code like:
# ```ap
# *patch*
# ```
# === AP FORMAT SPECIFICATION ===
#
EOF

    cat "$AP_HOME/ap.md" >> "$tmpfile"

    echo -e "\n\n=== CURRENT CODE (with line numbers) ===\n" >> "$tmpfile"
    sc --stdout --no-numbers >> "$tmpfile" 2>&1

    cat >> "$tmpfile" << 'EOF'

# === WAITING FOR TASK ===
#
# I have analyzed the project structure and code.
# I am ready to generate AP patches.
# Just tell me what to change.
# If I write something to analyze, the analysis should not contain a patch.
# The patch must be located inside a block of code like:
# ```ap
# *patch*
# ```
# === PROJECT STRUCTURE (again) ===
#
EOF

    tree >> "$tmpfile" 2>/dev/null

    echo -e "\n# === END ===" >> "$tmpfile"

    cat "$tmpfile" | pbcopy
    rm "$tmpfile"
    echo "✅ Copied to clipboard: tree + instructions + ap.md + sc output"
}

function jf() {
    _ensure_ap || return 1

    local tmpfile="/tmp/jf_patch_$(date +%s).ap"
    pbpaste > "$tmpfile"
    if [[ ! -s "$tmpfile" ]]; then
        echo "❌ Буфер обмена пуст. Скопируйте сначала ap-патч."
        rm -f "$tmpfile"
        return 1
    fi
    python3 "$AP_HOME/implementation/ap.py" "$tmpfile" "$@"
    rm -f ./afailed.ap 2>/dev/null
    rm "$tmpfile"
}
