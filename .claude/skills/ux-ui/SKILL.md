---
name: ux-ui
description: >-
  Padrão da casa de UX/UI para Web, Android e iOS: design system (tokens), componentes e
  estados, formulários, feedback (loading/vazio/erro/offline), navegação, responsividade,
  acessibilidade (WCAG 2.2 AA / NBR 17225, leitor de tela, fonte ampliada), microcopy pt-BR,
  i18n (multi-idioma, plurais, data/moeda/fuso com Intl) e convenções de plataforma. Use
  SEMPRE que for planejar, desenhar, gerar ou revisar tela, fluxo ou componente — "faz a
  tela de...", "layout", "design system", "tema", "dark mode", "responsivo",
  "acessibilidade", "TalkBack", "VoiceOver", "tradução", "multi-idioma", "i18n",
  "formulário", "dashboard", "estado vazio", "mensagem de erro", "revisa a UX", "modal",
  "navegação", "guia visual", "padrões de interface a partir das histórias" — mesmo sem
  dizer "UX". Trabalha com a skill de código expo-app (única
  stack de frontend da casa): esta decide comportamento e aparência; aquela, a arquitetura. Complementa frontend-web. Não use para backend ou infraestrutura.
---

# UX/UI — padrão da casa

**Um produto. Um design system. Uma experiência coerente. Interfaces diferentes quando a
plataforma pede.** Web, Android e iOS não precisam ser idênticos — o usuário precisa
reconhecer que está no mesmo produto, e cada plataforma precisa se comportar como ele espera.

Ordem de valores — nunca inverta:
**clara → previsível → consistente → rápida → acessível → bonita.**
Se o usuário precisa descobrir por tentativa e erro como usar algo básico, o design falhou.

## Como esta skill conversa com as outras

| Skill | Responsável por | Relação com esta |
|---|---|---|
| `expo-app` | Código de app (Android/iOS/Web via Expo) | Esta define a tela; aquela define pastas, `Screen`, `theme.ts`, `components/feedback`, Query. Rode as duas juntas. |
| `frontend-web` | Identidade visual (paleta, tipografia, tom estético) | Esta garante o piso de usabilidade; aquela dá personalidade **dentro** dos tokens. |

Regras de convivência (detalhes e tabela de nomes em `references/implementacao-por-stack.md`):

1. **Código segue a skill de stack; experiência segue esta.** Nunca crie pasta, lib ou
   padrão de estado aqui — use o que a skill de stack manda. Aqui se decide o que a tela
   mostra, em que ordem, com quais estados, textos e comportamentos.
2. **A identidade do projeto é a fonte da verdade visual.** `docs/guia-visual.md` (decisões)
   → `tokens/tokens.json` (valores) → `tokens.ts`/`tokens.css` gerados por
   `scripts/build-tokens.py --check`. Cada app muda marca, fonte, raio, tema padrão; ninguém
   muda as regras inegociáveis, os papéis semânticos nem os componentes base
   (`implementacao-por-stack.md` §7).
3. **Produto x marketing.** Em sistema, app, painel, CRM, dashboard: esta skill manda
   (previsível antes de criativa). Em landing page, site institucional, peça de marca:
   `frontend-web` lidera a estética, e esta vira o piso (contraste, foco, alvo de toque,
   responsivo, movimento reduzido, microcopy).

## Fonte da verdade (em caso de conflito)

```text
Regra de negócio  →  História aprovada / spec  →  docs/stack.md + docs/guia-visual.md (design system do projeto)
→  esta skill  →  docs/mapa-de-telas.md  →  implementação
```

Designer, frontend e IA **não inventam regra funcional**. Se a história não diz se o
usuário pode excluir, pergunte — não decida pela UI.

## Passo 0 — Situar (sempre, antes de desenhar ou gerar tela)

Leia o que existir; pergunte só o que faltar:

1. `docs/stack.md`, `AGENTS.md`, `CLAUDE.md` → stack e convenções (valem acima desta skill).
2. `docs/guia-visual.md` + `tokens/tokens.json` → design system do projeto.
   Não existe? **Proponha criar** a partir de `assets/templates/docs/guia-visual.md` e
   `assets/tokens/tokens.json` antes de gerar várias telas — é o que mantém a IA
   consistente entre sessões e dá a cara de cada software.
3. História / regras (RN-xx) / `mapa-de-telas.md` / specs do Spec Kit da tela em questão.
4. Plataforma-alvo: Web, Android, iOS, tablet? Uso em campo (mobile-first) ou escritório
   (desktop-first)?
5. Quem usa, com que frequência, em que contexto (uma mão, em movimento, tela grande).

## Fluxo para criar uma tela

Não comece por cor ou sombra. Na ordem:

1. **Objetivo do usuário** — o que ele quer concluir nesta tela (uma frase).
2. **Fluxo** — entrada → ação → validação → resultado → próximo passo; mais cancelamento,
   erro, interrupção e retorno.
3. **Hierarquia** — onde estou · o que estou vendo · o que posso fazer · qual a ação principal.
4. **Componentes existentes** — reutilize ou evolua (80–100% atende = reutiliza). Nunca
   crie `BotaoSalvar` ao lado de `Button`.
5. **Layout** — estrutura previsível (PageHeader → filtros → conteúdo; ver `navegacao-e-layout.md`).
6. **Estados** — loading, vazio, erro, sucesso, offline, desabilitado, sem permissão.
7. **Responsividade** — reorganizar, não encolher (mobile, tablet, desktop, wide).
8. **Acessibilidade** — semântica, rótulos, foco, contraste, alvo de toque, texto ampliado,
   card agrupado, alternativa a gesto (`acessibilidade.md`).
9. **Microcopy e idioma** — verbos específicos, erros humanos, vocabulário oficial; se o
   projeto é multi-idioma, textos via `t()` e formatação via `Intl` (`i18n.md`).
10. **Implementar** com a skill de stack → **testar** com o checklist de QA abaixo.

## Regras inegociáveis

O porquê está entre parênteses — use-o para julgar o que as regras não cobrem.

1. **Uma ação principal por tela**, visualmente dominante. (Cinco botões primários = nenhum.)
2. **Nada de valor visual solto.** Cor, espaço, raio, fonte, sombra e duração vêm de token
   semântico (`colors.primary`, não `#3478F6`). (Trocar a marca não pode exigir caçar 300 arquivos.)
3. **Cor nunca é o único portador de significado.** Sempre texto e/ou ícone junto: `⚠ Atrasado`.
   (Daltonismo, sol na tela, leitor de tela.)
4. **Contraste WCAG 2.2 AA:** texto 4,5:1; texto grande e componentes/ícones essenciais 3:1.
5. **Todo input tem label visível.** Placeholder é exemplo, não rótulo. (Some ao digitar.)
6. **Toda ação importante dá feedback** imediato (pressionado/“Salvando…”) e final
   (sucesso ou erro com saída). O usuário nunca pensa "será que foi?".
7. **Toda tela assíncrona trata os estados**: loading, vazio (que ensina o próximo passo),
   erro (o que houve + o que fazer + botão), sucesso e, em app, sem rede.
8. **Erro nunca apaga o que o usuário digitou** e nunca mostra código técnico (500, FK, stack).
9. **Destrutivo é protegido:** confirmação específica ("Excluir 27 usuários?") ou desfazer.
   Não confirme o que é trivial ("Tem certeza que deseja salvar?").
10. **Alvo de toque:** ≥ 44×44 pt (iOS) e ≥ 48×48 dp (Android) — em código cross-platform,
    use **48** como área mínima (ícone pode ser 24, a área não). Web: ≥ 24×24 px (WCAG 2.5.8),
    preferir 44.
11. **Foco visível sempre.** Nunca `outline: none` sem substituto equivalente.
12. **Nada importante só no hover ou só em gesto.** Hover não existe no toque; gesto precisa
    de alternativa visível (menu ⋮).
13. **Safe area e teclado virtual** respeitados em toda tela de app (Android 16 é
    edge-to-edge obrigatório — não há mais opt-out).
14. **Responsivo = reorganizar.** Tabela desktop vira lista/cards no celular; nunca "desktop espremido".
15. **Movimento com propósito** (transição, continuidade, feedback) e respeitando "reduzir movimento".
16. **Mesmo nome para a mesma coisa** no produto inteiro (vocabulário oficial no `guia-visual.md`).
17. **Esconder botão é UX, não segurança.** Permissão é validada no backend sempre.
18. **Convenção antes de invenção.** ← voltar, × fechar, ⋮ mais opções, 🔍 buscar. Não
    recrie componente nativo sem motivo.

## Regra de plataforma

```text
Web     = esta skill + design system + regras Web          (plataformas.md §Web)
Android = esta skill + design system + regras App + Android (plataformas.md §App/§Android)
iOS     = esta skill + design system + regras App + iOS     (plataformas.md §App/§iOS)
```

**Compartilhe** entre plataformas: marca, tokens, hierarquia, conteúdo, termos, fluxos,
regras, estados, mensagens. **Adapte** por plataforma: navegação, controles, gestos,
diálogos, permissões, densidade. Antes de criar diferença entre Web e App, pergunte:
*é exigência da plataforma ou só inconsistência?*

## Mapa de referências — leia só o necessário

| Quando | Leia |
|---|---|
| Tokens, cores, tipografia, espaçamento, raio, sombra, ícones, dark mode, DTCG | `references/design-system.md` |
| Botões, inputs, formulários, validação, modais, toasts, tooltips, cards, tabelas, badges | `references/componentes.md` |
| Feedback, loading, vazio, erro, offline, confirmação, undo, optimistic UI, performance percebida | `references/estados-e-feedback.md` |
| Navegação Web/Mobile, busca, filtros, paginação, dashboards, KPIs, gráficos, responsividade, breakpoints, layouts de página | `references/navegacao-e-layout.md` |
| Diferenças Web × App × Android × iOS (hover, teclado, safe area, edge-to-edge, Liquid Glass, gestos, haptics) | `references/plataformas.md` |
| WCAG 2.2 AA, NBR 17225/LBI, leitores de tela, foco, zoom, movimento, código acessível por stack | `references/acessibilidade.md` |
| Textos da interface, erros, verbos, datas/números pt-BR, notificações, permissões, vocabulário | `references/conteudo-e-microcopy.md` |
| Multi-idioma, i18next, chaves tipadas, plurais, datas/moeda/fuso com Intl, validação traduzida, layout que aguenta tradução | `references/i18n.md` |
| Como cada regra vira código na expo-app (app e Web); nomes de tokens e componentes; pipeline de identidade por projeto | `references/implementacao-por-stack.md` |
| Gerar ou atualizar o `guia-visual.md` a partir das Histórias: IDs GV-*, reutilizar × criar, pendências de marca, conflitos | `references/guia-a-partir-de-historias.md` |

Templates em `assets/templates/docs/` (`guia-visual.md`, `spec-de-tela.md`).
Tokens de partida em `assets/tokens/tokens.json` (formato DTCG 2025.10) e
`scripts/build-tokens.py` gera `tokens.css` (web) e `tokens.ts` (Expo/React Native) a partir dele.

## Formatos de entrega

**Especificar tela** (antes do código ou quando pedirem "desenha/planeja a tela"):
use `assets/templates/docs/spec-de-tela.md` — objetivo, hierarquia, wireframe ASCII por
breakpoint, componentes, estados com textos reais, a11y, microcopy e critérios de aceite.
Depois registre a tela no `docs/mapa-de-telas.md` (formato da skill `dah-documentacao`, citando os `GV-*`) e a rota no `docs/rotas.md` (skill `expo-app`).

**Gerar tela com código:** siga o formato de entrega da skill de stack (arquivos completos
com caminho). Esta skill entra garantindo estados, tokens, rótulos, textos e responsivo —
nada de pseudo-código nem placeholder "Lorem ipsum": use conteúdo real do domínio.

**Revisar UX/UI:** para cada problema → onde está, qual regra viola (número/seção),
impacto para o usuário e a correção concreta (texto, layout ou código). Ordem de
prioridade: bloqueio de tarefa > acessibilidade > perda de dados/erro sem saída >
feedback ausente > inconsistência > estética.

## Checklist de QA de tela (Definition of Done de UX)

```text
[ ] Título claro e ação principal evidente
[ ] Loading, vazio, erro, sucesso (e offline no app) implementados com texto real
[ ] Desabilitado e sem-permissão considerados
[ ] Feedback imediato no toque/clique; sem duplo envio
[ ] Ação destrutiva protegida (confirmação específica ou desfazer)
[ ] Erro preserva dados e diz como resolver
[ ] Só tokens — nenhuma cor/medida mágica
[ ] Contraste AA; significado nunca só por cor
[ ] Labels, roles e nomes acessíveis; ordem de foco lógica; foco visível
[ ] Funciona com teclado (web) e leitor de tela (TalkBack/VoiceOver)
[ ] Cards lidos como unidade; gestos com alternativa (menu ⋮ / ações acessíveis)
[ ] Modal/sheet isola o fundo e devolve o foco ao fechar
[ ] Texto ampliado (200% web / fonte grande do sistema) sem cortar nada
[ ] Alvos de toque ≥ 48 em app cross-platform (44pt iOS / 48dp Android); safe area e teclado virtual ok
[ ] Mobile, tablet e desktop conferidos (reorganiza, não espreme)
[ ] Suporta textos maiores (i18n, nomes longos) — testado com pseudo-idioma se multi-idioma
[ ] Datas, números e moeda via Intl; nenhum texto de UI fixo no código (se multi-idioma)
[ ] Termos consistentes com o vocabulário oficial
[ ] Movimento respeita "reduzir movimento"
```

## Regra mestre

Antes de adicionar qualquer elemento: **isso ajuda o usuário a entender, decidir ou agir?**
Se não, remova. Antes de criar um padrão novo: **já existe um padrão conhecido que resolve?**
Se existe, use. Quando dois problemas são iguais, mesma solução; quando são diferentes,
não force a mesma solução. Entre duas soluções equivalentes, a mais simples, convencional
e fácil de manter.
