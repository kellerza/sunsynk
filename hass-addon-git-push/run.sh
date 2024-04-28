#!/bin/bash

#### config ####

CONFIG_PATH=/data/options.json
HOME=~

DEPLOYMENT_KEY=$(jq --raw-output ".deployment_key[]" $CONFIG_PATH)
DEPLOYMENT_KEY_PROTOCOL=$(jq --raw-output ".deployment_key_protocol" $CONFIG_PATH)
DEPLOYMENT_USER=$(jq --raw-output ".deployment_user" $CONFIG_PATH)
# DEPLOYMENT_PASSWORD=$(jq --raw-output ".deployment_password" $CONFIG_PATH)
# GIT_BRANCH=$(jq --raw-output '.git_branch' $CONFIG_PATH)
# GIT_COMMAND=$(jq --raw-output '.git_command' $CONFIG_PATH)
# GIT_REMOTE=$(jq --raw-output '.git_remote' $CONFIG_PATH)
# GIT_PRUNE=$(jq --raw-output '.git_prune' $CONFIG_PATH)
REPOSITORY=$(jq --raw-output '.repository' $CONFIG_PATH)
# AUTO_RESTART=$(jq --raw-output '.auto_restart' $CONFIG_PATH)
# RESTART_IGNORED_FILES=$(jq --raw-output '.restart_ignore | join(" ")' $CONFIG_PATH)
REPEAT_ACTIVE=$(jq --raw-output '.repeat.active' $CONFIG_PATH)
REPEAT_INTERVAL=$(jq --raw-output '.repeat.interval' $CONFIG_PATH)
################

#### functions ####
function add-ssh-key {
    echo "[Info] Start adding SSH key"
    mkdir -p ~/.ssh

    (
        echo "Host *"
        echo "    StrictHostKeyChecking no"
    ) > ~/.ssh/config

    echo "[Info] Setup deployment_key on id_${DEPLOYMENT_KEY_PROTOCOL}"
    rm -f "${HOME}/.ssh/id_${DEPLOYMENT_KEY_PROTOCOL}"
    while read -r line; do
        echo "$line" >> "${HOME}/.ssh/id_${DEPLOYMENT_KEY_PROTOCOL}"
    done <<< "$DEPLOYMENT_KEY"

    chmod 600 "${HOME}/.ssh/config"
    chmod 600 "${HOME}/.ssh/id_${DEPLOYMENT_KEY_PROTOCOL}"
}

function check-ssh-key {
if [ -n "$DEPLOYMENT_KEY" ]; then
    echo "Check SSH connection"
    IFS=':' read -ra GIT_URL_PARTS <<< "$REPOSITORY"
    # shellcheck disable=SC2029
    DOMAIN="${GIT_URL_PARTS[0]}"
    if OUTPUT_CHECK=$(ssh -T -o "StrictHostKeyChecking=no" -o "BatchMode=yes" "$DOMAIN" 2>&1) || { [[ $DOMAIN = *"@github.com"* ]] && [[ $OUTPUT_CHECK = *"You've successfully authenticated"* ]]; }; then
        echo "[Info] Valid SSH connection for $DOMAIN"
    else
        echo "[Warn] No valid SSH connection for $DOMAIN"
        add-ssh-key
    fi
fi
}

function git_push {
    # is /config a local git repo?
    if git rev-parse --is-inside-work-tree &>/dev/null
    then
        export CHANGED=`date +'%Y-%m-%d %H:%M:%S'`
        echo changed - $CHANGED > git_backup.log
        git add . && git commit -m "Backup $CHANGED" && git push origin HEAD

    else
        echo "[Warn] Git repository doesn't exist"
        git-clone
    fi
}

#### Main program ####
cd /config || { echo "[Error] Failed to cd into /config"; exit 1; }

while true; do
    check-ssh-key
    git_push
    # do we repeat?
    if [ ! "$REPEAT_ACTIVE" == "true" ]; then
        exit 0
    fi
    sleep "$REPEAT_INTERVAL"
done

