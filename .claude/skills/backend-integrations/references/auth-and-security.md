# Autenticação e segurança

Índice: Configuração · Segredos · Ambientes · OAuth · Refresh token · API keys · Assinatura de request · Multi-tenant · Rotação · Certificados · SSRF · Redirects · TLS · IP allowlist · PII e dados regulados

---

## Configuração centralizada

Toda integração tem bloco próprio de configuração:

```text
CRM_BASE_URL
CRM_API_KEY
CRM_TIMEOUT
CRM_ENABLED
```

Uma base URL por integração. Montar URL absoluta em dezenas de arquivos é como se descobre, em produção, que metade do sistema ainda aponta para o host antigo.

## Segredos

Nunca no Git: API key, client secret, private key, refresh token, senha, token.

Use variável de ambiente, secret manager ou configuração segura da plataforma.

Isso vale também para: fixture de teste, docker-compose versionado, README, comentário de código e print em issue.

## Ambientes

Separe `dev`, `homologação` e `produção`. Integração de homologação nunca pode usar credencial de produção por acidente — é assim que se dispara cobrança real num teste.

Quando o provider oferecer, use chave de sandbox com prefixo distinguível e valide no boot que o ambiente bate com a chave.

---

## OAuth

Separe as etapas em módulo próprio:

```text
authorization · token exchange · refresh · revogação · escopos
```

Peça apenas os escopos necessários (least privilege). `full_access` por conveniência é dívida de segurança que ninguém revisa depois.

### Refresh token

Armazene de forma segura (criptografado em repouso quando possível). Trate expiração, revogação e rotação — provider que rotaciona refresh token invalida o anterior, então gravar o novo é parte do fluxo, não detalhe.

Nunca logue refresh token nem access token.

## API keys

Envie conforme a especificação do provider: `Authorization` header ou `X-API-Key`. Evite query string para segredo — query string vai para log de servidor, de proxy e de CDN.

## Assinatura de requisição

Alguns providers exigem HMAC com timestamp, nonce e canonical string. Implemente em módulo isolado e cubra com testes determinísticos (vetores fixos de entrada e assinatura esperada) — erro de assinatura é difícil de diagnosticar em produção.

## Credenciais por tenant

Em produto multi-tenant onde cada cliente conecta a própria conta do provider:

- credencial vive por tenant, isolada;
- o client é construído por tenant, não como singleton global;
- log e métrica identificam o tenant;
- revogação de um tenant não afeta os demais.

## Rotação de segredo

Toda credencial deve poder ser trocada sem downtime. Suporte período com duas chaves válidas quando o provider permitir, e monitore data de expiração.

## Certificados

Integrações com mTLS ou certificado de cliente: monitore validade e alerte com antecedência. Certificado vencido derruba integração inteira num domingo de madrugada.

---

## SSRF

Nunca aceite URL arbitrária do usuário para o backend acessar.

```text
POST /fetch-url    ← anti-pattern
```

Quando for inevitável buscar recurso externo informado:

- allowlist de domínios;
- bloquear IP privado, loopback e link-local (169.254.169.254 é metadata de cloud);
- resolver DNS e validar o IP resolvido, não só a string;
- timeout curto e limite de tamanho;
- não seguir redirect cegamente — revalide o destino de cada redirect.

## TLS

Valide certificado sempre. Desabilitar verificação TLS "para funcionar em homologação" é como a integração vai para produção.

Cert pinning só quando o requisito justificar — ele quebra quando o provider rotaciona certificado, e alguém precisa manter isso.

## IP allowlist, DNS e proxy

Alguns providers exigem IP de origem fixo: documente quais IPs saem do nosso ambiente e o que acontece num redeploy.

Se o tráfego sai por proxy corporativo, isso é configuração da integração, não gambiarra local.

---

## PII e dados regulados

- minimize PII enviada: mande só o campo que o provider precisa;
- payload com dado pessoal não vai para log, nem em nível DEBUG;
- dado regulado (saúde, financeiro, biometria) exige verificar base legal e contrato com o provider antes de trafegar;
- retenção de payload de webhook tem prazo definido.

## Não exponha segredo no Admin nem na API

Django Admin não mostra token em texto puro. No máximo:

```text
********abcd
```

Isso vale igualmente para qualquer endpoint consumido pelo app Expo.
