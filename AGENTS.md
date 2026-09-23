# AGENTS.md

## Visão geral

Este projeto utiliza **DAH — Desenvolvimento Assistido por Histórias**.

O trabalho deve seguir uma trilha operacional composta por seis prompts principais:

```text
P-01 — Gerenciar Backlog e Cronograma
P-02 — Escrever e Revisar História
P-03 — Atualizar Documentação DAH
P-04 — Definir e Atualizar Interface
P-05 — Implementar e Validar História
P-06 — Homologar e Publicar
```

Os prompts são a interface operacional do projeto.

As skills são capacidades técnicas utilizadas internamente por esses prompts, e ficam em:

```text
.claude/skills/
```

O diretório é `skills`, no plural. Cada skill é uma pasta com um `SKILL.md` na raiz:

```text
.claude/skills/dah-historia/SKILL.md
```

O agente deve seguir a trilha, respeitar os gates definidos e evitar executar etapas fora de ordem.

Há **três gates humanos** na trilha, e nenhum agente atravessa qualquer um deles sozinho:

```text
pronta para aprovação   → aprovada    "Aprovo H-017."                (P-02)
pronta para homologação → homologada  "Homologo a release 1.4.0."    (P-06)
homologada              → publicada   "Aprovo publicação da 1.4.0."  (P-06)
```

---

# 1. Princípio central

```text
BACKLOG
  ↓
HISTÓRIA
  ↓
DOCUMENTAÇÃO
  ↓
INTERFACE
  ↓
IMPLEMENTAÇÃO
  ↓
VALIDAÇÃO
  ↓
HOMOLOGAÇÃO
  ↓
PRODUÇÃO
```

Nada deve ser implementado com base apenas em ideia, título ou suposição.

---

# 2. Regra de ouro

```text
NÃO INVENTAR REQUISITOS.

NÃO ALTERAR COMPORTAMENTO
SEM ATUALIZAR A DAH.

NÃO CONSIDERAR UMA HISTÓRIA CONCLUÍDA
SEM TESTES E EVIDÊNCIAS.

NÃO PUBLICAR PRODUÇÃO
SEM HOMOLOGAÇÃO E APROVAÇÃO HUMANA.

NÃO ESCREVER EM DOCUMENTO
QUE PERTENCE A OUTRA SKILL.
```

---

# 3. Documentos oficiais da DAH

A documentação oficial do projeto fica em:

```text
docs/
├── historias/
│   ├── indice.md
│   └── H-xxx ...
├── regras-de-negocio.md
├── modelo-de-dados.md
├── contratos-de-api.md
├── mapa-de-fluxos.md
├── mapa-de-telas.md
├── guia-visual.md
├── mapa-de-testes.md
├── mapa-de-decisoes.md
├── diario-de-bordo.md
└── cronograma.md
```

`docs/deploy.md` também vive aqui, mas é documento **operacional**, não DAH:
registra remoto, ambientes, pipeline, backup e credenciais do projeto. Dono:
`git-deploy`, com a `devops`.

Arquivos de história usam slug, sem espaços e sem acentos:

```text
docs/historias/H-017-recuperar-senha.md
```

O título legível, com acentos, fica no `#` do arquivo e no `indice.md`.

Não criar documentação paralela sem necessidade explícita.

Antes de criar um novo documento, perguntar:

```text
essa informação cabe em um documento oficial existente?
```

Se sim, usar o documento existente.

---

# 3.1. Propriedade dos documentos

Cada documento tem **uma** skill proprietária. As demais apenas leem.

Essa é a regra que impede dois agentes de escreverem a mesma verdade de formas
diferentes.

| Documento | Proprietária | Escrito durante |
|---|---|---|
| `docs/historias/indice.md` | `dah-historia` | P-01, P-02 |
| `docs/historias/H-xxx-*.md` | `dah-historia` | P-02 |
| `docs/regras-de-negocio.md` | `dah-documentacao` | P-03 |
| `docs/modelo-de-dados.md` | `dah-documentacao` | P-03 |
| `docs/contratos-de-api.md` | `dah-documentacao` | P-03 |
| `docs/mapa-de-fluxos.md` | `dah-documentacao` | P-03 |
| `docs/mapa-de-telas.md` | `dah-documentacao` | P-03 |
| `docs/mapa-de-decisoes.md` | `dah-documentacao` | P-03, e ver abaixo |
| `docs/guia-visual.md` | `ux-ui` | P-04 |
| `docs/mapa-de-testes.md` | `testing-quality` | P-05, P-06 |
| `docs/cronograma.md` | `project-governance` | todos |
| `docs/diario-de-bordo.md` | `project-governance` | todos |
| `docs/deploy.md` (operacional) | `git-deploy`, com a `devops` | criação do repositório, P-06 |

`cronograma.md` e `diario-de-bordo.md` são atravessados por toda a trilha. Por isso não
pertencem a nenhum prompt específico: são da governança, que os mantém em nome de quem
estiver executando.

## Skills de implementação não escrevem documentação

`backend-core`, `backend-api`, `backend-async`, `backend-integrations`, `backend-ai-mcp`,
`expo-app`, `security`, `devops` e `git-deploy` **implementam** o que está nos
documentos, e nunca os editam.

`frontend-web` não implementa: é skill de designer e apoia o P-04. Também não edita o
`guia-visual.md` — a dona é a `ux-ui`.

Se uma dessas skills discordar do documento, ela informa o usuário. Quem corrige é o
prompt proprietário.

## Exceção: mapa de decisões

`mapa-de-decisoes.md` tem quatro escritores, com escopos separados:

| Prompt | Numera decisão de | Pode editar decisão existente? |
|---|---|---|
| P-03 | produto, regra, dados, API, fluxo, estrutura | sim — é o único |
| P-04 | visual e movimento | não, só acrescenta |
| P-05 | técnica de implementação | não, só acrescenta |
| P-06 | operacional, deploy, infraestrutura | não, só acrescenta |

P-04, P-05 e P-06 numeram direto porque rodam depois do P-03 e não teriam quem
numerasse. Antes de numerar, os três seguem o mesmo procedimento:

```text
1. reler mapa-de-decisoes.md inteiro
2. identificar o maior D-xxx em uso
3. usar o próximo número
4. gravar imediatamente
5. nunca reservar faixa
```

Decisão fora do próprio escopo não é numerada: volta para o P-03.

Substituir decisão é exclusivo do P-03.

---

# 4. Índice de histórias

O backlog oficial fica em:

```text
docs/historias/indice.md
```

Formato:

```markdown
| Código | Título | Capítulo | Release | Status |
|---|---|---|---|---|
| H-001 | Criar novo usuário | Credenciamento e acesso | MVP | planejada |
```

`Release` guarda o escopo da entrega (`MVP`, `V1`, `V2`). O número da **Versão** da
história fica apenas dentro do arquivo dela, para não haver dois lugares a sincronizar.

Linha sem `Código` = história planejada e ainda não escrita.

---

# 5. Numeração das histórias

A numeração é global:

```text
H-001
H-002
H-003
...
```

Regras:

- nunca reutilizar código;
- nunca renumerar histórias existentes;
- história cancelada mantém seu código;
- capítulo não interfere na numeração;
- nova história recebe o próximo número livre.

## Demais sequências

Todas são globais e nenhuma reutiliza código.

| Código | Significado | Quem atribui | Documento |
|---|---|---|---|
| `H-xxx` | História | P-01 (`dah-historia`) | `indice.md` |
| `RN-xxx` | Regra de negócio | P-03 (`dah-documentacao`) | `regras-de-negocio.md` |
| `F-xxx` | Fluxo | P-03 (`dah-documentacao`) | `mapa-de-fluxos.md` |
| `TL-xxx` | Tela | P-03 (`dah-documentacao`) | `mapa-de-telas.md` |
| `INT-xxx` | Integração externa | P-03 (`dah-documentacao`) | `contratos-de-api.md` |
| `D-xxx` | Decisão | P-03, P-04, P-05, P-06 (ver 3.1) | `mapa-de-decisoes.md` |
| `T-xxx` | Teste | `testing-quality` | `mapa-de-testes.md` |

O P-02 pode **descrever** uma regra ou uma decisão em aberto na seção `Pendências` da
história, mas sem número. O P-03 converte ao consolidar.

Integrações externas não têm documento próprio: são seções `INT-xxx` dentro de
`contratos-de-api.md`, que cobre as duas direções — a API que o sistema expõe e a que
ele consome.

---

# 6. Status oficiais das histórias

```text
planejada
rascunho
pronta para aprovação
aprovada
em desenvolvimento
pronta para homologação
homologada
implementada
cancelada
```

Fluxo padrão:

```text
planejada
   ↓
rascunho
   ↓
pronta para aprovação
   ↓
APROVAÇÃO HUMANA
   ↓
aprovada
   ↓
em desenvolvimento
   ↓
pronta para homologação
   ↓
homologada
   ↓
implementada
```

---

# 7. Aprovação humana

São três atos distintos, e nenhum deles é do agente:

| Ato | Transição | Confirmação | Prompt |
|---|---|---|---|
| Aprovar | `pronta para aprovação` → `aprovada` | "Aprovo H-017." | P-02 |
| Homologar | `pronta para homologação` → `homologada` | "Homologo a release 1.4.0." | P-06 |
| Autorizar | `homologada` → publicada | "Aprovo publicação da release 1.4.0." | P-06 |

Aprovar diz que a **especificação** está certa.

Homologar diz que a **entrega** está certa.

Autorizar diz que é **hora** de publicá-la.

Passar nos testes não homologa. Estar homologada não autoriza publicação.

Sem confirmação explícita, a história não avança.

---

# 8. Significado dos estados finais

```text
pronta para homologação
=
implementação concluída em DEV
+
testes aplicáveis aprovados
+
documentação atualizada
+
nenhuma pendência bloqueante
```

```text
homologada
=
validada em HOM
```

```text
implementada
=
entregue e validada em PROD
```

---

# 9. Capítulos

Capítulo é classificação funcional.

Exemplos:

```text
Credenciamento e acesso
Perfil
Permissões
Comunicação
Financeiro
Relatórios
Administração
```

Capítulo:

- não define numeração;
- não exige pasta própria;
- pode receber novas histórias futuramente.

---

# 10. Cronograma

O cronograma oficial fica em:

```text
docs/cronograma.md
```

A unidade de produtividade é:

```text
histórias prontas para homologação / dia
```

O calendário usa:

```text
dias corridos
```

A capacidade é definida no processo.

Valores comuns:

```text
10 histórias/dia
5 histórias/dia
3 histórias/dia
```

Aceitar outro valor quando explicitamente definido.

Não alterar a capacidade automaticamente.

---

# 11. Cronograma vivo

O cronograma deve ser atualizado quando ocorrer:

```text
nova história
cancelamento
aprovação
início de desenvolvimento
bloqueio
desbloqueio
teste crítico falhando
teste aprovado
mudança de escopo
história pronta para homologação
homologação
publicação
decisão que altera dependências
```

---

# 12. Capacidade planejada x real

Registrar separadamente quando houver histórico suficiente:

```text
Capacidade configurada: 5/dia
Média real observada: 4,2/dia
```

Se houver diferença persistente:

```text
sugerir revisão
↓
aguardar decisão humana
```

Não mudar a capacidade automaticamente.

---

# 13. Trilha operacional

## P-01 — Gerenciar Backlog e Cronograma

Responsável por:

```text
capítulos
backlog
indice.md
numeração
dependências
bloqueios
cronograma
```

O P-01:

- cria ou atualiza o backlog;
- não escreve histórias completas;
- não aprova histórias;
- não implementa código.

Saída típica:

```text
Próxima ação:
P-02 H-xxx
```

---

## P-02 — Escrever e Revisar História

Trabalha com:

```text
UMA história por execução
```

Responsável por:

```text
contexto
objetivo
atores
pré-condições
fluxo principal
fluxos alternativos
exceções
regras
validações
permissões
dados envolvidos
integrações
dependências
resultado esperado
critérios de aceite
```

Fluxo:

```text
planejada
↓
rascunho
↓
pronta para aprovação
↓
aguardar usuário
```

O P-02 nunca aprova a história sozinho.

Após aprovação humana:

```text
status → aprovada
↓
P-03
```

---

## P-03 — Atualizar Documentação DAH

Recebe:

```text
UMA história aprovada
```

Atualiza, quando houver impacto:

```text
docs/regras-de-negocio.md
docs/modelo-de-dados.md
docs/contratos-de-api.md
docs/mapa-de-fluxos.md
docs/mapa-de-telas.md
docs/mapa-de-decisoes.md
```

O P-03:

- consolida o estado atual do sistema;
- não cria documentos por história;
- detecta conflitos;
- pergunta antes de inventar;
- não implementa código;
- não cria o guia visual.

O `mapa-de-telas.md` é **inteiramente** dele: estrutura, estados, navegação, permissão,
confirmação, plataforma e reorganização em tela estreita. O P-04 não escreve nele.

Integrações externas entram como `INT-xxx` dentro de `contratos-de-api.md`.

---

## P-04 — Definir Grafismo e Animação da Interface

O P-04 define **como a interface se apresenta e se move**. Não define o que ela faz,
quais telas existem nem como o usuário navega — isso é do P-03.

Regra de corte:

```text
"o que acontece?"   → P-03, mapa-de-telas.md
"como isso aparece?" → P-04, guia-visual.md
```

| Assunto | P-03 define | P-04 define |
|---|---|---|
| Navegação | o padrão (sidebar, tabs, bottom nav) | largura, cor, ícones, animação |
| Estado vazio | o que falta e qual a saída | ilustração, tipografia, espaçamento |
| Confirmação | quais ações exigem | aparência do modal e dos botões |
| Sem permissão | ocultar, desabilitar ou explicar | aparência do desabilitado |
| Carregamento | que a operação é assíncrona | spinner ou skeleton, duração, easing |
| Tela estreita | tabela vira lista ou card | densidade e tipografia dessa forma |

Atualiza:

```text
docs/guia-visual.md
```

Pode perguntar sobre:

```text
público
identidade
cores
tipografia
densidade
referências
modo escuro
intensidade de movimento
contraste e texto mínimo
```

Não pergunta plataforma: ela já está registrada por tela no `mapa-de-telas.md`.

Executar antes da primeira implementação de frontend, e depois quando a história
introduzir componente, tratamento visual ou animação que o guia ainda não cobre. Tela
nova que só recombina padrões existentes vai direto ao P-05.

O P-04 não implementa frontend.

Se o guia atual já cobre a história:

```text
nenhuma alteração necessária
↓
P-05
```

---

## P-05 — Implementar e Validar História

Recebe:

```text
UMA história aprovada
```

Antes do código:

```text
verifica documentação
↓
cria/atualiza mapa-de-testes.md
↓
status → em desenvolvimento
```

Depois implementa somente o necessário:

```text
backend
frontend
integrações
tasks
IA/MCP
storage
migration
infra necessária para DEV
```

Seleciona as skills a partir do impacto documental, confirmando a sugestão que o P-03
já deixou na sua saída:

```text
modelo-de-dados.md alterado   → backend-core
contratos-de-api.md alterado  → backend-api
INT-xxx criado                → backend-integrations
task ou fila                  → backend-async
IA ou MCP                     → backend-ai-mcp
tela web, aplicativo ou ambas → expo-app
```

Depois executa:

```text
testing-quality    (funcional, integração, E2E, usabilidade)
security    quando aplicável
devops             somente para rodar em DEV
```

Se falhar:

```text
corrigir
↓
retestar
```

Quando tudo aplicável estiver aprovado:

```text
status → pronta para homologação
```

O P-05 não publica HOM ou PROD.

---

## P-06 — Homologar e Publicar

Recebe:

```text
uma ou mais histórias prontas para homologação
```

Fluxo:

```text
DEV
↓
HOM
↓
testing-quality + security + usabilidade + E2E
↓
GATE HUMANO 1 — "Homologo a release"
↓
homologada
↓
gate operacional
↓
GATE HUMANO 2 — "Aprovo publicação"
↓
PROD
↓
smoke + health + observabilidade
↓
implementada
```

Passar nos testes de HOM **não** homologa. O agente apresenta o resultado e aguarda.

## Publicação mobile

Se a release incluir tela de plataforma `aplicativo` ou `ambas`, há duas publicações a
coordenar:

```text
servidor    → git-deploy promove o artefato, devops prepara o ambiente
aplicativo  → expo-app faz build assinado e submete às lojas
```

Ordem obrigatória: **backend primeiro**. Depois que o app é publicado, versões antigas
continuam instaladas chamando a API por semanas, então a API em PROD precisa atender a
versão anterior antes de o app novo ser submetido.

O aplicativo não tem rollback. A única correção é publicar outra versão e esperar a
revisão da loja.

As histórias só passam a `implementada` quando o app estiver disponível na loja — não
quando a submissão é enviada.

O P-06:

- não cria funcionalidade;
- não corrige bug diretamente;
- não edita decisão de outro prompt;
- retorna para P-05 quando houver falha;
- exige homologação humana antes de `homologada`;
- exige aprovação humana antes de PROD.

---

# 14. Skills

Skills são nomeadas pelo domínio, em minúsculas, com hífen, **sem prefixo numérico**.

## Governança

| Skill | Responsável por |
|---|---|
| `project-governance` | estado do projeto, máquina de status, dependências, bloqueios, consistência entre documentos, Definition of Ready e Done, `cronograma.md`, `diario-de-bordo.md` |

Fronteira com as skills DAH, para não se sobreporem:

```text
project-governance  → o ESTADO do trabalho
                      qual história está onde, o que bloqueia, quanto falta

dah-historia        → o CONTEÚDO das histórias
                      backlog, índice, texto da história, critérios de aceite

dah-documentacao    → a VERDADE do sistema
                      regras, dados, API, fluxos, telas, decisões
```

## DAH

| Skill | Executa | Mantém |
|---|---|---|
| `dah-historia` | P-01, P-02 | `indice.md`, arquivos de história |
| `dah-documentacao` | P-03 | os seis documentos consolidados |

## Backend

| Skill | Domínio |
|---|---|
| `backend-core` | models, services, selectors, validators, permissions, transactions, migrations |
| `backend-api` | DRF, serializers, views, urls, filters, pagination, OpenAPI |
| `backend-async` | Celery, Redis, tasks, jobs, retry, idempotência, Beat, queues |
| `backend-ai-mcp` | LLM, RAG, agents, MCP, tools, structured output |
| `backend-integrations` | REST, GraphQL, webhooks, OAuth, clients, adapters, retries, rate limits |

## Interface

| Skill | Domínio |
|---|---|
| `ux-ui` | executa o P-04: grafismo, tipografia, cor, espaçamento, animação. Mantém `guia-visual.md` |
| `frontend-web` | skill de designer: direção estética. Apoia o P-04 e não é dona de documento |
| `expo-app` | implementa `frontend/` — web, iOS e Android — e publica nas lojas |

Design e programação são camadas distintas:

```text
DESIGN       P-04   ux-ui + frontend-web   →  decisão visual
PROGRAMAÇÃO  P-05   expo-app               →  código
```

`ux-ui` e `frontend-web` **não implementam**. Elas definem; `expo-app` constrói.

## Qualidade e operação

| Skill | Domínio |
|---|---|
| `testing-quality` | testes de todos os tipos, quality gates, evidências. Mantém `mapa-de-testes.md` |
| `security` | autenticação, autorização, tenant isolation, secrets, hardening |
| `devops` | ambientes, Docker, CI/CD, migrations, PostgreSQL, Redis, MinIO, Traefik, health, logs, métricas, backup |
| `git-deploy` | branch, merge, tag, release, promoção de artefato, rollback de versão |

### Fronteira devops × git-deploy

A confusão comum é tratar deploy como uma coisa só. São duas:

```text
git-deploy  → O QUE é promovido
              artefato, commit, tag, release, merge, rollback de versão

devops      → PARA ONDE e SOB QUE CONDIÇÕES
              ambiente, variáveis, secrets, banco, Redis, storage,
              workers, proxy, health, backup, observabilidade
```

> **Renomeação aplicada:** `frontend-design` passou a `frontend-web`, porque o nome
> anterior colidia com uma skill pública que opina sobre tokens e direção visual —
> justamente o terreno do `guia-visual.md`. A varredura foi concluída: não há mais
> referências ao nome antigo. Sobre o papel dela na camada de design, ver `D-004`.

---

# 15. Detalhamento das skills de backend

## `backend-core`

```text
models
services
selectors
validators
permissions
transactions
persistência
```

## `backend-api`

```text
DRF
serializers
views
urls
filters
pagination
OpenAPI
HTTP permissions
```

## `backend-async`

```text
Celery
Redis
tasks
jobs
retry
idempotência
Beat
queues
```

Princípio:

```text
CELERY EXECUTA
SERVICE DECIDE
POSTGRESQL GUARDA ESTADO
REDIS TRANSPORTA TRABALHO
```

## `backend-ai-mcp`

```text
LLM
RAG
agents
MCP
tools
structured output
```

IA não é autoridade de:

```text
permissão
integridade
decisão determinística crítica
```

## `backend-integrations`

```text
REST
GraphQL
webhooks
OAuth
API keys
clients
adapters
timeouts
retries
rate limits
sync
```

---

# 16. `testing-quality`

Responsável por:

```text
testes unitários
integração
API
frontend
E2E
regressão
contratos
usabilidade técnica
quality gates
evidências
```

O documento oficial é:

```text
docs/mapa-de-testes.md
```

---

# 17. `security`

Responsável por:

```text
autenticação
autorização
tenant isolation
secrets
API security
XSS
CSRF
SSRF
uploads
dados sensíveis
integrações
IA/MCP
hardening
supply chain
```

Testes de segurança devem ser registrados em:

```text
docs/mapa-de-testes.md
```

---

# 18. `devops` e `git-deploy`

Responsável por:

```text
ambientes
Docker
CI/CD
build
deploy
migrations
rollback
PostgreSQL
Redis
Celery
MinIO
Traefik
HTTPS
health
logs
métricas
alertas
backup
restore
```

`git-deploy` é responsável por:

```text
branch
merge
tag
release
versionamento
promoção do artefato entre ambientes
rollback de versão
```

`devops` cuida do ambiente; `git-deploy` cuida do que entra nele.

Numa promoção para PROD, as duas atuam em sequência:

```text
git-deploy  identifica e promove a imagem homologada
devops      garante variáveis, banco migrado e workers ativos
devops      confirma health
git-deploy  executa rollback se devops reprovar
```

---

# 19. Arquitetura backend

Padrão:

```text
Python
Django
Django REST Framework
PostgreSQL
Redis
Celery quando necessário
MinIO quando necessário
```

Arquitetura:

```text
monólito modular
API-first
frontend desacoplado
```

---

# 20. Organização por domínio

Preferir:

```text
backend/apps/<dominio>/
├── models.py
├── services.py
├── selectors.py
├── validators.py
├── permissions.py
├── tasks.py
├── api/
└── tests/
```

Princípio:

```text
models.py
→ estrutura e integridade

services.py
→ casos de uso e mudança de estado

selectors.py
→ consultas

permissions.py
→ autorização de domínio

api/
→ HTTP

tasks.py
→ adaptação assíncrona
```

Esta seção é a **fonte única** dessa arquitetura. Os prompts não devem reespecificá-la:
se o P-05 repetir a mesma estrutura, as duas versões divergem na primeira edição.

---

# 21. Frontend

O frontend deve permanecer desacoplado do backend.

Pode existir em:

| Diretório | Skill |
|---|---|
| `frontend/` | `expo-app` — Android, iOS e Web a partir da mesma base |

`expo-app` é a única stack de frontend da casa. O web sai de `frontend/` por
`expo export --platform web`, que é o que `frontend/Dockerfile.web` constrói. Por isso
o campo **plataforma** de cada tela em `mapa-de-telas.md` — `web`, `aplicativo` ou
`ambas` — decide o alvo do build, não a skill: ela é sempre a mesma.

Não existe um segundo projeto de frontend.

Frontend deve seguir:

```text
mapa-de-telas.md     → o QUE acontece: estrutura, estados, navegação, permissão
guia-visual.md       → COMO aparece: cor, tipografia, espaço, animação
mapa-de-fluxos.md    → percurso do usuário
contratos-de-api.md  → comunicação
```

Acessibilidade está dividida entre os dois primeiros:

```text
mapa-de-telas.md  → ordem de teclado, foco em modal, labels, semântica
guia-visual.md    → contraste, anel de foco, texto mínimo, área de toque
```

---

# 22. Mapa de testes

Documento:

```text
docs/mapa-de-testes.md
```

Proprietária: `testing-quality`, acionada pelo P-05 e pelo P-06.

Nenhum outro prompt escreve neste arquivo diretamente.

Identificação global:

```text
T-001
T-002
T-003
...
```

Tipos possíveis:

```text
Funcional
Integração
E2E
Usabilidade
Segurança
Performance
```

Status:

```text
planejado
pendente
em execução
aprovado
falhou
bloqueado
quarentena
não aplicável
```

`quarentena` é teste instável, que falha de forma intermitente: fica isolado
para não mascarar regressão real, e a pendência de correção é registrada.

Regra:

```text
ANTES DO CÓDIGO
→ definir o que precisa ser provado

DEPOIS DO CÓDIGO
→ executar e registrar evidência
```

Uma história não fica pronta para homologação com teste crítico:

```text
pendente
falhou
bloqueado
```

---

# 23. Regras de negócio

Documento:

```text
docs/regras-de-negocio.md
```

Numeração:

```text
RN-001
RN-002
...
```

Não duplicar regra existente.

Uma regra pode estar relacionada a várias histórias.

---

# 24. Decisões

Documento:

```text
docs/mapa-de-decisoes.md
```

Numeração:

```text
D-001
D-002
...
```

Proprietária: `dah-documentacao`. P-04, P-05 e P-06 podem acrescentar dentro do próprio
escopo, sem editar o que já existe. Ver seção 3.1.

Status preferidos:

```text
proposta
ativa
substituída
cancelada
```

O código é atribuído já na proposta, para não haver duas decisões disputando o mesmo
número enquanto uma aguarda resposta.

Criar decisão quando houver escolha relevante sobre:

```text
arquitetura
tecnologia
dados
segurança
integração
fluxo estrutural
produto
infraestrutura
```

Se depender de escolha humana:

```text
registrar como proposta
↓
perguntar
↓
aguardar resposta
```

Não decidir silenciosamente.

---

# 25. Diário de bordo

Documento:

```text
docs/diario-de-bordo.md
```

Serve para:

```text
retomar o projeto
entender onde parou
saber o que falta
ver bloqueios
ver decisões
ver próximo passo
```

Não é log técnico.

Registrar:

```text
marcos
bloqueios
decisões
mudanças importantes
resultado de implementação
resultado de homologação
incidentes
próximo passo
```

---

# 26. Mudança de requisito durante implementação

Se P-05 descobrir mudança funcional:

```text
NÃO ALTERAR SILENCIOSAMENTE
```

Fluxo:

```text
história → rascunho
↓
incrementar versão quando aplicável
↓
P-02
↓
aprovação humana
↓
P-03
↓
P-04 se necessário
↓
P-05 continua
```

---

# 27. Nova história descoberta durante implementação

Não criar comportamento extra dentro da história atual.

Fluxo:

```text
necessidade nova
↓
P-01
↓
novo item no backlog
```

---

# 28. Conflito documental

Detectar conflitos entre:

```text
história ↔ regras
história ↔ dados
história ↔ API
história ↔ fluxo
história ↔ telas
história ↔ decisão
dados ↔ API
fluxo ↔ telas
decisão ↔ implementação
```

Se houver conflito relevante:

```text
não escolher silenciosamente
```

Perguntar.

---

# 29. Fonte de verdade

```text
Histórias
→ definem comportamento aprovado

Documentos consolidados
→ definem o estado esperado do sistema

Código
→ implementa esse estado

Testes
→ comprovam o comportamento

Decisões
→ explicam por que escolhas foram feitas

Diário
→ registra a evolução

Cronograma
→ mostra a previsão atual
```

---

# 30. Ambientes oficiais

```text
DEV
HOM
PROD
```

## DEV

```text
desenvolvimento
integração
testes locais/CI
preparação da história
```

## HOM

```text
homologação
QA integrado
E2E
segurança
usabilidade
migration test
validação pré-produção
```

## PROD

```text
uso real
dados reais
operação
monitoramento
backup
```

Produção deve ter:

```text
DEBUG=False
HTTPS
secrets protegidos
health checks
logs
backup
rollback
```

---

# 31. QA não é ambiente

Por padrão, não existe ambiente separado chamado `QA`.

QA é processo executado em:

```text
DEV/CI
+
HOM
```

---

# 32. Branch não é ambiente

```text
main
```

é branch.

```text
DEV
HOM
PROD
```

são ambientes.

Neste template, cada ambiente é construído a partir de uma branch própria, por decisão da casa:

```text
dev   → DEV
hom   → HOM
main  → PROD
```

Promoção: `feat|fix/H-xxx` (a partir de `dev`) → PR para `dev` → PR `dev → hom` → PR `hom → main`.
Hotfix: `hotfix/slug` a partir de `main` → PR para `main` → back-merge `main → hom → dev`.
Detalhes do projeto em `docs/deploy.md`, que prevalece sobre o fluxo `develop`/`main` das skills.

Não criar outras branches de ambiente além dessas três.

---

# 33. Artefato

Preferir:

```text
MESMO ARTEFATO
DEV → HOM → PROD
```

Exemplos de identificação:

```text
commit SHA
tag
versão
digest da imagem
```

Evitar depender apenas de:

```text
latest
```

---

# 34. Produção exige aprovação humana

Antes do deploy final:

```text
P-06
↓
testes de HOM aprovados
↓
resumo apresentado
↓
HOMOLOGAÇÃO HUMANA
↓
homologada
↓
gate operacional
↓
resumo da release e riscos
↓
APROVAÇÃO HUMANA PARA PUBLICAR
↓
PROD
```

Sem confirmação explícita:

```text
não publicar
```

---

# 35. Segurança

Nunca armazenar em documentação:

```text
senha
token
API key
private key
secret real
```

Usar nomes de variáveis e referências seguras.

Não copiar dados reais de PROD para DEV/HOM sem necessidade, autorização e sanitização adequada.

---

# 36. Git

Quando adotado branch por história:

```text
feat/H-017-nome-da-historia
```

Commits podem referenciar:

```text
H-017
```

Não misturar várias histórias independentes no mesmo trabalho sem necessidade.

---

# 37. Retomada de trabalho

Ao retomar um projeto:

1. leia `AGENTS.md`;
2. leia `docs/historias/indice.md`;
3. leia `docs/cronograma.md`;
4. leia entradas recentes do `docs/diario-de-bordo.md`;
5. leia decisões pendentes;
6. identifique:
   - história atual;
   - status;
   - bloqueios;
   - próximo prompt;
   - próxima ação.

Não recomeçar do zero.

---

# 38. Seleção automática do próximo prompt

```text
planejada
→ P-02

rascunho
→ P-02

pronta para aprovação
→ aguardar aprovação humana

aprovada
→ P-03
→ P-04 se necessário
→ P-05

em desenvolvimento
→ P-05

pronta para homologação
→ P-06

homologada
→ P-06 para publicação
→ com mobile: permanece homologada até o app sair da revisão da loja

implementada
→ próxima história / P-01

cancelada
→ nenhuma implementação
```

---

# 39. Gate entre P-03 e P-04

Se a história não tem frontend:

```text
P-03
↓
P-05
```

Se tem frontend e o guia visual já é suficiente:

```text
P-03
↓
P-04 valida sem alteração
↓
P-05
```

Se o guia é insuficiente:

```text
P-03
↓
P-04 atualiza
↓
P-05
```

---

# 40. Definition of Ready para P-05

```text
[ ] história aprovada
[ ] regras definidas
[ ] fluxo claro
[ ] dados suficientes
[ ] API suficiente quando aplicável
[ ] telas suficientes quando aplicável
[ ] guia visual suficiente quando aplicável
[ ] dependências resolvidas
[ ] nenhuma decisão crítica pendente
[ ] nenhuma ambiguidade bloqueante
```

---

# 41. Definition of Done — pronta para homologação

```text
[ ] história aprovada
[ ] documentação coerente
[ ] backend implementado quando aplicável
[ ] frontend implementado quando aplicável
[ ] integrações implementadas quando aplicável
[ ] migrations testadas quando aplicável
[ ] mapa de testes atualizado
[ ] critérios de aceite validados
[ ] testes funcionais aprovados
[ ] integração aprovada quando aplicável
[ ] E2E aprovado quando aplicável
[ ] usabilidade aprovada quando aplicável
[ ] segurança aprovada quando aplicável
[ ] nenhuma falha crítica
[ ] nenhuma decisão crítica pendente
[ ] nenhuma pendência bloqueante
[ ] diário atualizado
[ ] cronograma atualizado
```

---

# 42. Definition of Done — release

```text
[ ] histórias homologadas pelo usuário
[ ] testing-quality aprovado em HOM
[ ] security aprovado em HOM
[ ] E2E aplicável aprovado
[ ] migrations aprovadas em HOM
[ ] artefato identificado
[ ] aprovação humana para PROD
[ ] PROD publicado
[ ] health aprovado
[ ] smoke aprovado
[ ] logs verificados
[ ] nenhuma falha crítica
[ ] mapa de testes atualizado
[ ] diário atualizado
[ ] cronograma atualizado
[ ] aplicativo disponível na loja, quando a release tiver mobile
[ ] nenhuma decisão de outro prompt foi editada
[ ] histórias marcadas como implementadas
```

---

# 43. Ordem de trabalho recomendada

```text
P-01
↓
P-02
↓
APROVAÇÃO HUMANA
↓
P-03
↓
P-04 se necessário
↓
P-05
↓
P-06
↓
P-01
```

---

# 44. Quando perguntar

Perguntar quando houver ambiguidade capaz de mudar:

```text
escopo
comportamento
dados
permissão
fluxo
segurança
integração
arquitetura
cronograma
interface estrutural
```

Não perguntar por detalhes já definidos em:

```text
decisão ativa
história aprovada
regra existente
guia visual vigente
contrato vigente
padrão técnico explícito
```

---

# 45. Simplicidade

Não criar:

```text
pastas
serviços
filas
documentos
ambientes
microserviços
monitoramento avançado
```

sem necessidade real.

Preferir o padrão mais simples que atenda o requisito.

---

# 46. Regra final

```text
P-01
ORGANIZA O QUE PRECISA SER FEITO.

P-02
DEFINE UMA HISTÓRIA.

P-03
ATUALIZA A VERDADE DO SISTEMA.

P-04
DEFINE COMO A INTERFACE DEVE SER.

P-05
CONSTRÓI E PROVA QUE FUNCIONA.

P-06
HOMOLOGA, PUBLICA E FECHA O CICLO.
```

E:

```text
PROMPTS
= FLUXO DE OPERAÇÃO

SKILLS
= CAPACIDADES TÉCNICAS

DOCUMENTOS DAH
= MEMÓRIA DO SISTEMA

CÓDIGO
= IMPLEMENTAÇÃO

TESTES
= EVIDÊNCIA

DECISÕES
= MOTIVO

DIÁRIO
= CONTINUIDADE

CRONOGRAMA
= PREVISÃO
```

E a regra que sustenta todas as outras:

```text
CADA DOCUMENTO TEM UM DONO.

QUEM NÃO É DONO, LÊ.

SE DISCORDAR, AVISA.

NUNCA CORRIGE POR CONTA PRÓPRIA.
```
