# Segurança, autenticação e privacidade

## Regra zero

Tudo no bundle (JS, `EXPO_PUBLIC_*`, app config, assets) pode ser extraído. **Nunca** no app:
senha de banco, JWT secret, chave privada, token de API administrativa, credencial de storage (MinIO/S3 admin), SMTP, chave de API paga de IA/serviços, token master de BaaS ou ferramenta low-code (NocoDB, Supabase `service_role`, Firebase admin, webhook "aberto" de automação).

Arquitetura correta:

```
App ──HTTPS──> Backend/API (autentica, autoriza, valida, limita taxa) ──> Banco / Storage / IA / Automação
```

Se o backend for low-code (ex.: webhooks de automação), coloque autenticação no webhook (validar JWT do usuário), nunca confie num "segredo" guardado no app. Para upload de arquivo, o backend gera **URL pré-assinada** e o app envia direto ao storage.

## Autenticação × autorização

- Autenticação: quem é você (login → tokens).
- Autorização: o que você pode fazer — **sempre no backend**. Esconder botão (`canDelete && <Button/>`) é só UX; a API responde 403.

## Tokens

- `accessToken` curto (minutos) + `refreshToken` longo, rotacionado a cada uso.
- Guardar em `expo-secure-store` (Keychain/Keystore). Valores pequenos apenas (~2 KB); não é banco de dados.
- Em memória: manter o access token num módulo/estado para não ler do SecureStore a cada request.
- Refresh: um único refresh em andamento por vez (fila das requisições que tomaram 401). Se falhar → limpar tokens → `session-store` vai para `unauthenticated` (o `Stack.Protected` leva ao login).
- Logout: apagar tokens, `queryClient.clear()`, avisar o backend para revogar o refresh.
- **Web**: SecureStore não funciona na web. Para web, prefira cookie `httpOnly` + `SameSite` emitido pelo backend; faça um adapter de storage por plataforma (`token-storage.native.ts` / `token-storage.web.ts`, ou `Platform.OS` dentro do adaptador).

Exemplo pronto: `assets/templates/token-storage.ts` (destino `src/services/storage/token-storage.ts`).

## Fluxo de sessão (templates prontos)

| Peça | Arquivo (template) | Papel |
|---|---|---|
| Contrato | `features/auth/schemas/auth-schema.ts` (`auth-schema.ts`) | login, usuário da sessão, form de login |
| Chamadas | `features/auth/services/auth-service.ts` (`auth-service.ts`) | `login`, `getMe`, `revokeSession` |
| Tokens | `services/storage/token-storage.ts` | SecureStore / memória na Web |
| Refresh | `services/api/api-client.ts` | 401 → um refresh (single-flight) → repete; falhou → handler |
| Estado | `stores/session-store.ts` (`session-store.ts`) | `status` loading/authenticated/unauthenticated, `bootstrap`, `login`, `logout` |
| Guarda | `app/_layout.tsx` (`root-layout.tsx`) | splash até `bootstrap` terminar; `Stack.Protected` por status |

Contrato com o backend (registrar em `docs/contratos-de-api.md`):
`POST /auth/login` → `{ accessToken, refreshToken, user }` · `POST /auth/refresh` →
`{ accessToken, refreshToken }` (refresh **rotativo**) · `POST /auth/logout` (revoga o
refresh) · `GET /auth/me` → usuário.

Regras:
- Sessão restaurada **antes** da primeira tela (status `loading` segura a splash): nada de a
  tela de login piscar para quem já está logado.
- Depois de `login()`/`logout()` **não navegue**: o `Stack.Protected` troca de grupo sozinho.
- Logout limpa tokens **e** `queryClient.clear()`. Em aparelho compartilhado (recepção,
  balcão), esquecer o `clear()` mostra dados de um cliente para o próximo.
- Área por papel (admin): outro `Stack.Protected guard={user?.role === "admin"}` dentro do
  grupo `(app)`. Só esconde tela; a API valida.

### Tela de login
- É um formulário comum (`formularios.md`) com `loginFormSchema` (senha só "não vazia").
- Senha: `secureTextEntry`, `autoComplete="current-password"`, `textContentType="password"`
  (cadastro: `new-password`/`newPassword`) — ativa o gerenciador de senhas; permitir colar
  senha (WCAG 3.3.8).
- Erro de credencial **genérico**: "E-mail ou senha incorretos." Nunca diga qual dos dois
  errou (revela quais e-mails têm conta).
- 429 (muitas tentativas): diga quanto esperar, sem culpar o usuário.

## Login social / OAuth

- `expo-auth-session` + `expo-web-browser` para OAuth/OIDC com PKCE.
- Apple Sign In: `expo-apple-authentication` (obrigatório oferecer na App Store se houver outros logins sociais, com exceções da Apple).
- Google nativo, Clerk, Auth0, Supabase Auth etc. normalmente exigem **development build**.
- Validação final do token do provedor é no backend.

## Biometria

`expo-local-authentication` **destrava a sessão que já existe no aparelho**; não é método de
login e não substitui o login no servidor. Exige development build.

- Configure o texto do Face ID no plugin (`["expo-local-authentication", { faceIDPermission: "..." }]`);
  sem ele o iOS encerra o app na primeira tentativa. Mudança de plugin = build novo.
- Fluxo: depois do primeiro login com senha, ofereça ativar (só se `hasHardwareAsync()` e
  `isEnrolledAsync()`). Nas aberturas seguintes, peça a biometria **antes** do `bootstrap()`.
- Biometria falhou/cancelada: **não** faça logout — mande para o login com senha
  (`cancelLabel: "Usar senha"`). Digital falha por dedo molhado; senha é sempre a saída.
- A preferência "usar biometria" não é segredo: vai no `preferences-store`. Logout manual desativa.
- Proteção mais forte (financeiro, saúde): `requireAuthentication: true` no SecureStore — o
  próprio sistema exige biometria para ler o refresh token. O item é invalidado quando o
  usuário cadastra digital nova: trate a leitura falhando como "logar com senha".

## Permissões do sistema

- Pedir no momento de uso, depois de explicar o porquê (tela/modal própria), nunca na abertura do app.
- Tratar negação: mostrar como habilitar em Ajustes (`Linking.openSettings()`).
- Declarar textos de permissão no app config (plugins de `expo-camera`, `expo-location`, etc.). A Apple reprova texto genérico.

## Logs e monitoramento

- Nunca logar: senha, tokens, CPF completo, cartão, dados de saúde, conteúdo de formulário sensível.
- Produção: serviço de crash/erro (Sentry com `@sentry/react-native` tem suporte Expo; EAS Observe para performance). Enviar versão do app, ambiente, rota, id interno do usuário — não dados pessoais.
- `console.log` fora de produção (remover ou usar `logger` que silencia em prod).

## LGPD (Brasil)

- Coletar só o necessário; explicar finalidade.
- Política de privacidade acessível no app e na ficha da loja.
- Permitir exclusão da conta pelo app (exigência da Apple e do Google Play também).
- Formulário "Segurança dos dados" (Play) e "Privacy Nutrition Labels" (App Store) coerentes com o que o app faz.

## Transporte

HTTPS sempre. Android bloqueia HTTP em release por padrão; não habilite cleartext em produção. Em dev com API local, use o IP da máquina na rede (não `localhost` no aparelho físico) ou um túnel.
