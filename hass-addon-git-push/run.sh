#!/bin/bash
#cd "${0%/*}"
cd /config
export CHANGED=`date +'%Y-%m-%d %H:%M:%S'`
echo changed - $CHANGED > git_backup.log
git add . && git commit -m "Backup $CHANGED" && git push origin HEAD
