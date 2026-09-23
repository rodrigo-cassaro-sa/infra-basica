# Infraestrutura, dependências e pipeline

Índice: dependências e supply chain · containers · rede e serviços · ambientes · proxy e headers · cache e CDN · backups · CI/CD · scanners e gate técnico · incidentes.

---

## Dependências e supply chain

Toda dependência aumenta a superfície de ataque. Antes de adicionar, pergunte: **é necessária? é mantida? tem vulnerabilidade conhecida?**

- Use lockfile quando o ecossistema suportar; fixe versões críticas.
- Automação de atualização (Dependabot/Renovate) ajuda a detectar; atualização major é revisada, não mesclada automaticamente.
- Evite biblioteca abandonada quando houver alternativa mantida.
- Vale igual para frontend e backend — `node_modules` é supply chain tanto quanto o `requirements.txt`.

**Dependência vulnerável**: avalie se é explorável no seu contexto, se há patch e se há mitigação. CVSS ajuda a priorizar, mas nota isolada sem contexto de exploração e impacto não decide nada. Atualização de segurança crítica tem prioridade adequada.

---

## Containers

- Menor privilégio: evite rodar como root quando não for necessário.
- Imagens oficiais, mínimas e versionadas.
- Nenhum segredo dentro da imagem.
- `.dockerignore` impedindo que `.env`, credenciais e backups entrem no build context.
- Exponha apenas as portas necessárias.

---

## Rede e serviços

- Redis não exposto publicamente; autenticação/ACL quando aplicável.
- PostgreSQL não exposto diretamente à Internet sem necessidade e proteção apropriada.
- MinIO com console e API autenticados, acesso restrito e buckets privados por padrão.
- Presigned URL com expiração curta, escopo específico e objeto específico.

---

## Ambientes

Separe **dev / hom / prod**.

Não copie dados de produção para desenvolvimento sem sanitização e autorização — é o vazamento mais comum e o mais fácil de evitar.

Em produção: `DEBUG=False`, sem stack trace, SQL, path interno, configuração ou segredo na resposta ao usuário. Health check não revela detalhes sensíveis.

---

## Proxy e headers

- Configure security headers no framework, no Traefik ou no proxy, conforme a arquitetura (HSTS, CSP, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, frame-ancestors).
- **Proxy trust**: configure `X-Forwarded-Proto` e proxies confiáveis corretamente, para não aceitar header forjado de origem não confiável.
- **IP real**: só confie em header de IP quando ele vier de um proxy conhecido. Rate limit e auditoria baseados em IP forjável não valem nada.
- CORS com origens explícitas.
- **Rate limit de infraestrutura**: para abuso volumétrico, a aplicação pode não bastar — avalie proxy, WAF ou CDN.

---

## Cache e CDN

- Chave de cache inclui o escopo (usuário/tenant). Nunca misture dados de tenants.
- Não cacheie dado privado em cache compartilhado sem chave e política corretas.
- Não cacheie publicamente conteúdo autenticado por erro de configuração de CDN.

---

## Backups

```text
protegidos · criptografados quando necessário · acesso restrito · testados
```

Backup não validado é risco, não proteção: teste a restauração. Defina política de retenção — não guarde dados indefinidamente sem necessidade.

---

## CI/CD

Proteja tokens, deploy keys, credenciais de cloud e de registry.

- Pipeline com permissões mínimas.
- Secrets no secret store da plataforma. Nunca ecoe segredo em log de build.
- Branch protection em projetos relevantes: PR obrigatório, review, checks.
- Artefato publicado não contém `.env`, chaves, dump ou dados sensíveis.

---

## Scanners e gate técnico

Conforme a maturidade do projeto, incorpore ao pipeline:

```text
SAST         → Bandit, Semgrep, linters especializados
SCA          → dependências vulneráveis
secret scanning → segredo acidental no repositório
container scanning → imagens de produção
DAST         → em homologação, quando a maturidade justificar
```

Scanner é apoio, não veredito: ele não conhece a lógica de autorização do seu domínio, que é onde moram as falhas mais graves.

---

## Incidentes

O projeto precisa saber **como detectar, conter, investigar, corrigir e recuperar**.

Incidente relevante é registrado no diário de bordo, sem expor segredo. Se um segredo esteve exposto, rotacione — remover o commit não basta.

---

## Checklist de infra

```text
[ ] HTTPS
[ ] portas mínimas
[ ] banco privado
[ ] Redis privado
[ ] MinIO privado
[ ] containers não-root quando possível
[ ] secrets fora da imagem
[ ] backups protegidos e testados
[ ] logs protegidos
[ ] proxy trust configurado
```
