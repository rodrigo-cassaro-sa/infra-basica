# Mapa de Decisões

Registro das decisões do projeto e de seus motivos.
Proprietária: `dah-documentacao` (P-03). P-04, P-05 e P-06 acrescentam dentro do
próprio escopo, sem editar o que já existe — ver `AGENTS.md` §3.1.

**D-001 a D-005 vieram do template**, não deste projeto. Estão aqui porque o
código entregue depende delas e porque substituí-las é uma decisão que precisa
ser registrada. A numeração própria do projeto **começa em D-006**.

Para trocar qualquer uma: registre um `D-xxx` novo com status `ativa` e marque a
anterior como `substituída`. Não edite a original.

---

## D-001 — Backend padrão

**Origem:** decisão da casa (template DAH) · **Status:** ativa (herdada)

Python + Django + PostgreSQL como backend padrão, para manter um único padrão
entre ERP, CRM, SaaS e sistemas internos.

Detalhamento em `AGENTS.md` §19.

---

## D-002 — Arquitetura

**Origem:** decisão da casa (template DAH) · **Status:** ativa (herdada)

Monólito modular: reduz complexidade mantendo os domínios separados dentro de
uma aplicação. Cada domínio em `backend/apps/<dominio>/`.

Detalhamento em `AGENTS.md` §20.

---

## D-003 — Organização DAH

**Origem:** decisão da casa (template DAH) · **Status:** ativa (herdada)

Histórias como arquivos `.md` em um único diretório, com numeração global,
para simplificar planejamento e navegação.

Detalhamento em `AGENTS.md` §3 e §5.

---

## D-004 — Uma única stack de frontend

**Origem:** decisão da casa (template DAH) · **Status:** ativa (herdada)

Expo + React Native + TypeScript cobrindo Android, iOS e Web a partir de
`frontend/`. Não existe um segundo projeto de frontend. Uma base evita dois
design systems, dois clients de API e dois pipelines para o mesmo produto.

`expo-app` é a única skill de programação de frontend; a plataforma da tela
decide o alvo do build, não a skill. `ux-ui` e `frontend-web` são skills de
design e não implementam.

Uma stack web separada exigiria nova decisão, skill de implementação própria e
um Dockerfile irmão.

Detalhamento em `AGENTS.md` §21.

---

## D-005 — Health check é público

**Origem:** decisão da casa (template DAH) · **Status:** ativa (herdada)

`GET /api/health/` não exige autenticação.

### Motivo

O EasyPanel, o monitor externo e quem opera o sistema precisam saber se a API
está no ar justamente quando o sistema está com problema, e o template não
entrega autenticação.

### Consequência aceita

A resposta informa apenas `status`, `service` e o módulo de settings em uso.
Nunca endereço, versão de biblioteca, string de conexão nem texto de exceção.

Projeto que considere essa informação sensível deve registrar um `D-xxx`
próprio e proteger a rota.
