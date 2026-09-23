#!/usr/bin/env bash
set -euo pipefail

CODER_HOME=/home/coder
WORKSPACE=/home/coder/workspace

mkdir -p \
  "$WORKSPACE" \
  "$CODER_HOME/.claude" \
  "$CODER_HOME/.config/code-server/User" \
  "$CODER_HOME/.config/git" \
  "$CODER_HOME/.config/gh" \
  "$CODER_HOME/.local/share/code-server/User" \
  "$CODER_HOME/.ssh"

# O arquivo legado do Claude fica dentro do volume persistente do Claude.
if [ ! -e "$CODER_HOME/.claude.json" ]; then
  ln -s "$CODER_HOME/.claude/.claude.json" "$CODER_HOME/.claude.json"
fi

# Preferências iniciais. Não sobrescreve escolhas posteriores do usuário.
SETTINGS="$CODER_HOME/.local/share/code-server/User/settings.json"
if [ ! -s "$SETTINGS" ]; then
  cat > "$SETTINGS" <<'JSON'
{
  "workbench.colorTheme": "Default Dark Modern",
  "window.autoDetectColorScheme": false,
  "files.autoSave": "afterDelay",
  "editor.formatOnSave": true,
  "terminal.integrated.defaultProfile.linux": "bash"
}
JSON
fi

# Permissões dos volumes e do checkout montado pelo EasyPanel.
chown -R coder:coder \
  "$WORKSPACE" \
  "$CODER_HOME/.claude" \
  "$CODER_HOME/.config" \
  "$CODER_HOME/.local" \
  "$CODER_HOME/.ssh"

chmod 700 "$CODER_HOME/.ssh" || true

exec gosu coder code-server "$@"
