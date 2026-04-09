#!/bin/sh
cd "$(dirname "$0")" || exit 1

export ADDON="$1"
export VER="$2"
export PACKAGE="sunsynk"

if [ -z "$VER" ] || [ -z "$ADDON" ]; then
  echo "Error: Usage $0 <addon> <version>"
  exit 1
fi

if [ ! -f "$ADDON/config.yaml" ]; then
  echo "Error: Invalid addon [./$ADDON]. Please provide a valid add-on name."
  exit 1
fi

echo "Preparing build for '$ADDON' with version '$VER'"

mkdir -p $ADDON/$PACKAGE
cp pyproject.toml MANIFEST.in LICENSE README.md uv.lock $ADDON/$PACKAGE/
cp -r ./src $ADDON/$PACKAGE/

# update version in pyproject.toml
# sed "s/version =.*/version = \"$VER\"/g" pyproject.toml > $ADDON/$PACKAGE/pyproject.toml
echo "$VER" > $ADDON/VERSION
