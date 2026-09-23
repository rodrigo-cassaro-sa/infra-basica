# Filas e workers

Conteúdo: filas · separação de workloads · roteamento · prioridade · rate limit · concorrência · pool · Windows · prefetch · memória.

---

## Filas

Começar simples. Padrão inicial: `default`.

Criar filas adicionais quando houver necessidade real:

```text
default
emails
integrations
long_running
high_priority
ai
```

## Separação de workloads

Não colocar tarefas muito diferentes no mesmo worker quando uma puder bloquear as outras.

```text
Worker A → tarefas rápidas
Worker B → integrações
Worker C → relatórios pesados
Worker D → IA
```

Isso permite dimensionar cada carga separadamente.

## Roteamento

Preferir roteamento configurável e central:

```python
CELERY_TASK_ROUTES = {
    "apps.notifications.tasks.*": {
        "queue": "emails",
    },
    "apps.integrations.tasks.*": {
        "queue": "integrations",
    },
}
```

Evitar espalhar nomes de filas em dezenas de chamadas `apply_async()` quando uma regra central resolve.

## Prioridade

Usar prioridade só quando existir necessidade de negócio:

```text
reset de senha  >  envio de newsletter
```

Não transformar todas as tarefas em "alta prioridade". Prioridade de broker não substitui filas dedicadas para workloads muito diferentes.

## Rate limit

Serve principalmente para proteger integrações externas.

```python
@shared_task(rate_limit="60/m")
def send_external_request_task(...):
    ...
```

Atenção: o rate limit do Celery é aplicado **por worker**. Para um limite global rígido, projetar a fila/worker de acordo (ex.: fila dedicada com um único worker).

---

## Concorrência

Não definir concorrência arbitrariamente. Considerar CPU disponível, RAM, tipo da task, latência externa, conexões de banco e limites de APIs externas.

Tasks CPU-bound e I/O-bound se comportam de forma diferente. Medir antes de aumentar workers.

## Pool padrão

Em Linux, `prefork` é a escolha segura para o padrão geral. Não trocar por `gevent`, `eventlet`, `threads` ou `solo` sem entender as limitações das bibliotecas utilizadas.

## Windows

Celery não tem suporte oficial a workers nativos em Windows nas versões modernas. Em máquinas Windows, rodar workers em Docker, WSL2 ou máquina/servidor Linux.

Não criar padrão de produção dependente de worker Celery nativo no Windows.

## Prefetch

Prefetch influencia a distribuição das tasks entre workers. Para cargas com tasks longas ou duração muito variada, avaliar `worker_prefetch_multiplier`.

Não alterar sem medir. Separar tasks longas em fila própria costuma ser mais claro do que ajustar prefetch.

## Consumo excessivo de memória

Celery pode reciclar processos após N tasks ou ao atingir limite de memória:

```text
worker_max_tasks_per_child
worker_max_memory_per_child
```

Usar como proteção operacional, não como substituto para corrigir vazamento de memória.
