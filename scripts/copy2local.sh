#!/bin/sh
# Copy addon sources to a local Home Assistant addons share (Mac/Linux).
# Mount first: open 'smb://192.168.1.8/addons'
# Override destination: DEST=/Volumes/addons ./scripts/copy2local.sh

set -e
cd "$(dirname "$0")/.."

DEST="${DEST:-/Volumes/addons}"
ADDON=hass-addon-sunsynk-edge

print() {
    echo
    echo "$1"
    echo "==========================================================="
    echo
}

# rsync patterns equivalent to scripts/copyexclude.txt (xcopy substring match)
rsync_excl() {
    rsync -a \
        --exclude '__pycache__' \
        --exclude '*.egg-info' \
        --exclude '.*' \
        --exclude 'tests' \
        --exclude '.mypy_cache' \
        --exclude 'config.localtest.yaml' \
        --exclude 'config.yaml' \
        "$@"
}

copy_sunsynk() {
    print "Copy sunsynk package for '$1'"
    mkdir -p "$DEST/$1/sunsynk"
    for f in pyproject.toml LICENSE README.md uv.lock; do
        cp -f "$f" "$DEST/$1/sunsynk/"
    done
    rsync_excl src/ "$DEST/$1/sunsynk/src/"
}

copy_addon() {
    print "Copy '$1' to '$DEST/$1'"
    num=$(( $(od -An -N2 -tu2 /dev/urandom | tr -d ' ') % 100 + 1 ))
    print "Set version to v$num for local testing"
    mkdir -p "$DEST/$1"
    rsync_excl "$1/" "$DEST/$1/"

    cf="$1/config.localtest.yaml"
    cp "$1/config.yaml" "$cf"
    sed -i '' 's/image:/# image:/' "$cf"
    sed -i '' 's/name: /name: A_LOCAL /' "$cf"
    sed -i '' "s/version: \"/version: \"v${num}_/" "$cf"
    cp -f "$cf" "$DEST/$1/config.yaml"
}

copy_builder() {
    print "Copy builder files for '$1'"
    mkdir -p "$DEST/$1"
    cp -f hass-addon-sunsynk-edge/Dockerfile "$DEST/$1/"
    rsync -a hass-addon-sunsynk-edge/rootfs/ "$DEST/$1/rootfs/"
    echo 0.0.0 > "$DEST/$1/VERSION"
}

if [ ! -d "$DEST" ]; then
    echo "Destination not found: $DEST"
    echo "Mount the share, then re-run:"
    echo "  open 'smb://192.168.1.8/addons'"
    echo "Or set DEST to the mount point:"
    echo "  DEST=/Volumes/addons $0"
    exit 1
fi

copy_builder "$ADDON"
copy_addon "$ADDON"
copy_sunsynk "$ADDON"
