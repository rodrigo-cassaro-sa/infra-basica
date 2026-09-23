# RAG — ingestão, indexação e recuperação

Índice:
1. Fluxo geral
2. Pipeline de ingestão
3. Documento original e metadados
4. Hash e deduplicação
5. Chunking e overlap
6. Embeddings
7. Vector store e filtros SQL
8. Autorização no retrieval
9. Top-K, busca híbrida e reranking
10. Resposta fundamentada e ausência de evidência
11. Avaliação e observabilidade
12. Migração de embeddings

---

## 1. Fluxo geral

```text
Usuário → autorização → consulta → retrieval filtrado → chunks → LLM → resposta + referências
```

RAG reduz a dependência do conhecimento interno do modelo, mas não garante verdade automaticamente. Continua valendo: o domínio valida.

## 2. Pipeline de ingestão

```text
Fonte → extração → normalização → chunking → metadados → embedding → indexação
```

Cada etapa precisa ser rastreável: dado um chunk, deve ser possível chegar ao documento, à versão e ao arquivo original.

Ingestão é trabalho longo — roda em Celery, pela BE-03, com `AIJob` (base `ProcessingStateModel` + `ProgressMixin`) acompanhando status e progresso. Arquivos de origem vêm de `FileAsset` (storage da BE-05).

## 3. Documento original e metadados

O arquivo original fica em MinIO/S3. O banco guarda `metadata`, `object_key`, `hash`, `version`, `status`.

Metadados recomendados por chunk:

```text
document_id
source
tenant_id
version
page
section
created_at
updated_at
permission_scope
```

`tenant_id` e `permission_scope` não são opcionais em produto multi-tenant — são o que torna o filtro de autorização possível.

## 4. Hash e deduplicação

SHA-256 do conteúdo serve para detectar duplicata, evitar reprocessamento, validar versão e rastrear a ingestão. Reindexar o mesmo PDF cinco vezes é desperdício de custo e fonte de ruído no retrieval.

## 5. Chunking e overlap

Não existe tamanho universal. Considerar estrutura do documento, modelo de embedding, perguntas esperadas, custo e semântica. Preferir respeitar títulos, seções e parágrafos.

Overlap só quando melhorar a recuperação de fato — excesso aumenta custo, duplicação, armazenamento e ruído.

## 6. Embeddings

Registrar sempre:

```text
embedding_provider
embedding_model
embedding_dimension
embedding_version
```

Trocar o modelo de embedding costuma exigir reindexação completa. Sem esses campos, você não sabe quais vetores são compatíveis entre si.

## 7. Vector store e filtros SQL

Padrão inicial: **PostgreSQL + pgvector**. Reduz o número de tecnologias e atende bem a maioria dos sistemas corporativos. Banco vetorial dedicado entra quando escala ou requisito justificar — com medição, não por moda.

Divisão de responsabilidade:

- SQL para filtros determinísticos: tenant (via `scope_to_tenant(qs, actor)`), `status`, data, tipo, permissão.
- Busca vetorial para similaridade semântica.

## 8. Autorização no retrieval

```text
usuário → escopo autorizado → retrieval → LLM
```

O filtro acontece na query, antes da similaridade. O retrieval é um **selector** e recebe `actor`, nunca `tenant_id` solto:

```python
# apps/ai/rag/retrieval.py
def chunk_retrieve_for(*, actor, query: str, top_k: int = 8) -> list[DocumentChunk]:
    embedding = embed_query(query)
    qs = scope_to_tenant(DocumentChunk.objects.all(), actor)       # filtro SQL primeiro
    qs = qs.filter(permission_scope__in=scopes_of(actor))
    return list(qs.order_by(CosineDistance("embedding", embedding))[:top_k])
```

 Nunca recuperar documento de outro tenant esperando que o modelo o ignore: um chunk do tenant B pode ser semanticamente mais parecido com a pergunta do que qualquer chunk do tenant A, e o vazamento é silencioso.

Teste automatizado obrigatório: tenant A nunca recebe documento do tenant B, mesmo com similaridade maior.

## 9. Top-K, busca híbrida e reranking

Top-K é configurado por caso de uso. Mais chunks não significam resposta melhor — excesso gera ruído, custo, conflito de informação e perda de relevância.

Busca híbrida (filtro SQL + busca lexical + busca vetorial) entra quando a avaliação demonstrar ganho. Reranking idem:

```text
retrieve 20 → rerank → usar 5
```

Não adicionar complexidade sem medir.

## 10. Resposta fundamentada e ausência de evidência

Quando a resposta precisa ser auditável, preservar referência a `source_id`, `document_id`, `page`, `chunk_id` — e devolvê-las na API para o app exibir.

Se não houver contexto suficiente, o estado correto é explícito:

```text
AI_INSUFFICIENT_CONTEXT   (AIInsufficientContext → BusinessRuleError → 422)
```

Não forçar o modelo a inventar resposta. Um "não encontrei isso nos documentos" é um resultado válido e o app deve saber renderizá-lo.

## 11. Avaliação e observabilidade

Medir qualidade: retrieval relevance, answer correctness, groundedness, citation correctness, latência, custo.

Medir operação: tempo de retrieval, número de chunks, top-k usado, scores, documentos encontrados, respostas sem evidência.

A taxa de `AI_INSUFFICIENT_CONTEXT` costuma ser o melhor termômetro precoce de que a ingestão quebrou.

## 12. Migração de embeddings

```text
novo índice → reindexação → avaliação → switch → remoção do antigo
```

Não misturar vetores incompatíveis sem controle. Manter o índice antigo até a avaliação aprovar o novo.
