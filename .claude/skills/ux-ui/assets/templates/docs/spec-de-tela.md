# Tela: [Nome da tela]

- **Rota**: `/…` · **História**: H-00X · **Regras**: RN-0X, RN-0Y
- **Quem usa / contexto**: [perfil, dispositivo, frequência]
- **Objetivo do usuário (1 frase)**: [ex.: encontrar um aluno e ver se a mensalidade está em dia]
- **Ação principal**: [verbo + objeto]

## Hierarquia
1. Onde estou: [título]
2. O que vejo: [conteúdo]
3. O que posso fazer: [ações]
4. Ação principal: [ ]

## Wireframe

Mobile (< 768):
```text
┌──────────────────────┐
│ Título          [＋] │
│ [Buscar …          ] │
│ [chip] [chip]        │
│ ┌──────────────────┐ │
│ │ Item             │ │
│ └──────────────────┘ │
├──────────────────────┤
│ tab · tab · tab      │
└──────────────────────┘
```

Desktop (≥ 1024):
```text
[sidebar] | Título                         [+ Ação principal]
          | Descrição
          | [Buscar …] [Filtros] [chips]
          | Tabela: Col ↑ | Col | Col | ⋮
```

## Componentes
| Área | Componente (existente?) | Observação |
|---|---|---|

## Estados (com texto real)
| Estado | O que aparece | Texto |
|---|---|---|
| Loading | skeleton da lista | — |
| Vazio | EmptyState | "Nenhum … · … · [Ação]" |
| Vazio por filtro | EmptyState | "Nenhum resultado para … [Limpar filtros]" |
| Erro | ErrorState | "Não foi possível carregar … [Tentar novamente]" |
| Sem rede (app) | OfflineState/banner | "Sem conexão. …" |
| Sem permissão | … | "Você não tem permissão para …" |
| Sucesso de ação | toast | "… salvo." |

## Interações
| Gatilho | Resultado | Feedback |
|---|---|---|
| Toque em item | abre detalhe | pressed |
| Excluir | diálogo "Excluir …?" / desfazer | toast |

## Responsividade
- Mobile: …  · Tablet: … · Desktop: …

## Acessibilidade
- Ordem de foco: título → busca → filtros → lista → ação
- Nomes acessíveis dos ícones: …
- Anúncios (live region): …

## Critérios de aceite de UX
- [ ] Checklist de QA da skill `ux-ui` completo
- [ ] …
