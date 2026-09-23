# Formato dos cinco documentos estruturais

Todos ficam em `docs/` (ou na pasta já em uso no projeto). Identificadores são sequenciais, permanentes e nunca reutilizados.

---

# 1. regras-de-negocio.md — `RN-`

Regras permanentes ou reutilizáveis do domínio. Sem detalhe visual nem de implementação.

```md
# Regras de Negócio

## RN-001 — E-mail único

### Regra

Cada usuário ativo deve possuir um endereço de e-mail único no sistema.

### Aplicação

Aplica-se a:

- criação de usuário;
- alteração de e-mail.

### Histórias relacionadas

- H-001 — Criar novo usuário
- H-008 — Editar e-mail
```

Deve conter: código, nome, descrição objetiva, condições, exceções quando houver, Histórias relacionadas.

**Crie regra somente quando** a condição representar comportamento ou restrição reutilizável: e-mail deve ser único; somente superusuário pode criar permissões; usuário bloqueado não pode fazer login; escala aceita não pode ser aceita de novo. Detalhe trivial de interface não vira regra de negócio.

Origem principal na História: **O que não pode acontecer**.

---

# 2. modelo-de-dados.md — `ENT-`

Entidades, atributos, relações e restrições lógicas, independentes de tecnologia de banco.

```md
# Modelo de Dados

## ENT-001 — Usuário

### Finalidade

Representar uma pessoa com acesso ao sistema.

### Atributos

| Campo | Tipo lógico | Obrigatório | Descrição |
|---|---|---:|---|
| id | identificador | sim | Identificador único |
| email | texto | sim | E-mail utilizado para acesso |
| status | enum | sim | Situação atual do usuário |
| criado_em | data/hora | sim | Data de criação |

### Restrições

- e-mail deve ser único;
- usuário deve possuir um status válido.

### Relacionamentos

- possui um Perfil;
- pode possuir uma ou mais Permissões.

### Regras relacionadas

- RN-001
- RN-005

### Histórias relacionadas

- H-001 — Criar novo usuário
- H-007 — Visualizar perfil
```

**Tipos lógicos permitidos:** `texto`, `inteiro`, `decimal`, `booleano`, `data`, `hora`, `data/hora`, `enum`, `identificador`, `arquivo`, `lista`, `objeto`.

Evite `VARCHAR(255)`, `BIGINT`, `JSONB`, `UUID`, `TIMESTAMPTZ` — pertencem à implementação.

Nos relacionamentos, indique quando possível: um para um, um para muitos, muitos para muitos, obrigatório, opcional.

Origem principal: entidades e atributos citados em **O que acontece**; restrições em **O que não pode acontecer**.

---

# 3. mapa-de-fluxos.md — `FL-`

Sequências de comportamento que atravessam ações, decisões, telas ou serviços. Um fluxo não é uma tela.

```md
# Mapa de Fluxos

## FL-001 — Autenticação

### Objetivo

Autenticar o usuário e encaminhá-lo ao destino apropriado.

### Início

Usuário solicita acesso ao sistema.

### Fluxo

1. Usuário informa e-mail e senha.
2. Sistema valida credenciais.
3. Sistema verifica situação do usuário.
4. Sistema verifica se o perfil está completo.
5. Sistema cria a sessão.
6. Sistema encaminha o usuário.

### Decisões

#### Credenciais inválidas

Exibir erro de autenticação.

#### Usuário bloqueado

Impedir acesso.

#### Perfil incompleto

Encaminhar para preenchimento do perfil.

#### Perfil completo

Encaminhar para o painel principal.

### Término

Usuário autenticado ou tentativa recusada.

### Telas relacionadas

- T-001 — Login
- T-004 — Completar perfil
- T-010 — Painel

### Histórias relacionadas

- H-004 — Realizar login
- H-006 — Recuperar senha
```

**Crie fluxo quando** houver sequência relevante com múltiplas etapas, decisões, estados, telas, atores ou serviços. Não crie fluxo para operação simples sem sequência significativa.

Origem principal: **O que acontece** (passos), **Resultados possíveis** (decisões e términos) e **Histórias relacionadas** (encadeamento entre Histórias — a primeira relação é a continuação natural do fluxo).

---

# 4. mapa-de-telas.md — `TL-`

Telas necessárias e suas responsabilidades. Sem implementação de framework. A ligação tela → rota → arquivo fica em `docs/rotas.md`, mantido pela skill `expo-app`.

```md
# Mapa de Telas

## TL-001 — Login

### Objetivo

Permitir autenticação do usuário.

### Atores

- Usuário

### Campos

- E-mail
- Senha

### Ações

- Entrar
- Recuperar senha

### Estados

- inicial;
- carregando;
- erro de autenticação;
- usuário bloqueado;
- sucesso.

### Navegação

Entrada:
- acesso direto;
- sessão expirada.

Saída:
- painel principal;
- completar perfil;
- recuperar senha.

### Histórias relacionadas

- H-004 — Realizar login
- H-006 — Recuperar senha
```

Deve conter, quando aplicável: código, nome, objetivo, atores, campos, ações, estados, navegação de entrada e saída, componentes funcionais, permissões de acesso, Histórias relacionadas.

**Antes de criar uma tela, verifique se a ação cabe numa existente.** `Visualizar usuário`, `Editar usuário` e `Bloquear usuário` provavelmente são a mesma tela.

Origem principal: **Local** (identifica a tela), **Atores**, **O que acontece** (campos e ações) e **Resultados possíveis** (estados).

Quando `guia-visual.md` existir, referencie os padrões em vez de descrever aparência:

```md
### Componentes

- GV-LAY-002 — Formulário centralizado
- GV-CMP-001 — Botão (primary)
- GV-CMP-002 — Campo
```

---

# 5. contratos-de-api.md — `API-`

Comunicação entre o app e o backend — a fronteira que permite os dois evoluírem desacoplados.

O arquivo começa com o bloco **Convenções gerais** do template
(`assets/templates/docs/contratos-de-api.md`): envelope de erro, códigos HTTP, paginação,
autenticação e formato de datas/valores. Cada `API-` só registra o que foge ou completa isso.

````md
## API-001 — Criar usuário

- **Método / recurso:** `POST /usuarios`
- **Objetivo:** criar um novo usuário não confirmado
- **Autenticação:** pública
- **Autorização:** —

### Entrada
```json
{ "email": "usuario@exemplo.com", "senha": "texto (mín. 8)" }
```

### Sucesso — 201
```json
{ "id": "identificador", "email": "usuario@exemplo.com", "status": "nao_confirmado" }
```

### Erros (envelope padrão)
| Status | code | Quando | fieldErrors |
|---|---|---|---|
| 422 | DADOS_INVALIDOS | campo ausente ou fora do formato | `email`, `senha` |
| 409 | EMAIL_DUPLICADO | e-mail já cadastrado (RN-001) | `email` |

### Rastreabilidade
- Regras: RN-001 · Entidades: ENT-001 · Histórias: H-001 — Criar novo usuário
````

Os contratos devem definir: intenção da operação, método, recurso, autenticação, autorização, parâmetros, entrada, saída, estados de sucesso, erros com `code` e `fieldErrors` quando for erro de campo, e — quando aplicável — paginação, filtros e ordenação. O que não estiver definido vira `PENDENTE_DE_DEFINICAO`.

Regras de contrato da casa (valem para qualquer backend):
- Todo erro usa o envelope `{ "code", "message", "fieldErrors" }`; o app nunca mostra `message` cru — traduz pelo `code`.
- Erro de campo é **422** com `fieldErrors` apontando os campos (o app marca cada campo).
- `code` em MAIÚSCULAS_COM_UNDERLINE, estável: é o que o app e os testes usam.
- Lista longa usa paginação por cursor (`limit`, `cursor` → `items`, `nextCursor`).
- Nomes de campos seguem um padrão só por projeto (definido nas Convenções gerais); o app converte no mapper.
- Se o backend gerar `openapi.json`, ele deve bater com este arquivo; divergência é `CONFLITO`.

Sem código de implementação de nenhum framework.

Origem principal: **O que acontece** (operação e entrada), **Resultados possíveis** (respostas de sucesso e erro), **O que não pode acontecer** (códigos de erro) e **Atores** (autenticação e autorização).

---

# Resultado esperado

```text
/projeto
│
├── docs/
│   ├── produto.md            (normativo: capítulos, papéis, vocabulário)
│   ├── historias/
│   │   ├── H-001-criar-novo-usuario.md
│   │   ├── ...
│   │   └── indice.md
│   ├── regras-de-negocio.md
│   ├── modelo-de-dados.md
│   ├── mapa-de-fluxos.md
│   ├── mapa-de-telas.md
│   ├── contratos-de-api.md
│   ├── guia-visual.md        (skill ux-ui)
│   └── rotas.md              (skill expo-app: T- → rota → arquivo)
├── app/                      (Expo)
└── api/                      (backend)
```

# Definições

```text
História         = unidade de intenção
Regra de negócio = restrição ou comportamento permanente do domínio
Fluxo            = sequência de comportamento
Tela             = ponto de interação com o usuário
Modelo de dados  = estrutura conceitual da informação
Contrato de API  = acordo de comunicação entre partes do sistema
```
