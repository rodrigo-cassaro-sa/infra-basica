# Testes e desenvolvimento local

Conteúdo: o que testar na task vs no service · teste de publicação após commit · teste de retry · eager mode · ambiente local.

---

## O que testar

Não testar apenas `task.delay()`.

A maior parte da lógica está nos services e deve ter testes unitários próprios. Testar a task quando ela tiver comportamento próprio de: retry, roteamento, tratamento de exceção, publicação, atualização de estado.

## Teste de service

```python
def test_order_process(order):
    order_process(order_id=order.id)

    order.refresh_from_db()

    assert order.status == "processed"
```

Esse teste independe de Celery — que é justamente o objetivo da separação task/service.

## Teste de publicação após commit

Para fluxos críticos, testar que:

```text
sem commit → task não é publicada
com commit → task é publicada
```

Isso protege contra corridas entre transação e worker.

```python
def test_event_only_after_commit(django_capture_on_commit_callbacks, manager, order):
    with django_capture_on_commit_callbacks(execute=False) as callbacks:
        order_approve(actor=manager, order_id=order.pk)
    assert InMemoryEventBus.published == []          # ainda não commitou
    for cb in callbacks:
        cb()
    assert ("order.approved", {"order_id": order.pk}) in InMemoryEventBus.published
```

## Testar retry

Validar:

```text
TransientError   → retry
PermanentError   → não retry, job failed
DomainError      → não retry
```

```python
def test_sync_retries_on_transient(mocker):
    mocker.patch("apps.crm.tasks.customer_sync", side_effect=IntegrationTimeout("t"))
    with pytest.raises(Retry):
        customer_sync_task.apply(kwargs={"customer_id": 1}, throw=True)
```

Não fazer testes dependentes de espera real. Mockar a integração, não o domínio inteiro.

## Eager mode

Celery eager pode ser útil em testes locais. Porém:

```text
eager ≠ worker real
```

Manter também testes de integração para fluxos importantes quando necessário.

---

## Desenvolvimento local

Com Docker:

```text
django
celery-worker
celery-beat
redis
postgres
```

Isso aproxima o desenvolvimento do ambiente real. Em Windows, rodar o processo do Celery em Docker/WSL2.
