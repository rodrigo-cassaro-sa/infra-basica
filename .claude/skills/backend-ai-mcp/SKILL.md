---
name: backend-ai-mcp
description: Padrão BE-04 da software house para adicionar IA generativa, LLM, RAG, embeddings, pgvector, agentes, tools e MCP (server e client) a backends Django/DRF desacoplados do frontend Expo (app iOS/Android e painel web). Use sempre que a tarefa envolver LLM, prompt, OpenAI/Anthropic/Gemini/Ollama, chat, assistente, classificação ou extração por IA, busca semântica, RAG, vector store, agente, tool calling, Model Context Protocol, servidor MCP, custo de tokens, avaliação de qualidade de IA ou revisão de código de IA em backend — mesmo que o usuário não cite "BE-04" nem peça explicitamente pelo padrão. Use também quando o usuário pedir estrutura de app `ai/` ou `mcp/`, quiser conectar o app/painel a um recurso de IA, precisar de confirmação humana (PendingAction) para ação de agente, ou perguntar onde colocar prompts, providers e embeddings.
---

# BE-04 — backend-ai-mcp

Padrão da software house para IA e MCP em backends Django que servem o **frontend Expo desacoplado** (app iOS/Android e painel/site web consumindo REST/DRF — "painel" nesta skill = esse frontend) e, quando necessário, hosts de IA via MCP.

Dependências: BE-01 (core/domínio), BE-02 (API), BE-03 (async/Celery). Integrações externas ficam na BE-05.
Convenções comuns (erros, nomes, tenant, correlation id, status de job): `backend-core/references/contratos-entre-skills.md` — em divergência, vale o contrato.

**Esta skill é dona de:** providers de LLM/embeddings (`AI_PROVIDERS`/`AI_MODELS`), prompts, RAG, agentes, servidor MCP, `AIRun`, `AIJob`, `PendingAction`. Cliente de MCP externo que é porta de um sistema de terceiro → BE-05.
Stack padrão: Django + DRF + PostgreSQL + pgvector (quando necessário) + MinIO/S3 + Celery + SDK oficial de MCP em Python.

---

## 1. Regra de ouro

```text
LLM PROPÕE
DOMÍNIO VALIDA
SERVICE DECIDE
BANCO GUARDA
```

E a consequência prática:

```text
IA NÃO É AUTORIDADE   ·   IA NÃO É BANCO   ·   IA NÃO É PERMISSÃO
IA É UMA CAPACIDADE CONTROLADA PELO BACKEND
```

Camadas, sempre nessa ordem — nada pula etapa:

```text
DOMÍNIO → SERVICE → AI SERVICE → PROVIDER / RAG / MCP
```

Se a troca de provider ou de modelo obrigar a mexer no domínio, a abstração está errada.

---

## 2. Antes de escrever código: IA é mesmo necessária?

Se a regra pode ser determinística, ela **permanece** determinística. Um `if` testável é melhor que um prompt.

| IA é adequada para | IA nunca é a única responsável por |
| --- | --- |
| classificação, extração de texto não estruturado, resumo | autenticação, permissões, escopo de tenant |
| busca semântica, RAG, assistentes | saldo, estoque, cálculo financeiro, regra fiscal |
| geração de conteúdo, interpretação de linguagem natural | constraints, integridade, transações |
| apoio à decisão e agentes controlados | qualquer decisão irreversível sem validação |

Quando o pedido chegar como "coloca uma IA aqui", separe primeiro a parte determinística. Costuma sobrar bem menos IA do que o pedido original sugeria — e isso é um bom resultado, não uma recusa.

---

## 3. Fluxo de trabalho ao implementar um caso de uso

1. **Nomear o caso de uso** no padrão da família `<entidade>_<ação>`: `message_classify`, `contract_extract`, `docs_answer`. O mesmo nome vale para o AI service, a chave em `AI_MODELS` e a pasta de prompts. Sem nome, não há prompt versionado, métrica nem avaliação.
2. **Escolher o modo de execução.** Síncrono só se couber no timeout da request do app; caso contrário job + BE-03 (ver §6).
3. **Definir o contrato de saída.** Texto livre para humano ler; schema Pydantic quando a saída alimenta código.
4. **Escrever o AI Service** em `apps/ai/services.py`, não na view, não no serializer. Recebe `actor` (keyword-only), faz `require_perm` e tira o tenant do actor — nunca recebe `tenant_id` solto. Nunca dentro de `transaction.atomic`.
5. **Versionar o prompt** em `apps/ai/prompts/<use_case>/vN.txt` com `metadata.yaml`.
6. **Validar a saída** e tratar falha de parsing como erro normal de aplicação.
7. **Instrumentar**: `AIRun` com provider, modelo, versão de prompt, tokens, latência, custo estimado (`Decimal`) e `correlation_id` — gravado por `ai_run_start/ai_run_succeed/ai_run_fail`, nunca por método no model.
8. **Testar** com `FakeLLMProvider`, incluindo saída inválida, tenant cruzado e prompt injection.
9. **Rodar o checklist** de `references/checklists.md` antes de abrir o PR.

Ao revisar código existente, percorra a mesma lista e aponte o que falta — normalmente é o passo 5, 7 ou 8.

---

## 4. Estrutura de arquivos

```text
backend/
├── apps/
│   ├── ai/
│   │   ├── models.py          # AIRun, AIJob, PendingAction, documentos/chunks de RAG
│   │   ├── services.py        # AI services por caso de uso
│   │   ├── runs.py            # ai_run_start / succeed / fail
│   │   ├── pending.py         # pending_action_propose / confirm / reject
│   │   ├── selectors.py
│   │   ├── tasks.py           # entra pela BE-03
│   │   ├── schemas.py         # Pydantic dos outputs
│   │   ├── exceptions.py      # AIOutputInvalid, AIBudgetExceeded, AIInsufficientContext
│   │   ├── providers/         # base.py, openai.py, anthropic.py, gemini.py, ollama.py
│   │   ├── prompts/           # <use_case>/v1.txt, v2.txt, metadata.yaml
│   │   ├── rag/               # ingestion, chunking, embeddings, retrieval, ranking
│   │   ├── agents/
│   │   └── evaluations/
│   └── mcp/
│       ├── server.py
│       ├── tools/
│       ├── resources/
│       ├── prompts/
│       ├── auth.py            # só autentica → principal.user (autorização = require_perm do core)
│       └── clients/
```

Criar apenas as partes efetivamente usadas. Um projeto que só classifica mensagens não precisa de `rag/`, `agents/` nem do app `mcp/`.

**IA e MCP são coisas distintas.** IA é modelo, prompt, RAG, agente. MCP é protocolo para expor ou consumir contexto e ações. Um sistema pode ter um sem o outro.

---

## 5. Backend desacoplado do app (Expo)

O app é um cliente como qualquer outro. Consequências que valem para todo projeto da house:

- **Nenhuma chave de provider sai do backend.** O app nunca fala com OpenAI/Anthropic/Gemini direto. Se o front precisa de IA, existe um endpoint DRF que chama um AI Service.
- **O contrato da API não expõe o provider.** `POST /api/v1/messages/{id}/classify/` devolve `{category, confidence}` — não devolve o JSON cru do modelo, nem o nome do modelo, nem o prompt. Trocar de provider não quebra o app.
- **Permissão é do DRF + domínio**, exatamente como em qualquer endpoint da BE-02. O LLM entra depois da checagem, nunca antes.
- **Operação longa vira job.** A API cria o `AIJob` (base `ProcessingStateModel`), devolve `202` com o id, e o app acompanha por polling (streaming de resposta: SSE, ver `backend-api/references/cliente-expo.md`). Nada de request de 90 segundos porque "o modelo demora".
- **Streaming**, quando usado, continua sujeito a autenticação, autorização, limites, logs, cancelamento e tratamento de erro. ASGI só onde for necessário; o domínio segue síncrono no Django.
- **Erros de IA são erros de API**, no formato único da família e com code MAIÚSCULO:

| Exceção | Base | HTTP |
|---|---|---|
| `AIInsufficientContext` (`AI_INSUFFICIENT_CONTEXT`) | `BusinessRuleError` | 422 |
| `AIBudgetExceeded` (`AI_BUDGET_EXCEEDED`) | `BusinessRuleError` | 422 |
| `AIOutputInvalid` (`AI_OUTPUT_INVALID`) | `AIPermanentError` → `PermanentError` | 502 |
| `AITransientError` (`AI_PROVIDER_UNAVAILABLE`) | `TransientError` | 503 (e retry na task) |
| `AIPermanentError` (`AI_PROVIDER_REJECTED`) | `PermanentError` | 502 |

REST serve o app, MCP serve hosts de IA, e os dois reutilizam os **mesmos services e selectors**:

```text
                   DOMÍNIO
                     │
             ┌───────┴───────┐
             ▼               ▼
          REST/DRF          MCP
             │               │
             ▼               ▼
        App Expo         AI Hosts
```

---

## 6. Síncrono ou assíncrono

| Síncrono (request do app) | Assíncrono (BE-03 / Celery) |
| --- | --- |
| classificação curta, roteamento | ingestão de RAG, embeddings em lote |
| extração de um campo | processamento de documentos |
| resposta de chat com streaming | agentes longos, relatórios, sincronizações |

Toda chamada de LLM tem timeout. Jobs longos têm `AIJob` próprio com status e progresso — não depender apenas do task id do Celery. Em task, retry só para `TransientError` e o SDK do provider com retry embutido desligado (uma camada só).

---

## 7. Segurança inegociável

Estes pontos não são negociáveis em nenhum projeto; o resto do detalhamento está em `references/security.md`.

```text
DADO NÃO VIRA PERMISSÃO
TEXTO NÃO VIRA AUTORIZAÇÃO
MODELO NÃO ELEVA PRIVILÉGIO
```

- Nunca perguntar ao LLM se o usuário tem permissão. Permissão é checada antes, no backend.
- Todo texto vindo de usuário, documento, PDF, web, e-mail, resource MCP, tool result ou integração externa é **dado hostil**, nunca instrução privilegiada. Separar explicitamente `INSTRUÇÕES` / `DADOS DO USUÁRIO` / `CONTEXTO RECUPERADO` no contexto.
- Segredos (`SECRET_KEY`, senhas, API keys, tokens, cookies, chaves privadas) nunca entram em prompt.
- RAG filtra tenant **no retrieval**, via SQL (`scope_to_tenant(qs, actor)` num selector que recebe `actor`). Não recuperar documento de outro tenant esperando que o modelo o ignore.
- Tool MCP e agente agem **em nome de um actor**; autorização é a do core (`require_perm` no service, visibilidade no selector). Ação sensível → `PendingAction` confirmada por humano.
- Nada de SQL gerado executado direto, `eval`/`exec` de código gerado, shell genérico como tool, fetch de URL arbitrária ou MCP expondo o ORM automaticamente.
- Data minimization: enviar só o contexto necessário reduz risco, custo, tokens e ruído ao mesmo tempo.

---

## 8. Anti-patterns

```text
❌ IA chamada direto na View            ❌ prompt espalhado pelo código
❌ LLM decidindo autorização            ❌ modelo usado como banco de dados
❌ RAG sem filtro de tenant             ❌ agente com acesso total
❌ SQL livre ou shell como tool         ❌ MCP expondo ORM automaticamente
❌ agente sem budget/max_steps          ❌ fallback invisível entre providers
❌ SDK de provider importado no domínio ❌ eval/exec de código gerado
❌ tool passando tenant_id solto         ❌ error code em minúsculas
❌ FK para "users.User" à mão           ❌ lógica de status em método do model
❌ salvar prompt/output indefinidamente ❌ chave de provider no app
```

---

## 9. Onde aprofundar

Carregue apenas o que a tarefa exigir:

| Assunto da tarefa | Arquivo |
| --- | --- |
| Providers, catálogo de modelos, AI services, output estruturado, prompts versionados, timeout, retry, fallback, cache, custos e orçamentos | `references/providers-and-prompts.md` |
| Ingestão, chunking, embeddings, pgvector, busca híbrida, top-k, reranking, citações, migração de índice | `references/rag.md` |
| Agentes, limites de passos, tools de leitura/escrita, human-in-the-loop, schema de tool | `references/agents-and-tools.md` |
| Expor MCP server: tools, resources, prompts, transporte, auth, privilégio mínimo | `references/mcp-server.md` |
| Consumir MCP externo: allowlist, credenciais, validação de resultado, circuit breaker | `references/mcp-client.md` |
| Prompt injection, PII/LGPD, SSRF, SQL e código gerados, upload de arquivos, retenção | `references/security.md` |
| Métricas, tracing, testes com fakes, golden datasets, avaliação offline, feature flags, versionamento | `references/observability-and-testing.md` |
| Checklists de PR e Definition of Done | `references/checklists.md` |

Templates prontos para copiar em `assets/templates/`: `providers_base.py` (erros + resolução por settings), `ai_service_example.py` (service + runs + exceptions), `models_airun.py` (AIRun, AIJob, PendingAction), `mcp_server_example.py`, `test_fakes.py`.

---

## 10. Resultado esperado

Ao abrir qualquer backend da house, um desenvolvedor deve descobrir em minutos: onde estão os providers, qual modelo cada caso de uso usa, onde estão os prompts e qual versão está ativa, como outputs são validados, como o RAG é indexado e filtrado por permissão, quais agentes existem e quais tools cada um pode usar, quais servidores MCP existem e o que expõem, como o custo é medido, como falhas são tratadas e como a qualidade é avaliada.

Se alguma dessas respostas exigir arqueologia no código, o padrão não foi aplicado.
