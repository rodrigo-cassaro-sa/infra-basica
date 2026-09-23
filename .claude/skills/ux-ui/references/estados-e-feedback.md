# Estados e feedback

## Sumário
1. Mapa de estados de uma tela
2. Feedback de ação
3. Loading (spinner, skeleton, progresso)
4. Estado vazio
5. Estado de erro
6. Offline e sincronização
7. Sem permissão
8. Confirmação × desfazer
9. Optimistic UI
10. Performance percebida

---

## 1. Mapa de estados de uma tela

Não pense só "tem dado / não tem dado". Lista canônica da casa (unifica os "4 estados" do
web e os "5 estados" do `expo-app`):

| Estado | Quando | Componente |
|---|---|---|
| loading inicial | primeira carga | Skeleton (conteúdo estruturado) ou Spinner |
| sucesso / conteúdo | tem dados | a tela |
| vazio | sucesso sem itens | EmptyState |
| vazio por filtro/busca | há dados, mas o filtro zerou | EmptyState com "Limpar filtros" |
| erro | falha ao carregar | ErrorState com "Tentar novamente" |
| sem rede | app sem conexão | OfflineState / banner |
| sem permissão | 403 | mensagem + caminho (voltar, pedir acesso) |
| não encontrado | 404 / deep link inválido | mensagem + voltar ao início |
| refresh | recarregando com dado na tela | indicador discreto, **mantém** o conteúdo |
| paginação | carregando mais | spinner no fim da lista |
| parcial | parte carregou, parte falhou | conteúdo + alerta na seção que falhou |

Ordem de render (padrão das skills de stack): loading → erro → vazio → conteúdo.
Recarregar **não** volta para o skeleton de tela cheia.

## 2. Feedback de ação

Toda interação importante informa o resultado. Sequência:

```text
toque/clique ──► pressed imediato (< 100ms)
             ──► "Salvando…" (botão em loading, sem duplo envio)
             ──► sucesso: "Usuário criado." (toast ou navegação para o item criado)
             ──► falha:  "Não foi possível salvar o usuário. [Tentar novamente]" (dados preservados)
```

Mesmo verbo no fluxo todo: botão "Publicar" → toast "Publicado". Feedback tátil (app) só
como complemento.

## 3. Loading

| Padrão | Quando |
|---|---|
| Spinner | ação curta ou área pequena |
| Skeleton | carregar conteúdo com forma conhecida (lista, card, detalhe) — imita o layout real |
| Progresso determinado | upload, importação, operação com etapas mensuráveis — **nunca % falso** |
| Progresso por etapas | "Validando… Enviando… Concluído" quando não há % |

- Até ~1s: muitas vezes só o pressed/loading do botão basta; evite "piscar" spinner.
  Mostre indicador após ~300ms de espera e mantenha-o ≥ ~500ms para não piscar.
- Não bloqueie a tela inteira por uma parte; carregue por seção.
- Leitor de tela: `aria-busy`/`accessibilityState.busy` na região; anuncie o fim se relevante.

## 4. Estado vazio

Lista vazia não pode parecer erro. Deve **ensinar o próximo passo**:

```text
Nenhum aluno cadastrado
Cadastre o primeiro aluno para começar a montar as turmas.
                        [+ Cadastrar aluno]
```

Vazio por busca/filtro é diferente: "Nenhum resultado para 'Maria' em Ativos. [Limpar filtros]".
Sem permissão para criar? Não mostre o botão; explique quem pode.

## 5. Estado de erro

Estrutura: **o que aconteceu + o que significa + o que fazer**.

```text
Não foi possível carregar os usuários.
Verifique sua conexão e tente novamente.
                        [Tentar novamente]
```

- Nada de "Error 500", "Foreign key violation", stack trace. Detalhe técnico vai para log
  (sem token, senha, CPF). Nas skills de stack: erro tipado → `getUserMessage`.
- Erro de campo fica no campo; erro de tela fica na área; erro global vira banner.
- Se o problema persiste, ofereça caminho (suporte, contato) — WCAG 3.2.6 pede ajuda em
  lugar consistente.

## 6. Offline e sincronização

Só prometa offline se o app realmente suporta. Estados:

```text
Online · Offline · Sincronizando · Falha de sincronização
```

- Sem suporte offline: banner "Sem conexão. Algumas ações ficam indisponíveis." e
  desabilite o que depende de rede (com explicação).
- Com suporte offline: "Sem conexão. As alterações serão enviadas quando a conexão voltar."
  + indicador por item pendente + tela/ação para resolver falhas de sync.
- Voltou a conexão: revalide dados (a Query faz isso) e avise discretamente.

## 7. Sem permissão

Decida conscientemente: **ocultar** (o usuário não precisa saber que existe) ou
**mostrar desabilitado com motivo** ("Excluir usuário — indisponível para seu perfil")
quando saber que existe ajuda. Erro de autorização vira texto humano: "Você não tem
permissão para editar este usuário." — nunca "403 Forbidden". O backend valida sempre.

## 8. Confirmação × desfazer

- **Não confirme o trivial** (salvar, filtrar, arquivar reversível).
- **Prefira desfazer** quando tecnicamente possível: "Usuário arquivado. [Desfazer]" —
  mais rápido e mais seguro que diálogo.
- **Confirme** o que é destrutivo e irreversível ou de grande impacto, dizendo o quê, em
  quem e o impacto: "Desativar João Silva? Ele perderá acesso imediatamente."
- Irreversível e muito grave (excluir conta, apagar base): peça digitar o nome ou
  confirmação extra.

## 9. Optimistic UI

Quando seguro (favoritar, marcar como lido, reordenar), atualize antes da resposta e
sincronize depois: `☆ → ★`. Se falhar: **restaure o estado + informe**. Não use em
pagamento, envio de documento, permissão ou qualquer operação sensível sem estratégia de
recuperação. (Nas stacks com TanStack Query: `onMutate` + rollback em `onError`.)

## 10. Performance percebida

- Resposta visual imediata ao toque, mesmo que o servidor demore.
- Mostre progresso quando passar de ~1s; não trave a tela inteira.
- Carregue o que está acima da dobra primeiro; imagens com dimensões definidas (sem pulo de layout).
- Lembre preferências de uso diário: último filtro, ordenação, visualização, densidade,
  tema, tamanho da página.
