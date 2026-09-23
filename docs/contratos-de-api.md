# Contratos de API — [NOME DO PRODUTO]

> Fronteira entre o app (Expo) e o backend. Os dois lados seguem este arquivo; ele muda
> primeiro. Derivado das Histórias pela skill `dah-documentacao`. Se o backend gerar
> `openapi.json`, ele deve bater com este arquivo.

## Convenções gerais

**Base:** HTTPS + JSON · URL por ambiente (no app: `EXPO_PUBLIC_API_URL`).
**Campos:** [camelCase | snake_case] · idioma dos nomes: [português | inglês] — um padrão só.
**Datas:** ISO 8601 em UTC (`2026-09-21T13:00:00Z`) · **dinheiro:** [inteiro em centavos | decimal em texto] · **identificadores:** texto opaco.

### Envelope de erro (todas as operações)
```json
{ "code": "EMAIL_DUPLICADO", "message": "Texto para log/suporte", "fieldErrors": { "email": ["Já cadastrado"] } }
```
- `code`: MAIÚSCULAS_COM_UNDERLINE, estável — o app decide a mensagem pelo `code`.
- `fieldErrors`: só em erro de campo; chave = nome do campo na entrada.

| Status | Uso | O app faz |
|---|---|---|
| 400 | requisição malformada | mensagem genérica |
| 401 | sem sessão / sessão expirada | tenta renovar uma vez; falhou → login |
| 403 | sem permissão | "Você não tem permissão para isso" |
| 404 | recurso não existe | estado "não encontrado" |
| 409 | conflito de estado (duplicado, já processado) | mensagem pelo `code` |
| 422 | erro de campo (`fieldErrors`) | marca os campos |
| 429 | muitas tentativas | diz quanto esperar |
| 5xx | falha do servidor | "tente novamente" |

### Paginação (listas)
`GET /recurso?limit=30&cursor=<opaco>` → `{ "items": [ ... ], "nextCursor": "texto | null" }`
Filtros e ordenação como query string, definidos em cada operação.

### Autenticação
| Cliente | Sessão |
|---|---|
| App Android/iOS | `Authorization: Bearer <accessToken>`; refresh **rotativo** |
| Web | cookie `httpOnly` + `Secure` emitido pelo backend; o front não lê token |

Operações de sessão: `POST /auth/login` · `POST /auth/refresh` · `POST /auth/logout` (revoga) · `GET /auth/me`.
[PENDENTE_DE_DEFINICAO: expiração do access token e do refresh]

---

## API-001 — [Nome da operação]

- **Método / recurso:** `[POST] /[recurso]`
- **Objetivo:** [ ]
- **Autenticação:** [pública | sessão]
- **Autorização:** [papel / regra RN-xxx]

### Entrada
```json
{ }
```

### Sucesso — [200 | 201 | 204]
```json
{ }
```

### Erros (envelope padrão)
| Status | code | Quando | fieldErrors |
|---|---|---|---|
| 422 | DADOS_INVALIDOS | [ ] | [campos] |

### Rastreabilidade
- Regras: [RN-] · Entidades: [ENT-] · Histórias: [H-]

---

## Rotas de operação

Contrato de infraestrutura, não de produto: EasyPanel, monitor externo e smoke
de deploy batem direto nelas. Não exigem autenticação (ver `D-005`).

| Rota | Serviço | Uso | Resposta |
|---|---|---|---|
| `GET /api/health/` | Django (dev/hom/prod) | health check da API | `200` com `{"status": "ok", "service": "django", "settings": "<módulo>"}` |
| `GET /healthz` | Nginx do Expo web (hom/prod) | health check do web | `200` `ok` |
