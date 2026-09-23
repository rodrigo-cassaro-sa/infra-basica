# Backup e recuperação

> BACKUP NÃO TESTADO = BACKUP NÃO CONFIÁVEL.

## 1. Definir por projeto (registrar no docs/deploy.md)

- **RPO** — quanto dado pode ser perdido (padrão: 24 h; sistema financeiro/saúde: 1 h com WAL/PITR).
- **RTO** — quanto tempo para voltar (padrão: 4 h).

## 2. O que proteger (prod)

| Item | Como | Frequência | Retenção |
|---|---|---|---|
| Postgres | backup do EasyPanel (pg_dump) → destino off-site (S3/R2/Backblaze) | diário (ou WAL contínuo se RPO < 24 h) | 7 diários, 4 semanais, 6 mensais |
| MinIO | versionamento do bucket + `mc mirror` para destino off-site | diário | 30 dias |
| Config crítica | envs e segredos no cofre de senhas; `docs/deploy.md` no repo | a cada mudança | — |

Criptografar backup que contém dado pessoal/sensível. hom: backup opcional (dados sintéticos).

## 3. Restore test (mensal em prod)

```bash
createdb restore_test
pg_restore -d restore_test --no-owner --no-privileges backup.dump
psql restore_test -c "select count(*) from <tabela_principal>;"   # confere volume plausível
dropdb restore_test
```

Registrar data, duração e resultado no diário de bordo. Duração real alimenta o RTO.

## 4. Desastre

| Cenário | Recuperação |
|---|---|
| servidor perdido | novo servidor + EasyPanel → recriar projeto pelo `docs/deploy.md` → restore postgres/minio → apontar DNS |
| banco corrompido / delete errado | restore em banco novo → conferir → trocar `DATABASE_URL` |
| bucket perdido | restaurar do espelho off-site |
| segredo vazado | `runbook.md` |

Pontos únicos de falha (um servidor, um banco) são aceitos conscientemente no início —
registrar como decisão com o RPO/RTO que eles implicam.
