# Rotas — [NOME DO APP]

> Liga as telas do `docs/mapa-de-telas.md` (T-) ao código. Estados, campos e navegação
> ficam no mapa de telas; aqui só o endereço de cada coisa.

| Tela | Rota | Arquivo de rota | Screen | Hook de dados | Acesso |
|---|---|---|---|---|---|
| T-001 — Login | `/login` | `src/app/(auth)/login.tsx` | `features/auth/screens/login-screen.tsx` | `useLogin` | público |
| T-002 — Início | `/home` | `src/app/(app)/home.tsx` | `features/home/screens/home-screen.tsx` | `useResumo` | logado |
| T-003 — Detalhe do usuário | `/usuarios/[id]` | `src/app/(app)/usuarios/[id].tsx` | `features/users/screens/user-detail-screen.tsx` | `useUser(id)` | logado + papel admin |

## Permissões do sistema (câmera, localização, notificações…)
| Permissão | Tela | Texto explicativo |
|---|---|---|
| Câmera | T-0XX `/perfil/foto` | "Para tirar sua foto de perfil" |
