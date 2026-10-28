#!/bin/bash
# VPS cron wrapper: pull через deploy-ключ + poster.py (main)
set -u
cd "$(dirname "$0")" || exit 1

# 1. Pull через deploy-ключ (read-only этого репо, без passphrase)
GIT_SSH_COMMAND="ssh -i $HOME/.ssh/id_ed25519_deploy -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  timeout 30 git pull --rebase --autostash origin main >> log-sync.txt 2>&1
SYNC_RC=$?

# 2. Постинг: main → test последовательно (DRY=1 — только pull)
MAIN_RC="skip"; TEST_RC="skip"
if [ "${DRY:-0}" != "1" ]; then
  /usr/bin/python3 poster.py config.main.json >> log-main.txt 2>&1
  MAIN_RC=$?
  # TEST убран — чтобы не было дубля в VK (шлёт в чужую группу 179225207)
  TEST_RC="skip"
fi

# 3. Однострочный итог прогона
{
  printf '=== %s ===\n' "$(date -Iseconds)"
  echo "sync=$SYNC_RC  main=$MAIN_RC  test=$TEST_RC"
} >> log-runs.txt

exit 0
