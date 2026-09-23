# Mapa de testes

## Índice

- [Documento e identificação](#documento-e-identificação)
- [Tipos de teste](#tipos-de-teste)
- [Estados de teste](#estados-de-teste)
- [Regra do mapa de testes](#regra-do-mapa-de-testes)
- [Rastreabilidade](#rastreabilidade)
- [Bloqueio por teste](#bloqueio-por-teste)

---

## Documento e identificação

`docs/mapa-de-testes.md` é consolidado para o sistema inteiro — não há um mapa
por história.

Identificação sequencial: `T-001`, `T-002`, `T-003`, ... Nunca reutilizar código.

## Tipos de teste

```text
Funcional · Integração · E2E · Usabilidade · Segurança · Performance
```

Somente os aplicáveis são obrigatórios — mas a não aplicabilidade é declarada,
não presumida.

## Estados de teste

```text
planejado · pendente · em execução · aprovado · falhou · bloqueado · não aplicável
```

## Regra do mapa de testes

```text
ANTES DO CÓDIGO  → definir o que precisa ser provado
DEPOIS DO CÓDIGO → executar e registrar evidência
```

Definir os testes depois de implementar tende a produzir testes que confirmam o
que o código faz, em vez de provar o que a história exigia.

## Rastreabilidade

```text
T-xxx → H-xxx → critério de aceite / regra
```

Exemplo:

```text
T-081
História: H-023
Tipo: Segurança
Cenário: acesso por outro tenant
Resultado esperado: acesso negado
```

## Bloqueio por teste

Uma história **não** pode atingir `pronta para homologação` quando houver teste
crítico `pendente`, `falhou` ou `bloqueado`, salvo decisão explícita registrada
que altere o requisito.

Cenários de segurança vêm da SEC-01 e entram no mapa como qualquer outro teste.
