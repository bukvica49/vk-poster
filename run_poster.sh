#!/bin/bash
# VPS cron wrapper: pull через deploy-ключ + poster.py (main)
# Deploy-ключ имеет write — используется для push state после поста
set -u
cd "$(dirname "$0")" || exit 1

# 1. Pull через deploy-ключ (write-доступ, без passphrase)
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

# 2b. Публикация state при успешном main и реальных изменениях
PUSH_RC="skip"
if [ "${DRY:-0}" != "1" ] && [ "$MAIN_RC" = "0" ]; then
  if ! git diff --quiet state-*.json 2>/dev/null; then
    git add state-*.json
    git commit -m "state: auto $(date +%Y-%m-%d_%H:%M)" --no-verify >> log-sync.txt 2>&1
    GIT_SSH_COMMAND="ssh -i $HOME/.ssh/id_ed25519_deploy -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
      timeout 30 git push origin main >> log-sync.txt 2>&1
    PUSH_RC=$?
  else
    PUSH_RC="nochange"
  fi
fi

# 3. Однострочный итог прогона
{
  printf '=== %s ===\n' "$(date -Iseconds)"
  echo "sync=$SYNC_RC  main=$MAIN_RC  test=$TEST_RC  push=$PUSH_RC"
} >> log-runs.txt

exit 0
