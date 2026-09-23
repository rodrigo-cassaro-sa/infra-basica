# Stack backend-django (OPS-01)

Como os backends da família BE viram containers em hom e prod. Regras gerais (ambientes,
pipeline, promoção, backup) estão no SKILL.md da devops — aqui só o específico do Django.

## Arquivos

| Arquivo | Vai para | Função |
|---|---|---|
| `Dockerfile` | `backend/Dockerfile` | imagem única multi-stage com uv; `ARG RELEASE` = tree hash de `backend/` |
| `dockerignore` | `backend/.dockerignore` | fora: `.env`, `.git`, `.venv`, caches |
| `entrypoint.sh` | `backend/docker/entrypoint.sh` | `ROLE=web|asgi|worker|beat|manage`; migrate só com `RUN_MIGRATIONS=1` |
| `gunicorn.conf.py` | `backend/docker/gunicorn.conf.py` | workers/timeouts por env, logs em stdout |
| `health.py` | `backend/config/health.py` + comando `worker_health` | live/ready com `release` e `env` |
| `settings_ops.py` | fim de `config/settings/production.py` | WhiteNoise, cache Redis, Sentry por `APP_ENV`, `OUTBOUND_ALLOWLIST` |
| `docker-compose.yml` | `backend/docker-compose.yml` | ambiente **dev**: web, worker, beat, postgres, redis, minio |
| `env.example` | referência para o EasyPanel | chaves iguais em hom/prod, valores diferentes |

## Uma imagem, vários papéis, dois ambientes

```text
ghcr.io/<org>/<repo>-api:tree-<hash>
        │  ROLE=web (+RUN_MIGRATIONS=1)   → serviço api
        │  ROLE=worker                   → serviço worker
        │  ROLE=beat (1 réplica)         → serviço beat
        └─ APP_ENV=hom | prod            → diferença entre ambientes é só configuração
```

- `config.settings.production` serve hom **e** prod. Não existe `settings/hom.py`.
- `APP_ENV` define o `environment` do Sentry e exige `OUTBOUND_ALLOWLIST` fora de prod
  (o settings falha no start se hom estiver sem allowlist).
- `RELEASE` vem da imagem; `/health/ready/` devolve `{"status","checks","release","env"}`.

## Regras do stack

- Migrate só no serviço api, no start. Worker/beat nunca migram. Migration falhou = container não sobe.
- Beat com 1 réplica. Worker separado por fila só quando uma fila atrapalha outra (`ai`, `integrations`).
- Health não chama provider externo; `ready` testa Postgres e, se houver fila, Redis.
- `SECURE_REDIRECT_EXEMPT` cobre `/health/` (o check interno do EasyPanel é HTTP).
- Cache Redis no DB 1 (broker no DB 0), `IGNORE_EXCEPTIONS=True`, chave com tenant.
- Sentry `send_default_pii=False`, tag `correlation_id`.
- Dependências no `pyproject.toml` do backend-core (bloco "devops").
