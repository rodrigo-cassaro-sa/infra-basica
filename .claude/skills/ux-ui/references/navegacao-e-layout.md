# Navegação, layout e responsividade

## Sumário
1. Perguntas da navegação
2. Web: header + sidebar, breadcrumb
3. Mobile: tabs, pilha, profundidade
4. Deep links e estado entre dispositivos
5. Busca, filtros, ordenação, paginação
6. Layouts de página (lista, detalhe, edição)
7. Dashboards, KPIs e gráficos
8. Densidade
9. Responsividade e breakpoints
10. Tablet, orientação e uso com uma mão
11. Internacionalização de layout

---

## 1. Perguntas da navegação

Toda tela responde: **onde estou? de onde vim? para onde posso ir?** Título de tela/página
sempre presente; item ativo destacado no menu; voltar leva ao nível anterior.

## 2. Web: header + sidebar

```text
┌──────────────────────────────────────────────┐
│ Header (busca global, notificações, conta)   │
├────────────┬─────────────────────────────────┤
│ Sidebar    │ PageHeader                      │
│            │ Filtros                         │
│            │ Conteúdo                        │
└────────────┴─────────────────────────────────┘
```

Ideal para ERP, CRM, painel administrativo. Sidebar organizada por **grupos funcionais**,
não pela ordem em que as telas foram feitas:

```text
Visão geral
Operação      Campanhas · Profissionais · Escalas
Financeiro    Faturamento · Pagamentos
Administração Usuários · Perfis · Permissões · Configurações
```

- Sidebar recolhível (só ícones com tooltip) em telas médias; vira drawer abaixo de `md`.
- Breadcrumb para hierarquia profunda (`Usuários > Rodrigo Silva > Permissões`), nunca
  substituindo a navegação principal.
- URL reflete o estado útil (filtros, aba, página) para compartilhar e voltar.

## 3. Mobile: tabs, pilha, profundidade

**Tab bar** (bottom navigation): 3 a 5 destinos principais e frequentes. Não transforme
cada tela em aba. Cada aba **guarda seu estado** (voltar à aba volta onde parou). Rótulo +
ícone sempre (ícone sozinho é ambíguo).

**Pilha** para hierarquia: `Lista → Detalhe → Edição`. Voltar retorna um nível.
Android: botão/gesto voltar do sistema deve funcionar em todo lugar (inclusive fechar
modal/sheet) e o Android 16 usa *predictive back* por padrão — não intercepte o voltar sem
necessidade. iOS: gesto de borda para voltar não pode ser bloqueado.

**Modal** para tarefa separada e curta (criar, filtrar); fecha com × / Cancelar.

Com Expo Router: tabs nativas (tab bar do sistema — no iOS 26 ganha Liquid Glass
automaticamente), `Stack` para pilha, rota `modal` para modais — ver `expo-app`
`references/navegacao.md`.

## 4. Deep links e estado entre dispositivos

- Recurso relevante tem endereço próprio: `/notificacoes/123`, `/alunos/45`. Link abre
  direto nele (após login, restaurar o destino), não "início → menu → procurar".
- Deep link inválido/sem permissão → estado 404/403 amigável com saída.
- Web e App mostram **o mesmo estado do produto**: alterou no web, o app reflete ao voltar
  ao foco. UI diferente, dado igual.

## 5. Busca, filtros, ordenação, paginação

**Busca**: diga o escopo — "Buscar alunos por nome, CPF ou telefone", não "Buscar…".
Debounce (~300ms), mostra o termo buscado no resultado, limpar com ×. Web: `Ctrl/Cmd+K`
para busca global em sistemas de uso intenso.

**Filtros**: aplicados ficam visíveis como chips removíveis + "Limpar filtros". O usuário
precisa entender por que algo não aparece. No mobile, filtros em sheet/tela com
"Aplicar (23 resultados)".

**Ordenação**: indique coluna e direção (`Nome ↑`, `Data ↓`). Nunca mude a ordem em silêncio.

**Paginação × infinite scroll**:
- Paginação numerada: quando o usuário localiza, compara ou volta a um ponto (tabelas admin).
- Carregar mais / infinite: exploração contínua (feed, lista no app).
- Mostre total quando útil ("1–20 de 348").

## 6. Layouts de página

**Lista (web)**:
```text
Usuários                                       [+ Novo usuário]
Gerencie quem pode acessar o sistema.
[Buscar usuários por nome ou e-mail]  [Filtros]  [Ativos ×]
─────────────────────────────────────────────────────────────
Nome ↑          Perfil           Status           
Rodrigo Silva   Administrador    ● Ativo          ⋮
```
Estrutura fixa: `PageHeader (título, descrição opcional, ação principal) → Filtros → Conteúdo`.

**Detalhe**:
```text
← Usuários
Rodrigo Silva                          [Editar] [⋮]
Administrador • Ativo
Informações
  Nome      Rodrigo Silva
  E-mail    rodrigo@empresa.com
```

**Edição**: modo claro, Salvar como ação principal, Cancelar volta sem salvar (avisa se
houver alteração não salva).

**App**: título na barra de navegação (ou grande no topo, estilo iOS), ação principal no
header (ícone/texto) ou botão fixo no rodapé para formulários; FAB só para a ação de criar
realmente dominante.

## 7. Dashboards, KPIs e gráficos

Dashboard **responde perguntas**, não coleciona gráficos: Quantas campanhas ativas? Alguma
atrasada? Quem não confirmou? O que exige atenção agora? O que é crítico vem primeiro.

**KPI**:
```text
Campanhas ativas
42
↑ 8% vs. mês anterior
```
Sempre período, unidade e referência. "↑ 8%" solto não diz nada. Seta + texto + cor
(nunca só verde/vermelho). Clicar no KPI leva à lista filtrada.

**Gráfico conforme a pergunta**:
| Pergunta | Gráfico |
|---|---|
| Evolução no tempo | linha |
| Comparar categorias | barras (horizontais se rótulos longos) |
| Composição | barras empilhadas / 100% |
| Distribuição | histograma |
| Um número vs. meta | número + barra de progresso |

Sem 3D. Pizza só com 2–4 fatias. Eixo começa em zero em barras. Rótulos diretos em vez de
legenda distante. Tabela alternativa ou resumo textual para leitor de tela.

**Prioridade operacional**: `Crítico · Urgente · Atenção · Normal` com rótulo e ícone
(`⚠ Atrasado`), não só fundo vermelho.

## 8. Densidade

Mesmo design system ≠ mesmo layout. Web admin aceita densidade maior (linhas de 40–48px,
body 14 em tabela). Mobile precisa de mais respiro e alvos de 48. Em sistemas de uso diário,
ofereça "Confortável / Compacto".

## 9. Responsividade e breakpoints

A interface **se reorganiza** — não só encolhe.

```text
Desktop:  [Nome] [CPF] [E-mail] [Telefone] [Status]
Mobile:   Nome · Status
          Telefone
          E-mail          (resto em "Ver detalhes")
```

Breakpoints de partida (referência, não lei — o conteúdo manda):

| Nome | Largura | Layout típico |
|---|---|---|
| xs | < 480 | 1 coluna, tab bar |
| sm | 480–767 | 1 coluna larga |
| md | 768–1023 | tablet: 2 colunas, lista \| detalhe, sidebar recolhida |
| lg | 1024–1439 | desktop: sidebar + conteúdo |
| xl | ≥ 1440 | conteúdo com `maxWidth`, colunas extras, não esticar texto |

Prioridade em tela pequena: 1) conteúdo principal 2) ação principal 3) informação essencial
4) ações secundárias (vão para "Mais opções", detalhe ou expansão).

Estratégia: **desktop-first** consciente para sistema corporativo complexo; **mobile-first**
para uso em campo. Em ambos, componentes construídos responsivos. Web: prefira container
queries/flex/grid a breakpoints por tela quando o componente muda pelo espaço que ele tem.
App (Expo): `useWindowDimensions()` + `breakpoints` do tema; `maxWidth` ~720 para
formulário/leitura em tela larga.

## 10. Tablet, orientação e uso com uma mão

- Tablet não é telefone gigante: use **split view** (lista | detalhe), sidebar, 2 colunas.
  Android 16 ignora travas de orientação/redimensionamento em telas grandes (≥ 600dp) para
  apps que miram API 36 — o layout **precisa** funcionar em paisagem e janela redimensionada.
- Portrait sempre; landscape quando fizer sentido (e não quebrar quando o sistema forçar).
- Ações frequentes na zona do polegar (metade inferior); não deixe todas as ações
  essenciais só no topo de telas longas.

## 11. Internacionalização de layout

Mesmo produto só em pt-BR: não assuma que "Salvar" terá 6 letras nem que o nome do aluno
cabe em 12 caracteres. Botões e badges crescem; textos quebram linha ou truncam com
reticências **e** o texto completo fica acessível (detalhe/tooltip/label). Teste com nome
longo ("Maria Aparecida dos Santos Albuquerque") e valores grandes (R$ 1.250.000,00).
