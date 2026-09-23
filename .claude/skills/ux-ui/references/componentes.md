# Componentes

## Sumário
1. Catálogo mínimo e regra de reutilização
2. Estados obrigatórios
3. Botões
4. Inputs
5. Formulários e validação
6. Modais, sheets e diálogos
7. Toasts, alerts e banners
8. Tooltips e popovers
9. Cards
10. Tabelas e listas
11. Badges e chips
12. Componentes de negócio

---

## 1. Catálogo mínimo e regra de reutilização

```text
Button · IconButton · Input · Textarea · Select · Checkbox · Radio · Switch
DatePicker · TimePicker · Search · Badge · Chip · Avatar · Tooltip · Popover
Dropdown/Menu · Modal/Dialog · BottomSheet · Toast · Alert · Card · Tabs
Accordion · Breadcrumb · Pagination · Table · List · Skeleton · Spinner
Progress · EmptyState · ErrorState · OfflineState
```

Antes de criar componente: procure o existente. Atende 80–100%? **Reutilize ou evolua
com variante/prop.** Um `Button` com variantes, nunca `BotaoSalvar`, `ButtonEnviar`,
`SubmitPrimary` cada um com cara própria. Onde cada um mora no código: ver
`implementacao-por-stack.md`.

## 2. Estados obrigatórios

Avalie para todo componente (nem todos se aplicam, mas todos são considerados):

```text
default · hover (web) · focus · pressed · selected · disabled · loading · error · empty · read-only
```

Pressed é obrigatório no toque: controle sem resposta visual parece quebrado.

## 3. Botões

| Variante | Uso | Regra |
|---|---|---|
| primary | a ação principal da tela | **uma** por área visível |
| secondary | importante, não principal (Cancelar, Exportar) | |
| tertiary / ghost | discreta (Ver detalhes, Limpar filtros) | parece link, mas é botão |
| destructive / danger | exclui, desativa, cancela algo com impacto | cor `error` + verbo explícito |
| icon | ação compacta | nome acessível obrigatório; área ≥ 44/48 |

- **Rótulo = verbo + objeto**: "Salvar usuário", "Enviar proposta". Evite "OK", "Confirmar",
  "Continuar" quando não fica claro o que acontece.
- **Loading** troca o rótulo ("Salvando…"), mantém a largura, bloqueia novo clique
  (sem duplo envio) e marca `busy` para leitor de tela.
- **Disabled**: explique o porquê quando não for óbvio (texto de ajuda perto, não só tooltip).
  Em formulário, prefira deixar enviar e mostrar os erros a travar o botão sem explicação.
- Ordem em par: web e iOS → [Cancelar] [Ação] (principal à direita); no app, botão de largura
  total no rodapé para a ação principal de formulário é bom para o polegar.

## 4. Inputs

- **Label visível sempre**; placeholder só como exemplo de formato (`000.000.000-00`).
- Texto de ajuda abaixo quando o formato não é óbvio; erro substitui/acompanha a ajuda.
- Estados: default · hover · focus · filled · disabled · read-only · error · success (raro).
- Erro humano e específico: "Digite um e-mail válido, como nome@empresa.com" — nunca "Erro 1042".
- Tipo de teclado/`inputMode` e `autocomplete` corretos (e-mail, telefone, número, URL, CPF,
  CEP, senha nova/atual, código OTP). Ver `plataformas.md` §App.
- Máscaras brasileiras (CPF, CNPJ, telefone, CEP, moeda) não podem impedir colar valor
  sem máscara.
- Campos de senha com "mostrar senha". Nunca bloquear colar (WCAG 3.3.8 — autenticação acessível).

## 5. Formulários e validação

**Estrutura**: principal → complementar → avançado. Não peça dado antes de precisar.
Uma coluna no celular; no desktop, duas colunas só para campos curtos relacionados
(Cidade | UF).

**Obrigatórios**: marque com `*` e legenda; se quase todos forem obrigatórios, diga "Todos
obrigatórios, exceto os marcados como opcionais" e marque só os opcionais.

**Validação no momento certo**:
- Validar ao sair do campo (blur), não a cada tecla enquanto o usuário ainda digita.
- Depois que um campo mostrou erro, revalide a cada mudança (para o erro sumir assim que
  corrigir).
- No envio: valide tudo, **leve o foco ao primeiro erro**, mostre resumo se o form for longo,
  e anuncie ao leitor de tela.
- Backend revalida sempre; erros do servidor voltam para o campo certo quando possível.

**Prevenção > correção**: desabilite datas inválidas no picker, limite formato, ofereça
seleção em vez de digitação livre quando o conjunto é fechado.

**Preservar dados**: falhou o envio, tudo continua preenchido. Formulário longo guarda
rascunho. Não peça de novo o que já foi informado no mesmo fluxo (WCAG 3.3.7 — entrada redundante).

**Defaults**: preencha quando for seguro, provável e fácil de mudar. Nunca escolha em
silêncio uma opção crítica (plano pago, permissão, envio a terceiros).

**Formulário longo** → etapas por contexto com progresso ("Etapa 2 de 5"), revisão antes de
enviar, voltar sem perder dados.

**Progressive disclosure**: básico visível, "Mostrar configurações avançadas" para o resto.

**Visualizar × editar**: quando editar é tarefa relevante, modo de edição claro (tela ou
estado próprio), com Salvar/Cancelar; não misture campos editáveis soltos numa tela de leitura.

## 6. Modais, sheets e diálogos

- **Diálogo** (alert): decisão curta — confirmar exclusão, escolher opção.
- **Modal**: tarefa curta e focada. Formulário enorme não vai em modal; vira tela.
- **Bottom sheet** (app): ações contextuais, filtros, seleção. Sempre com fechar explícito
  além do gesto.
- Nunca modal sobre modal.
- Web: foco vai para o modal ao abrir, fica preso nele, `Esc` fecha, foco volta ao gatilho
  ao fechar. Use `<dialog>` ou componente acessível equivalente.
- App: use o modal/sheet nativo da stack (rota modal do Expo Router, `@expo/ui` BottomSheet)
  — botão voltar do Android fecha o modal.

Diálogo destrutivo:
```text
Excluir usuário?
Rodrigo Silva perderá o acesso imediatamente. Esta ação não pode ser desfeita.
                                   [Cancelar] [Excluir]
```
O botão diz o verbo, não "Sim".

## 7. Toasts, alerts e banners

| Componente | Quando | Duração |
|---|---|---|
| Toast/snackbar | confirmação transitória ("Alterações salvas") | 4–6 s; com ação ("Desfazer") ≥ 6 s e pausa no hover/foco |
| Alert inline | erro/aviso ligado a uma área da tela | até resolver |
| Banner | estado global (sem conexão, manutenção, conta vencendo) | até resolver ou fechar |

Não use toast para algo que o usuário **precisa** ler ou decidir. Toast é anunciado ao leitor
de tela (`role="status"` / `accessibilityLiveRegion="polite"`); erro crítico usa `alert`/`assertive`.
No app, toast acima da tab bar e fora da área do teclado.

## 8. Tooltips e popovers

Tooltip: rótulo de ícone não óbvio, explicação curta. Nunca informação essencial só nele —
não existe hover no toque e ele some. Web: aparece também no foco de teclado. Popover:
conteúdo interativo pequeno (ajuda com link, mini-form), fecha com `Esc`/toque fora.

## 9. Cards

Card = uma unidade (um aluno, uma campanha). Não transforme cada pedaço de texto em card;
cards demais viram ruído. Card clicável inteiro tem **um** alvo principal (e ações
secundárias separadas por menu ⋮), estado pressed/hover e nome acessível.

```text
┌───────────────────────────┐
│ João Silva            ⋮   │
│ Administrador             │
│ ● Ativo                   │
└───────────────────────────┘
```

## 10. Tabelas e listas

**Web administrativo**: tabela continua sendo o melhor para dado denso. Suporte, quando útil:
busca, filtros, ordenação, paginação, seleção, ações. Cabeçalho fixo em tabela longa,
números alinhados à direita, coluna principal (nome) primeiro e clicável.

**Ações por linha**: não dez botões. Ação muito frequente visível + menu ⋮ (Visualizar,
Editar, Desativar, Excluir — destrutivo por último e separado).

**Ações em massa**: checkbox por linha + "Selecionar todos", barra contextual com contagem
("2 selecionados · [Alterar status] [Exportar] [⋮]"). Destrutivo em massa diz o número:
"Excluir 27 usuários?".

**Mobile**: nunca a tabela espremida. Vira lista estruturada ou card com o essencial
(nome, status, 1–2 dados) e "Ver detalhes"; o resto vai para a tela de detalhe.
Tabela realmente necessária no celular: rolagem horizontal dentro do próprio container
com primeira coluna fixa.

**Listas no app**: lista virtualizada da stack (`FlatList`), pull-to-refresh, paginação
incremental, separadores discretos, item com altura mínima de 48.

## 11. Badges e chips

Badge = informação concreta ("3" notificações, "Atrasado"). Não deixe "99+" eterno sem
utilidade; zere quando visto. Status com texto + cor + (ícone). Chip = filtro/seleção,
removível com × e nome acessível ("Remover filtro Ativos").

## 12. Componentes de negócio

Podem existir (`CampaignCard`, `ProfessionalStatus`, `DoseCounter`, `ScheduleCard`,
`PermissionMatrix`, `AlunoCard`), mas **compostos pelos fundamentais** — nunca redesenham
botão, input ou badge por dentro. Moram na feature (`features/<f>/components/`).
