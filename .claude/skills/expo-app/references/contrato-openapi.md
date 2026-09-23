# Contrato gerado por OpenAPI (front e back desacoplados de verdade)

Escrever o DTO Zod à mão funciona, mas o contrato pode divergir do backend sem ninguém
perceber. Quando o backend publica `openapi.json`, **gere** os schemas do app a partir dele.

## Quando usar

- Backend próprio (Fastify, Django, FastAPI) → **sim**, é o padrão da casa.
- Backend low-code (n8n/webhooks, NocoDB) sem OpenAPI confiável → continue com
  `docs/contratos-de-api.md` + schemas manuais.

Registre a escolha em `docs/stack.md` (linha "Contrato").

## Backend: expor o OpenAPI

| Backend | Como |
|---|---|
| FastAPI | nativo: `/openapi.json` |
| Django + DRF | `drf-spectacular` → `python manage.py spectacular --file openapi.json` |
| Fastify | `@fastify/swagger` + type provider Zod (`fastify-type-provider-zod`) — as rotas já são descritas em Zod e o OpenAPI sai delas |

Exija no OpenAPI: `operationId` em toda rota, schema de erro padrão
(`{ code, message, fieldErrors }`) e respostas 4xx documentadas.

## App: gerar só os schemas Zod

Gere **apenas schemas/tipos**. Não use hooks nem clients gerados — o padrão da casa
(apiClient → service → mapper → hook com query keys) continua valendo, e hooks gerados
quebrariam a arquitetura.

Ferramenta padrão: **Orval** em modo Zod (confira a sintaxe na doc da versão instalada):

```ts
// orval.config.ts (raiz do app)
import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: { target: "../backend/openapi.json" }, // ou URL: https://api-dev.../openapi.json
    output: {
      mode: "tags-split",
      client: "zod",
      target: "src/services/api/generated",
      fileExtension: ".zod.ts",
    },
  },
});
```

```json
// package.json
{ "scripts": { "api:gen": "orval --config orval.config.ts" } }
```

Alternativa equivalente: `@hey-api/openapi-ts` com o plugin `zod`. Escolha uma e não misture.

## Como encaixa na feature

`src/services/api/generated/` é **somente leitura** (nunca editar à mão; regenera com
`npm run api:gen`). A feature reexporta com o nome da casa:

```ts
// src/features/users/schemas/user-schema.ts
export {
  getUserResponse as userDtoSchema,
  listUsersResponse as userListDtoSchema,
} from "@/services/api/generated/users/users.zod";

// Schema de formulário continua manual (mensagens em português, regras de UX)
export const userFormSchema = z.object({ /* ... */ });
```

O resto não muda: service chama `apiClient.get(path, userDtoSchema)`, mapper converte
DTO → modelo, hook usa query keys.

## Evitar divergência

- CI: rode `npm run api:gen && git diff --exit-code src/services/api/generated` — se o
  backend mudou o contrato e o app não foi regenerado, o PR falha.
- Mudou o contrato? Ordem: backend atualiza OpenAPI → `api:gen` → `tsc` aponta tudo que
  quebrou → corrige mapper/tela.
- O `ContractError` do `apiClient` continua como rede de segurança em runtime.
