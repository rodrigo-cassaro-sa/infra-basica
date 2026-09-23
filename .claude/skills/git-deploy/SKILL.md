---
name: git-deploy
description: >-
  Versionar no git e levar para os ambientes — criar repositório (main + develop), pull,
  branch por história (feat/H-xxx), revisão do diff, commit, push, PR para develop (hom),
  release PR develop → main (prod), hotfix e back-merge, tag de release, e acompanhar o
  deploy. Configuração de cada projeto fica em docs/deploy.md. O COMO do deploy (imagens,
  EasyPanel, pipeline, rollback) é da skill devops (OPS-01). Use quando pedirem para
  commitar, subir, sincronizar, versionar, abrir PR, mandar para homologação, publicar em
  produção, fazer hotfix ou deploy. Gatilhos: "faz o commit", "sobe isso", "manda pro git",
  "sincroniza", "manda pra hom", "publica em produção", "release", "hotfix", "deploy",
  "salva no repositório", "cria o repositório".
---

# Git e publicação — padrão da casa

**Git primeiro, deploy depois.** O deploy parte do repositório remoto, nunca da máquina
local: nunca oriente deploy de código que não subiu.

## Branches = ambientes

| Branch | Ambiente | Chega como | Deploy |
|---|---|---|---|
| `feat/H-xxx-slug`, `fix/H-xxx-slug`, `chore/slug` | dev (local) | criada a partir de `develop` | — |
| `develop` | **hom** | PR das branches de trabalho (CI verde) | automático (pipeline da devops) |
| `main` | **prod** | **release PR** `develop → main` | com aprovação no GitHub Environment `prod` |
| `hotfix/slug` | prod urgente | criada a partir de `main`, PR para `main` | + **back-merge** `main → develop` |

- `main` e `develop` protegidas: sem push direto, merge só por PR com CI verde.
- `develop` é a branch padrão do repositório no GitHub (PR novo já aponta para ela).
- Nada vai para `main` sem ter passado por `develop`/hom — exceto hotfix, que volta para `develop` em seguida.
- Mapeamento para o app nativo, imagens, EasyPanel e rollback: skill **devops**.

## Passo 0 — Ler a configuração do projeto

Tudo que é específico do projeto fica em **`docs/deploy.md`** (template em
`assets/templates/docs/deploy.md`): remoto, estrutura, serviços por ambiente, domínios,
forma de deploy, secrets/vars do pipeline, RPO/RTO, credenciais de terceiros.

- Não existe? Crie a partir do template e pergunte só o que faltar. Campo desconhecido fica `PENDENTE`.
- Detecte o ambiente em vez de supor: `git --version`, `gh --version` (sem `gh`, operações
  de GitHub são pelo site), `git config user.name` / `user.email`.

## Criar o repositório

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "sem repo"
```

Repositório **local** é reversível: pode criar sem pedir de novo. Publicar em **remoto**
exige pedido explícito.

1. `git init -b main` e conferir `user.name`/`user.email`.
2. **`.gitignore` antes do primeiro `git add`** (`assets/templates/gitignore` cobre Expo +
   Django). Arquivo que entra no primeiro commit fica no histórico mesmo se ignorado depois.
3. Revisar o que será rastreado:
   ```bash
   git add -A && git status --short && git diff --cached --stat
   ```
   Procure segredo, keystore, arquivo grande, `node_modules`, `.venv`, `dist`.
4. Primeiro commit: `chore: cria monorepo do <produto> (app Expo + backend Django + docs)`.
5. Criar `develop`: `git switch -c develop`.
6. **Remoto — só com pedido explícito.** Privado por padrão.
   ```bash
   gh repo create <nome> --private --source . --push     # sobe a branch atual
   git push -u origin main && git push -u origin develop
   gh repo edit --default-branch develop
   ```
   Depois (pelo site ou `gh api`): proteger `main` e `develop` (PR obrigatório + status `ci`),
   criar Environments `hom` e `prod` (este com required reviewers). Detalhes na devops.

`.claude/skills/` do projeto **entra** no repositório; `.claude/settings.local.json` não.

## Fluxo de uma história (até hom)

### 1. Sincronizar e criar a branch
```bash
git switch develop && git pull --rebase
git switch -c feat/H-023-visualizar-permissoes      # fix/H-031-..., chore/atualiza-deps
```
Conflito: **pare e resolva com o usuário**, nunca escolha um lado sozinho.

### 2. Revisar o que vai subir
```bash
git status
git diff --stat
git diff            # leia de fato quando o volume permitir
```
Procure: segredo, `.env`, temporário, saída de build, alteração não pedida,
**migration** (sinalizar no PR), mudança de contrato da API (sinalizar no PR).

### 3. Commitar
Agrupe por intenção. Formato: **prefixo convencional + descrição em português, no
imperativo, dizendo o que muda**, citando a História.

| Boa | Ruim |
|---|---|
| `feat: adiciona cadastro de aluno com validação de CPF (H-018)` | `atualiza arquivos` |
| `fix: corrige loop de refresh quando o token expira (H-031)` | `mudanças` |
| `docs: sincroniza H-028 e mapa de telas com o fluxo de matrícula` | `wip` |

Prefixos: `feat` · `fix` · `refactor` · `test` · `docs` · `chore` · `style` · `perf` · `ci`.
Corpo quando o porquê não cabe na linha. Encerre com a linha de atribuição que a sessão
atual indicar (não fixe nome de modelo aqui).

Monorepo (padrão da casa): História, docs derivados e código que a implementa no **mesmo
PR**. Repositórios separados: PR dos docs primeiro, PRs de código citam o mesmo `H-xxx`.

### 4. Enviar e abrir PR para `develop`
```bash
git push -u origin feat/H-023-visualizar-permissoes
gh pr create --base develop --title "feat: visualizar permissões (H-023)" --body-file -
```
Corpo do PR: história, o que muda, **migration? (sim/não, arriscada?)**, **contrato da API
muda? (compatível?)**, como testar em hom. Push rejeitado = o remoto andou: volte ao passo 1.
`--force` e `--no-verify` só com pedido explícito.

### 5. Merge → hom
CI verde → merge (squash por padrão). O pipeline sobe para **hom** sozinho. Acompanhe:
- Actions → `deploy` (develop) verde, smoke ok.
- `app.hom…` / `api.hom…/health/ready/` com o `release` novo.
- App nativo: update no channel `preview`.

## Release para prod

Quando o que está em hom foi validado (QA/aceite):

```bash
git switch develop && git pull --rebase
gh pr create --base main --head develop --title "release: $(date +%Y-%m-%d)" --body-file -
```

Corpo da release PR (é o change management da OPS-01):

```text
Histórias: H-018, H-023, H-031
Migrations: sim — 0014_add_status (compatível) | migration-risk: não
Contrato da API: só campos novos (compatível com o app publicado)
Validado em hom: <data>, por <quem>
Rollback: tree anterior da api/web (resumo do último deploy de prod)
```

- **Merge commit** (não squash) na release PR: preserva o histórico e a ligação com `develop`.
- Com `migration-risk`: backup manual antes de aprovar (devops `migrations-e-rollback.md`).
- Merge → Actions pede **aprovação** do environment `prod` → aprovar → smoke.
- Opcional: tag `vAAAA.MM.DD[-N]` no merge commit da `main` (`git tag -a … && git push --tags`).

## Hotfix

```bash
git switch main && git pull --rebase
git switch -c hotfix/corrige-calculo-mensalidade
# commit(s) com fix: … (H-xxx se houver)
gh pr create --base main --title "fix: corrige cálculo da mensalidade (hotfix)"
```

Depois do merge e do deploy em prod, **back-merge obrigatório**:

```bash
gh pr create --base develop --head main --title "chore: back-merge do hotfix"
```

Sem o back-merge, a próxima release desfaz o hotfix.

## Confirmar

```bash
git log --oneline -3
git status -sb      # branch sincronizada com origin
```

Para dizer que "está no ar": o `/health` do ambiente mostra o `release` (tree hash) que o
resumo do deploy no Actions informou. Sem conferir isso, não anuncie deploy concluído.

## Sem pipeline ainda (deploy manual)

Projeto que ainda não tem os workflows da devops: após o merge, entregue SHA, o que mudou
em uma linha e onde agir (`EasyPanel → <produto>-<hom|prod> → <serviço> → Deploy`).
Depois confira junto: painel com o SHA certo, build sem erro, serviço `running`, URL
respondendo. Falhou: **peça o log do build** antes de propor qualquer coisa.
Sugira **uma vez** adotar o pipeline da devops; escolhido, registre no `docs/deploy.md`.

## Nunca

Commitar ou dar push sem pedido · push direto em `main`/`develop` · levar para `main` o que
não passou por hom (exceto hotfix) · esquecer o back-merge do hotfix · `--force`/`--no-verify`
por conta própria · commitar segredo, `.env` com valor real, keystore, `credentials.json`,
token do painel ou URL de webhook de deploy · resolver conflito escolhendo um lado sozinho ·
orientar deploy antes de o código chegar ao remoto · anunciar deploy sem conferir o release no `/health`.
