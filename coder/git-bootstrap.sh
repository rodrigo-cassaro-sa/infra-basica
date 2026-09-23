#!/usr/bin/env bash

MARKER="$HOME/.config/git/bootstrap-complete"
CONFIG="$HOME/.config/git/config"
export GIT_CONFIG_GLOBAL="$CONFIG"

[ -f "$MARKER" ] && exit 0
[ -t 0 ] || exit 0

mkdir -p "$(dirname "$MARKER")"

echo
echo "============================================================"
echo " Configuração inicial Git / GitHub deste projeto"
echo "============================================================"

current_name="$(git config --global user.name 2>/dev/null || true)"
current_email="$(git config --global user.email 2>/dev/null || true)"

if [ -z "$current_name" ]; then
  read -r -p "Nome para os commits Git: " git_name
  [ -n "$git_name" ] || { echo "Configuração adiada."; exit 0; }
  git config --global user.name "$git_name"
fi

if [ -z "$current_email" ]; then
  read -r -p "E-mail para os commits Git: " git_email
  [ -n "$git_email" ] || { echo "Configuração adiada."; exit 0; }
  git config --global user.email "$git_email"
fi

git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.autocrlf input

if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  echo
  echo "Agora vamos autenticar no GitHub para clone/pull/push/criação de repositórios."
  echo "O GitHub mostrará um código e um endereço para confirmar o login."
  read -r -p "Pressione ENTER para continuar..." _
  gh auth login --hostname github.com --git-protocol https --web || exit 0
fi

gh auth setup-git >/dev/null 2>&1 || true

touch "$MARKER"
echo
echo "Git/GitHub configurados."
echo "Workspace: /home/coder/workspace"
echo
