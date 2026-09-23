# EasyPanel — um projeto por ambiente

```text
<produto>-hom                         <produto>-prod
├── api      (:hom, domínio hom)       ├── api      (:prod, domínio prod)
├── worker   (:hom)                    ├── worker   (:prod)
├── beat     (:hom, 1 réplica)         ├── beat     (:prod, 1 réplica)
├── web      (:hom, domínio hom)       ├── web      (:prod, domínio prod)
├── postgres                           ├── postgres (backup off-site)
├── redis                              ├── redis
└── minio    (bucket <produto>-hom)    └── minio    (bucket <produto>-prod)
```

Projeto separado = rede, volumes e envs separados: isolamento sem esforço. Serviços que o
projeto não usa (worker/beat sem Celery, minio sem arquivos) simplesmente não existem.

## Serviços de aplicação

| Serviço | Source | Env de papel | Domínio | Health |
|---|---|---|---|---|
| api | imagem `ghcr.io/<org>/<repo>-api:<hom|prod>` | `ROLE=web`, `RUN_MIGRATIONS=1` | `api[.hom].<produto>.com.br` → 8000 | `/health/ready/` |
| worker | mesma imagem da api | `ROLE=worker`, `CELERY_QUEUES` | — | `python manage.py worker_health` |
| beat | mesma imagem da api | `ROLE=beat` | — | — |
| web | `ghcr.io/<org>/<repo>-web:<hom|prod>` | `API_URL`, `APP_ENV` | `app[.hom].<produto>.com.br` → 8080 | `/health` |

- Source sempre **imagem do GHCR** (build no Actions). Build no servidor só em projeto
  pequeno sem pipeline ainda — e nunca para o web Expo (OOM).
- Registry privado: cadastrar credencial do GHCR (token com `read:packages`) no EasyPanel.
- Deploy webhook de cada serviço → secret no GitHub Environment correspondente.
- hom pode ter recursos menores (worker concurrency 1, 1 worker gunicorn).

## Criar um ambiente

1. Projeto `<produto>-<env>`; postgres e redis pelos templates (senha forte, sem porta pública).
2. minio (se houver storage): bucket privado `<produto>-<env>`, access key só do app.
3. api: imagem `:<env>`, envs de `stacks/backend-django/env.example`, domínio, health.
4. worker e beat: mesma imagem e envs comuns, `ROLE` próprio.
5. web: imagem `:<env>`, `API_URL=https://api[.hom].<produto>.com.br`, `APP_ENV=<env>`.
6. Webhooks de deploy → GitHub → Settings → Environments → `<env>` → secrets.
7. Primeiro deploy pelo pipeline → smoke → `createsuperuser` pelo console da api.
8. prod: backup do postgres configurado + primeiro restore testado.

## Recursos (VPS pequena, ponto de partida)

```text
prod: api 512 MB (3 workers) · worker 512 MB (concurrency 2) · beat 128 MB · web 64 MB
      postgres 1 GB · redis 128–256 MB (noeviction no DB do broker)
hom:  metade disso
```

Medir antes de aumentar. hom e prod no mesmo servidor é aceitável no começo (decisão
registrada); o prod mais crítico migra para servidor próprio quando justificar.
