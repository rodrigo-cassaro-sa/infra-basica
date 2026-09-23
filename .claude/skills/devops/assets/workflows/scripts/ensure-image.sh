#!/usr/bin/env bash
# .github/scripts/ensure-image.sh <imagem> <tree> <contexto> [dockerfile]
# Build uma vez, promover sempre: se a imagem daquele conteúdo (tree hash) já existe no
# registry, reusa; senão, builda com RELEASE=<tree> embutido.
set -euo pipefail
IMAGE="$1"; TREE="$2"; CONTEXT="$3"; DOCKERFILE="${4:-$CONTEXT/Dockerfile}"

if docker buildx imagetools inspect "$IMAGE:tree-$TREE" >/dev/null 2>&1; then
  echo "reuso: $IMAGE:tree-$TREE já existe (mesmo conteúdo testado antes)"
  echo "built=false" >> "${GITHUB_OUTPUT:-/dev/null}"
  exit 0
fi

echo "build: $IMAGE:tree-$TREE"
docker buildx build "$CONTEXT" \
  --file "$DOCKERFILE" \
  --build-arg "RELEASE=$TREE" \
  --tag "$IMAGE:tree-$TREE" \
  --tag "$IMAGE:sha-${GITHUB_SHA:-local}" \
  --label "org.opencontainers.image.revision=${GITHUB_SHA:-local}" \
  --cache-from "type=gha,scope=$(basename "$IMAGE")" \
  --cache-to "type=gha,mode=max,scope=$(basename "$IMAGE")" \
  --push
echo "built=true" >> "${GITHUB_OUTPUT:-/dev/null}"
