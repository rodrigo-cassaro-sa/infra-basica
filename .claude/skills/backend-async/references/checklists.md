# Checklists, anti-patterns e Definition of Done

---

## Checklist de uma nova task

```text
[ ] precisa realmente ser assíncrona?
[ ] regra de negócio está no service?
[ ] argumentos são simples e pequenos?
[ ] nenhum segredo vai na mensagem?
[ ] publicação ocorre após commit quando necessário?
[ ] task é idempotente?
[ ] duplicidade foi considerada?
[ ] exceptions transitórias estão definidas?
[ ] retry tem limite?
[ ] backoff foi avaliado?
[ ] jitter foi avaliado?
[ ] integração possui timeout?
[ ] task possui time limit quando necessário?
[ ] fila correta foi escolhida?
[ ] rate limit foi avaliado?
[ ] resultado precisa ser armazenado?
[ ] logs são suficientes?
[ ] métricas são suficientes?
[ ] testes foram criados?
```

## Checklist de tarefa periódica

```text
[ ] periodicidade definida
[ ] timezone definido
[ ] apenas um scheduler ativo
[ ] execução duplicada é segura
[ ] task é idempotente
[ ] duração não ultrapassa intervalo sem controle
[ ] concorrência entre execuções foi considerada
[ ] falhas são observáveis
[ ] retries são adequados
```

## Checklist operacional

```text
[ ] broker isolado por ambiente
[ ] Redis não exposto publicamente
[ ] workers rodando
[ ] Beat rodando quando necessário
[ ] filas sendo consumidas
[ ] logs centralizados
[ ] métricas disponíveis
[ ] backlog monitorado
[ ] falhas monitoradas
[ ] retries monitorados
[ ] graceful shutdown configurado
[ ] limites de CPU/RAM revisados
```

---

## Anti-patterns

**Task como service** — evitar:

```python
@shared_task
def create_invoice(...):
    # valida cliente
    # calcula imposto
    # grava invoice
    # atualiza pedido
    # baixa saldo
    # envia e-mail
```

Preferir:

```python
@shared_task
def invoice_create_task(*, order_id):
    invoice_create(order_id=order_id)
```

**Task gigante** — evitar uma task de horas processando tudo quando o trabalho pode ser dividido. Preferir `Job → Chunk 1, Chunk 2, Chunk 3...` com progresso persistido.

**Retry de tudo** — `autoretry_for=(Exception,)` sem classificação. Usar a classificação única de `common/errors.py`: só `TransientError` gera retry automático; `PermanentError` e `DomainError` não.

**Fila como banco** — o broker não é fonte da verdade. Dados de negócio importantes ficam no PostgreSQL. A fila transporta trabalho; o banco mantém estado.

**Delay de meses** — `countdown = 2.592.000` como agenda de negócio. Persistir o agendamento no banco e usar scheduler/dispatcher.

**Polling agressivo** — task a cada poucos segundos só para descobrir se algo mudou, quando existe webhook, evento interno pode disparar, ou a consulta pode ser agrupada. Polling precisa de justificativa operacional.

---

## Convenção de nomes

Tasks: `<ação>_<entidade>_task`

```text
send_invoice_task
process_order_task
sync_customer_task
generate_report_task
```

Services:

```text
send_invoice
process_order
sync_customer
generate_report
```

Isso deixa a separação visível na leitura do código.

---

## Definition of Done — BE-03

Uma implementação assíncrona está pronta quando:

1. a necessidade de assíncrono está justificada;
2. regras de negócio permanecem nos services da BE-01;
3. tasks são pequenas e explícitas;
4. argumentos são simples e serializáveis;
5. tasks dependentes de transação são publicadas após commit;
6. idempotência foi tratada;
7. retries existem apenas para falhas adequadas;
8. retries possuem limites;
9. backoff/jitter foram considerados;
10. chamadas externas possuem timeout;
11. tarefas longas possuem limites quando apropriado;
12. filas estão separadas apenas quando necessário;
13. agendamentos persistentes não dependem de delays gigantes;
14. apenas um scheduler executa cada agenda;
15. falhas importantes ficam observáveis;
16. estado crítico de negócio não depende apenas do Celery;
17. workers possuem métricas e logs;
18. testes cobrem services e comportamento assíncrono relevante;
19. broker e workers estão isolados e protegidos;
20. o deploy suporta shutdown seguro.

---

## Resultado esperado

Ao abrir qualquer backend da software house, um desenvolvedor deve descobrir rapidamente:

```text
quais tarefas existem
qual service cada task executa
qual fila processa a task
quando existe retry
qual política de retry
qual timeout existe
como duplicidade é evitada
como tarefas são agendadas
onde o estado do job é persistido
como falhas são investigadas
como workers são monitorados
```

Esse é o propósito da **BE-03 — backend-async**.
