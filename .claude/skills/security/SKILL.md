---
name: security
description: Padrão de segurança transversal (SEC-01) aplicado em conjunto no backend e no frontend — autenticação, autorização, permissão por objeto, isolamento de tenant, validação de entrada, XSS/CSRF/CORS/CSP, SQL injection, SSRF, path traversal, mass assignment, upload e download de arquivos, secrets, dados pessoais, logs seguros, rate limit, webhooks, OAuth, IA/RAG/MCP, Docker, CI/CD e dependências. Use esta skill sempre que a tarefa envolver login, senha, sessão, token, JWT, cookie, permissão, perfil, admin, multi-tenant, dados pessoais ou financeiros, pagamento, upload, webhook, API pública, integração externa, agente com tools, variável de ambiente, deploy ou revisão de código — mesmo que a pessoa não use a palavra "segurança". Use também para revisar uma história/PR sob ótica de risco, montar cenários de teste de segurança em docs/mapa-de-testes.md ou decidir se algo pode ir para produção.
---

# SEC-01 — Segurança transversal

Segurança não é uma etapa no fim nem uma responsabilidade só do backend. Ela atravessa história → backend → frontend → dados → integrações → IA → infra → operação.

Esta skill serve para duas coisas: **construir** com os controles certos desde o desenho e **revisar** o que já existe antes de ir para produção.

## Regra de ouro

Não confiar em entrada, usuário, cliente, rede, integração ou modelo sem validação e controle.

Zero trust interno: nada é seguro só por estar na mesma aplicação, na mesma rede, no mesmo tenant, no frontend próprio ou em serviço interno. Sempre validar **identidade, permissão, escopo e integridade**.

## Fluxo

```text
HISTÓRIA → TRIAGEM DE RISCO → CONTROLES → IMPLEMENTAÇÃO (back + front) → TESTES → GATE
```

### 1. Triagem de risco

Antes de escrever código, responda: o que esta mudança introduz?

```text
[ ] novo dado sensível ou pessoal?
[ ] nova permissão ou perfil?
[ ] nova rota / endpoint?
[ ] nova integração externa ou webhook?
[ ] novo upload ou download de arquivo?
[ ] nova ação destrutiva ou em massa?
[ ] novo segredo ou credencial?
[ ] novo acesso que cruza tenants?
[ ] nova tool de IA/MCP?
[ ] dinheiro envolvido?
```

Qualquer "sim" transforma a história em história com impacto de segurança: os controles correspondentes viram parte do escopo, não um follow-up.

Se a história for crítica, faça threat modeling curto — **o que pode dar errado, quem abusaria disso, qual ativo está em risco, qual controle reduz o risco** (detalhes em `references/testes-e-gates.md`).

### 2. Escolha dos controles

Segurança no desenho, não remendo depois. Roteie pela superfície afetada:

| Superfície afetada | Leia |
|---|---|
| Endpoint, view, model, query, task, upload no servidor | `references/backend.md` |
| Tela, componente, estado de permissão, token no browser, bundle, mobile | `references/frontend.md` |
| Segredo, chave, criptografia, PII, log, auditoria, mascaramento | `references/dados-e-segredos.md` |
| API de terceiro, webhook, OAuth, pagamento, LLM, RAG, MCP, agente com tools | `references/integracoes-ia-mcp.md` |
| Docker, ambiente, headers, proxy, CI/CD, dependência, backup, scanner | `references/infra-pipeline.md` |
| Cenário de teste, mapa de testes, gate, exceção de risco, DoD | `references/testes-e-gates.md` |

Leia só os arquivos relevantes à mudança. Uma história de login toca backend + frontend + dados-e-segredos; uma história de "exportar relatório" toca backend + dados-e-segredos + testes.

### 3. Implementação

Backend e frontend são implementados com a mesma análise de risco, mas com responsabilidades diferentes — nunca duplicadas por engano nem delegadas para o lado errado:

| Controle | Backend | Frontend |
|---|---|---|
| Autenticação | decide e emite | envia credencial, trata estado |
| Autorização | **fonte da verdade** | esconde o que o usuário não pode fazer (UX) |
| Permissão por objeto | valida sempre | não assume nada |
| Validação de entrada | revalida tudo | valida para feedback rápido |
| Regras de negócio e valores | calcula e confere | exibe |
| Escape / sanitização | escapa na serialização e nos templates | escapa na renderização |
| Segredos | guarda | **nunca guarda** |
| Mensagem de erro | genérica para fora, detalhada no log | não expõe detalhe interno |

A assimetria importa: validação e autorização no frontend são experiência do usuário; se o backend não repetir, não existe controle. E backend correto com frontend que injeta HTML de terceiro continua sendo uma aplicação vulnerável.

### 4. Testes

Todo controle relevante vira cenário registrado em `docs/mapa-de-testes.md`, com rastreabilidade `T-xxx → H-xxx → controle`. A QA-01 automatiza e executa; a SEC-01 verifica se a cobertura de segurança é suficiente. Ver `references/testes-e-gates.md`.

### 5. Gate

Nada vai para produção com vulnerabilidade crítica conhecida, segredo exposto, autenticação quebrada, isolamento de tenant quebrado ou controle essencial ausente. Risco aceito conscientemente é registrado com motivo, mitigação e prazo — nunca ignorado em silêncio.

## O núcleo que nunca pode faltar

Se não houver tempo para mais nada, garanta estes dez. São a origem da maioria das falhas reais:

1. **Autorização existe no backend** e é a fonte da verdade.
2. **Deny by default** — acesso só é concedido explicitamente.
3. **Permissão por objeto** — não basta "pode ver clientes?", tem que ser "pode ver ESTE cliente?".
4. **Isolamento de tenant** em query, cache, storage, RAG e MCP.
5. **Toda entrada é validada no servidor**, venha de onde vier.
6. **Segredo fora do código** e fora do bundle.
7. **Resposta mínima** — só os campos necessários, sem mass assignment na entrada.
8. **Erro genérico para o usuário, detalhado no log**, sem segredo em nenhum dos dois.
9. **Rate limit** em login, reset, OTP, cadastro, busca cara, IA e API pública.
10. **Fail closed** — se o controle falhar ou ficar indisponível, negue.

## Antipadrões que reprovam a revisão

```text
CSRF desligado globalmente "para facilitar o desenvolvimento"
CORS com "*" junto de credenciais
Model.objects.create(**request.data) sem controle de campos
SELECT concatenando entrada do usuário
serializer com __all__ em recurso sensível
queryset sem filtro de tenant/dono
DEBUG=True em produção
token ou API key em log, URL, analytics ou bundle
LLM decidindo se o usuário tem permissão
RAG que busca tudo e pede para o modelo ignorar o que não pode ver
frontend escondendo o botão e backend sem checar
```

## Registro

- Mudança estrutural de segurança vira decisão no mapa de decisões (ex.: `D-021 usar sessão HttpOnly em vez de token em localStorage`).
- Incidente relevante vai para o diário de bordo, sem expor segredo.
- Exceção de risco é documentada com prazo.

## Formato da revisão de segurança

Ao revisar uma história, PR ou sistema, entregue nesta estrutura:

```markdown
## Triagem
Superfícies tocadas e classificação de risco (baixo / médio / crítico).

## Achados
Para cada um: [severidade] onde está → por que é explorável → como corrigir.
Ordene por severidade, não pela ordem do arquivo.

## Controles ausentes
O que a história exigia e não foi implementado.

## Cenários para docs/mapa-de-testes.md
Lista de abuse cases concretos, prontos para virar teste.

## Veredito
Liberado / liberado com ressalva / bloqueado — com o motivo objetivo.
```

Seja específico sobre exploração: "esse endpoint não filtra por tenant, então `GET /invoice/123` com o token do tenant B retorna a fatura do tenant A" vale mais do que "falta validação". Quando o risco for teórico no contexto, diga que é teórico — inflar severidade faz a revisão inteira ser ignorada.

## Dependências

- **DAH-01 project-governance** — a história define o escopo e bloqueia conclusão com risco crítico aberto.
- **QA-01 testing-quality** — automatiza e executa os cenários definidos aqui.
- **OPS-01** — configura ambiente e operação a partir dos controles definidos aqui.

## Resultado esperado

Ao final deve ser possível responder: quem pode acessar? quem pode alterar? o tenant está isolado? há segredo exposto? há dado sensível desnecessário? a API está protegida? o frontend expõe algo indevido? uploads são seguros? integrações são confiáveis? IA/MCP podem elevar privilégio? há vulnerabilidade crítica aberta? dá para ir para produção com risco aceitável?
