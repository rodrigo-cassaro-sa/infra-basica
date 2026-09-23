# Checklists BE-05

Use antes de abrir PR e antes de subir integração para produção.

---

## Nova integração

```text
[ ] objetivo definido
[ ] fonte da verdade definida
[ ] síncrono ou assíncrono definido
[ ] client isolado
[ ] adapter isolado
[ ] interface interna definida
[ ] base URL configurável
[ ] credenciais seguras (fora do Git)
[ ] timeout definido
[ ] retry na camada certa (task por padrão; client só em request síncrona + idempotente)
[ ] backoff/jitter avaliados
[ ] idempotência avaliada
[ ] rate limit conhecido
[ ] paginação conhecida
[ ] schemas validados
[ ] erros traduzidos para IntegrationError
[ ] logs definidos (sem segredo)
[ ] métricas definidas
[ ] contract tests criados
[ ] sandbox configurado
[ ] feature flag / mecanismo de disable
[ ] segurança revisada
```

## Webhook recebido

```text
[ ] assinatura validada
[ ] raw body preservado quando necessário
[ ] timestamp/replay avaliado
[ ] schema validado
[ ] external event ID persistido com unicidade
[ ] idempotência garantida
[ ] resposta rápida (sem trabalho pesado antes do 200)
[ ] processamento assíncrono quando necessário
[ ] ordem dos eventos considerada
[ ] logs
[ ] reprocessamento possível
[ ] reconciliação avaliada
```

## Webhook enviado

```text
[ ] evento persistido antes do envio
[ ] assinatura HMAC
[ ] timeout
[ ] retry
[ ] backoff
[ ] limite de tentativas
[ ] status persistido
[ ] alertas
[ ] endpoint morto tratado
[ ] verificação documentada para o consumidor
```

## Sincronização

```text
[ ] full ou incremental?
[ ] checkpoint
[ ] paginação
[ ] batching
[ ] source of truth
[ ] política de conflito
[ ] external ID
[ ] idempotência
[ ] status de sync exposto
[ ] reprocessamento
[ ] reconciliação
```

## Segurança

```text
[ ] TLS validado
[ ] secrets fora do código
[ ] tokens não aparecem em logs
[ ] scopes mínimos
[ ] URLs controladas
[ ] SSRF mitigado
[ ] payload limitado
[ ] arquivos validados
[ ] PII minimizada
[ ] webhooks autenticados
[ ] certificados monitorados
[ ] credenciais separadas por ambiente
```

## Operação

```text
[ ] métricas
[ ] logs
[ ] dashboards
[ ] alertas
[ ] runbook
[ ] last successful sync visível
[ ] retry visibility
[ ] backlog visibility
[ ] token/cert expiry monitorado
[ ] feature flag
[ ] mecanismo de disable
```

## Painel web (backend desacoplado)

```text
[ ] app Expo não fala com o provider diretamente
[ ] nenhum segredo de terceiro exposto na API
[ ] sync_status / last_synced_at / last_sync_error expostos onde fazem sentido
[ ] erros externos traduzidos para o contrato da nossa API
[ ] ações operacionais (reprocessar, desabilitar) expostas como endpoint com permissão
[ ] endpoint de webhook fora do fluxo de autenticação do app (assinatura, não JWT)
[ ] estados de consistência eventual representáveis na interface
```

---

## Definition of Done — BE-05

Uma integração está pronta quando:

1. o domínio não conhece detalhes do provider;
2. existe client/adapter isolado;
3. configuração está fora do código;
4. segredos estão protegidos;
5. timeout está definido;
6. retries são limitados e conscientes;
7. idempotência foi avaliada;
8. rate limit foi considerado;
9. respostas externas são validadas;
10. erros externos são traduzidos;
11. source of truth está definido;
12. sincronização possui checkpoint quando necessário;
13. webhooks possuem assinatura e deduplicação;
14. processamento pesado usa BE-03;
15. logs não expõem segredos;
16. métricas permitem detectar falhas;
17. contract tests existem para integração crítica;
18. sandbox/homologação foi utilizada;
19. segurança de rede/URLs foi revisada;
20. operação possui runbook quando crítica;
21. o app Expo consegue representar o estado da integração sem acessar o provider.

---

## Arquitetura padrão final

```text
                         DOMÍNIO
                            │
                            ▼
                         SERVICE
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
          Integration Interface     PostgreSQL
                 │
                 ▼
               Adapter
                 │
                 ▼
               Client
                 │
                 ▼
        Sistema / Provider Externo
                 │
        ┌────────┴────────┐
        ▼                 ▼
     Response          Webhook
        │                 │
        ▼                 ▼
     Adapter         Webhook Handler
        │                 │
        └────────┬────────┘
                 ▼
              Service
                 │
          ┌──────┴──────┐
          ▼             ▼
     PostgreSQL       Celery
                        │
                        ▼
                      Worker
```
