# Prompts, skills e ambientes

## Índice

- [P-01 — Gerenciar Backlog e Cronograma](#p-01--gerenciar-backlog-e-cronograma)
- [P-02 — Escrever e Revisar História](#p-02--escrever-e-revisar-história)
- [P-03 — Atualizar Documentação DAH](#p-03--atualizar-documentação-dah)
- [P-04 — Definir e Atualizar Interface](#p-04--definir-e-atualizar-interface)
- [P-05 — Implementar e Validar História](#p-05--implementar-e-validar-história)
- [P-06 — Homologar e Publicar](#p-06--homologar-e-publicar)
- [Skills coordenadas](#skills-coordenadas)
- [Relação prompt → skill](#relação-prompt--skill)
- [Ambientes oficiais](#ambientes-oficiais)
- [Gate de produção](#gate-de-produção)
- [Fluxo operacional completo](#fluxo-operacional-completo)

---

## P-01 — Gerenciar Backlog e Cronograma

Responsável por: capítulos, backlog, `indice.md`, numeração, dependências,
bloqueios, ordem lógica, cronograma.

P-01 **não** escreve a história completa, não aprova história e não implementa
código. História nova entra normalmente como `planejada`.

## P-02 — Escrever e Revisar História

Trabalha com **uma** história por execução.

```text
planejada → rascunho → pronta para aprovação → aguardar aprovação humana
```

Após aprovação explícita do usuário: `status → aprovada`.

Antes de marcar "pronta para aprovação", conferir a Definition of Ready para
aprovação em `checklists.md`.

## P-03 — Atualizar Documentação DAH

Recebe **uma** história aprovada. Atualiza, quando aplicável:
`regras-de-negocio.md`, `modelo-de-dados.md`, `contratos-de-api.md`,
`mapa-de-fluxos.md`, `mapa-de-telas.md`, `mapa-de-decisoes.md`.

Consolida o estado do sistema. Não criar um documento por história — os
documentos representam o sistema inteiro, não o histórico de cada entrega.

## P-04 — Definir e Atualizar Interface

Executar antes da primeira implementação de frontend e sempre que houver mudança
visual estrutural. Atualiza `guia-visual.md`.

- Guia já suficiente → validar e seguir para P-05.
- História sem frontend → P-03 direto para P-05.

## P-05 — Implementar e Validar História

Recebe **uma** história aprovada.

```text
verificar documentação
↓ criar/atualizar mapa de testes
↓ status → em desenvolvimento
↓ implementar
↓ QA → SEC quando aplicável → usabilidade quando aplicável
↓ corrigir → retestar
↓ atualizar documentos → decisões → diário → cronograma
↓ status → pronta para homologação
```

P-05 **não** publica em HOM nem em PROD.

Antes de iniciar, conferir a Definition of Ready para implementação; antes de
marcar "pronta para homologação", a Definition of Done DEV (`checklists.md`).

## P-06 — Homologar e Publicar

Pode receber uma ou mais histórias prontas para homologação.

```text
DEV → HOM → QA + SEC + usabilidade + E2E → homologada
→ gate operacional → APROVAÇÃO HUMANA → PROD
→ health + smoke + logs → implementada
```

Falha funcional devolve a história para P-05.

---

## Skills coordenadas

```text
Governança      DAH-01 project-governance

Backend         BE-01 backend-core
                BE-02 backend-api
                BE-03 backend-async
                BE-04 backend-ai-mcp
                BE-05 backend-integrations

Transversais    QA-01 testing-quality
                SEC-01 security
                OPS-01 devops

Frontend        skills de frontend disponíveis no projeto, conforme stack
```

A DAH-01 responde *o que deve acontecer, em que etapa estamos, qual prompt
executar, qual skill é necessária, o que está bloqueado, o que falta, o que foi
concluído, qual documentação mudou, qual decisão está pendente*. As skills
especializadas respondem *como executar tecnicamente*. Uma não substitui a outra.

## Relação prompt → skill

Durante P-05, acionar conforme a natureza da mudança:

```text
altera domínio            → BE-01
cria API                  → BE-02
usa task assíncrona       → BE-03
usa IA / MCP              → BE-04
integra provider externo  → BE-05
exige testes              → QA-01
afeta segurança           → SEC-01
altera infraestrutura     → OPS-01
possui interface          → skills frontend / UX / UI
```

O usuário não deve precisar chamar cada skill manualmente quando o prompt puder
orquestrá-las.

### Responsabilidades transversais

**QA-01**: testes unitários, services, selectors, models, API, frontend,
integração, E2E, regressão, contratos, usabilidade técnica, evidências, quality
gates.

**SEC-01**: autenticação, autorização, tenant isolation, input validation,
secrets, API security, XSS, CSRF, SSRF, uploads, dados sensíveis, webhooks,
IA/MCP, hardening. Alimenta o mapa de testes com cenários de segurança.

**OPS-01**: DEV, HOM, PROD, Docker, CI/CD, build, migrations, deploy, rollback,
PostgreSQL, Redis, Celery, MinIO, Traefik, HTTPS, health, logs, métricas,
alertas, backup, restore.

---

## Ambientes oficiais

```text
DEV · HOM · PROD
```

QA não é ambiente separado por padrão — é processo executado em DEV/CI e em HOM.

### Branch ≠ ambiente

`main` é branch Git; DEV, HOM e PROD são ambientes. Não criar branches
`dev`/`hom`/`prod` automaticamente só porque os ambientes existem.

Quando o projeto adotar branch por história:

```text
feat/H-023-visualizar-permissoes
```

Commits podem referenciar `H-023`. Pull Request, quando usado, indica: história,
documentos alterados, decisões, testes e pendências.

### Promoção de artefato

Preferir promover **o mesmo artefato** DEV → HOM → PROD, identificado por commit
SHA, tag, versão ou digest. Evitar depender apenas de `latest` — sem identidade
estável, "o que foi homologado" e "o que foi publicado" deixam de ser a mesma
coisa e a homologação perde valor.

## Gate de produção

```text
histórias homologadas → QA aprovado → SEC aprovado → OPS pronto
→ rollback considerado → resumo da release → APROVAÇÃO HUMANA → PROD
```

Sem aprovação humana explícita: **não publicar**.

## Fluxo operacional completo

```text
P-01 backlog + cronograma
↓ P-02 escrever história → pronta para aprovação
↓ APROVAÇÃO HUMANA
↓ P-03 documentação consolidada
↓ P-04 interface, se necessário
↓ P-05 implementação + validação → pronta para homologação
↓ P-06 HOM → homologada
↓ APROVAÇÃO HUMANA → PROD → implementada
↓ P-01 próximo ciclo
```
