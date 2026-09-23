---
name: artifact-analysis
description: "ART-01 — Análise de artefatos gerados por IA (ChatGPT, Claude, Gemini, Copilot, Lovable, Bolt, v0 etc.) para extrair evidências, capacidades e dúvidas que alimentam o PA-01 (índice proposto) e o PA-02 (histórias provisórias A-xxx) do método DAH. Use SEMPRE que o usuário enviar ou apontar um ZIP, repositório, pasta, protótipo, screenshot ou código gerado por IA e pedir para analisar, entender, mapear, extrair histórias/funcionalidades, comparar com a DAH, rodar PA-01/PA-02, ou descobrir o que um projeto 'faz'. Vale para frontend, backend, dados, APIs, integrações e interface (React, Expo, Next, Vite, HTML, Django, FastAPI, Node, Firebase, Supabase). Não cria H-xxx nem implementa nada."
---

# ART-01 — artifact-analysis

Categoria: transversal (frontend, backend, dados, API, integrações, interface, configuração).
Dependências: `AGENTS.md`, DAH-01 e documentação DAH do projeto, quando existirem.

Esta skill define **como analisar** um artefato gerado por IA e entregar evidências confiáveis para PA-01 e PA-02. Não existe versão separada para frontend ou backend: é uma skill só.

## Regra principal

```text
ARTEFATO DE IA ≠ FONTE DE VERDADE
```

O artefato é matéria-prima, protótipo, referência ou implementação candidata. A fonte oficial continua sendo: histórias aprovadas (H-xxx), documentos DAH e decisões ativas. Se o artefato conflita com uma história aprovada, **a história prevalece** até decisão humana — nunca ajuste a DAH para o artefato parecer correto.

## Fluxo em que a skill se encaixa

```text
ARTEFATO → ART-01 → PA-01 (indice-proposto.md) → PA-02 (histórias A-xxx) → análise humana → DAH oficial
```

- **PA-01** usa a ART-01 para extrair o índice de capacidades.
- **PA-02** usa a ART-01 para aprofundar **uma A-xxx por vez** e escrever a história provisória.

## Faz / Não faz

**Faz:** inspecionar estrutura, identificar stack, mapear telas, rotas, ações, fluxos, entidades, APIs, integrações e permissões aparentes; detectar mocks, código demonstrativo, código morto, funcionalidades implícitas, duplicidades, conflitos, lacunas, dependências e secrets; separar comportamento de implementação e evidência de inferência; comparar com a DAH; produzir evidências com proveniência.

**Não faz:** criar H-xxx, aprovar histórias, alterar backlog ou regra oficial, implementar funcionalidade, homologar, publicar. Os códigos gerados aqui são sempre `A-xxx` (A = análise); a promoção para `H-xxx` pertence ao fluxo oficial da DAH.

## Procedimento

Siga nesta ordem. Em projetos grandes, trabalhe em camadas: **estrutura → módulos → capacidades → histórias específicas**.

1. **Identificar formato** — ZIP, diretório, repositório, arquivo solto, protótipo visual/screenshot, JSON/Markdown.
2. **Listar estrutura** — árvore de pastas (ignore `node_modules`, `.venv`, `dist`, `build`, lockfiles no conteúdo).
3. **Identificar stack** — leia primeiro: README, `package.json` / `pyproject.toml` / `requirements.txt`, arquivos de config, Dockerfile. Registre o inventário técnico (ver `references/checklists.md` §1).
4. **Localizar pontos de entrada** — `main`, `App`, `index`, `urls.py`, `app/` do Expo Router, `pages/`, `routes`.
5. **Telas e rotas** — navegação, páginas, deep links.
6. **Comportamentos** — ações do usuário, formulários, estados (loading/empty/error/success), modais, confirmações.
7. **Dados** — entidades, campos, relações, status, enums, constraints aparentes.
8. **APIs** — método, rota, entrada, saída, auth, autorização aparente, erros, uso no frontend.
9. **Integrações** — e-mail, SMS, WhatsApp, pagamento, storage, maps, OAuth, webhooks, APIs externas, LLM, MCP, analytics.
10. **Mocks e simulações** — classificar como `MOCK` ou `SIMULAÇÃO`; nunca virar requisito automaticamente.
11. **Permissões** — quem parece poder fazer o quê.
12. **Regras aparentes** — validações, limites, condições.
13. **Dúvidas** — tudo que não dá para saber pelo artefato.
14. **Comparar com a DAH** — quando houver projeto oficial.

Os checklists detalhados de cada etapa (frontend, backend, mocks, segurança, dependências, conversões de stack) estão em `references/checklists.md`. Consulte-o durante a análise.

## Stack oficial prevalece

A stack encontrada é **descrita, não adotada**. Stack oficial da empresa: Expo (web/iOS/Android) + Django (monólito modular) + PostgreSQL, projetos desacoplados. Se o artefato for, por exemplo, React + Firebase, extraia comportamento, fluxos, dados e interface — **não introduza Firebase silenciosamente**. As regras de conversão (React Web → Expo, backend externo → Django) estão em `references/checklists.md` §7.

## Evidência, inferência e dúvida

Toda afirmação da análise pertence a uma destas classes, e elas nunca se misturam:

- **Evidência** — algo observável: arquivo, rota, componente, endpoint, model, texto, botão, validação, teste.
- **Inferência** — conclusão necessária para interpretar. Ex.: evidência = botão "Bloquear usuário" → inferência = o sistema provavelmente suporta bloqueio.
- **Dúvida** — o que não dá para saber: quem pode executar? qual regra? qual limite? qual consequência?

**Nunca transforme inferência em fato.** Funcionalidade implícita (ex.: link "Esqueci minha senha" → "Recuperar senha") fica marcada `INFERIDA` até haver evidência suficiente.

Cuidados que evitam falsos requisitos:
- Um model sozinho não prova que existe CRUD correspondente.
- Uma biblioteca no `package.json` não prova requisito.
- Componentes (`UserCard`, `Header`, `AuthContext`, hooks) não são histórias.
- Código morto (arquivo não importado, componente não usado, rota inacessível, função nunca chamada) não é funcionalidade.
- Feature flags, TODOs, `future`, placeholders, "coming soon" são **indícios**, não requisitos.
- Protótipo visual/screenshot: marcar `PROTÓTIPO VISUAL` e não inferir backend inexistente.
- Se README, testes e código se contradizem: registrar `CONFLITO INTERNO`, sem escolher silenciosamente.

## De técnico para capacidade funcional

Converta elementos técnicos em comportamento observável. Ex.: `SignupForm.tsx` + `POST /users` → **Criar usuário**.

- Verbos preferidos: Criar, Visualizar, Editar, Excluir, Bloquear, Aprovar, Cancelar, Enviar, Consultar, Listar, Realizar, Recuperar.
- Evitar: Implementar, Programar, Criar componente, Criar endpoint, Criar model.
- Granularidade: cada capacidade deve ser **compreensível, implementável, testável e homologável**. Nada de "Gerenciar usuários" — quebre em Criar / Visualizar / Editar / Bloquear usuário.
- Duplicidades: unifique equivalentes (ex.: "Atualizar cliente" = "Editar cliente") e registre a equivalência.

## Proveniência

Sempre registre de onde veio cada evidência:

```text
A-006 — Recuperar senha
Evidências:
- clients/web/pages/ForgotPassword.tsx
- botão "Esqueci minha senha" em Login.tsx
- POST /api/password/reset
```

## Secrets e segurança

Procure API keys, tokens, senhas, private keys, connection strings e credenciais. **Nunca reproduza valores reais** — cite só arquivo e linha, ex.: `secret hardcoded em src/firebase.ts:4 (valor omitido)`. Sinalize riscos aparentes (auth/autorização ausente, IDOR, input não validado, upload inseguro, CORS amplo, SQL inseguro, execução arbitrária, exposição de dados). Quando relevante, encaminhe para **SEC-01**.

## Comparação com a DAH

Quando houver projeto oficial, compare com: `docs/historias/indice.md`, histórias, `regras-de-negocio.md`, `modelo-de-dados.md`, `contratos-de-api.md`, `mapa-de-fluxos.md`, `mapa-de-telas.md`, `guia-visual.md`, `mapa-de-decisoes.md`.

Classifique cada capacidade como:

| Classe | Significado |
|---|---|
| NOVA | não existe na DAH |
| EQUIVALENTE | já existe com o mesmo escopo |
| PARCIAL | existe, mas o artefato cobre só parte |
| MAIS AMPLA | o artefato vai além da história existente |
| CONFLITANTE | contradiz história/regra aprovada |
| TÉCNICA | item técnico, não é capacidade de negócio |
| VISUAL | questão de interface/guia visual |

Sem DAH disponível, diga isso explicitamente e classifique tudo como `NOVA` (correspondência: "sem DAH para comparar").

## Saídas

Os modelos completos estão em `references/formatos-saida.md`. Resumo:

- **Modo PA-01** (visão geral) — resumo do sistema + inventário de stack + lista de capacidades no formato: Título / Capítulo sugerido / Tipo / Evidência / Inferência / Correspondência DAH / Dúvidas. Mais seções de mocks, itens técnicos, itens visuais, riscos e dúvidas gerais. PA-01 transforma isso em `analise-artefato/indice-proposto.md`.
- **Modo PA-02** (uma A-xxx) — localize tudo relacionado à capacidade (arquivos, telas, rotas, dados, APIs, fluxos, regras, mocks, permissões, integrações) e entregue: Evidências / Comportamento / Fluxo / Dados / Regras aparentes / Permissões / Integrações / Mocks / Inferências / Dúvidas / Conflitos.

Se o usuário não disser o modo: artefato inteiro sem A-xxx específica → modo PA-01; pedido sobre uma capacidade/A-xxx → modo PA-02.

A saída mínima precisa responder: que sistema parece ser? qual stack? quais módulos, capacidades, telas, APIs, entidades? quais mocks, riscos, dúvidas? o que já existe na DAH, o que é novo, o que conflita?

## Encaminhamento

A ART-01 identifica e encaminha; não substitui outras skills.

| Situação | Destino |
|---|---|
| nova capacidade | P-01 |
| história precisa de especificação | P-02 (dah-historia) |
| documentação oficial | P-03 (dah-documentacao) |
| questão visual | P-04 / ux-ui |
| implementação aprovada | P-05 |
| backend | BE-01..05 |
| frontend web / Expo | frontend-web / expo-app |
| qualidade | QA-01 |
| segurança | SEC-01 |
| infraestrutura | OPS-01 |
| governança | DAH-01 |

## Simplicidade

O objetivo é **entender**, não reescrever. Evite overengineering, refatoração prematura, introdução de stack nova e duplicação.

## Definition of Done

- [ ] stack identificada
- [ ] estrutura principal compreendida
- [ ] comportamentos separados de detalhes técnicos
- [ ] mocks e simulações identificados
- [ ] evidências e inferências separadas
- [ ] capacidades duplicadas tratadas
- [ ] riscos e secrets aparentes sinalizados (sem valores)
- [ ] relação com a DAH identificada, quando aplicável
- [ ] dúvidas relevantes explícitas
- [ ] PA-01 ou PA-02 consegue continuar sem redescobrir o artefato inteiro

## Regra final

```text
ART-01 NÃO TRANSFORMA CÓDIGO EM REQUISITO AUTOMATICAMENTE.
ELA DESMONTA O ARTEFATO, ENCONTRA EVIDÊNCIAS, RECONSTRÓI COMPORTAMENTOS,
SEPARA FATO DE INFERÊNCIA E ENTREGA CONTEXTO PARA A DAH DECIDIR.
```
