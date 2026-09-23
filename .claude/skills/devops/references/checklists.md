# Checklists

## Readiness (antes do primeiro deploy em prod)

```text
[ ] build reproduzível; imagem versionada (tree/sha) no GHCR
[ ] testes e gates no CI; deploy bloqueia em falha
[ ] security checks (SEC-01) no pipeline
[ ] migrations revisadas e aplicadas em hom
[ ] secrets só em env/Environments; .env.example atualizado
[ ] health live/ready (api), /health (web), worker_health
[ ] logs JSON com correlation_id; Sentry por ambiente
[ ] backup off-site + restore testado
[ ] rollback testado em hom
[ ] smoke automático no pipeline
```

## Ambiente

```text
[ ] projeto EasyPanel próprio (<produto>-hom / -prod)
[ ] banco, Redis, bucket, secrets e credenciais só deste ambiente
[ ] APP_ENV correto; DEBUG=False (hom e prod)
[ ] domínio correto + HTTPS; CORS/ALLOWED_HOSTS/CSRF com os domínios dele
[ ] hom: OUTBOUND_ALLOWLIST preenchida e credenciais sandbox
```

## Docker

```text
[ ] imagem oficial com versão fixa; multi-stage
[ ] sem secrets em ARG/ENV; .dockerignore (.git, .env, node_modules, .venv)
[ ] usuário não-root; HEALTHCHECK; comando correto por ROLE
[ ] RELEASE embutido e visível no /health
```

## Banco

```text
[ ] volume persistente; sem porta pública
[ ] backup + restore testado; disco monitorado
[ ] migrations aplicadas só pela api; conexões dentro do limite (PgBouncer só se preciso)
```

## Celery

```text
[ ] broker por ambiente; worker e beat com a mesma imagem da api
[ ] beat com 1 réplica; filas definidas; worker_health; backlog monitorado
```

## MinIO

```text
[ ] bucket privado por ambiente; access key só do app
[ ] volume persistente; espelho off-site em prod
```

## Frontend web / app

```text
[ ] imagem web sem URL de API embutida (config.js em runtime)
[ ] /health do web com release; cache: assets imutáveis, HTML no-cache
[ ] EAS: channel preview (hom) e production (prod); runtimeVersion fingerprint
[ ] backend deployado antes do web/update do app
```

## Deploy

```text
[ ] artefato identificado (tree) e o mesmo de hom
[ ] migration revisada; backup se migration-risk
[ ] aprovação do environment prod
[ ] smoke verde; logs e Sentry observados 15 min
[ ] rollback disponível (tree anterior anotado)
```

## Observabilidade / backup / produção

```text
[ ] logs · uptime · error rate · latência · CPU · RAM · disco · DB · fila
[ ] backup banco e storage · frequência · retenção · off-site · restore testado
[ ] DEBUG=False · HTTPS · secrets · health · firewall · rollback
```

## Definition of Done — OPS-01

1. ambientes separados (dev/hom/prod); 2. configuração externalizada; 3. build reproduzível;
4. artefato versionado e promovido de hom para prod; 5. deploy com processo definido (pipeline);
6. migrations revisadas e testadas em hom; 7. rollback considerado; 8. secrets protegidos;
9. banco persistente com backup; 10. restore testado quando a criticidade exigir;
11. health checks em todos os serviços; 12. logs permitem investigação; 13. métricas quando
necessário; 14. alertas críticos definidos; 15. workers/filas monitorados; 16. storage
persistente; 17. HTTPS em hom e prod; 18. smoke após todo deploy; 19. capacidade adequada;
20. DAH-01 pode considerar a história operacionalmente pronta.

Ao terminar, dá para responder: como sobe, como é construído e publicado, como migrations
são aplicadas, como volta, onde ficam os secrets, como o banco é protegido, como workers são
operados, onde ficam os arquivos, como saber que falhou, como recuperar, como restaurar.
