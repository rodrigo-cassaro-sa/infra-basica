# ART-01 — Formatos de saída

## Modo PA-01 — visão geral do artefato

```markdown
# Análise do artefato — <nome>

## 1. Que sistema parece ser
<2–4 frases. Marcar o que é inferência.>

## 2. Formato e stack encontrada
- Formato: <ZIP | repositório | protótipo visual | ...>
- Frontend: ...
- Backend: ...
- Dados: ...
- Integrações: ...
- Stack oficial do projeto: Expo + Django + PostgreSQL → <divergências a tratar>

## 3. Módulos / capítulos possíveis
- <Capítulo> — <escopo em 1 linha>

## 4. Capacidades

### A-001 — <Verbo + objeto>
Título: <Verbo + objeto>
Capítulo sugerido: <capítulo>
Tipo: <FUNCIONAL | INFERIDA | MOCK | SIMULAÇÃO | TÉCNICA | VISUAL | PROTÓTIPO VISUAL>
Evidência:
- <arquivo/rota/componente>
Inferência:
- <ou "nenhuma">
Correspondência DAH: <NOVA | EQUIVALENTE H-xxx | PARCIAL H-xxx | MAIS AMPLA H-xxx | CONFLITANTE H-xxx | sem DAH para comparar>
Dúvidas:
- <pergunta>

## 5. Mocks e simulações
| Item | Classe | Onde |

## 6. Itens técnicos (não são histórias)
## 7. Itens visuais
## 8. Riscos e secrets (valores omitidos)
## 9. Conflitos (com DAH e internos)
## 10. Dúvidas gerais
## 11. Encaminhamentos
```

## Modo PA-02 — aprofundamento de uma A-xxx

```markdown
# HISTÓRIA DE ANÁLISE A-xxx — <Verbo + objeto>

Status: PROVISÓRIA (não é H-xxx)

## Evidências
- <arquivo:linha / rota / tela> — <o que mostra>

## Comportamento
Contexto aparente / objetivo aparente / atores.

## Fluxo
Pré-condições:
Fluxo observado: 1. ... 2. ...
Alternativos:
Exceções:

## Dados
Entidades e campos envolvidos; estados.

## Regras aparentes
Validações e limites observados.

## Permissões
Quem parece poder executar (evidência ou dúvida).

## Integrações

## Mocks

## Critérios observáveis
- Dado ..., quando ..., então ...

## Inferências
## Dúvidas
## Conflitos
```

Regras: cada item de Regras/Permissões/Critérios aponta para uma evidência ou vai para Inferências/Dúvidas. Nada sem origem.
