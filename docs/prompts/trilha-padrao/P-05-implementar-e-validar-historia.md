# P-05 — Implementar e Validar História

## Objetivo

Implementar **uma única história aprovada** de ponta a ponta, utilizando as skills técnicas necessárias e mantendo a DAH sincronizada durante todo o processo.

O P-05 é o principal prompt de execução do projeto.

Ele deve:

```text
ler a história
      ↓
verificar prontidão
      ↓
planejar testes
      ↓
atualizar mapa-de-testes.md
      ↓
implementar backend/frontend
      ↓
executar QA, segurança e usabilidade
      ↓
corrigir falhas
      ↓
retestar
      ↓
atualizar documentos afetados
      ↓
atualizar diário
      ↓
atualizar decisões
      ↓
atualizar cronograma
      ↓
marcar "pronta para homologação"
```

Este prompt trabalha com **uma história por execução**.

---

# Prompt

Você é o agente responsável pela implementação e validação de uma história em um projeto que utiliza DAH — Desenvolvimento Assistido por Histórias.

Trabalhe com **uma única história por execução**.

Receba preferencialmente:

```text
P-05 H-017
```

Antes de alterar código:

1. leia `AGENTS.md`;
2. leia `docs/historias/indice.md`;
3. leia a história solicitada;
4. leia:
   - `docs/regras-de-negocio.md`
   - `docs/modelo-de-dados.md`
   - `docs/contratos-de-api.md`
   - `docs/mapa-de-fluxos.md`
   - `docs/mapa-de-telas.md`
   - `docs/guia-visual.md`
   - `docs/mapa-de-testes.md`
   - `docs/mapa-de-decisoes.md`
   - `docs/diario-de-bordo.md`
   - `docs/cronograma.md`
5. leia histórias diretamente relacionadas quando necessário;
6. inspecione o código existente antes de alterar a arquitetura;
7. leia a saída do P-03 para a história: ela já sugere as skills de implementação;
8. verifique o último `D-xxx` e o último `T-xxx` usados antes de numerar qualquer coisa.

Não implemente com base apenas no título da história.

---

# 0. Mapa de prompts e skills

| Prompt | Responsabilidade | Skill |
|---|---|---|
| P-01 | Gerenciar backlog e cronograma | `dah-historia` |
| P-02 | Escrever e revisar história | `dah-historia` |
| P-03 | Consolidar documentação DAH | `dah-documentacao` |
| P-04 | Grafismo e animação | `ux-ui` |
| P-05 | Implementar e validar (este prompt) | skills de domínio |
| P-06 | Homologar e publicar | `testing-quality`, `security`, `devops`, `git-deploy`, `expo-app` |

O P-05 é o único prompt que **aciona** skills de domínio. Ele não implementa por conta
própria: identifica o impacto técnico e delega.

## Documentos que o P-05 escreve

```text
docs/historias/H-xxx-*.md     status
docs/historias/indice.md      status
docs/mapa-de-testes.md        via testing-quality
docs/mapa-de-decisoes.md      apenas acrescentando (ver seção 34)
docs/diario-de-bordo.md
docs/cronograma.md
```

## Documentos que o P-05 apenas lê

```text
docs/regras-de-negocio.md
docs/modelo-de-dados.md
docs/contratos-de-api.md
docs/mapa-de-fluxos.md
docs/mapa-de-telas.md
docs/guia-visual.md
```

Se o código exigir mudar qualquer um desses seis, **pare**. Eles pertencem ao P-03 e ao
P-04. Ver seções 32, 33 e 53.

---

# 1. Pré-condição

A história deve estar:

```text
aprovada
```

Não iniciar implementação de história em:

```text
planejada
rascunho
pronta para aprovação
cancelada
```

Se estiver `em desenvolvimento`, o P-05 pode continuar a implementação após recuperar o estado atual no diário de bordo.

Se estiver em estágio posterior, não reimplementar silenciosamente.

---

# 2. Verificar documentação antes do código

Confirme que o P-03 já consolidou, quando aplicável:

```text
regras de negócio
modelo de dados
contratos de API
fluxos
telas
decisões
```

Se houver frontend, confirme que:

```text
guia-visual.md
```

é suficiente para a história.

Se não for:

```text
interromper frontend
↓
executar P-04
```

---

# 3. Definition of Ready para implementação

Antes de iniciar:

```text
[ ] história aprovada
[ ] regras necessárias definidas
[ ] fluxo claro
[ ] modelo de dados suficiente
[ ] contrato de API suficiente quando aplicável
[ ] telas definidas quando aplicável
[ ] guia visual suficiente quando houver frontend
[ ] dependências concluídas ou disponíveis
[ ] nenhuma decisão crítica pendente
[ ] nenhuma ambiguidade bloqueante
```

Se algum item essencial falhar:

```text
NÃO IMPLEMENTAR POR SUPOSIÇÃO
```

Informe o bloqueio.

---

# 4. Alterar status

Quando a implementação realmente começar:

```text
aprovada
↓
em desenvolvimento
```

Atualize:

```text
docs/historias/indice.md
arquivo da história
docs/cronograma.md
```

---

# 5. Recuperação de sessão

Se a história já estiver `em desenvolvimento`:

1. leia `docs/diario-de-bordo.md`;
2. identifique:
   - o que já foi concluído;
   - o que falta;
   - testes já executados;
   - decisões pendentes;
   - bloqueios;
3. inspecione o código atual;
4. continue do ponto correto.

Não recomece automaticamente do zero.

---

# PLANEJAMENTO DOS TESTES

## 6. Criar testes antes de implementar

Antes de escrever o código da história, derive os cenários de teste dos:

```text
critérios de aceite
regras de negócio
permissões
fluxos
contratos
telas
```

Atualize:

```text
docs/mapa-de-testes.md
```

antes da implementação.

---

## 7. Tipos de teste

Avalie para cada história:

```text
Funcional
Integração
E2E
Usabilidade
Segurança
Performance
```

Somente os aplicáveis devem ser criados.

---

## 8. Testes funcionais

Devem comprovar o comportamento principal e os erros relevantes.

Exemplo:

```text
T-081 — Funcional
H-023
Usuário autorizado visualiza permissões.
```

---

## 9. Testes de integração

Criar quando houver interação entre:

```text
frontend ↔ API
service ↔ banco
backend ↔ provider
worker ↔ fila
storage ↔ aplicação
```

---

## 10. Testes E2E

Criar quando a história fizer parte de fluxo crítico que precise ser validado do ponto de vista do usuário.

Não transformar toda história em teste E2E se testes menores forem suficientes.

---

## 11. Testes de usabilidade

Quando houver interface, registrar cenários verificáveis de:

```text
clareza da ação
mensagem de erro
loading
sucesso
estado vazio
navegação
responsividade
acessibilidade
confirmações
```

Usabilidade não deve ser tratada apenas como preferência estética.

---

## 12. Testes de segurança

Quando aplicável, `security` deve gerar cenários de:

```text
autenticação
autorização
acesso por objeto
isolamento de tenant
validação de entrada
exposição de dados
upload
rate limit
operação crítica
```

---

## 13. Numeração de testes

Usar sequência global:

```text
T-001
T-002
T-003
...
```

Nunca reutilizar código.

`T-xxx` é atribuído por `testing-quality`, acionada pelo P-05. O
`docs/mapa-de-testes.md` pertence a essa skill — o P-05 não escreve nele diretamente.

Antes de numerar, reler o arquivo e usar o próximo número livre. Nunca reservar faixa.

---

## 14. Estado inicial dos testes

Antes da implementação:

```text
planejado
```

ou:

```text
pendente
```

conforme o padrão adotado no mapa.

---

# PLANEJAMENTO TÉCNICO

## 15. Identificar impacto técnico

Determine o que a história realmente exige:

```text
backend
frontend web
frontend mobile
banco
migration
task assíncrona
integração externa
IA/MCP
storage
cache
permissão
infraestrutura
```

Não alterar partes não relacionadas do sistema.

---

## 16. Selecionar skills

O P-03 já sugeriu as skills na sua saída, derivadas dos documentos que ele alterou.

O P-05 **confirma ou amplia** essa lista a partir do impacto técnico real (seção 15).
Não recomeça a escolha do zero, e não reduz a lista sem justificar.

### Backend

| Skill | Aciona quando a história envolve |
|---|---|
| `backend-core` | domínio, models, services, selectors, permissions, migrations |
| `backend-api` | endpoints, serializers, views, filtros, contratos |
| `backend-async` | tasks, jobs, filas, agendamento |
| `backend-ai-mcp` | IA, RAG, agents, servidores MCP |
| `backend-integrations` | APIs externas, webhooks, adapters |

Gatilho documental: se o P-03 alterou `modelo-de-dados.md`, é `backend-core`; se alterou
`contratos-de-api.md`, é `backend-api`; se criou um `INT-xxx`, é `backend-integrations`.

### Frontend

A escolha vem do campo **plataforma** de cada tela em `mapa-de-telas.md`:

| Plataforma no mapa | Skill |
|---|---|
| web | `expo-app` |
| aplicativo | `expo-app` |
| ambas | `expo-app`, a partir do mesmo registro de tela |

A plataforma decide o alvo do build, não a skill: ela é sempre a mesma.

`ux-ui` **não** é skill de implementação. Ela executa o P-04 e entrega o
`guia-visual.md`. Se o guia estiver insuficiente, o P-05 para o frontend e chama o P-04
(seção 2) — não chama `ux-ui` para programar.

### Transversais

| Skill | Quando |
|---|---|
| `testing-quality` | sempre — planeja e executa os testes, e mantém o `mapa-de-testes.md` |
| `security` | história com impacto de autenticação, autorização, tenant, dados sensíveis, upload ou webhook |
| `devops` | somente quando a história exigir mudança operacional para rodar em DEV (seção 60) |
| `git-deploy` | branch, commit e rastreabilidade (seções 63 a 65) |

`devops` não é acionada para preparar HOM ou PROD durante o P-05. Isso é P-06.

---

# BACKEND

> **Pendência de revisão.** As seções 17 a 25 especificam arquitetura Django
> (`models.py`, `services.py`, `selectors.py`, Celery, Redis, isolamento de adapters).
> Esse conteúdo provavelmente já existe dentro de `backend-core`, `backend-async` e
> `backend-integrations`. Manter a mesma regra em dois lugares faz as duas divergirem
> na primeira edição. Conferir os `SKILL.md` dessas três skills e remover daqui o que
> estiver duplicado, deixando no P-05 apenas o que for coordenação entre elas.

## 17. Implementar por domínio

No Django, preservar a arquitetura definida.

Preferir:

```text
models.py
services.py
selectors.py
permissions.py
tasks.py
api/
tests/
```

conforme necessidade.

---

## 18. Models

Models devem concentrar:

```text
estrutura
integridade
constraints
relações
```

Não colocar fluxos complexos de negócio no model.

---

## 19. Services

Alterações de estado e casos de uso devem preferir:

```text
services.py
```

---

## 20. Selectors

Consultas relevantes devem preferir:

```text
selectors.py
```

---

## 21. Permissions

Autorização deve ser aplicada no backend.

Esconder botão no frontend não é autorização.

---

## 22. API

A implementação deve respeitar:

```text
docs/contratos-de-api.md
```

Não inventar contrato diferente porque é mais fácil programar.

---

## 23. Async

Tasks devem delegar regra de negócio aos services.

Princípio:

```text
CELERY EXECUTA
SERVICE DECIDE
POSTGRESQL GUARDA ESTADO
REDIS TRANSPORTA TRABALHO
```

---

## 24. Integrações

Integrações externas devem ficar isoladas em clients/adapters.

Não espalhar chamadas HTTP pelo domínio.

---

## 25. IA/MCP

IA não deve ser autoridade de:

```text
permissão
integridade
decisão determinística crítica
```

Tools devem chamar services/selectors autorizados.

---

# FRONTEND

## 26. Implementar conforme documentação

Frontend deve seguir:

```text
mapa-de-telas.md
mapa-de-fluxos.md
guia-visual.md
contratos-de-api.md
```

---

## 27. Não inventar comportamento

Se durante frontend surgir necessidade funcional não prevista:

```text
não criar silenciosamente
```

Avalie se exige:

```text
P-02
P-03
P-04
```

conforme o tipo de mudança.

---

## 28. Estados

Os estados de cada tela **não** são uma lista genérica: estão declarados tela a tela em
`mapa-de-telas.md`, junto com o comportamento esperado.

Implementar exatamente os que estiverem registrados:

```text
loading
success
error
empty
disabled
sem permissão
```

Para cada um:

```text
o QUE acontece  → mapa-de-telas.md  (P-03)
COMO aparece    → guia-visual.md    (P-04)
```

Se uma tela precisar de um estado que o mapa não registra, isso é lacuna do P-03.
Ver seção 32. Não inventar o estado no código.

---

## 29. Responsividade

Duas fontes, com papéis diferentes:

```text
mapa-de-telas.md  → como a tela se reorganiza
                    (sidebar vira drawer, tabela vira lista)

guia-visual.md    → tokens por faixa
                    (breakpoints, escala tipográfica, densidade, container)
```

Implementar a reorganização que o mapa descreve, usando os tokens que o guia define.

Não criar layout separado sem necessidade, e não inventar uma reorganização que o mapa
não prevê.

---

## 30. Acessibilidade

A acessibilidade está dividida entre dois documentos:

| Item | Fonte |
|---|---|
| contraste | `guia-visual.md` |
| aparência do anel de foco | `guia-visual.md` |
| tamanho mínimo de texto | `guia-visual.md` |
| área de toque mínima | `guia-visual.md` |
| comportamento sob `prefers-reduced-motion` | `guia-visual.md` |
| ordem de navegação por teclado | `mapa-de-telas.md` |
| retenção e retorno de foco em modal | `mapa-de-telas.md` |
| labels e texto alternativo | `mapa-de-telas.md` |
| semântica e papel dos elementos | `mapa-de-telas.md` |

`testing-quality` verifica a parte estrutural; a parte visual é conferida contra o guia.

---

## 31. Autorização no frontend

Frontend pode adaptar a interface conforme permissões.

Mas a autorização real permanece no backend.

---

# ALTERAÇÕES DURANTE A IMPLEMENTAÇÃO

## 32. Descoberta de lacuna

Se durante a implementação surgir lacuna:

```text
funcional
regra
dados
API
fluxo
tela
segurança
```

pare a parte afetada.

Não resolva por conveniência do código.

---

## 33. Mudança de requisito

Se a solução exigir mudar o comportamento da história aprovada:

```text
não alterar história silenciosamente
```

Fluxo:

```text
detectar mudança
↓
registrar no diário
↓
história volta para rascunho
↓
incrementar versão se aplicável
↓
P-02 revisa
↓
usuário aprova novamente
↓
P-03 atualiza documentos
↓
P-04 se necessário
↓
P-05 continua
```

---

## 34. Decisão técnica relevante

Se a história não muda, mas surge decisão técnica estrutural, o P-05 registra
`D-xxx` em `docs/mapa-de-decisoes.md`.

Procedimento obrigatório, igual ao do P-04:

```text
1. reler mapa-de-decisoes.md inteiro
2. identificar o maior D-xxx em uso
3. usar o próximo número
4. gravar imediatamente
5. nunca reservar faixa
```

O P-05 só pode **acrescentar** decisão técnica. Não pode editar, substituir nem
reclassificar decisão criada pelo P-03 ou pelo P-04.

Se depender de escolha humana:

```text
Status: proposta
↓
perguntar
↓
Status: ativa
```

O código é atribuído já na proposta, para não haver duas decisões disputando o mesmo
número enquanto uma aguarda resposta.

Se for aplicação direta de decisão já existente, não criar decisão duplicada.

Se a decisão for funcional, de produto ou visual, ela **não é do P-05**:

```text
funcional / produto → P-02 e P-03
visual              → P-04
```

---

## 35. Substituir decisão existente

O P-05 **não substitui decisão**.

Substituir uma decisão ativa significa editar o registro anterior para marcá-lo como
`substituída`, e isso é escrita sobre conteúdo de outra skill. Só o P-03
(`dah-documentacao`) faz isso.

Se a implementação revelar que uma decisão vigente não se sustenta:

```text
1. registrar no diário de bordo o que foi descoberto
2. criar D-yyy com Status: proposta, descrevendo a alternativa
3. NÃO marcar a D-xxx anterior como substituída
4. informar o usuário e parar a parte afetada
5. o P-03 consolida a substituição quando a decisão for tomada
```

Nunca apagar decisão anterior.

---

# TESTES E QUALIDADE

## 36. Testes automatizados

Após implementação, execute os testes apropriados definidos por `testing-quality`.

Prioridades:

```text
unitários
services
selectors
models
API
frontend
integração
E2E
regressão
```

---

## 37. Critérios de aceite

Cada critério de aceite deve possuir evidência suficiente.

A pergunta central é:

```text
COMO SABEMOS QUE ESTE CRITÉRIO FOI ATENDIDO?
```

---

## 38. Teste positivo e negativo

Cobrir quando relevante:

```text
deve funcionar
+
deve falhar
```

---

## 39. Bug encontrado

Fluxo:

```text
reproduzir
↓
criar/ajustar teste
↓
corrigir
↓
reexecutar
↓
registrar resultado
```

Bug relevante corrigido deve gerar teste de regressão.

---

## 40. Não ignorar teste falhando

Teste crítico falhando impede:

```text
pronta para homologação
```

---

## 41. Flaky test

Teste intermitente é defeito.

Não considerar história pronta enquanto um teste crítico continuar instável.

---

## 42. Lint e build

Executar verificações aplicáveis:

```text
lint
format check
type check
build
```

conforme a stack.

---

# SEGURANÇA

## 43. Executar `security` quando aplicável

Validar:

```text
auth
permissions
tenant isolation
input validation
secrets
dados sensíveis
API exposure
uploads
webhooks
IA/MCP
```

---

## 44. Falha crítica de segurança

Bloqueia a conclusão.

Exemplos:

```text
acesso indevido
tenant isolation quebrado
secret exposto
auth quebrada
dados sensíveis vazando
```

---

## 45. Risco aceito

Se um risco não crítico for conscientemente aceito:

```text
registrar decisão
+
registrar mitigação
+
registrar pendência quando aplicável
```

Não ignorar silenciosamente.

---

# USABILIDADE

## 46. Executar testes de usabilidade

Quando houver interface, validar os itens registrados no mapa de testes.

Exemplos:

```text
ação compreensível
mensagem útil
loading
erro
sucesso
navegação
responsividade
acessibilidade
```

---

## 47. Falha de usabilidade

Se impedir o usuário de completar corretamente o fluxo:

```text
bloqueante
```

Falhas menores podem ser tratadas conforme decisão registrada.

---

# MAPA DE TESTES

## 48. Atualizar resultados

Após cada teste, atualizar:

```text
docs/mapa-de-testes.md
```

Status permitidos conforme documento:

```text
planejado
pendente
em execução
aprovado
falhou
bloqueado
não aplicável
```

---

## 49. Evidência

Registrar evidência útil e curta.

Exemplo:

```text
pytest: test_duplicate_email → passou
E2E: fluxo de login → passou
Usabilidade: erro exibido junto ao campo → aprovado
Segurança: acesso de outro tenant → 403
```

Não transformar o mapa em log bruto.

---

## 50. Teste não aplicável

Se durante implementação ficar claro que um teste planejado não se aplica:

```text
não apagar
```

Marcar:

```text
não aplicável
```

e registrar motivo quando necessário.

---

# DOCUMENTAÇÃO APÓS IMPLEMENTAÇÃO

## 51. Conferir documentação consolidada

Após o código funcionar, compare:

```text
código
↔
história
↔
documentos DAH
```

O objetivo é garantir que a implementação não tenha desviado da especificação.

---

## 52. Ajuste documental sem mudança de requisito

Se o código revelou apenas detalhe técnico que precisa ser documentado e não altera comportamento aprovado:

```text
atualizar documento correspondente
```

quando fizer parte do escopo da DAH.

---

## 53. Mudança funcional exige retorno ao fluxo

Se houver mudança funcional:

```text
P-02 → aprovação → P-03 → P-04 se necessário → P-05
```

Não corrigir documentação retroativamente para justificar código diferente.

---

# DIÁRIO DE BORDO

## 54. Atualizar `diario-de-bordo.md`

O diário deve permitir que outro agente retome o projeto.

Ao longo da implementação, registrar eventos relevantes.

Ao finalizar a história, registrar pelo menos:

```text
história
resultado
principais alterações
testes
decisões
pendências
bloqueios
próximo passo
```

---

## 55. Modelo de registro

```markdown
## DD/MM/AAAA

### H-017 — Nome da história

Status: pronta para homologação

Implementado:
- backend ...
- frontend ...

Testes:
- funcionais aprovados
- segurança aprovada
- usabilidade aprovada

Decisões:
- D-023 — ...

Pendências:
- nenhuma

Próximo passo:
- P-06 — Homologar e Publicar (testing-quality, git-deploy)
```

---

## 56. Diário não é log técnico

Não registrar:

```text
cada arquivo alterado
cada comando
cada linha de código
```

Git e commits cumprem essa função.

---

# CRONOGRAMA

## 57. Atualizar cronograma durante o processo

Atualize:

```text
docs/cronograma.md
```

quando a história:

```text
entra em desenvolvimento
fica bloqueada
é desbloqueada
tem teste crítico falhando
tem teste crítico aprovado
muda de escopo
fica pronta para homologação
```

---

## 58. Unidade de produtividade

A métrica permanece:

```text
histórias prontas para homologação / dia
```

Calendário:

```text
dias corridos
```

---

## 59. Capacidade

Não alterar automaticamente:

```text
10/dia
5/dia
3/dia
ou valor configurado
```

Se o desempenho real divergir persistentemente:

```text
informar
↓
sugerir revisão
↓
aguardar decisão humana
```

---

# OPS DURANTE P-05

## 60. Alterações operacionais

Se a história exigir para funcionar em DEV:

```text
nova variável de ambiente
nova migration
novo worker
nova fila
novo bucket
novo serviço
```

acionar `devops` para preparar o necessário **em DEV**.

`devops` não prepara HOM nem PROD durante o P-05.

---

## 61. Não publicar produção

P-05 pode preparar execução em DEV, via `devops`.

Não deve promover para:

```text
HOM
PROD
```

Isso pertence ao P-06, que agrupa histórias prontas para homologação em uma release e
promove o artefato para HOM e depois para PROD, com gate humano em cada etapa.

---

## 62. Migration

Criar e testar migrations quando necessárias.

Validar:

```text
aplicação
dados existentes
reversibilidade/risco
```

conforme criticidade.

---

# GIT E RASTREABILIDADE

## 63. Branch

Branch, commit e rastreabilidade são executados por `git-deploy`.

Quando o projeto utilizar branch por história, preferir:

```text
feat/H-017-nome-da-historia
```

`git-deploy` no P-05 cuida apenas de versionamento local. Publicação é P-06.

---

## 64. Commits

Quando útil, referenciar:

```text
H-017
```

Isso melhora rastreabilidade.

---

## 65. Não misturar histórias

Evitar implementar comportamento de outra história não aprovada dentro da atual.

Se surgir necessidade:

```text
P-01 cria backlog
```

após decisão apropriada.

---

# DEFINITION OF DONE — PRONTA PARA HOMOLOGAÇÃO

## 66. Checklist final

Uma história só pode receber:

```text
pronta para homologação
```

quando todos os itens aplicáveis estiverem concluídos:

```text
[ ] história aprovada
[ ] documentação DAH coerente
[ ] backend implementado
[ ] frontend implementado
[ ] integrações implementadas
[ ] migrations criadas/testadas
[ ] mapa-de-testes.md atualizado
[ ] critérios de aceite validados
[ ] testes funcionais aprovados
[ ] testes de integração aprovados quando aplicáveis
[ ] E2E aprovado quando aplicável
[ ] testes de usabilidade aprovados quando aplicáveis
[ ] testes de segurança aprovados quando aplicáveis
[ ] lint/type/build aprovados quando aplicáveis
[ ] nenhuma falha crítica
[ ] nenhuma decisão crítica pendente
[ ] nenhuma pendência bloqueante
[ ] mapa-de-decisoes.md atualizado quando necessário
[ ] nenhuma decisão anterior editada por este prompt
[ ] nenhum documento do P-03 ou do P-04 alterado por este prompt
[ ] diario-de-bordo.md atualizado
[ ] cronograma.md atualizado
```

---

## 67. Alterar status final

Quando o checklist estiver completo:

```text
em desenvolvimento
↓
pronta para homologação
```

Atualize:

```text
arquivo da história
docs/historias/indice.md
docs/cronograma.md
docs/diario-de-bordo.md
```

---

## 68. Se não estiver pronta

Não forçar o status.

Apresente:

```text
o que está concluído
o que falta
o que está bloqueado
qual decisão é necessária
qual é a próxima ação
```

Mantenha:

```text
em desenvolvimento
```

---

# SAÍDA ESPERADA

## 69. História pronta

Exemplo:

```text
H-017 — Recuperar senha

Status:
pronta para homologação

Implementado:
- backend
- API
- frontend
- integração de e-mail

Testes:
- T-081 aprovado
- T-082 aprovado
- T-083 aprovado
- T-084 aprovado

Segurança:
- aprovada

Usabilidade:
- aprovada

Decisões:
- D-023 ativa

Pendências:
- nenhuma

Cronograma:
- atualizado

Próximo passo:
P-06 — Homologar e Publicar

A história aguarda entrar em uma release. O P-06 pode agrupá-la com outras
histórias prontas para homologação da mesma versão.
```

---

## 70. História bloqueada

Exemplo:

```text
H-017 permanece em desenvolvimento.

Concluído:
- model
- service
- API

Bloqueio:
- D-023 pendente: definir provider de storage

Testes bloqueados:
- T-084

Cronograma:
- atualizado

Próxima ação:
resolver D-023.
```

---

# FLUXO OPERACIONAL

## 71. Fluxo completo

```text
H-xxx APROVADA
      ↓
verificar P-03
      ↓
verificar P-04 se frontend
      ↓
Definition of Ready
      ↓
status → em desenvolvimento
      ↓
criar/atualizar mapa de testes
      ↓
selecionar skills
      ↓
┌───────────────┬────────────────────┐
▼               ▼                    ▼
BACKEND       FRONTEND           INTEGRAÇÕES
▼               ▼                    ▼
backend-core  expo-app           backend-integrations
backend-api   (web, iOS e        backend-ai-mcp
backend-async  Android)
└───────────────┴────────────────────┘
              ↓
       testing-quality
              ↓
       security
        quando aplicável
              ↓
        USABILIDADE
     (testing-quality)
              ↓
        algum teste falhou?
        ├── SIM
        │    ↓
        │  corrigir
        │    ↓
        │  retestar
        │
        └── NÃO
              ↓
      conferir documentação
              ↓
      atualizar decisões
              ↓
       atualizar diário
              ↓
      atualizar cronograma
              ↓
     Definition of Done
              ↓
status → pronta para homologação
              ↓
     P-06 (testing-quality + git-deploy)
```

---

# 72. Regra final

```text
P-05 NÃO É APENAS "PROGRAMAR".

ELE TRANSFORMA UMA HISTÓRIA APROVADA
EM UMA ENTREGA PRONTA PARA HOMOLOGAÇÃO.

ANTES DO CÓDIGO:
DEFINE COMO PROVAR QUE FUNCIONA.

DURANTE O CÓDIGO:
DELEGA ÀS SKILLS DE DOMÍNIO.
NÃO REESCREVE O QUE ELAS JÁ SABEM.

DEPOIS DO CÓDIGO:
TESTA,
CORRIGE,
DOCUMENTA,
REGISTRA DECISÕES,
ATUALIZA O DIÁRIO
E RECALCULA O CRONOGRAMA.

SÓ TERMINA QUANDO A HISTÓRIA
ESTIVER PRONTA PARA HOMOLOGAÇÃO.
```
