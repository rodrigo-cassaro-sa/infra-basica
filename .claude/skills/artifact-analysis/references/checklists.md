# ART-01 — Checklists de análise

Consulte a seção da etapa em que estiver. Nem tudo se aplica a todo artefato.

## Sumário
1. Inventário técnico
2. Frontend
3. Backend
4. Dados e APIs
5. Mocks e simulações
6. Dependências
7. Conversões para a stack oficial
8. Firebase / Supabase / outros providers
9. Artefato visual (protótipo/screenshot)
10. Segurança
11. Testes e documentação do artefato

---

## 1. Inventário técnico

Registrar quando aplicável: linguagens, frameworks, bibliotecas, package manager, arquivos de configuração, Docker, banco, ORM, APIs, rotas, middleware, autenticação, filas, storage, variáveis de ambiente (só nomes), testes, build.

Arquivos prioritários: README, `package.json` / `pyproject.toml` / `requirements.txt`, entrypoints, `screens/` / `pages/` / `app/`, rotas, models, API, services, tests, config.

## 2. Frontend

Procurar: telas, navegação, ações do usuário, formulários, estados, validações, componentes, dados exibidos, loading, empty, error, success, modais, confirmações.

Lembrete: componentes, contexts e hooks são implementação — a capacidade é o que o usuário consegue fazer com eles.

## 3. Backend

Procurar: models, services, endpoints, serializers, views/controllers, permissions, tasks, integrations, validators, events.

Lembrete: model existente ≠ CRUD existente. Só conte a ação se houver endpoint, service ou tela que a execute.

## 4. Dados e APIs

**Dados:** entidades, campos, relações, status, enums, constraints aparentes. Não inventar cardinalidade ou obrigatoriedade sem evidência.

**APIs** — para cada endpoint:

| Método | Rota | Entrada | Saída | Auth | Autorização aparente | Erros | Usado em (frontend) |
|---|---|---|---|---|---|---|---|

`POST /auth/login` → evidência de "Realizar login".

## 5. Mocks e simulações

Sinais: arrays estáticos, JSON local, faker, `Promise.resolve`, `setTimeout` simulando latência, mock server, dados hardcoded, gráficos com valores fixos, botões sem ação (`onClick={() => {}}`, `console.log`), formulários sem persistência.

Classificar como `MOCK` (dado falso) ou `SIMULAÇÃO` (comportamento falso). Registrar, não transformar em requisito.

## 6. Dependências

Analisar `package.json`, `requirements.txt`, `pyproject.toml`, lockfiles. Classificar cada dependência relevante como: utilizada, não utilizada, duplicada, desnecessária, crítica. Para saber se é utilizada, procure imports (`grep -r "from 'lib'"`, `import lib`).

## 7. Conversões para a stack oficial

A conversão é **semântica, nunca textual cega**.

**React Web → Expo:**

| Web | Expo / React Native |
|---|---|
| `div` | `View` |
| `p` / `span` | `Text` |
| `button` | `Pressable` |
| `input` | `TextInput` |
| `img` | `Image` |

React Router serve como evidência de navegação para futura implementação em Expo Router.

**Backend externo → Django (monólito modular):**

| Responsabilidade | Destino |
|---|---|
| dados / integridade | `models.py` |
| casos de uso | `services.py` |
| consultas | `selectors.py` |
| autorização | `permissions.py` |
| HTTP | `api/` |
| assíncrono | `tasks.py` |
| providers externos | `integrations/` |

A ART-01 só **aponta** o destino provável; a implementação é das skills BE-01..05 / expo-app.

## 8. Firebase / Supabase / outros providers

Extrair entidades, campos, operações, autenticação, storage, eventos (triggers, listeners, realtime). Depois comparar com a arquitetura oficial. Não carregar o provider automaticamente.

Pistas: `firebase.initializeApp`, `collection(...)`, `onSnapshot`, `firestore.rules`, `supabase.from('tabela')`, `auth.signIn*`, policies RLS.

## 9. Artefato visual (protótipo/screenshot)

Extrair: telas, navegação aparente, campos, botões, menus, tabelas, cards, modais, ações aparentes, dados exibidos, estados, hierarquia. Marcar tudo como `PROTÓTIPO VISUAL`. Não inferir backend inexistente — ações de dados viram dúvidas ("de onde vem esta lista?").

## 10. Segurança

**Secrets a procurar:** API keys, tokens, passwords, private keys, connection strings, credentials. Padrões úteis: `sk-`, `AIza`, `ghp_`, `-----BEGIN`, `postgres://`, `mongodb+srv://`, `password=`, `.env` versionado. **Nunca reproduzir o valor** — citar arquivo:linha e "(valor omitido)".

**Riscos aparentes:** auth ausente, autorização ausente, IDOR, secret hardcoded, input não validado, upload inseguro, CORS amplo (`*`), SQL inseguro (concatenação/raw), execução arbitrária (`eval`, `exec`, `subprocess` com input), exposição de dados. Encaminhar para SEC-01 quando relevante.

## 11. Testes e documentação do artefato

Testes dão evidência de cenários, comportamentos, erros, permissões e regras. README e docs também ajudam. Se docs, testes e código se contradizem → `CONFLITO INTERNO`, registrando as três versões.
