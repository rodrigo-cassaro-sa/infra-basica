# Tarefas periódicas e agendamento

Conteúdo: Celery Beat · uma única instância por agenda · `django-celery-beat` · timezone · `countdown`/`eta` · agendamentos de negócio persistidos.

---

## Celery Beat

Usar para tarefas recorrentes: todo dia às 03:00, a cada 15 minutos, toda segunda-feira, todo primeiro dia do mês.

```text
Celery Beat → Broker → Worker
```

## Apenas um scheduler por agenda

Para a mesma agenda deve existir **uma única instância ativa** do scheduler responsável.

```text
Beat A + Beat B → mesma tarefa publicada duas vezes
```

No deploy, garantir apenas uma instância de Celery Beat para aquele schedule. Isso não é negociável: duas réplicas do container de beat duplicam toda a agenda silenciosamente.

## `django-celery-beat`

Usar quando as tarefas periódicas precisarem de administração dinâmica:

- agenda armazenada no banco;
- gerenciamento pelo Django Admin;
- alteração sem novo deploy.

Adequado quando administradores precisam configurar horário, frequência, ativação e desativação — o caso comum quando existe um painel web operado pelo cliente.

Se a agenda é fixa e faz parte do código, configuração em código é suficiente.

## Horário e timezone

Padronizar timezone.

```python
USE_TZ = True
```

Celery deve usar configuração coerente com o projeto (`CELERY_TIMEZONE = TIME_ZONE`).

Sempre revisar tarefas periódicas quando houver horário de verão, alteração de timezone ou usuários em múltiplas regiões.

---

## `countdown` e `eta`

Úteis para atrasos relativamente curtos.

```python
task.apply_async(
    args=[id],
    countdown=60,
)
```

Não usar milhares de tarefas com `eta` muito distante como substituto de scheduler persistente. Para horas/dias/meses, preferir modelo de agendamento + Beat/dispatcher quando a escala justificar.

## Agendamentos de negócio

"Enviar cobrança em 30 dias" **não** significa task com countdown de 30 dias — uma mensagem parada no broker por um mês é invisível, não auditável e some se o broker for limpo.

Preferir:

```text
ScheduledAction
├── execute_at
├── status
└── payload/referência
```

Um dispatcher periódico busca as ações vencidas e publica os trabalhos executáveis. O estado fica persistente no banco, visível no painel e corrigível por um operador.
