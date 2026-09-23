# Decisões, diário de bordo e conflitos

## Índice

- [Mapa de decisões](#mapa-de-decisões)
- [Quando criar uma decisão](#quando-criar-uma-decisão)
- [Decisão pendente](#decisão-pendente)
- [Mudança de decisão](#mudança-de-decisão)
- [Diário de bordo](#diário-de-bordo)
- [Conflitos documentais](#conflitos-documentais)
- [Código x documentação](#código-x-documentação)

---

## Mapa de decisões

`docs/mapa-de-decisoes.md`, numeração `D-001`, `D-002`, ...

Status preferidos:

```text
proposta · ativa · substituída · cancelada
```

## Quando criar uma decisão

Criar quando a escolha:

- afeta várias histórias;
- muda arquitetura;
- muda tecnologia;
- altera persistência;
- altera segurança;
- muda contrato estrutural;
- altera comportamento do produto;
- altera infraestrutura;
- pode ser questionada futuramente.

O critério prático é: alguém daqui a três meses vai perguntar "por que isso foi
feito assim?". Se sim, registrar.

## Decisão pendente

Quando a escolha depende do humano:

```text
registrar como proposta
↓ apresentar contexto
↓ apresentar alternativas relevantes
↓ perguntar
↓ aguardar decisão
```

Não escolher silenciosamente.

## Mudança de decisão

Nunca apagar a decisão anterior:

```text
D-010
Status: substituída por D-031
```

Registrar motivo, consequência e histórias afetadas.

## Diário de bordo

`docs/diario-de-bordo.md` deve permitir responder: onde paramos? o que foi
concluído? o que falta? o que está bloqueado? qual decisão está pendente? qual é
o próximo passo?

**Registrar:** marcos, início/conclusão relevante, bloqueio, desbloqueio, decisão
relevante, mudança de escopo, resultado de validação, homologação, publicação,
incidente, rollback, próximo passo.

**Não registrar:** cada linha de código, cada comando, cada arquivo trivial,
narrativa excessiva. O diário não substitui o Git.

## Conflitos documentais

Detectar contradições entre:

```text
história × regra · história × API · história × dados · história × fluxo
história × tela · história × decisão · regra × dados · dados × API
fluxo × tela · guia visual × tela · decisão × implementação
índice × arquivo da história
```

Resolução:

```text
detectar → não escolher silenciosamente → identificar fontes
→ registrar decisão quando necessário → perguntar
→ atualizar documentos → continuar
```

## Código x documentação

Se o código contradiz a documentação, **não** assumir que o código está certo.
Analisar história aprovada, decisão vigente, documentos e testes — e corrigir o
elemento que estiver incorreto, que tanto pode ser o código quanto o documento.
