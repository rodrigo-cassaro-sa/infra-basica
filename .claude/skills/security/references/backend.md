# Backend

Índice: identidade · autorização · sessão e tokens · validação e injeção · arquivos · API · abuso e limites · tasks e desserialização · banco e cache · ações críticas · configuração Django.

---

## Identidade

**Autenticação responde "quem é o usuário?"**. Sessão, token, OAuth, OIDC ou JWT — a estratégia é uma decisão de arquitetura e deve estar documentada, não improvisada por endpoint.

**Autenticação ≠ autorização.** Login válido não é acesso permitido. Sempre verifique os dois.

**Senhas** usam o hashing do framework (no Django: o auth system e os password hashers). Nunca texto puro, nunca hashing artesanal. A política de senha segue o risco: comprimento mínimo, bloqueio de senhas comprometidas/fracas. Regras complexas demais sem benefício só empurram o usuário para práticas piores.

**MFA**: avalie para admin, superusuário, financeiro, dados sensíveis e operações críticas.

**Recuperação de senha** usa token único, expirável e não reutilizável. Nunca envie a senha atual por e-mail.

**Confirmação de e-mail / OTP**: expiração, limite de tentativas, uso único.

---

## Autorização

**Autorização responde "o que esse usuário pode fazer?"** e vive no backend. O frontend nunca é fonte da verdade.

**Deny by default.** O acesso é concedido explicitamente; a ausência de regra significa negar.

**Permissão por objeto (evita IDOR/BOLA).** Além de "pode visualizar clientes?", valide "pode visualizar ESTE cliente?". `GET /invoice/123` precisa verificar se o usuário pode acessar a invoice 123 — não basta estar autenticado.

Essencial em multi-tenant, filiais, portais de cliente e de fornecedor.

**Isolamento de tenant.** Tenant A nunca acessa dados do tenant B. Valide em:

```text
queries · selectors · API · RAG · MCP · storage · cache
```

O ponto de falha típico não é a view principal: é o autocomplete, o relatório, o export, o endpoint de detalhe por ID e a chave de cache sem escopo.

**Fail closed.** Se o serviço de permissão falhar, negue. Falha inesperada nunca deve abrir acesso.

---

## Sessão e tokens

**Sessões**: expiração definida, cookie `HttpOnly`, `Secure`, `SameSite` conforme a arquitetura.

**Logout** invalida sessão/token conforme a estratégia. Remover o estado visual no frontend não é logout.

**JWT**, se usado: expiração curta quando aplicável, refresh seguro, rotação, revogação quando necessária, assinatura e claims validadas, nenhum segredo no payload. Não adote JWT por padrão quando sessão simples resolve — ele adiciona o problema de revogação que a sessão não tem.

**Nunca exponha** access token, refresh token, API key ou session secret em logs, URL, analytics, mensagens de erro ou no frontend sem necessidade.

---

## Validação e injeção

Toda entrada é validada no backend, independentemente de já ter sido validada no cliente. Fontes de entrada:

```text
frontend · API · webhook · arquivo · integração · MCP · LLM · CSV · query param · header
```

**Allowlist antes de blacklist** — status, tipos, formatos, origens, hosts. É mais fácil enumerar o permitido do que prever todo ataque.

**SQL injection**: ORM ou queries parametrizadas. Nunca concatene entrada em SQL. Se raw SQL for necessário: parâmetros, query fixa, revisão e teste.

**Command injection**: nunca `os.system(user_input)` ou equivalente. Se um comando externo for inevitável — parâmetros fixos, sem shell quando possível, allowlist, sandbox.

**`eval()` / `exec()`**: não execute conteúdo vindo de usuário, IA ou integração.

**Path traversal**: `../../secret` precisa ser bloqueado. Trabalhe com caminhos controlados e derivados de identificadores internos, não de strings do cliente.

**Open redirect**: valide URLs de redirecionamento contra uma lista de destinos permitidos.

**SSRF**: o backend nunca acessa URL arbitrária sem validação de scheme, host, IP, porta, redirect e DNS. Bloqueie a rede interna quando não for necessária. Ver `integracoes-ia-mcp.md`.

---

## Arquivos

**Upload** valida tamanho, extensão, MIME, conteúdo, nome e permissão. Extensão e MIME vêm do cliente: são pistas, não prova.

**Nome do arquivo**: não confie no nome enviado. Gere identificador interno seguro.

**Malware**: em cenários de risco (upload aberto, arquivo compartilhado entre usuários), adicione varredura antimalware.

**Storage**: arquivo privado não é público por padrão. Use ACL, presigned URL com expiração curta e escopo de objeto específico, bucket privado.

**Download**: autenticar → autorizar → validar o objeto, antes de entregar o arquivo. Um link "não listado" não é controle de acesso.

**Parsing de arquivo externo** é entrada hostil: XML com entidades externas desabilitadas (XXE), ZIP protegido contra zip slip e zip bomb, PDF tratado como não confiável, bibliotecas de parser mantidas atualizadas.

**Export CSV**: neutralize formula injection quando o arquivo for aberto em planilha — campos iniciando por `=`, `+`, `-`, `@`.

---

## API

Toda API privada tem: auth, permission, validation, rate limit quando necessário, logging.

**Mass assignment**: não faça `Model.objects.create(**request.data)` sem controlar quais campos o usuário pode definir. O campo perigoso raramente é o óbvio — é `is_admin`, `tenant_id`, `status`, `price`.

**Excessive data exposure**: não serialize tudo automaticamente. Exponha apenas os campos necessários. `__all__` em recurso sensível vaza campos que ninguém pretendia expor, inclusive os que forem adicionados no futuro.

**Paginação obrigatória** — nunca lista ilimitada em endpoint público.

**Erro seguro**: mensagem genérica o suficiente para o usuário, log interno detalhado o suficiente para investigar, sem stack trace, SQL, path interno, configuração ou segredo na resposta.

**Health check** não revela detalhes sensíveis de infraestrutura.

**CSRF**: com autenticação por cookie/sessão, a proteção CSRF fica habilitada. Não desative globalmente para facilitar o desenvolvimento.

**CORS**: apenas as origens necessárias. Nunca `*` com credenciais.

---

## Abuso e limites

**Rate limit** em: login, reset de senha, cadastro, OTP, API pública, busca cara, IA, webhook sensível.

**Brute force**: rate limit, lockout progressivo, monitoramento, MFA — sem criar um vetor fácil de negação de serviço contra usuários legítimos.

**Enumeração de usuários**: quando o risco justificar, "e-mail ou senha inválidos" em vez de revelar se o cadastro existe. Vale também para reset de senha e cadastro.

**DoS na aplicação**: limites em upload, payload, query, paginação, IA e relatórios.

- Evite filtros que permitam carga arbitrária sem controle.
- Evite regex suscetível a ReDoS.
- N+1 em endpoint público é vetor de DoS: performance e segurança se cruzam aqui.

---

## Tasks, filas e desserialização

Tasks validam argumentos, permissões quando necessário, estado e idempotência — a task roda fora do request e não herda o contexto de permissão dele.

- Broker (Redis/RabbitMQ) protegido e não exposto.
- Não trafegue segredo desnecessário no payload da fila.
- Prefira JSON. Evite serialização insegura.
- **Pickle** nunca para mensagens de fonte não confiável.
- Toda desserialização é entrada potencialmente hostil.

---

## Banco, cache e storage

- A aplicação não precisa do superuser do PostgreSQL. Separe o role de migration (privilégio maior) do runtime quando a maturidade justificar. Ferramentas de relatório podem usar role read-only.
- Redis com autenticação/ACL quando aplicável; não exposto publicamente.
- Worker Celery não precisa de acesso a tudo — separe credenciais quando possível.
- MinIO com credencial de serviço de política restrita, buckets privados, console autenticado.
- **Cache**: a chave inclui o escopo. Nunca misture dados de tenants. Não cacheie dado privado em cache compartilhado sem chave e política corretas.
- Backups de banco com acesso e credenciais protegidos.

---

## Ações críticas

**Admin** (inclusive Django Admin): autenticação exigida, permissão restrita, HTTPS, sem exposição de segredos. Conta superuser é rara e protegida, e não é usada em integrações comuns.

Ações administrativas críticas exigem **permission + audit + confirmation**.

- **Delete irreversível**: confirmação, permissão, auditoria.
- **Exportação**: quem pode exportar, quais dados, qual volume, auditoria.
- **Importação**: schema, volume, formato, permissão.
- **Operações em massa**: proteção extra — o raio de alcance do erro ou do abuso é multiplicado.

**Valores financeiros**: o backend calcula e valida. Nunca aceite o valor final vindo do frontend nem confie só no retorno do cliente para confirmar pagamento — confirme com o provider.

---

## Configuração Django

Revise conforme o ambiente:

```text
DEBUG=False
SECRET_KEY segura e fora do código
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
SECURE_SSL_REDIRECT
SESSION_COOKIE_SECURE
CSRF_COOKIE_SECURE
SECURE_HSTS_SECONDS
```

```bash
python manage.py check --deploy
```

Use como uma das validações — não como prova suficiente de que está seguro.
