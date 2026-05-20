showcopy() {
    emulate -L zsh

    local dir="."
    local temp_file=$(mktemp)
    local stdout_only=0
    local use_numbers=1

    zmodload zsh/zutil 2>/dev/null

    local -a stdout_flag
    local -a no_numbers_flag
    local -a args
    zparseopts -D -E \
        -stdout=stdout_flag \
        -no-numbers=no_numbers_flag \
        -n=no_numbers_flag 

    if [[ ${#stdout_flag[@]} -gt 0 ]]; then
        stdout_only=1
    fi

    if [[ ${#no_numbers_flag[@]} -gt 0 ]]; then
        use_numbers=0
    fi

    args=("$@")

    # First non-flag argument is directory (if provided)
    if [[ ${#args[@]} -gt 0 ]]; then
        dir="${args[0]}"
    fi

    local text_exts=(
        "*.c" "*.h" "*.cpp" "*.hpp" "*.cc" "*.cxx" "*.hh" "*.hxx"
        "*.py" "*.pyx" "*.pyi"
        "*.sh" "*.bash" "*.zsh" "*.fish" "*.ksh" "*.dash"
        "*.js" "*.ts" "*.jsx" "*.tsx" "*.mjs" "*.cjs"
        "*.html" "*.htm" "*.xhtml"
        "*.css" "*.scss" "*.sass" "*.less" "*.styl"
        "*.yaml" "*.yml" "*.toml" "*.ini"
        "*.md" "*.markdown" "*.rst" "*.tex" "*.latex" "*.ltx"
        "*.lua" "*.rb" "*.go" "*.rs" "*.swift" "*.kt" "*.kts" "*.java"
        "*.sql" "*.psql" "*.r" "*.m" "*.mm" "*.pl" "*.pm" "*.t" "*.pod"
        "*.php" "*.phtml" "*.phps" "*.asp" "*.aspx" "*.jsp"
        "*.scala" "*.sc" "*.clj" "*.cljs" "*.edn" "*.erl" "*.hrl"
        "*.ex" "*.exs" "*.el" "*.lisp" "*.cl" "*.rkt" "*.ss"
        "*.dart" "*.nim" "*.cr" "*.zig" "*.v" "*.vsh" "*.fs" "*.fsx"
        "*.f" "*.f90" "*.f95" "*.f03" "*.for" "*.ada" "*.adb" "*.ads"
        "*.d" "*.di" "*.mli" "*.ml" "*.hs" "*.lhs"
        "*.asm" "*.s" "*.S" "*.nasm"
        "*.cfg" "*.conf" "*.config" "*.cnf"
        "*.vim" "*.vimrc" "*.gvimrc" "*.nvimrc"
        "*.zshrc" "*.bashrc" "*.bash_profile" "*.profile" "*.bash_logout"
        "*.gitignore" "*.gitattributes" "*.gitconfig" "*.gitmodules"
        "*.dockerfile" "Dockerfile*" "*.containerfile"
        "Makefile" "makefile" "*.mk" "*.mak" "*.cmake" "CMakeLists.txt"
        "*.gradle" "*.gradle.kts" "*.sbt"
        "*.vue" "*.svelte" "*.astro"
        "*.graphql" "*.gql"
        "*.ejs" "*.hbs" "*.mustache"
        "*.twig" "*.jinja" "*.jinja2"
        "*.ipynb" "*.julia" "*.jl"
        "*.qmd" "*.rmd" "*.Rnw"
        "*.stan" "*.bugs" "*.jags"
        "*.tf" "*.tfvars" "*.hcl"
        "*.sls"
        "*.pp"
        "*.erb"
        "*.ps1" "*.psm1" "*.psd1"
        "*.j2"
        "*.txt" "*.text"
        "*.nfo" "*.readme" "README*" "CHANGELOG*" "LICENSE*" "CONTRIBUTING*"
        "*.adoc" "*.asciidoc"
        "*.org"
        "*.wiki"
        "*.rtf"
        "*.csv" "*.tsv" "*.psv"
        "*.ics"
        "*.desktop"
        "*.service" "*.timer" "*.socket" "*.target"
        "*.cron" "*.tab" "crontab"
        "*.sed" "*.awk"
        "*.regex"
        "*.prolog" "*.pl" "*.p"
        ".env" ".env.*" "env" "environment"
        "Procfile"
        "Gemfile" "Gemfile.lock"
        "Rakefile"
        "Cargo.toml" "Cargo.lock"
        "go.mod" "go.sum"
        "requirements.txt" "Pipfile" "Pipfile.lock" "pyproject.toml" "setup.py" "setup.cfg"
        ".pre-commit-config.yaml"
        ".eslintrc*" ".prettierrc*" ".babelrc*"
        "*.patch" "*.diff"
        "*.sig" "*.asc"
        "*.gcode"
        "*.scad"
        "*.led"
    )

    local files=()
    for ext in "${text_exts[@]}"; do
        while IFS= read -r file; do
            if [[ -n "$file" ]]; then
                files+=("$file")
            fi
        done < <(find "$dir" -type f -name "$ext" 2>/dev/null | grep -v -E "(\.git|node_modules|__pycache__|\.venv|venv|build|dist|.idea|.vscode)")
    done

    printf "%s\n" "${files[@]}" | sort -u > "$temp_file.list"

    local file_count=$(wc -l < "$temp_file.list" | tr -d ' ')

    if [ "$file_count" -eq 0 ]; then
        rm -f "$temp_file" "$temp_file.list"
        return 1
    fi

    while IFS= read -r file; do
        if [[ -z "$file" ]]; then
            continue
        fi
        echo "=== $file ===" >> "$temp_file"
        if [[ $use_numbers -eq 1 ]]; then
            nl -ba "$file" 2>/dev/null >> "$temp_file"
        else
            cat "$file" 2>/dev/null >> "$temp_file"
        fi
        echo "" >> "$temp_file"
        echo "" >> "$temp_file"
    done < "$temp_file.list"

    local copy_msg="Скопировано $file_count файлов"
    if [[ $use_numbers -eq 1 ]]; then
        copy_msg="$copy_msg с нумерацией строк"
    else
        copy_msg="$copy_msg без нумерации строк"
    fi

    if [[ $stdout_only -eq 1 ]]; then
        cat "$temp_file"
    else
        if command -v pbcopy &> /dev/null; then
            cat "$temp_file" | pbcopy
            echo "$copy_msg"
        elif command -v xclip &> /dev/null; then
            cat "$temp_file" | xclip -selection clipboard
            echo "$copy_msg"
        elif command -v clip.exe &> /dev/null; then
            cat "$temp_file" | clip.exe
            echo "$copy_msg"
        else
            echo "Не найдена команда для копирования в буфер обмена"
            cat "$temp_file"
        fi
    fi

    rm -f "$temp_file" "$temp_file.list"
}

alias sc="showcopy"
