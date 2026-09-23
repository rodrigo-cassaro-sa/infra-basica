# Setup e configuração

Conteúdo: stack padrão · Redis vs RabbitMQ · estrutura do projeto · `config/celery.py` · configuração por ambiente · serialização · `async/await` vs Celery.

---

## `async/await` não é Celery

```text
async/await   →  concorrência de I/O dentro de uma execução
Celery        →  trabalho fora do processo da requisição
```

```text
requisição HTTP → Django → publica mensagem → responde ao cliente

                                  Worker Celery → executa depois
```

Confundir os dois leva a "tornar a view async" achando que resolveu o problema de uma integração de 40 segundos. Não resolve: a requisição continua presa.

---

## Stack padrão

```text
Django
Celery
Redis
PostgreSQL
```

Adicionar apenas quando houver necessidade: `django-celery-beat`, Flower, RabbitMQ.

Redis cumpre dois papéis no padrão inicial: broker do Celery e infraestrutura de fila. O **result backend só deve ser habilitado quando houver necessidade real** de consultar resultados de task — se o painel acompanha progresso, isso vem de um model de job, não do result backend.

---

## Redis ou RabbitMQ

**Redis é o broker padrão da software house.** Já faz parte da infraestrutura, tem configuração simples, atende a maioria dos sistemas e reduz a quantidade de tecnologias que a casa precisa operar.

Avaliar RabbitMQ apenas quando houver necessidade de topologia de mensageria sofisticada, roteamento AMQP avançado, requisitos específicos de broker, grande complexidade de filas ou políticas de mensageria que justifiquem infraestrutura dedicada — incluindo dead-letter routing avançado.

Não adicionar RabbitMQ antecipadamente.

---

## Estrutura do projeto

```text
backend/
├── config/
│   ├── celery.py
│   └── settings/
│       └── base.py
│
├── apps/
│   ├── sales/
│   │   ├── services.py
│   │   ├── selectors.py
│   │   └── tasks.py
│   │
│   ├── notifications/
│   │   ├── services.py
│   │   └── tasks.py
│   │
│   └── integrations/
│       └── tasks.py
│
└── tests/
```

Cada domínio mantém suas próprias tasks, ao lado do service que elas executam.

---

## `config/celery.py`

```python
import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings.production",
)

app = Celery("backend")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks()
```

`config/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

---

## Configuração via ambiente

```python
CELERY_BROKER_URL = env("CELERY_BROKER_URL")

CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
```

```text
CELERY_BROKER_URL=redis://redis:6379/0
```

Nunca fixar credenciais reais no código.

---

## Serialização

JSON é o padrão.

```python
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
```

Evitar serializers capazes de executar objetos arbitrários (pickle) sem necessidade excepcional e revisão de segurança — uma mensagem forjada no broker vira execução de código.
