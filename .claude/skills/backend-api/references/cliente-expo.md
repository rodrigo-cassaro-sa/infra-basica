# Contrato com o frontend Expo

O consumidor da API é o app Expo (iOS, Android e web a partir da mesma base). Três artefatos
mantêm backend e app sincronizados sem conversa informal.

## 1. OpenAPI → client TypeScript gerado

O schema do `drf-spectacular` é a fonte da verdade. O app **não escreve tipos de API à mão**.

```bash
# backend (CI e local)
uv run python manage.py spectacular --file openapi.yaml --validate --fail-on-warn
```

No repositório do Expo, gerar client + tipos (escolha uma ferramenta por projeto):

```bash
npx orval --input ../backend/openapi.yaml --output src/api/generated   # client + hooks React Query
# ou
npx openapi-typescript ../backend/openapi.yaml -o src/api/schema.d.ts  # só tipos
```

CI do backend: gerar o `openapi.yaml` e falhar se houver diff não commitado. Mudança no schema =
PR com o schema novo → app regenera o client.

Para o schema sair bom:

- serializers de entrada e saída separados (`COMPONENT_SPLIT_REQUEST = True`);
- `@extend_schema` com `responses` em toda view (inclusive erros relevantes);
- enums com nome estável (`ENUM_NAME_OVERRIDES`) para o tipo TS não mudar de nome;
- dinheiro como `DecimalField(coerce_to_string=True)` → `string` no TS (nunca `number`).

## 2. Catálogo de error codes

`docs/api/error-codes.md` — uma linha por `code`: HTTP, significado, o que o app deve fazer.

```markdown
| code | HTTP | quando | ação no app |
|---|---|---|---|
| VALIDATION_ERROR | 400 | formato inválido | marcar `fields` no formulário |
| TOKEN_INVALID | 401 | access expirado | refresh automático |
| PERMISSION_DENIED | 403 | sem permissão | esconder ação / aviso |
| ORDER_INVALID_TRANSITION | 409 | status não permite | recarregar o pedido |
| TEMPORARILY_UNAVAILABLE | 503 | provider fora | "tente novamente" + retry com backoff |
```

Gerar a lista automaticamente é simples: percorrer as subclasses de `DomainError`
(`code` + `default_message`) num management command `export_error_codes`.

## 3. Trabalho demorado, progresso e tempo real

Padrão: **202 + recurso de job + polling**.

```text
POST /api/v1/reports/          → 202 {"id": 42, "status": "pending"}
GET  /api/v1/reports/42/       → {"status": "processing", "processed": 120, "total": 500}
```

- O app faz polling com intervalo crescente (2s → 5s → 10s) e para em `completed`/`failed`/`canceled`
  (status de `common.jobs.ProcessingStatus`).
- Notificação ao usuário fora do app → push (Expo Push, backend-integrations `references/push.md`).
- **SSE** só para streaming de resposta de IA (BE-04), servido por ASGI e autenticado com o mesmo JWT.
  WebSocket/Channels só com requisito real (chat multiusuário, colaboração ao vivo) — decisão de projeto.

## 4. Convenções de payload

- `snake_case` nos campos (o client gerado mantém; não converter no meio do caminho).
- Datas ISO 8601 com offset (`2026-09-21T14:03:00-03:00`).
- IDs inteiros (ou `public_id` UUID quando o recurso exigir anti-enumeração).
- Lista sempre paginada: `{count, next, previous, results}`.
