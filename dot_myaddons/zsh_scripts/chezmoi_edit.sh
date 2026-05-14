#!/bin/bash

chezmoi_edit() {
    if [ $# -eq 0 ]; then
        echo "Usage: chezmoi_edit <target>"
        echo "Example: chezmoi_edit ~/.zshrc"
        return 1
    fi

    chezmoi edit "$@"
    local edit_status=$?

    if [ $edit_status -eq 0 ]; then
        echo "Applying changes with chezmoi apply..."
        chezmoi apply
    else
        echo "chezmoi edit exited with error $edit_status — apply skipped."
        return $edit_status
    fi
}

alias ce='chezmoi_edit'
