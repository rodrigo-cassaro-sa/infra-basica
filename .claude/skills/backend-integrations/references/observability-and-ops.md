# Observabilidade e operação

Índice: Métricas · Logs · Correlation ID · Payload logging · Tracing · Auditoria · Alertas · Painel operacional · Runbook · Admin · SLA externo · Eventos internos

---

## Métricas por integração

Meça, por provider e por operação:

```text
requests · sucesso · falha · timeout · retry · 429 · 5xx · latência · volume
```

A pergunta que essas métricas precisam responder às 3h da manhã: *a integração X está fora, está lenta, ou está sendo limitada?* São três incidentes diferentes com três respostas diferentes.

Métricas de negócio complementam: quantidade de itens sincronizados, backlog pendente, idade do item mais antigo na fila.

## Logs

Registre em toda chamada externa:

```text
provider · operação · status · duração · tentativa · correlation id · resultado
```

Nunca registre: `Authorization`, token, refresh token, chave, senha, assinatura.

Log de integração é o que transforma "o cliente diz que não recebeu" em resposta em dois minutos.

## Correlation ID

Propague o `correlation_id` da família (app → API → task → chamada externa). O `BaseHTTPClient` já envia `common.logging.correlation_id` no header `X-Request-ID` e guarde o ID que o provider devolver — é o que se cita ao abrir chamado com o suporte deles.

## Payload logging

Payload completo só quando a política de dados permitir e com mascaramento de PII. Em geral: logue metadados sempre, payload apenas em erro e com retenção curta.

## Tracing

Para fluxo distribuído (request → task → integração → webhook de retorno), tracing mostra onde o tempo foi gasto. Vale o investimento quando há mais de duas saltos assíncronos.

## Auditoria

Operação sensível (cobrança, estorno, envio de dado pessoal, alteração em sistema externo) registra: quem pediu, quando, para qual provider, com qual resultado e qual external ID.

---

## Alertas

Alerte sobre o que exige ação humana:

```text
taxa de erro acima do limiar
integração parada (nenhum sucesso em X minutos)
backlog crescendo
webhook falhando repetidamente
token/certificado perto de expirar
last successful sync antigo demais
```

Alerta que dispara toda semana e ninguém olha é ruído — ajuste o limiar ou remova.

## Painel operacional

Para integração crítica, dê visibilidade de: última sincronização bem-sucedida, erros recentes, backlog, tentativas em andamento e status do circuito/feature flag.

Isso é consumido pelo app Expo via API (BE-02), com permissão — não por acesso direto ao banco.

## Runbook

Integração crítica tem runbook escrito, com:

- o que essa integração faz e o que quebra se ela parar;
- como verificar se o provider está fora (status page, endpoint de diagnóstico);
- como reprocessar com segurança;
- como desabilitar temporariamente;
- quem é o contato do provider e qual o SLA contratado.

## Ferramenta administrativa

Para integração crítica, a operação precisa conseguir (com permissão apropriada):

```text
ver última sincronização · ver último erro · reprocessar · desabilitar
```

Sem isso, todo incidente vira deploy ou acesso manual ao banco.

Lembrete: o Admin não exibe segredo em texto puro.

## SLA externo

Conheça e registre o SLA do provider: disponibilidade prometida, latência típica, janela de manutenção e limite de rate. O nosso SLA não pode ser melhor que o da dependência — se for prometido, será quebrado.

---

## Eventos internos e signals

Integração pode reagir a evento interno, mas evite cadeia invisível de signals — ninguém consegue descobrir, seis meses depois, por que salvar um `Customer` dispara três chamadas externas.

Publicação explícita, sempre:

```text
service (core) → on_commit → dispatch("customer.created") → EVENT_HANDLERS → task → adapter
```

Sem Django signals para disparar integração (o core proíbe regra/efeito em signal). O mapa
evento → task em `settings.EVENT_HANDLERS` (BE-03) é o lugar único onde se descobre por que
salvar um `Customer` chama o CRM.
