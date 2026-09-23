---
name: testing-quality
description: Padrão transversal de qualidade e testes (QA-01) para backend e frontend — deriva testes dos critérios de aceite, mantém o docs/mapa-de-testes.md, cobre unitário, integração, API, componente, contrato, permissão, regressão e E2E, e emite parecer APROVADO ou NÃO APROVADO com evidência. Use sempre que a conversa envolver testes, cobertura, critérios de aceite, como testar algo, QA, mapa de testes, definição de pronto, revisão de qualidade, pipeline/CI, teste falhando, flaky, regressão, ou antes de marcar qualquer história como concluída — inclusive quando a pessoa não disser a palavra teste explicitamente, por exemplo ao dizer que terminou a H-023, perguntar se algo está pronto, pedir revisão de uma feature ou reclamar que algo quebrou de novo.
---

# QA-01 — testing-quality

Skill **transversal**: não pertence ao backend nem ao frontend. Toda história atravessa esta skill antes de ser considerada concluída.

## Princípio central

```text
HISTÓRIA → CRITÉRIOS DE ACEITE → MAPA DE TESTES → EXECUÇÃO → EVIDÊNCIA → CONCLUSÃO
```

Uma história não está concluída porque o código existe. Está concluída quando existe evidência objetiva de que o comportamento especificado acontece.

Duas regras governam todas as decisões abaixo:

```text
SEM EVIDÊNCIA, NÃO HÁ QUALIDADE COMPROVADA
TESTAR COMPORTAMENTO ANTES DE TESTAR IMPLEMENTAÇÃO
```

## Fontes de verdade

Antes de escrever qualquer teste, leia o que existir em `docs/`:

| Arquivo | Usa para |
|---|---|
| `docs/historias/` | história, critérios de aceite, escopo |
| `docs/regras-de-negocio.md` | regras a validar em service/unitário |
| `docs/mapa-de-fluxos.md` | fluxos críticos → candidatos a E2E |
| `docs/modelo-de-dados.md` | constraints, relações, casos de borda |
| `docs/contratos-de-api.md` | testes de API e de contrato |
| `docs/mapa-de-telas.md` | estados e navegação de frontend |
| `docs/guia-visual.md` | consistência visual e usabilidade |
| `docs/mapa-de-testes.md` | documento oficial de QA (criar se não existir) |

Se a história não tiver critérios de aceite testáveis, isso é um bloqueio de QA — diga isso antes de escrever testes, não depois.

## Fluxo operacional

Execute nesta ordem. Não pule para "escrever testes" sem os passos 1–3.

**1. Enquadrar.** Identifique história (`H-xxx`) e cada critério de aceite (`AC-xx`). Cada AC precisa virar pelo menos um cenário observável:

```text
AC-01: não permitir e-mail duplicado
→ dado um e-mail já existente
  quando tentar criar novo usuário
  então a operação deve falhar
```

**2. Classificar o impacto.** Decida quais trilhas a mudança toca e carregue só as referências necessárias:

| A mudança toca… | Leia |
|---|---|
| models, services, selectors, API, permissões, tasks, integrações, IA, migrations | `references/backend.md` |
| componentes, formulários, navegação, estados de tela, acessibilidade, mobile | `references/frontend.md` |
| as duas pontas, contratos, filas, E2E, smoke, regressão, dados de teste, mocks | `references/transversal.md` |
| registro, rastreabilidade, evidência, template do mapa | `references/mapa-de-testes.md` |
| lint, cobertura, CI, quality gates, flaky | `references/pipeline-qualidade.md` |
| fechar a história, relatório, DoR/DoD | `references/checklists.md` |

A maioria das histórias reais toca backend **e** frontend. Nesse caso leia as três primeiras.

**3. Derivar cenários.** Para cada AC e cada regra crítica, liste o caso positivo, o negativo e as bordas relevantes. Só depois escolha o nível na pirâmide:

```text
       E2E  — poucos, só fluxos críticos
 Integração — moderados
  Unitários — muitos, rápidos, determinísticos
```

Se o mesmo comportamento pode ser provado num teste menor, prove no menor.

**4. Registrar no mapa.** Atualize `docs/mapa-de-testes.md` — documento único e consolidado do sistema, nunca um arquivo por história. Cada linha: `T-xxx | H-xxx | tipo | cenário | resultado esperado | status`. Formato completo e template em `references/mapa-de-testes.md`.

**5. Implementar e executar.** Escreva os testes, rode-os, e rode também lint/build quando o projeto tiver. Teste que não roda não é evidência.

**6. Emitir parecer.** Resultado é binário, com razões objetivas:

```text
H-023

Critérios:
- AC-01 OK
- AC-02 OK
- AC-03 FALHA

Testes:
- 18 passaram
- 1 falhou

Bloqueio:
- AC-03: permissão de leitura entre tenants não é negada

Status QA: NÃO APROVADO
```

Nunca invente score do tipo `qualidade = 8/10`. Critério é atendido ou não atendido.

**7. Entregar à governança.** QA-01 não muda status de história sozinha. Ela produz evidência; a DAH-01 decide se a história vira "implementada".

## Regras que valem nas duas pontas

Estas se aplicam a qualquer teste, em qualquer camada — por isso ficam aqui e não nas referências.

**Teste positivo e negativo.** Para cada regra relevante, prove quando funciona *e* quando falha. Erro é comportamento esperado: registro inexistente, permissão negada, payload inválido, provider fora do ar. Só caminho feliz não valida regra.

**Casos de borda.** Avalie zero, vazio, null, limite mínimo e máximo, duplicado, data limite, timezone e concorrência quando a regra os tornar possíveis.

**Determinismo.** Mesmo resultado sempre. Não dependa de hora atual, rede real, ordem aleatória, dados externos ou serviços reais sem controle. Congele o tempo quando o comportamento envolver expiração, prazo, agendamento ou timezone. Não dependa de IDs fixos (`id = 1`) que o teste não garante.

**Qualidade do assert.** O assert precisa provar a regra:

```python
assert order.status == Order.Status.APPROVED   # bom
assert result is not None                      # não prova nada
```

**Estrutura e nome.** Use Arrange/Act/Assert (ou Given/When/Then). O nome descreve comportamento: `test_user_cannot_access_other_company_invoice`, não `test_invoice_7`. Teste é documentação executável — outro dev precisa entender a regra lendo o teste.

**Mock só na fronteira.** Mocke provedor de e-mail, pagamento, LLM, CRM, WhatsApp. Se o teste mocka service + repository + model + validator + permission ao mesmo tempo, ele não testa nada real.

**Isolamento.** Nenhum teste depende da execução de outro. Cada um prepara o estado de que precisa. Dados mínimos; nada de fixture gigante sem relação com o caso.

**Regressão.** Todo bug relevante gera teste:

```text
BUG → TESTE QUE REPRODUZ → CORREÇÃO → TESTE PASSA
```

**Rastreabilidade.** A relação `H-xxx → AC-xx → teste` precisa ser identificável, seja pelo nome, por marcador/tag ou pelo mapa de testes. Não é obrigatório codificar a história em todo nome.

**Prioridade quando o tempo é curto:** dinheiro, permissão, dados, login, fluxo principal, integrações críticas. Nessa ordem.

## Fronteira entre as pontas

Teste de frontend que confirma botão escondido **não** é teste de autorização. A permissão verdadeira se prova no backend, com usuário autorizado, autenticado sem permissão, não autenticado e acesso a objeto de outro dono/tenant. O frontend prova que a interface reage corretamente à resposta do backend — são coisas diferentes e ambas precisam existir.

Quando frontend e backend deployam separado, o contrato entre eles vira teste próprio (`references/transversal.md`).

## Fronteira com outras skills

| Assunto | Dono |
|---|---|
| Status final da história, conclusão | DAH-01 (governança) |
| Controles de segurança profundos, pentest | SEC-01 |
| Pipeline, ambientes, deploy, backup/restore | OPS-01 |
| O *que* precisa rodar e passar | QA-01 (esta skill) |

QA-01 valida segurança **funcional**: 401, 403, isolamento de tenant, objeto de outro usuário.

## Anti-padrões que bloqueiam aprovação

- Marcar história como concluída com teste crítico falhando.
- `skip` sem motivo registrado.
- Teste flaky normalizado ("às vezes falha") — teste intermitente é defeito; se for isolado em quarentena, precisa existir pendência clara.
- Perseguir número de cobertura com testes sem assert relevante.
- Snapshot atualizado sem revisar a mudança.
- Dados reais sensíveis em fixtures.
- Suíte destrutiva rodando em produção.

## Resultado esperado

Ao terminar, a skill precisa conseguir responder, com evidência:

```text
o que foi testado?
qual critério de aceite cada teste valida?
o backend está correto?
o frontend está correto?
o fluxo completo funciona?
as permissões funcionam?
há regressão?
há teste crítico falhando?
existe evidência suficiente para concluir a história?
```

## Referências

- `references/backend.md` — models, services, selectors, API, permissões, tasks, integrações, IA, banco e migrations.
- `references/frontend.md` — componentes, formulários, navegação, estados, usabilidade, acessibilidade, responsividade, mobile.
- `references/transversal.md` — integração, contrato, E2E, smoke, assíncrono, idempotência, concorrência, performance, dados de teste.
- `references/mapa-de-testes.md` — formato do documento oficial, rastreabilidade, evidência.
- `references/pipeline-qualidade.md` — lint, type check, CI, cobertura, quality gates, flaky.
- `references/checklists.md` — checklists por trilha, DoR, DoD e formato do relatório de QA.
- `assets/mapa-de-testes-template.md` — template para criar o mapa do zero.

```text
QUALIDADE NÃO É UMA ETAPA NO FINAL.
QUALIDADE ACOMPANHA A HISTÓRIA DO CRITÉRIO DE ACEITE ATÉ A ENTREGA.
```
