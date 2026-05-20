#!/bin/bash

clean() {
    blue=$'\033[0;34m'
    reset=$'\033[0;39m'
    green=$'\033[0;32m'
    red=$'\033[0;31m'
    purple=$'\033[0;35m'
    cyan='\033[0;36m'
    yellow='\033[0;33m'
    bold='\033[1m'
    normal='\033[0m'

    show_disk_space() {
        local phase="$1"
        echo "$purple"'|----|'"$phase"'|----|'
        echo "$purple"'|'"$blue"'Size  '"$purple"'|  '"$red"'Used  '"$purple"'|  '"$green"'Avail '"$purple"'|'"$reset"

        disk_info=$(df -h "$HOME" | tail -1)
        if [ -n "$disk_info" ]; then
            total=$(echo "$disk_info" | awk '{print $2}')
            used=$(echo "$disk_info" | awk '{print $3}')
            avail=$(echo "$disk_info" | awk '{print $4}')
            echo "$purple|$blue$total $purple=  $red$used $purple+  $green$avail $purple|$reset"
        else
            disk_info=$(df -h / | tail -1)
            total=$(echo "$disk_info" | awk '{print $2}')
            used=$(echo "$disk_info" | awk '{print $3}')
            avail=$(echo "$disk_info" | awk '{print $4}')
            echo "$purple|$blue$total $purple=  $red$used $purple+  $green$avail $purple|$reset"
        fi
    }

    show_largest_files_full() {
        local dir="${1:-$HOME}"

        echo "${purple}|----| Top 10 Largest Files |----|${reset}"
        echo "${cyan}Searching in: $dir${reset}"
        echo ""

        file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "${yellow}📁 Total files scanned: $file_count${reset}"
        echo ""

        find "$dir" -type f -exec du -h {} + 2>/dev/null | \
            sort -rh | \
            head -10 | \
            awk -v r="$red" -v y="$yellow" -v g="$green" -v p="$purple" -v c="$cyan" -v rs="$reset" '
        BEGIN {
            print sprintf("%-8s  %s", "Size", "Full Path");
            print "--------  ------------------------------------------------------------";
        }
        {
            size = $1;
            $1 = "";
            file = substr($0, 2);

            # Color by size
            if (index(size, "G")) color = r;
            else if (index(size, "M") && size+0 > 100) color = y;
            else if (index(size, "M")) color = g;
            else color = c;

            printf "%s%8s%s  %s%s%s\n", p, size, rs, color, file, rs;
        }'

        echo ""
        echo "${purple}|----| File Type Analysis |----|${reset}"

        echo ""
        echo "${bold}📊 Largest files by type:${normal}"
        echo ""

        echo "${blue}🎬 Video files (>100MB):${reset}"
        find "$dir" -type f \( -iname "*.mp4" -o -iname "*.mov" -o -iname "*.avi" -o -iname "*.mkv" -o -iname "*.wmv" -o -iname "*.flv" \) \
            -size +100M -exec du -h {} + 2>/dev/null | \
            sort -rh | \
            head -3 | \
            while IFS= read -r line; do
                size=$(echo "$line" | awk '{print $1}')
                path=$(echo "$line" | awk '{for(i=2;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ *$//')
                printf "  %-7s %s\n" "$size" "$path"
            done
        [ $? -ne 0 ] && echo "  None found"

        echo ""

        echo "${blue}🗃️  Archives & Disk Images (>100MB):${reset}"
        find "$dir" -type f \( -iname "*.dmg" -o -iname "*.iso" -o -iname "*.zip" -o -iname "*.rar" -o -iname "*.7z" -o -iname "*.tar.gz" -o -iname "*.pkg" \) \
            -size +100M -exec du -h {} + 2>/dev/null | \
            sort -rh | \
            head -3 | \
            while IFS= read -r line; do
                size=$(echo "$line" | awk '{print $1}')
                path=$(echo "$line" | awk '{for(i=2;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ *$//')
                printf "  %-7s %s\n" "$size" "$path"
            done
        [ $? -ne 0 ] && echo "  None found"

        echo ""

        echo "${blue}💻 Development files (>50MB):${reset}"
        find "$dir" -type f \( -iname "*.node_modules" -o -path "*/.git/*" -o -iname "*.docker" -o -iname "*.vdi" -o -iname "*.vmdk" -o -iname "*.qcow2" \) \
            -size +50M -exec du -h {} + 2>/dev/null | \
            sort -rh | \
            head -3 | \
            while IFS= read -r line; do
                size=$(echo "$line" | awk '{print $1}')
                path=$(echo "$line" | awk '{for(i=2;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ *$//')
                printf "  %-7s %s\n" "$size" "$path"
            done
        [ $? -ne 0 ] && echo "  None found"

        echo ""
        echo "${purple}|----| Largest Directories |----|${reset}"
        echo ""

        echo "${bold}📁 Top 5 Largest Directories:${normal}"
        echo ""
        du -sh "$dir"/* 2>/dev/null | sort -rh | head -5 | \
            while IFS= read -r line; do
                size=$(echo "$line" | awk '{print $1}')
                dir_path=$(echo "$line" | awk '{for(i=2;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ *$//')

                if [[ "$size" == *G* ]]; then
                    color="$red"
                elif [[ "$size" == *M* ]]; then
                    color="$yellow"
                else
                    color="$green"
                fi

                printf "%s%8s%s  %s%s%s\n" "$purple" "$size" "$reset" "$color" "$dir_path" "$reset"
            done
    }

    paths=(
        ~/Library/Application\ Support/Slack/Code\ Cache/
        ~/Library/Application\ Support/Slack/Cache/
        ~/Library/Application\ Support/Slack/Service\ Worker/CacheStorage/
        ~/Library/Application\ Support/Slack/Cache
        ~/Library/Application\ Support/Slack/Code\ Cache
        ~/Library/Application\ Support/Slack/Service\ Worker/CacheStorage

        # System caches
        ~/Library/Caches/*
        ~/Library/42_cache/
        ~/Library/Caches/CloudKit
        ~/Library/Caches/com.apple.akd
        ~/Library/Caches/com.apple.ap.adprivacyd
        ~/Library/Caches/com.apple.appstore
        ~/Library/Caches/com.apple.appstoreagent
        ~/Library/Caches/com.apple.cache_delete
        ~/Library/Caches/com.apple.commerce
        ~/Library/Caches/com.apple.iCloudHelper
        ~/Library/Caches/com.apple.imfoundation.IMRemoteURLConnectionAgent
        ~/Library/Caches/com.apple.keyboardservicesd
        ~/Library/Caches/com.apple.nbagent
        ~/Library/Caches/com.apple.nsservicescache.plist
        ~/Library/Caches/com.apple.nsurlsessiond
        ~/Library/Caches/storeassetd
        ~/Library/Caches/com.apple.touristd
        ~/Library/Caches/com.apple.tiswitcher.cache
        ~/Library/Caches/com.apple.preferencepanes.usercache
        ~/Library/Caches/com.apple.preferencepanes.searchindexcache
        ~/Library/Caches/com.apple.parsecd
        ~/Library/42_cache

        # Browser caches
        ~/Library/Application\ Support/Firefox/Profiles/*/storage
        ~/Library/Application\ Support/Google/Chrome/Default/Service\ Worker/CacheStorage/*
        ~/Library/Application\ Support/Google/Chrome/Crashpad/completed/*
        ~/Library/Safari/*
        ~/Library/Containers/com.apple.Safari/Data/Library/Caches/*

        # Development tools cache
        ~/.kube/cache/*
        ~/Library/Developer/Xcode/DerivedData/*
        ~/Library/Application\ Support/Code/User/workspaceStorage
        ~/Library/Application\ Support/Code/CacheData
        ~/Library/Application\ Support/Code/Cache
        ~/Library/Application\ Support/Code/Crashpad/completed
        ~/Library/Application\ Support/Code/CachedData
        ~/Library/Application\ Support/Code/CachedExtension
        ~/Library/Application\ Support/Code/CachedExtensions
        ~/Library/Application\ Support/Code/CachedExtensionVSIXs
        ~/Library/Application\ Support/Code/Code\ Cache
        ~/Library/Application\ Support/Code/CachedData/*
        ~/Library/Application\ Support/Code/Crashpad/completed/*
        ~/Library/Application\ Support/Code/User/workspaceStorage/*
        ~/Library/Caches/com.microsoft.VSCode.ShipIt
        ~/Library/Caches/com.microsoft.VSCode

        # Multimedia applications cache
        ~/Library/Application\ Support/Spotify/PersistentCache

        # Google update tools cache
        ~/Library/Caches/com.google.SoftwareUpdate
        ~/Library/Caches/com.google.Keystone

        # Docker cache
        ~/Library/Containers/com.docker.docker/Data/vms/*

        # System trash
        ~/.Trash/*

        # My trash
        $HOME/Desktop/*.log
        $HOME/Desktop/*.tmp
    )

    cleaned_count=0
    show_disk_space "Before cleanup"

    for path in "${paths[@]}"; do
        expanded_path="${path/#\~/$HOME}"
        if [ -e "$expanded_path" ] || [ -L "$expanded_path" ]; then
            if rm -rf "$expanded_path" 2>/dev/null; then
                cleaned_count=$((cleaned_count + 1))
            fi
        fi
    done

    find ~/Downloads -name "*.dmg" -mtime +30 -delete 2>/dev/null
    find ~/Downloads -name "*.zip" -mtime +30 -delete 2>/dev/null
    find ~/Downloads -name "*.pkg" -mtime +30 -delete 2>/dev/null

    find ~/Library/Application\ Support -type d -iname "*cache*" 2>/dev/null -exec rm -rf {} \;

    echo ""
    echo "$purple"'Cleaned '"$cleaned_count"' items'

    echo ""
    show_disk_space "After cleanup"
}

alias c="clean"

# If script is executed directly (not sourced), run clean
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    clean
fi

