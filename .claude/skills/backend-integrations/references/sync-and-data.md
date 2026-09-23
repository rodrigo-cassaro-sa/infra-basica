# Sincronização e dados

Índice: Schemas · Mapeamento · Campos desconhecidos · Versionamento de API · Paginação · Importação e checkpoint · Incremental vs full · Fonte da verdade · Conflito · External ID · Sync status · Reconciliação · Tipos de dado · Arquivos · Multi-provider

---

## Schemas de resposta externa

Crie schema interno para toda resposta externa relevante. Dicionário arbitrário vindo da internet não é contrato.

```python
from pydantic import BaseModel


class ExternalCustomer(BaseModel):
    id: str
    name: str
    email: str | None = None
```

O schema documenta o que a gente realmente usa e falha cedo quando o provider muda.

## Mapeamento

Modelo externo e modelo interno nunca se misturam:

```text
first_name_external → adapter → Customer.first_name
```

O adapter é o único lugar da transformação. Ele recebe estrutura clara e devolve estrutura clara — não sai buscando dezenas de models internamente.

## Campos desconhecidos

Providers evoluem. Defina a política por criticidade:

```text
ignorar campos novos        (padrão para leitura tolerante)
falhar em breaking change   (campo obrigatório sumiu)
registrar schema mismatch   (log/métrica para descobrir antes do incidente)
```

## Versionamento da API externa

Fixe a versão quando o provider suportar (`Stripe-Version`, `API-Version`, `/v1/`). Depender de versão implícita significa acordar com comportamento diferente sem deploy.

Fluxo de upgrade:

```text
ler changelog → testar em sandbox → atualizar adapter
→ rodar contract tests → homologar → produção
```

Mudança grande pode justificar `StripeAdapterV1` e `StripeAdapterV2` convivendo, com depreciação planejada e data para remover a versão antiga.

---

## Paginação

Não assuma `page/size`. Tipos comuns:

```text
page/offset · cursor · token · next URL
```

Com cursor, siga exatamente o cursor devolvido. Reconstruir cursor manualmente quebra na primeira mudança do provider.

## Importação completa

```text
fetch page → process → persist checkpoint → next page
```

Nunca carregue tudo em memória. Um milhão de registros não cabe num `list()`.

### Checkpoint

Sincronização longa persiste onde parou:

```text
last_cursor · last_external_id · last_updated_at · last_page
```

Sem checkpoint, qualquer falha na página 4.700 reinicia do zero — e na prática a importação nunca termina.

## Incremental versus full

Quando o provider permitir, prefira incremental: `updated_since`, cursor, change token ou webhook.

Ainda assim, integração crítica costuma precisar de reconciliação periódica:

```text
incremental diário + full reconciliation mensal
```

O incremental é rápido; o full detecta o que o incremental perdeu.

---

## Fonte da verdade

Decida explicitamente, por entidade e por campo quando necessário:

```text
nosso sistema é a fonte?
o provider é a fonte?
bidirecional?
```

Sem essa definição, sincronização vira conflito e ninguém sabe qual valor é o certo.

### Unidirecional

Mais simples: `A → B`. Defina quem cria, quem altera e quem exclui.

### Bidirecional

Exige política de conflito explícita:

```text
last write wins · master por campo · version number · timestamp · revisão manual
```

Nunca deixe implícito. "Last write wins" escolhido por omissão é perda de dado silenciosa.

## External ID

Guarde o identificador externo sempre que existir:

```text
(provider, external_id) UNIQUE
```

Para integração complexa ou multi-provider, use tabela de mapeamento em vez de poluir o model de domínio:

```text
ExternalMapping
├── provider
├── entity_type
├── internal_id
├── external_id
└── last_synced_at
```

`Customer.stripe_customer_id` é aceitável num sistema com um gateway só e sem previsão de mudar. Deixa de ser quando aparece o segundo provider.

## Sync status e consistência eventual

Integração assíncrona significa que o nosso banco e o provider divergem por segundos ou minutos. Isso é normal e precisa ser **representado**, não escondido:

```text
pending · synced · failed · outdated
```

Campos úteis: `last_synced_at`, `last_sync_error`, `external_updated_at`.

O app Expo consome esses campos para mostrar o estado real ao usuário.

## Reconciliação e reprocessamento

Para integração crítica, rode rotina que compara local ↔ externo e aponta divergência. Não dependa só de chamadas em tempo real.

Reprocessamento de sync falho:

```text
failed → corrigir causa → retry manual
```

O reprocessamento tem que ser seguro e idempotente — rodar duas vezes não pode duplicar nada.

---

## Tipos de dado na borda

**Datas**: padronize timezone, ISO 8601 e UTC na borda. Converta para tipo interno imediatamente; não deixe string de data circular pelo domínio.

**Dinheiro**: nunca converta para `float`. Use `Decimal` internamente e o formato do provider (frequentemente inteiro em centavos) com precisão conhecida na borda.

**Enums**: providers usam `PAID`, `paid`, `1`, `SUCCESS` para a mesma coisa. Mapeie explicitamente para o enum interno. E tenha política para valor desconhecido — `IntegrationInvalidResponse` ou um `UNKNOWN` tratado — porque a lista de status do provider vai crescer sem avisar.

**Normalização**: telefone, e-mail, CPF/CNPJ, datas, moeda e country code são normalizados na borda, não espalhados pelo domínio.

**Validação**: mesmo que o provider valide e-mail ou CPF, o domínio mantém as próprias regras. Dado lido de integração também pode estar errado — valide antes de persistir.

---

## Arquivos

- valide tamanho e MIME antes de processar;
- use streaming; não carregue arquivo grande inteiro na RAM;
- armazene em S3/MinIO, não no banco;
- nunca baixe URL arbitrária sem controles (ver `auth-and-security.md`, SSRF).

CSV e planilhas de terceiros: valide cabeçalho, trate encoding, processe em lote com checkpoint e reporte erro por linha em vez de abortar o arquivo inteiro.

---

## Multi-provider

Quando a mesma capacidade tem mais de um provider (e-mail, pagamento, SMS):

```text
EmailGateway
├── ResendAdapter
└── SESAdapter
```

O roteamento entre eles é decisão de configuração ou de service — nunca fica dentro do adapter. Registre qual provider atendeu cada operação, para auditoria e conciliação.
