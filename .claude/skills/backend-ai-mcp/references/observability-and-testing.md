# Observabilidade, testes, avaliação e rollout

Índice:
1. Métricas de IA
2. Métricas de RAG e agentes
3. Tracing
4. O que não logar
5. Testes sem provider real
6. Contract tests
7. Testes obrigatórios de falha
8. Golden datasets e avaliação offline
9. LLM-as-judge
10. Feature flags e versionamento
11. AI Jobs e execução assíncrona

---

## 1. Métricas de IA

Medir por caso de uso: requests, latência, sucesso, falha, retry, input tokens, output tokens, custo estimado, provider, modelo.

Essas dimensões precisam existir juntas. "O custo subiu" sem `use_case` e `model` é uma métrica que não responde nada.

## 2. Métricas de RAG e agentes

RAG: tempo de retrieval, número de chunks, top-k, scores, documentos encontrados, respostas sem evidência.

Agentes: passos, tools chamadas, erros, tempo total, custo, motivo de parada, ações bloqueadas, confirmações humanas.

## 3. Tracing

Correlacionar quando possível:

```text
correlation_id   (nome único da família — X-Request-ID na API, propagado para tasks)
ai_run_id
job_id
tool_call_id
mcp_request_id
```

Com esses cinco identificadores, é possível reconstruir "o usuário tocou no app e três minutos depois isso aconteceu". `AIRun.correlation_id` é preenchido a partir de `common.logging.correlation_id`.

## 4. O que não logar

Registrar o necessário para operação: inputs permitidos, outputs úteis, tools, métricas, decisões explícitas do workflow.

Não tratar raciocínio interno do modelo como log de sistema, nem construir lógica de negócio em cima dele.

## 5. Testes sem provider real

A maior parte dos testes usa fake/mock:

```python
class FakeLLMProvider:
    def generate(self, **kwargs):
        return predefined_response
```

Isso mantém a suíte rápida, barata e determinística. Ver `assets/templates/test_fakes.py`.

## 6. Contract tests

Manter testes específicos contra o provider real para autenticação, structured output, timeout, erros e compatibilidade. Executar separadamente da suíte principal (marcador do pytest, job dedicado no CI, execução agendada).

## 7. Testes obrigatórios de falha

Toda funcionalidade de IA tem teste para:

- JSON quebrado, enum inválido, campo ausente, tool args inválidos → falha controlada, nunca persistência de dado inválido;
- permissão negada → o LLM não muda o resultado;
- tenant cruzado no RAG;
- prompt injection (ver `security.md`).

## 8. Golden datasets e avaliação offline

Para funcionalidades importantes, manter dataset de avaliação em `apps/ai/evaluations/`:

```text
input
expected category
expected fields
acceptable answer
source documents
```

Antes de trocar modelo, prompt, embedding, chunking ou retriever, comparar qualidade, latência, custo e erros. Trocar às cegas é como fazer deploy sem teste.

## 9. LLM-as-judge

Pode complementar a avaliação, mas não é a única fonte de verdade. Combinar métricas determinísticas, avaliação humana, datasets rotulados e julgamento por modelo quando útil.

## 10. Feature flags e versionamento

Novas capacidades entram gradualmente:

```text
AI_CLASSIFICATION_ENABLED
AI_AGENT_V2_ENABLED
MCP_WRITE_TOOLS_ENABLED
```

Versionar: prompt, schema, workflow, embedding model, índice, contrato de tool, integração MCP.

Mudança de maior risco precisa de rollback simples e barato.

## 11. AI Jobs e execução assíncrona

Processos longos (ingestão de RAG, embeddings em lote, processamento de documentos, agentes longos, relatórios, sincronizações) rodam pela BE-03.

```text
AIJob
├── id
├── type
├── status
├── progress
├── provider
├── model
├── started_at
├── finished_at
├── result_reference
└── error_code
```

Não depender apenas do task id do Celery: o app precisa de um recurso consultável (`AIJob`, base `ProcessingStateModel`), com status e progresso, que sobreviva a restart de worker.

Streaming melhora UX mas não contorna autenticação, autorização, limites, logs, cancelamento e tratamento de erro. Use ASGI onde houver necessidade real de streaming ou I/O assíncrono, sem misturar sync e async sem entender as bibliotecas envolvidas.
