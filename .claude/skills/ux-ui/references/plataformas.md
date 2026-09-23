# Plataformas: Web, App, Android, iOS

## Sumário
1. O que é compartilhado e o que é adaptado
2. Web
3. App (Android e iOS)
4. Android
5. iOS
6. Adaptação desktop → app

> Plataformas mudam todo ano (iOS 26 Liquid Glass, Android 16 edge-to-edge obrigatório,
> iOS 27 no horizonte). Antes de afirmar comportamento de versão nova, confira na doc
> oficial (developer.apple.com/design, developer.android.com, docs.expo.dev).

---

## 1. Compartilhado × adaptado

| Compartilhar | Adaptar |
|---|---|
| marca, tokens, cores semânticas | navegação (sidebar × tabs × pilha) |
| terminologia e microcopy | controles (select × picker nativo × sheet) |
| hierarquia e fluxos | gestos |
| regras de negócio e estados | diálogos e permissões |
| mensagens de erro e feedback | densidade e tamanho de alvo |

Exemplo — "Excluir usuário": mesmo nome, mesma cor semântica, mesma regra, mesma
confirmação. Web: menu ⋮ na linha. App: menu de ações / sheet no detalhe (e swipe como
atalho, nunca como único caminho).

Não copie Android → iOS nem iOS → Android. Não force os dois a serem idênticos.

## 2. Web

O web tem mouse, teclado, hover, clique direito, telas grandes, várias janelas e aceita
mais densidade. Aproveite — sem depender disso.

- **Hover**: feedback (botão, linha de tabela, card clicável, item de menu). Nenhuma
  função só no hover (ações de linha que só aparecem no hover precisam aparecer no foco e
  ter alternativa no toque).
- **Cursor e affordance**: clicável parece clicável (`cursor: pointer` em controles
  customizados); texto comum não parece botão; link parece link.
- **Teclado**: tudo que importa funciona com `Tab / Shift+Tab / Enter / Space / Esc /
  setas`. Foco visível, ordem lógica, "Pular para o conteúdo" em páginas com menu grande.
  Elemento focado não pode ficar escondido atrás de header fixo/cookie bar (WCAG 2.4.11).
- **Atalhos** (sistemas de uso intenso): `Ctrl/Cmd+K` busca global, `N` novo item — só se
  não conflitar com digitação/leitor de tela, com alternativa visual e lista de atalhos.
- **Arrastar**: toda ação de arrastar tem alternativa sem arrastar (botões mover/ordenar)
  — WCAG 2.5.7.
- **Links**: abrir em nova aba só quando necessário e avisando; URL compartilhável.
- **Input**: fonte ≥ 16px nos inputs (Safari iOS dá zoom automático abaixo disso).
- **Web via Expo**: teste de verdade no navegador (`npx expo start --web`) — hover, foco,
  scroll e tamanhos grandes se comportam diferente do celular.

## 3. App (Android e iOS)

Contexto: toque, gestos, tela menor, teclado virtual, orientação, permissões, câmera,
biometria, notificações, haptics, uso em movimento e com uma mão.

**Safe area**: nada crítico sob notch, Dynamic Island, status bar, indicador de home,
barra de navegação do Android. Use o `Screen` padrão (`expo-app`) com
`react-native-safe-area-context`. Fundo pode ir até a borda; conteúdo e toques, não.

**Teclado virtual**: campo ativo + contexto necessário + ação principal continuam
visíveis. Nunca o teclado cobre o campo em edição. "Próximo" leva ao campo seguinte
(`returnKeyType="next"` + foco); último campo usa "Concluído/Enviar".

**Tipo de teclado e autofill** (reduz erro e acelera):

| Campo | RN (`keyboardType` / `inputMode`) | `autoComplete` / `textContentType` |
|---|---|---|
| E-mail | `email-address` | `email` / `emailAddress` |
| Telefone | `phone-pad` | `tel` / `telephoneNumber` |
| Número/CPF/CEP | `number-pad` / `numeric` | `postal-code` p/ CEP |
| Valor | `decimal-pad` | — |
| URL | `url` | `url` |
| Senha | — (`secureTextEntry`) | `current-password` / `new-password` |
| Código SMS | `number-pad` | `sms-otp` / `oneTimeCode` |

**Haptics**: confirmação, seleção, ação importante, erro específico. Sempre complemento,
nunca o único sinal. Respeite configuração do sistema (`expo-haptics`).

**Permissões de dispositivo**: peça no momento de uso, com explicação antes ("Precisamos
da câmera para fotografar o documento" → então o prompt do sistema). Nunca todas na
abertura. Negada? Explique o impacto e ofereça abrir as configurações.

**Gestos**: aceleram, mas nunca são o único caminho (swipe para excluir também existe no
menu ⋮). Não crie gesto que conflite com os do sistema (bordas, voltar, home).

**Notificações**: contexto + informação + ação, e abrem direto no conteúdo (deep link).
"Escala alterada — A campanha Empresa ABC mudou para 08:30. [Ver escala]", nunca
"Você possui uma nova notificação."

## 4. Android

- **Alvo de toque ≥ 48×48 dp** (ícone pode ser 24; complete com padding/`hitSlop`).
- **Edge-to-edge obrigatório**: Android 15 força edge-to-edge para apps com targetSdk 35;
  no Android 16 (API 36) o opt-out foi removido, e a Play exige API 36 para atualizações
  desde ago/2026. Todo layout trata insets de status bar, barra de navegação e teclado (IME).
- **Voltar do sistema** e **predictive back** (padrão no Android 16): voltar fecha
  sheet/modal/menu antes de sair da tela; não sequestre o voltar sem motivo.
- **TalkBack**: toda ação alcançável e nomeada; ordem de leitura lógica.
- **Escala de fonte** do sistema (até 200% em versões recentes) — layout não pode cortar.
- **Telas grandes/dobráveis**: travas de orientação e redimensionamento são ignoradas em
  telas ≥ 600dp para API 36 — layout adaptável obrigatório.
- Convenções Material: FAB para a ação de criar dominante, snackbar para feedback, menu
  de 3 pontos verticais (⋮), diálogo com ações em texto à direita.

## 5. iOS

- **Alvo de toque ≥ 44×44 pt** (norma do iOS; em código cross-platform a casa usa 48 — `MIN_TOUCH_TARGET`).
- **Safe area** e **gesto de voltar pela borda** preservados; não recrie a barra de
  navegação sem necessidade.
- **iOS 26 / Liquid Glass**: tab bar e barras flutuam sobre o conteúdo (a tab bar pode
  minimizar na rolagem) e usam o material de vidro; o conteúdo rola por baixo. Regras
  práticas: use **componentes nativos** (tabs nativas do Expo Router, `Stack` nativo,
  `@expo/ui`) e eles adotam o visual sozinhos; vidro é para a **camada de navegação/
  controles**, nunca para o conteúdo (listas, cards, fundos); não empilhe vidro sobre vidro;
  garanta espaço no fim da rolagem para o conteúdo não ficar preso atrás da tab bar;
  respeite "Reduzir transparência" e "Aumentar contraste".
- **Dynamic Type**: suporte tamanhos grandes (inclusive acessibilidade); layouts em
  linha viram coluna quando a fonte cresce.
- **VoiceOver**: rótulos, traits (`button`, `header`, `selected`), rotor por títulos.
- Convenções: botão principal da barra à direita ("Salvar"), "Cancelar" à esquerda em
  modal; action sheet para escolher ações; alertas com o destrutivo em vermelho; switches
  para liga/desliga imediato.
- Cantos concêntricos: raio interno acompanha o externo (cartões dentro de sheets etc.).

## 6. Adaptação desktop → app

Nunca "diminuir a largura e chamar de app". Recalcule por:
**prioridade** (o que o usuário em campo precisa primeiro) · **densidade** (menos por
tela) · **contexto** (uma mão, sol, pressa) · **toque** (alvos, gestos) · **navegação**
(tabs + pilha) · **ergonomia** (ação na zona do polegar).
