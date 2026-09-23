# Desenvolvimento assistido por História (docs → código)

Feature não começa pelo código. Começa pelas Histórias e pelos documentos derivados delas,
que a IA lê antes de gerar qualquer arquivo. Isso mantém consistência entre sessões e deixa
app e backend evoluírem em paralelo, desacoplados.

## Quem produz cada documento

| Documento | Skill que produz | Formato |
|---|---|---|
| `docs/produto.md` | `dah-historia` (template) | visão, capítulos, papéis, vocabulário |
| `docs/historias/H-xxx-*.md` + `indice.md` | `dah-historia` | 12 campos |
| `docs/regras-de-negocio.md` (RN-001) | `dah-documentacao` | |
| `docs/modelo-de-dados.md` (ENT-001) | `dah-documentacao` | tipos lógicos |
| `docs/mapa-de-fluxos.md` (FL-001) | `dah-documentacao` | |
| `docs/mapa-de-telas.md` (T-001) | `dah-documentacao` | tela, estados, navegação, GV-* |
| `docs/contratos-de-api.md` (API-001) | `dah-documentacao` | envelope de erro, paginação, auth |
| `docs/guia-visual.md` + `tokens/tokens.json` | `ux-ui` | identidade e padrões GV-* |
| `docs/stack.md` | **esta skill** | libs e convenções do app |
| `docs/rotas.md` | **esta skill** | T- → rota → arquivo → hook |

Esta skill **não reescreve** esses documentos nem cria formatos próprios para eles. Faltou
algo (tela sem T-, operação sem API-)? Pare e derive primeiro com a skill responsável.

Projeto com GitHub Spec Kit / SDD: `spec.md` faz o papel de História + regras, `contracts/`
o de contrato e `data-model.md` o de modelo. Leia-os com o mesmo papel.

## Onde os docs moram

Um lugar só, lido pelo app e pelo backend: `docs/` na raiz do monorepo (padrão da casa)

```text
<produto>/
├── docs/     Histórias e documentos derivados
├── app/      este projeto Expo (tokens/, src/, docs do app em ../docs)
└── api/      backend
```

ou repositório de especificação próprio quando app e backend ficam em repositórios
separados. Nunca mantenha cópias dos docs no repositório do app.

## Como a IA usa os documentos

0. `docs/stack.md` → libs, versões e convenções fixadas.
1. `contratos-de-api.md` → `features/<f>/schemas/` (DTO Zod) exatamente como o contrato;
   `code` de erro → mensagem no `getUserMessage`/tela; 422 → `applyFieldErrors`.
2. `modelo-de-dados.md` → tipo do modelo (`types/`) e `mapper` (ENT-xxx no comentário).
3. `regras-de-negocio.md` → `utils/<f>-rules.ts`, um teste por regra citando o ID:
   `it("RN-003: bloqueia agendamento com mensalidade vencida há mais de 5 dias", ...)`.
   No app a regra serve à UX (desabilitar, avisar antes); a autoridade é o backend.
4. `mapa-de-telas.md` → screens, estados e navegação; `docs/rotas.md` → rotas em `src/app`.
5. `guia-visual.md` → componentes `GV-*` citados em cada T-.
6. Backend ainda não existe? Mock que respeita o contrato (os mesmos schemas validam o mock).
7. Contrato mudou? Atualize o doc **primeiro** (skill `dah-documentacao`), depois schema,
   depois o resto. Divergência entre API real e contrato = bug de um dos lados, nunca
   "ajuste silencioso" no app.

## `docs/rotas.md`

Única tabela que liga documento funcional a código. Template em
`assets/templates/docs/rotas.md`. Atualize ao criar ou mover uma tela.

| Tela | Rota | Arquivo de rota | Screen | Hook de dados |
|---|---|---|---|---|
| T-001 — Login | `/login` | `src/app/(auth)/login.tsx` | `features/auth/screens/login-screen.tsx` | `useLogin` |

## Rastreabilidade no código

- Nome de teste com o ID da regra (`RN-003`) ou da História (`H-012`) quando testa o fluxo.
- Comentário curto no schema: `// API-004 — Listar alunos`.
- Commit/PR cita a História: `feat: adiciona matrícula em turma (H-018)` (skill `git-deploy`).
