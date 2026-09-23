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

# Git/GitHub a partir das variáveis de ambiente (EasyPanel/.env).
# Sem as variáveis, o git-bootstrap.sh pergunta no primeiro terminal.
as_coder() { gosu coder env HOME="$CODER_HOME" "$@"; }

if [ -n "${GIT_USER_NAME:-}" ]; then
  as_coder git config --global user.name "$GIT_USER_NAME"
fi
if [ -n "${GIT_USER_EMAIL:-}" ]; then
  as_coder git config --global user.email "$GIT_USER_EMAIL"
fi
as_coder git config --global init.defaultBranch main
as_coder git config --global pull.rebase false
as_coder git config --global core.autocrlf input

# O gh lê GH_TOKEN do ambiente; o Git passa a usar o gh como credential helper.
if [ -n "${GH_TOKEN:-}" ]; then
  as_coder gh auth setup-git --hostname github.com || true
fi

exec gosu coder code-server "$@"
