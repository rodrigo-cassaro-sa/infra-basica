# docs/mapa-de-testes.md

Documento oficial da QA-01. **Consolidado para o sistema inteiro** — nunca um arquivo por história.

Se não existir, crie a partir de `assets/mapa-de-testes-template.md`.

## Formato da linha

Cada teste registrado tem, quando aplicável:

```text
código T-xxx
história H-xxx
tipo
cenário
resultado esperado
status
evidência
```

| Código | História | Tipo | Cenário | Resultado esperado | Status |
|---|---|---|---|---|---|
| T-001 | H-001 | Funcional | Criar usuário válido | Usuário criado | aprovado |
| T-002 | H-001 | Usabilidade | Campo obrigatório vazio | Erro claro é apresentado | aprovado |
| T-003 | H-001 | Segurança | Acesso sem permissão | Acesso negado | aprovado |
| T-004 | H-001 | Integração | E-mail duplicado | Operação falha com erro de domínio | falhou |

## Valores de tipo

```text
Funcional
Unitário
Integração
API
Componente
Contrato
E2E
Permissão
Segurança
Usabilidade
Acessibilidade
Regressão
Performance
Smoke
Manual
```

## Valores de status

```text
pendente
em execução
aprovado
falhou
bloqueado
quarentena
não aplicável
```

`quarentena` só com pendência de correção registrada. `bloqueado` exige motivo na coluna de evidência.

## Numeração

- `T-xxx` é sequencial e **nunca reutilizado**, mesmo quando um teste é removido. Reaproveitar código quebra o histórico.
- Um `T-xxx` pode validar mais de um `AC`, e um `AC` pode exigir vários `T-xxx`.

## Rastreabilidade

A cadeia precisa ser navegável nos dois sentidos:

```text
H-001 → AC-01 → T-004 → arquivo/nome do teste
```

Formas aceitáveis de amarrar o teste ao código:

```python
def test_h001_rejects_duplicate_email():
    ...
```

```python
@pytest.mark.story("H-001")
def test_rejects_duplicate_email():
    ...
```

Ou simplesmente a coluna do mapa apontando o caminho do teste. Não é obrigatório codificar a história em todo nome — obrigatória é a relação ser identificável.

## Evidência

A pergunta que o mapa precisa responder:

```text
como sabemos que H-023 funciona?
```

Resposta aceitável aponta para: testes que cobrem cada AC, resultado da última execução, e comportamentos validados. Resposta inaceitável: "o código foi revisado" ou "rodou na minha máquina".

Para teste manual, a evidência mínima é: passos executados, resultado observado, data e quem executou.

## Quando atualizar

```text
[ ] ao receber uma história nova (registra cenários como pendente)
[ ] ao implementar testes (muda para aprovado/falhou com o resultado real)
[ ] ao encontrar bug (registra o teste de regressão)
[ ] ao remover funcionalidade (marca os T-xxx como removidos, sem reutilizar o código)
```

O mapa só reflete execução real. Status `aprovado` sem execução é falsificação de evidência — e é exatamente o que a DAH-01 vai usar para fechar a história.
