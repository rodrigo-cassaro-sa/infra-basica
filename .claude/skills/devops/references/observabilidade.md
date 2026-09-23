# Observabilidade

Perguntas que todo sistema em prod responde: está funcionando? está lento? está falhando?
onde? desde quando?

## 1. Mínimo (obrigatório em prod, recomendado em hom)

| Sinal | Como |
|---|---|
| Logs | stdout JSON com `timestamp, level, service, correlation_id, msg` → logs do EasyPanel |
| Erros | Sentry: api, worker e web, `environment=hom|prod`, `release=<tree>`, tag `correlation_id` |
| Health | api `/health/live/` e `/health/ready/`; web `/health`; worker `worker_health` |
| Uptime | monitor externo (UptimeRobot/BetterStack) em `/health/live/` da api e `/health` do web de prod |
| Backup | diário off-site com restore testado |

`correlation_id` (header `X-Request-ID`) atravessa app → api → task → provider. O app Expo
gera um por ação e mostra no erro, para o usuário conseguir reportar.

## 2. Alertas (só o que exige ação)

```text
uptime de prod falhou 2× seguidas
taxa de 5xx da api acima do limite (Sentry alert)
erro novo em release recém-promovida
disco > 80% (postgres, minio, backups)
backlog da fila crescendo por > 10 min / beat parado
backup diário não rodou
certificado a < 14 dias de expirar (se não renova sozinho)
```

Sem alerta por tudo: alerta ignorado vira ruído (alert fatigue).

## 3. Maduro (quando a operação pedir)

- Métricas: Prometheus (`django-prometheus`, exporter do Celery/Redis/Postgres), endpoint
  **interno**, nunca público.
- Dashboards Grafana por serviço: disponibilidade, latência, erro, recursos, fila.
- Logs centralizados: Loki. Tracing: só com sistema distribuído que justifique.
- SLO interno (disponibilidade, latência p95) antes de assinar SLA com cliente.

Golden signals: latência, tráfego, erros, saturação. Métricas: request rate, error rate,
latência, CPU, RAM, disco, conexões do banco, backlog/idade da fila, workers ativos.

## 4. Custos

Acompanhar mensalmente CPU/RAM/disco da VPS, storage, egress, providers (WhatsApp,
e-mail, IA). Salto inesperado = bug, loop, abuso ou ataque: investigar antes de pagar.
Custo de IA por tenant/caso de uso vem do `AIRun` (BE-04).

## 5. Retenção

Logs: 14–30 dias (hom 7). Sentry: plano. Backups: ver `backup-e-recuperacao.md`.
Logs nunca com senha, token, CPF completo ou dado de saúde (filtro do `common/logging.py`).
