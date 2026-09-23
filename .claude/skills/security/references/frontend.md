# Frontend e mobile

Índice: premissa · XSS · headers e enquadramento · CSRF e CORS do lado cliente · tokens e armazenamento · bundle · autorização na interface · erros · mobile.

---

## Premissa

Tudo que é enviado ao navegador deve ser considerado público para o usuário. Código, bundle, variáveis de build, payload de API, source map: o usuário pode ler tudo.

Disso decorre o resto: o frontend protege a **experiência** e a **superfície do cliente**; ele não protege o dado. Quem protege o dado é o backend.

---

## XSS

Conteúdo dinâmico é escapado na renderização. Evite renderizar HTML não confiável.

Quando HTML for realmente necessário (editor rich text, conteúdo de CMS), sanitize com biblioteca dedicada e mantida — e sanitize no momento da renderização, não só na gravação.

Em React e frameworks equivalentes, não use a API de renderização de HTML cru (`dangerouslySetInnerHTML` e equivalentes) sem sanitização. Cuidado também com:

```text
href / src recebendo valor do usuário (javascript:)
atributos de estilo dinâmicos
redirecionamento com destino vindo de query param
render de markdown sem sanitização
```

**CSP** (Content Security Policy) reduz o impacto de um XSS que passar. Adote quando aplicável — é defesa em profundidade, não substituto do escape.

---

## Headers e enquadramento

Avalie e configure (no servidor/proxy, mas é o frontend que sofre a consequência):

```text
HSTS
CSP
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
X-Frame-Options / CSP frame-ancestors  → clickjacking
```

---

## CSRF e CORS do lado cliente

Com autenticação baseada em cookie/sessão, as requisições que alteram estado carregam a proteção CSRF do framework. Não contorne isso no cliente "porque dava erro no dev".

CORS é configurado no servidor com origens explícitas; se a tela precisa de uma origem nova, isso é uma decisão de segurança, não um ajuste de build.

**Open redirect**: destino de redirecionamento vindo de query param é validado contra allowlist antes de navegar.

---

## Tokens e armazenamento

- **Secret de servidor nunca no frontend.** API key só quando o provider a projetou para uso público/restrito (com domínio e escopo travados no painel do provider). Secret key, nunca.
- **LocalStorage**: não guarde token sensível ali por padrão — é legível por qualquer XSS. Cookie `HttpOnly` + `Secure` + `SameSite` tira o token do alcance do JavaScript. Escolha a estratégia conscientemente e registre a decisão.
- Não copie segredos para o clipboard automaticamente.
- Não coloque token em URL — ele vaza em histórico, referer, log de proxy e analytics.

---

## Bundle

- Nenhum segredo no bundle, incluindo variáveis de build que parecem inofensivas.
- **Source maps**: avalie a exposição em produção.
- Dependências de frontend contam como superfície de ataque igual às de backend — revise antes de adicionar e mantenha atualizadas (ver `infra-pipeline.md`).

---

## Autorização na interface

Esconder um botão é UX. O backend continua responsável por autorizar.

Ainda assim, os estados de permissão precisam estar corretos: a tela não deve oferecer uma ação que vai falhar com 403, nem exibir dados que o usuário obteve só porque a API devolveu campos demais. Se a interface mostra algo que o usuário não deveria ver, o problema é na API — reporte, não maquie no cliente.

Checklist de estados: sem permissão, sem autenticação, sessão expirada, permissão revogada no meio da sessão.

---

## Erros

Mensagem de erro no cliente não expõe stack trace, path interno, detalhe de infraestrutura ou payload bruto da API. Erro técnico vai para o monitoramento — e o monitoramento não pode virar canal de vazamento (ver `dados-e-segredos.md`).

---

## Mobile

- Segredos não são embutidos no APK/IPA — o binário é inspecionável.
- Tokens vão para armazenamento seguro da plataforma: Keychain, Keystore, SecureStore, conforme a stack.
- **Deep links**: valide parâmetros e origem quando relevante — são uma entrada externa como qualquer outra.
- **Screenshots**: para dados altamente sensíveis, avalie as restrições específicas da plataforma.

---

## Checklist rápido

```text
[ ] sem secret no bundle
[ ] sem HTML inseguro sem sanitização
[ ] token tratado pela estratégia decidida (cookie HttpOnly ou storage seguro)
[ ] estados de permissão corretos, incluindo sessão expirada
[ ] erro não expõe detalhe interno
[ ] redirect validado
[ ] dependências revisadas
```
