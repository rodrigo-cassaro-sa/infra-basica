# Operação e observabilidade

Conteúdo: logs · correlation ID · métricas · backlog · Flower · observabilidade · deploy · worker · beat · health checks · graceful shutdown · segurança do broker · ambientes.

---

## Logs

Cada task relevante deve permitir descobrir:

- qual task executou;
- qual entidade processou;
- quando começou;
- quando terminou;
- quantidade de tentativas;
- erro;
- `correlation_id`.

Evitar logar payloads sensíveis completos.

## Correlation ID

Quando uma task nasce de uma requisição do app, o `correlation_id` (header `X-Request-ID` na API,
ContextVar `common.logging.correlation_id` no código) deve acompanhar. Implementação com
signals do Celery: `event-bus.md` §3.

```text
API → task → integração
```

Isso permite rastrear um fluxo completo, do toque no app até a chamada externa.

## Métricas

Monitorar pelo menos:

```text
tasks publicadas
tasks executadas
tasks concluídas
tasks falhas
retries
tempo de execução
fila acumulada
idade da mensagem mais antiga
workers disponíveis
```

Para filas críticas, backlog deve gerar alerta.

## Backlog

Fila crescendo continuamente significa:

```text
taxa de entrada  >  capacidade de processamento
```

Soluções possíveis: aumentar workers, otimizar a task, dividir a fila, reduzir trabalho, aumentar o lote, limitar o produtor.

Não resolver apenas aumentando hardware sem descobrir a causa.

## Flower

Ferramenta operacional útil, mas **não é fonte de auditoria** de processo de negócio. Estado importante fica persistido no domínio.

## Observabilidade

Integrar workers ao padrão operacional do projeto (Prometheus, Grafana, Loki).

Monitorar separadamente: `web`, `worker`, `beat`, `broker`, `banco`.

---

## Deploy

Containers típicos:

```text
web
worker-default
worker-integrations
worker-long
beat
redis
postgres
```

Não é obrigatório começar com todos. Projeto simples:

```text
web
worker
beat
redis
postgres
```

### Worker

```bash
celery -A config worker -l INFO
```

Por fila:

```bash
celery -A config worker \
  -l INFO \
  -Q integrations
```

Configuração de produção fica no ambiente/orquestrador, não em comando manual.

### Beat

```bash
celery -A config beat -l INFO
```

Com `django-celery-beat`, configurar o scheduler de banco apropriado. Garantir **uma única instância** responsável pelo mesmo schedule.

---

## Health checks

Separar saúde do web e dos workers. Sinais úteis:

```text
worker conectado ao broker
broker acessível
fila consumindo
heartbeat recente
beat ativo
```

Não considerar o backend saudável só porque `/health/` da API responde — o painel pode estar recebendo 200 em tudo enquanto nenhuma fila é consumida.

## Graceful shutdown

O deploy deve permitir que workers parem de forma controlada. Evitar encerrar processo abruptamente durante tarefas importantes quando o orquestrador permitir shutdown gracioso. Revisar o timeout do container/orquestrador para permitir finalização adequada.

---

## Segurança do broker

Redis usado como broker não deve ficar publicamente exposto. Usar rede privada, autenticação, firewall, TLS quando aplicável, credenciais via secrets/env e isolamento entre ambientes.

Nunca expor porta Redis diretamente à Internet sem necessidade e proteção apropriada.

## Ambientes separados

Não compartilhar fila entre `dev`, `homologação` e `produção`. Cada ambiente deve possuir broker/namespace isolado.

Uma task de desenvolvimento nunca deve ser consumida por worker de produção.
