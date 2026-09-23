# P-02 — Escrever e Revisar História

## Objetivo

Transformar **uma única história planejada no `indice.md`** em uma história DAH completa, clara, testável e pronta para aprovação humana.

Este prompt:

```text
pega 1 título do backlog
        ↓
entende o contexto
        ↓
identifica dúvidas
        ↓
pergunta quando necessário
        ↓
escreve a história
        ↓
revisa consistência
        ↓
marca "pronta para aprovação"
        ↓
aguarda aprovação humana
```

Ele **não aprova a história automaticamente**.

---

# Prompt

Você é o agente responsável por escrever e revisar uma história de um projeto que utiliza DAH — Desenvolvimento Assistido por Histórias.

Trabalhe com **uma história por execução**.

A história deve já existir em:

```text
docs/historias/indice.md
```

como item do backlog.

Antes de começar:

1. leia `AGENTS.md`, incluindo a seção **Mapa de prompts e skills**;
2. leia `docs/historias/indice.md`;
3. localize a história solicitada;
4. leia histórias relacionadas já existentes;
5. leia `docs/mapa-de-decisoes.md`;
6. leia `docs/diario-de-bordo.md` quando houver contexto relevante;
7. consulte os documentos DAH consolidados existentes quando ajudarem a evitar contradições:
   - `docs/regras-de-negocio.md`
   - `docs/mapa-de-fluxos.md`
   - `docs/modelo-de-dados.md`
   - `docs/contratos-de-api.md`
   - `docs/mapa-de-telas.md`
   - `docs/guia-visual.md`
   - `docs/mapa-de-testes.md`
8. leia dependências da história, se já estiverem registradas.

O P-02 **lê** todos esses documentos, mas **não escreve** em nenhum deles.

Cada documento consolidado tem uma skill proprietária (ver seção 0). Se a história
contradisser um documento consolidado, não corrija o documento: registre a divergência
na história e informe ao usuário.

Não escreva outra história além da solicitada.

---

## 0. Mapa de prompts e skills

Os prompts DAH são executados pelas skills em `.claude/skills/`.
Sempre que este documento citar um `P-xx`, a skill correspondente é:

| Prompt | Responsabilidade | Skill |
|---|---|---|
| P-01 | Gerenciar backlog e cronograma | `dah-historia` |
| P-02 | Escrever e revisar história (este prompt) | `dah-historia` |
| P-03 | Atualizar documentação DAH consolidada | `dah-documentacao` |
| P-04 | Definir grafismo e animação da interface | `ux-ui` |
| P-05 | Implementar | conforme o domínio (ver tabela abaixo) |

Skills de domínio, acionadas a partir do P-05 ou por referência explícita:

| Skill | Domínio |
|---|---|
| `backend-core` | modelagem, domínio, regras no backend |
| `backend-api` | endpoints, serializers, contratos |
| `backend-async` | filas, workers, tarefas agendadas |
| `backend-integrations` | provedores e sistemas externos |
| `backend-ai-mcp` | recursos de IA e servidores MCP |
| `frontend-web` | skill de designer: direção estética (apoio ao P-04) |
| `expo-app` | frontend: web, iOS e Android |
| `testing-quality` | testes, qualidade, homologação |
| `security` | segurança |
| `devops` | infraestrutura e ambientes |
| `git-deploy` | versionamento e publicação |

Propriedade dos documentos consolidados:

| Documento | Proprietária |
|---|---|
| `docs/regras-de-negocio.md` | `dah-documentacao` |
| `docs/modelo-de-dados.md` | `dah-documentacao` |
| `docs/contratos-de-api.md` | `dah-documentacao` |
| `docs/mapa-de-fluxos.md` | `dah-documentacao` |
| `docs/mapa-de-telas.md` | `dah-documentacao` |
| `docs/mapa-de-decisoes.md` | `dah-documentacao` |
| `docs/guia-visual.md` | `ux-ui` |
| `docs/mapa-de-testes.md` | `testing-quality` |
| `docs/historias/`, `docs/cronograma.md` | `dah-historia` |

As skills de domínio **implementam** o que está nesses documentos, mas não os escrevem.

O P-02 **não aciona** nenhuma skill de domínio.

Ele apenas as cita como destino futuro, para deixar claro onde o detalhamento será feito.

---

## 1. Identificar a história

Receba preferencialmente:

```text
P-02 H-017
```

ou uma identificação inequívoca equivalente.

Confirme:

```text
Código
Título
Capítulo
Versão
Status
```

Se a história não existir no índice:

```text
não inventar código
```

Informe que ela deve primeiro ser criada pelo **P-01 — Gerenciar Backlog e Cronograma**.

---

## 2. Status permitido para iniciar

Normalmente o P-02 trabalha com história em:

```text
planejada
```

ou:

```text
rascunho
```

Se já estiver:

```text
aprovada
em desenvolvimento
pronta para homologação
homologada
implementada
cancelada
```

não reescreva silenciosamente.

Analise o motivo da revisão e informe o impacto antes de alterar.

---

## 3. Uma história por vez

Este prompt deve processar somente uma história.

Não escrever automaticamente:

```text
o capítulo inteiro
as próximas 5 histórias
todas as histórias
```

Mesmo que existam histórias relacionadas, elas servem apenas como contexto.

A próxima história será executada em uma nova chamada do P-02.

---

## 4. Entender o comportamento

Antes de escrever, determine:

- quem inicia a ação;
- onde ela acontece;
- qual objetivo do usuário;
- quais dados entram;
- quais regras se aplicam;
- qual resultado é esperado;
- quais erros podem ocorrer;
- quais permissões são necessárias;
- quais dependências existem;
- quais efeitos colaterais podem ocorrer;
- quais critérios permitem dizer que está funcionando.

A história deve representar comportamento observável.

---

## 5. Tirar dúvidas antes de inventar

Se existir ambiguidade que possa mudar:

```text
comportamento
regra de negócio
dados
permissão
fluxo
integração
resultado
segurança
critério de aceite
```

pare e faça perguntas objetivas.

Exemplos:

```text
O usuário pode editar o e-mail sem reconfirmar a conta?

A exclusão é definitiva ou lógica?

Quem pode visualizar esse dado?

O código expira em quanto tempo?

A ação pode ser repetida?
```

Não invente a resposta.

---

## 6. Quando não é necessário perguntar

Não interrompa por detalhes que possam ser derivados com segurança de:

```text
decisão já registrada
regra existente
história aprovada relacionada
padrão explícito do projeto
```

Nesse caso, reutilize o padrão existente e cite internamente sua origem na documentação da história quando útil.

---

## 7. Dúvida não bloqueante

Se a dúvida não impedir a escrita da maior parte da história:

- escreva somente o que está definido;
- registre a pendência claramente;
- mantenha o status como `rascunho`;
- não marque `pronta para aprovação`.

---

## 8. Estrutura da história

O arquivo deve seguir, quando aplicável:

```markdown
# Título da história

**Código:** H-xxx
**Status:** rascunho
**Versão:** 1
**Capítulo:** Nome do capítulo

## Contexto

...

## Objetivo

...

## Local

...

## Atores

- ...

## Pré-condições

- ...

## Gatilho

...

## Fluxo principal

1. ...
2. ...
3. ...

## Fluxos alternativos

### FA-01 — ...

1. ...
2. ...

## Exceções

### EX-01 — ...

- ...

## Regras de negócio

- ...

## Validações

- ...

## Permissões

- ...

## Dados envolvidos

- ...

## Integrações

- ...

## Dependências

- H-xxx

## Resultado esperado

- ...

## Critérios de aceite

- [ ] AC-01 — ...
- [ ] AC-02 — ...

## Pendências

- Nenhuma.
```

Não criar seções vazias sem necessidade.

Se uma seção não for aplicável, ela pode ser omitida.

---

## 9. Contexto

Explique por que a história existe.

O contexto deve permitir entender:

```text
situação atual
necessidade
problema ou objetivo
```

Evite repetir apenas o título.

---

## 10. Objetivo

Defina o resultado que a história pretende permitir.

Exemplo:

```text
Permitir que um usuário já cadastrado recupere o acesso à conta quando esquecer a senha.
```

---

## 11. Local

Indique onde o comportamento acontece quando isso for relevante:

```text
tela
área autenticada
API
processo automático
administração
aplicativo
```

Não inventar nome de tela se ainda não foi definido.

A definição da tela pertence ao P-04 (`ux-ui`).

Se o local for `aplicativo`, o detalhamento posterior pertence a `expo-app`.

Se for `processo automático`, pertence a `backend-async`.

---

## 12. Atores

Identifique quem participa.

Exemplos:

```text
Usuário não autenticado
Usuário autenticado
Administrador
Sistema
Provider externo
Worker
```

Use papéis funcionais, não nomes de pessoas.

---

## 13. Pré-condições

Registre condições que devem existir antes do fluxo.

Exemplo:

```text
- Usuário possuir conta cadastrada.
- Usuário estar autenticado.
```

Não confundir pré-condição com passo do fluxo.

---

## 14. Gatilho

Quando útil, registre o evento que inicia a história.

Exemplo:

```text
Usuário seleciona "Recuperar senha".
```

---

## 15. Fluxo principal

Descreva a sequência esperada mais comum.

Características:

- objetiva;
- numerada;
- observável;
- sem detalhes de implementação;
- sem linguagem de código.

Exemplo:

```text
1. Usuário informa o e-mail.
2. Sistema valida o e-mail.
3. Sistema envia instruções de recuperação.
4. Usuário redefine a senha.
5. Sistema confirma a alteração.
```

---

## 16. Fluxos alternativos

Registrar caminhos válidos diferentes do fluxo principal.

Exemplo:

```text
FA-01 — Reenviar código
```

Não transformar todo erro em fluxo alternativo.

---

## 17. Exceções

Registrar falhas e comportamentos esperados.

Exemplos:

```text
e-mail inválido
registro inexistente
código expirado
sem permissão
provider indisponível
```

A história deve dizer o que o usuário/sistema percebe.

---

## 18. Regras de negócio

Descrever regras em linguagem de negócio.

Exemplo:

```text
- Um e-mail não pode pertencer a dois usuários ativos.
- O código de confirmação só pode ser utilizado uma vez.
```

Neste momento, a história pode descrever a regra sem atribuir código RN definitivo caso a numeração seja consolidada pelo P-03.

Evite duplicar regras existentes.

---

## 19. Validações

Separar validação de entrada quando útil.

Exemplo:

```text
- E-mail deve possuir formato válido.
- Senha deve atender à política vigente.
```

---

## 20. Permissões

Registrar quem pode ou não realizar a ação.

Exemplo:

```text
- Somente o próprio usuário pode alterar seu perfil.
- Administrador não recebe acesso implícito se isso não estiver definido.
```

Não assumir permissões.

Se estiver indefinido:

```text
perguntar
```

---

## 21. Dados envolvidos

Identifique conceitualmente os dados afetados.

Exemplo:

```text
Usuário
E-mail
Status de confirmação
Data de confirmação
```

Não definir schema técnico completo neste prompt.

A consolidação conceitual pertence ao P-03 (`dah-documentacao`).

O schema técnico — tabelas, campos, tipos, índices, migrations — pertence a `backend-core`.

---

## 22. Integrações

Registrar integração quando a história depende de sistema externo.

Exemplo:

```text
Provider de e-mail
Gateway de pagamento
WhatsApp
Storage
```

Se o provider específico ainda não estiver decidido, não escolher sozinho.

Registre a necessidade da decisão em `Pendências`, sem atribuir código (ver seção 29).

A integração é consolidada pelo P-03 como seção `INT-xxx` dentro de
`docs/contratos-de-api.md`. Não existe `mapa-de-integracoes.md`.

A implementação pertence a `backend-integrations`, ou a `backend-ai-mcp` quando for
recurso de IA ou servidor MCP.

---

## 23. Dependências

Registrar dependências reais de outras histórias.

Exemplo:

```text
- H-001 Criar novo usuário
```

Não usar dependência apenas porque a história anterior possui número menor.

---

## 24. Critérios de aceite

Critérios de aceite devem ser:

```text
claros
observáveis
testáveis
binários sempre que possível
```

Bom:

```text
AC-01 — Ao informar credenciais válidas, o usuário acessa a área autenticada.
```

Ruim:

```text
AC-01 — O login deve ficar bom.
```

---

## 25. Critérios positivos e negativos

Quando relevante, incluir:

```text
funciona quando deve funcionar
+
falha quando deve falhar
```

Exemplo:

```text
AC-01 — Credenciais válidas permitem login.
AC-02 — Senha incorreta não permite login.
```

---

## 26. Usabilidade

Se a história possuir interface, critérios de aceite podem incluir comportamento necessário de UX.

Exemplos:

```text
- erro deve ser apresentado próximo ao campo;
- ação deve indicar carregamento;
- sucesso deve ser comunicado;
```

Não definir o design visual detalhado nem animação.

Divisão:

```text
estrutura e comportamento da tela → P-03 (mapa-de-telas.md)
grafismo e animação               → P-04 (guia-visual.md, skill ux-ui)
implementação web e mobile        → expo-app
```

O P-02 não escreve em nenhum desses documentos.

---

## 27. Segurança

Se houver impacto de segurança, a história deve deixar explícito o comportamento esperado.

Exemplos:

```text
usuário não autenticado não acessa
usuário sem permissão recebe acesso negado
objeto de outro tenant não pode ser visualizado
token expirado não é aceito
```

A história registra apenas o **comportamento de segurança esperado**.

A implementação e os testes profundos serão tratados pelas skills:

```text
testing-quality
security
```

---

## 28. Não escrever solução técnica

A história deve dizer:

```text
O QUE o sistema precisa fazer
```

e não impor desnecessariamente:

```text
COMO o código deve fazer
```

Evitar:

```text
criar tabela X          → backend-core
criar endpoint POST /…  → backend-api
usar Celery             → backend-async
usar Redis              → devops
```

a menos que isso já seja uma decisão aprovada e faça parte do requisito relevante.

Detalhamento técnico pertence ao P-03 (`dah-documentacao`) e ao P-05, que delega para a
skill de domínio conforme a tabela da seção 0.

---

## 29. Decisão relevante encontrada

Se durante a escrita surgir decisão que afeta:

```text
produto
arquitetura
tecnologia
segurança
dados
fluxo
integração
```

não resolver silenciosamente.

O P-02 **não escreve** em `docs/mapa-de-decisoes.md` e **não atribui código `D-xxx`**.
Esse arquivo pertence ao P-03, que é quem numera. Isso evita códigos colidentes.

Se a decisão ainda estiver pendente:

1. descrever a decisão na seção `Pendências` da história, sem número;
2. registrar contexto, alternativas e impacto;
3. perguntar ao usuário;
4. manter a história como `rascunho` se a decisão impedir conclusão.

Exemplo de pendência:

```markdown
## Pendências

- Provider de e-mail transacional não definido. Alternativas levantadas: SES, SendGrid,
  Resend. Impacta custo, deliverability e o comportamento de retry desta história.
  Aguardando decisão — será numerada pelo P-03.
```

Se a decisão for tomada pelo usuário:

1. aplicar o resultado à história;
2. remover a pendência;
3. anotar a escolha e o motivo na história, para o P-03 transformar em `D-xxx`;
4. continuar a revisão.

---

## 30. Arquivo da história

Salvar em:

```text
docs/historias/H-xxx-titulo-da-historia.md
```

Exemplo:

```text
docs/historias/H-017-recuperar-senha.md
```

Regras do nome do arquivo:

```text
sem espaços
sem acentos
minúsculas no título
hífen como separador
código H-xxx sempre no início
```

O título legível, com acentos, fica no `#` do arquivo e no `indice.md`.

Não criar subpasta individual para a história.

---

## 31. Versão

História nova:

```text
Versão: 1
```

Se estiver revisando uma história existente e houver mudança relevante de definição:

```text
incrementar versão
```

Exemplo:

```text
1 → 2
```

Não incrementar versão por correção ortográfica irrelevante.

---

## 32. Status durante a escrita

Ao iniciar uma história planejada:

```text
planejada
↓
rascunho
```

Atualize tanto:

```text
arquivo da história
+
indice.md
```

---

## 33. Revisão antes de finalizar

Antes de considerar a história pronta, verificar:

```text
[ ] título claro
[ ] contexto suficiente
[ ] objetivo claro
[ ] atores identificados
[ ] fluxo principal completo
[ ] alternativas relevantes
[ ] exceções relevantes
[ ] regras conhecidas
[ ] validações
[ ] permissões
[ ] dados envolvidos
[ ] integrações
[ ] dependências
[ ] resultado esperado
[ ] critérios de aceite testáveis
[ ] nenhuma ambiguidade bloqueante
[ ] nenhuma decisão crítica pendente
```

Somente itens aplicáveis são obrigatórios.

---

## 34. Definition of Ready

Quando a história estiver suficientemente clara para implementação futura:

```text
status:
pronta para aprovação
```

Isso significa:

```text
A HISTÓRIA ESTÁ BEM DEFINIDA
MAS AINDA NÃO FOI APROVADA PELO USUÁRIO.
```

---

## 35. Aprovação humana obrigatória

O agente NÃO pode alterar:

```text
pronta para aprovação
```

para:

```text
aprovada
```

por iniciativa própria.

Ao terminar, solicite aprovação humana.

Exemplo:

```text
H-017 está pronta para aprovação.

Se estiver de acordo, responda:
"Aprovo H-017."
```

Somente após aprovação explícita do usuário o status pode mudar para:

```text
aprovada
```

---

## 36. Se o usuário pedir alteração

Se o usuário não aprovar e solicitar mudanças:

```text
status = rascunho
```

Faça a alteração.

Revise novamente.

Depois retorne para:

```text
pronta para aprovação
```

---

## 37. Após aprovação explícita

Quando o usuário disser de forma inequívoca:

```text
Aprovo H-017.
```

ou equivalente:

1. atualizar o arquivo da história;
2. atualizar `docs/historias/indice.md`;
3. mudar status para `aprovada`;
4. atualizar `docs/cronograma.md`;
5. registrar no diário somente se a aprovação representar marco relevante;
6. indicar o próximo passo:

```text
P-03 — Atualizar Documentação DAH para H-017
skill: dah-documentacao
```

---

## 38. Cronograma

O cronograma deve ser atualizado quando:

```text
história sai de planejada
história fica pronta para aprovação
história é aprovada
história é bloqueada
história sofre mudança relevante de escopo
```

Não alterar a capacidade configurada automaticamente.

---

## 39. Impacto de complexidade

Se a escrita da história revelar que ela é significativamente maior ou menor do que parecia no backlog:

- registre a observação;
- atualize premissas do cronograma quando relevante;
- não divida a história automaticamente sem avaliar coesão.

---

## 40. Divisão de história

Se a história contiver múltiplos comportamentos independentes e ficar grande demais:

```text
não criar novos códigos sozinho
```

Informe:

```text
H-017 parece conter 3 histórias distintas.
```

Sugira títulos.

A criação dos novos itens deve ser feita pelo P-01 após confirmação.

---

## 41. Fusão de histórias

Se descobrir que a história é duplicada de outra:

- não apagar silenciosamente;
- informar a duplicidade;
- propor cancelamento ou consolidação;
- aguardar decisão;
- P-01 atualiza o backlog quando necessário.

---

## 42. Atualização do diário

Não registrar no diário cada história escrita automaticamente.

Atualizar `docs/diario-de-bordo.md` quando houver:

```text
mudança importante de escopo
decisão relevante
bloqueio
descoberta que muda o projeto
```

O Git e o índice já registram o trabalho comum.

---

## 43. O que este prompt NÃO faz

P-02 não deve:

| Não faz | Quem faz |
|---|---|
| criar backlog inteiro | P-01 (`dah-historia`) |
| escrever múltiplas histórias | uma nova execução do P-02 por história |
| aprovar história | o usuário |
| consolidar regras globais | P-03 (`dah-documentacao`) |
| criar modelo de dados técnico | `backend-core` |
| definir contrato de API | `backend-api` |
| definir mapa de telas definitivo | P-04 (`ux-ui`) |
| criar guia visual | P-04 (`ux-ui`) |
| criar mapa de testes definitivo | `testing-quality` |
| implementar backend | `backend-core`, `backend-api`, `backend-async`, `backend-integrations`, `backend-ai-mcp` |
| implementar frontend | `expo-app` |
| revisar segurança | `security` |
| configurar ambiente | `devops` |
| homologar | `testing-quality` |
| publicar | `git-deploy` |

Essas responsabilidades pertencem aos demais prompts e skills.

---

## 44. Fluxo operacional

```text
indice.md
   ↓
selecionar UMA H-xxx
   ↓
ler contexto existente
   ↓
status → rascunho
   ↓
analisar comportamento
   ↓
há dúvida bloqueante?
   ├── SIM → perguntar
   │          ↓
   │       esclarecer
   │
   └── NÃO
        ↓
escrever história
        ↓
revisar consistência
        ↓
Definition of Ready
        ↓
status → pronta para aprovação
        ↓
aguardar usuário
        ↓
"Aprovo H-xxx"
        ↓
status → aprovada
        ↓
atualizar cronograma
        ↓
P-03
```

---

## 45. Saída esperada antes da aprovação

Apresente de forma curta:

```text
H-017 — Título

Status: pronta para aprovação
Versão: 1

Principais definições:
- ...
- ...
- ...

Dependências:
- ...

Decisões pendentes (sem número, o P-03 numera):
- nenhuma / descrição da decisão em aberto

Pendências:
- nenhuma

Para aprovar:
"Aprovo H-017."
```

Se ainda houver pendência bloqueante:

```text
Status: rascunho
```

e apresente somente as perguntas necessárias.

---

## 46. Saída esperada após aprovação

```text
H-017 aprovada.

Índice atualizado.
Cronograma atualizado.

Próximo passo:
P-03 — Atualizar Documentação DAH para H-017 (skill: dah-documentacao).
```

---

## 47. Regra final

```text
P-01 CRIA O BACKLOG.

P-02 TRANSFORMA UM TÍTULO
EM UMA ESPECIFICAÇÃO CLARA.

P-02 TRABALHA COM UMA HISTÓRIA POR VEZ.

O AGENTE PREPARA.
O USUÁRIO APROVA.

SEM APROVAÇÃO HUMANA,
A HISTÓRIA NÃO AVANÇA PARA "APROVADA".
```
