# Acessibilidade

## Sumário
1. Meta e base legal
2. Critérios WCAG 2.2 que mais aparecem
3. Semântica e leitores de tela
4. Texto alternativo
5. Foco e teclado
6. Zoom e texto ampliado
7. Movimento e transparência
8. Código acessível por stack
9. Como testar

---

## 1. Meta e base legal

Acessibilidade é parte do produto, não etapa final.

- **Meta: WCAG 2.2 nível AA** (web e, por analogia, app).
- **Brasil**: a Lei Brasileira de Inclusão (Lei 13.146/2015, art. 63) obriga acessibilidade
  em sites de empresas com sede ou representação no país e de órgãos públicos. A
  **ABNT NBR 17225:2025** (Acessibilidade em conteúdo e aplicações web) é a referência
  técnica: foi construída a partir do WCAG 2.2, e sua "conformidade regular" (todos os
  requisitos) equivale ao nível AA. eMAG continua valendo para governo.
- Beneficia também idoso, quem está no sol, com uma mão ocupada, com braço machucado.

## 2. Critérios WCAG 2.2 que mais aparecem

| Critério | Nível | Na prática |
|---|---|---|
| 1.1.1 Conteúdo não textual | A | alt/label em imagem e ícone com função |
| 1.3.1 Info e relações | A | título é heading, lista é lista, label ligado ao input |
| 1.4.1 Uso de cor | A | significado nunca só por cor |
| 1.4.3 Contraste | AA | 4,5:1 texto; 3:1 texto grande |
| 1.4.4 Redimensionar texto | AA | 200% sem perda |
| 1.4.10 Reflow | AA | 320px de largura sem rolagem horizontal (exceto tabelas/mapas) |
| 1.4.11 Contraste não textual | AA | 3:1 em bordas de input, ícones, foco |
| 1.4.12 Espaçamento de texto | AA | não quebra com mais line-height/letter-spacing |
| 1.4.13 Conteúdo em hover/foco | AA | tooltip dispensável (Esc), persistente, alcançável |
| 2.1.1 Teclado | A | tudo operável por teclado |
| 2.4.3 Ordem do foco | A | ordem lógica |
| 2.4.7 Foco visível | AA | sempre |
| **2.4.11 Foco não obscurecido** (novo 2.2) | AA | header fixo/cookie bar não cobre o foco |
| **2.5.7 Movimentos de arrastar** (novo 2.2) | AA | alternativa sem arrastar |
| **2.5.8 Tamanho do alvo mínimo** (novo 2.2) | AA | ≥ 24×24 CSS px (ou espaçamento equivalente) |
| 3.3.1 / 3.3.3 Erro identificado + sugestão | A/AA | erro no campo, em texto, com como corrigir |
| **3.2.6 Ajuda consistente** (novo 2.2) | A | ajuda/contato no mesmo lugar em todas as páginas |
| **3.3.7 Entrada redundante** (novo 2.2) | A | não pedir de novo o que já foi informado |
| **3.3.8 Autenticação acessível** (novo 2.2) | AA | sem teste cognitivo; permitir colar senha, gerenciador de senhas, magic link/passkey |
| 4.1.2 Nome, função, valor | A | componente customizado expõe role, nome e estado |

## 3. Semântica e leitores de tela

Todo elemento tem o papel certo e um nome:
- Botão é botão (`<button>` / `role="button"`), link é link, título é heading.
- Campo tem label associado; erro associado ao campo e anunciado.
- Estado exposto: selecionado, marcado, expandido, desabilitado, ocupado.
- Imagem informativa tem descrição; decorativa é ignorada.
- Mudança dinâmica importante é anunciada (live region / `announceForAccessibility`).
- Agrupe o que é lido junto (card = um item lido de uma vez, com ação principal).

## 4. Texto alternativo

Descreva a **função** ou a informação, não "imagem". "Gráfico: matrículas subiram de 120
para 180 entre janeiro e março." Botão só-ícone: nome da ação ("Excluir aluno Maria"), não
do ícone ("lixeira"). Decorativa: `alt=""` / `accessible={false}` / `aria-hidden`.

## 5. Foco e teclado

- Ordem: título → busca → filtros → conteúdo → ações (a ordem lógica da tela).
- Nunca `outline: none` sem substituto: use `:focus-visible` com anel de 2px+ em
  `color.focus` com contraste 3:1.
- Modal prende o foco e devolve ao gatilho; menu abre com Enter/Space, navega por setas,
  fecha com Esc.
- Após ação que muda a tela (salvar, excluir item da lista, trocar de rota), leve o foco
  a um lugar sensato (título, item seguinte, mensagem).
- No envio com erro, foco no primeiro campo inválido.

## 6. Zoom e texto ampliado

Web: 200% de zoom e 320px de largura sem perder conteúdo. App: fonte grande do sistema
sem cortar. Portanto: sem altura fixa em container de texto, sem `numberOfLines` em texto
essencial, layout em linha que vira coluna quando a fonte cresce, unidades relativas
(`rem`) no web.

## 7. Movimento e transparência

- Animação comunica transição, continuidade, mudança de estado ou feedback. Nada de
  movimento só porque parece moderno; nada de apresentação cinematográfica.
- Durações: microinteração 100–200ms · transição comum 150–300ms · complexa até ~500ms.
- **Reduzir movimento**: troque deslocamento/escala/paralaxe por fade ou corte seco.
  Nenhum entendimento pode depender da animação. Nada piscando mais de 3 vezes/segundo.
- iOS: respeite também "Reduzir transparência" (vidro vira sólido).

## 8. Código acessível por stack

### Web (Expo Web e componentes DOM)

```html
<label for="email">E-mail</label>
<input id="email" type="email" autocomplete="email" inputmode="email"
       aria-invalid="true" aria-describedby="email-erro" />
<p id="email-erro" role="alert">Digite um e-mail válido, como nome@empresa.com.</p>

<button type="button" aria-label="Excluir aluno Maria Souza">
  <svg aria-hidden="true" focusable="false">…</svg>
</button>

<button type="submit" disabled aria-busy="true">Salvando…</button>
<div role="status" aria-live="polite">Alterações salvas.</div>
```

```css
:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
```

### React Native / Expo

RN aceita as props `accessibility*` e também os equivalentes ARIA (`role`, `aria-label`,
`aria-disabled`, `aria-busy`, `aria-checked`, `aria-expanded`, `aria-live`), que o
React Native Web converte para HTML. Escolha **um estilo por projeto**; o template da
`expo-app` usa `accessibility*`.

```tsx
<Pressable
  accessibilityRole="button"
  accessibilityLabel="Salvar aluno"
  accessibilityHint="Salva e volta para a lista"
  accessibilityState={{ disabled: isSaving, busy: isSaving }}
  hitSlop={8}                      // completa a área até 48 quando o visual é menor
  onPress={save}
  style={({ pressed }) => [styles.button, pressed && styles.pressed]}
/>

<Text accessibilityRole="header">Alunos</Text>

<Text accessibilityLiveRegion="polite">{errorMessage}</Text>   // Android
AccessibilityInfo.announceForAccessibility("Aluno salvo");      // iOS e Android

// Decorativo
<Image source={bg} accessible={false} importantForAccessibility="no" />
```

Reduzir movimento: `AccessibilityInfo.isReduceMotionEnabled()` + listener
`reduceMotionChanged`, ou `useReducedMotion()` do Reanimated se o projeto já usa.

Não trave `allowFontScaling={false}`; use `maxFontSizeMultiplier` pontualmente.

### React Native / Expo — padrões que mais faltam em app

**Card lido como uma unidade.** Sem agrupar, o leitor de tela para em cada `Text` do card
(nome, depois telefone, depois status). Agrupe e dê um rótulo que resume:

```tsx
<Pressable
  accessible
  accessibilityRole="button"
  accessibilityLabel={`${aluno.nome}, ${aluno.ativo ? 'ativo' : 'inativo'}, mensalidade ${formatMoeda(aluno.valor)}`}
  accessibilityHint="Abre os detalhes do aluno"
  onPress={abrir}
>
  {/* conteúdo visual livre */}
</Pressable>
```

**Gesto sempre com alternativa acessível.** Swipe para excluir, arrastar para reordenar e
long press não existem para quem usa leitor de tela. Exponha as mesmas ações como ações
customizadas (aparecem no menu de ações do TalkBack/VoiceOver) e mantenha o menu ⋮ visível:

```tsx
<View
  accessible
  accessibilityLabel={aluno.nome}
  accessibilityActions={[
    { name: 'editar', label: 'Editar' },
    { name: 'excluir', label: 'Excluir' },
  ]}
  onAccessibilityAction={(e) => {
    if (e.nativeEvent.actionName === 'editar') editar();
    if (e.nativeEvent.actionName === 'excluir') confirmarExclusao();
  }}
/>
```

**Modal e bottom sheet isolam o fundo.** Senão o leitor de tela navega para o conteúdo
atrás do modal. `Modal` nativo já faz isso; em sheet/overlay customizado:
`accessibilityViewIsModal` no container (iOS) e
`importantForAccessibility="no-hide-descendants"` no conteúdo de trás (Android).
Ao fechar, devolva o foco ao botão que abriu.

**Mover o foco depois de uma ação.** Ao trocar de etapa, abrir erro ou concluir envio:

```tsx
const tituloRef = useRef<Text>(null);
useEffect(() => {
  const tag = findNodeHandle(tituloRef.current);
  if (tag) AccessibilityInfo.setAccessibilityFocus(tag);
}, [etapa]);
```

**Fonte grande muda o layout, não só o tamanho.** Use `fontScale` para trocar linha por coluna:

```tsx
const { fontScale } = useWindowDimensions();
const empilhar = fontScale >= 1.3;
<View style={{ flexDirection: empilhar ? 'column' : 'row', gap: 8 }}>…</View>
```

**Leitor de tela ligado muda a interação.** Carrossel com autoplay, toast que some em 3s e
timeout de sessão curto são inutilizáveis com leitor de tela. Detecte e ajuste
(pause o autoplay, prolongue ou fixe a mensagem):

```ts
const [leitorAtivo, setLeitorAtivo] = useState(false);
useEffect(() => {
  AccessibilityInfo.isScreenReaderEnabled().then(setLeitorAtivo);
  const sub = AccessibilityInfo.addEventListener('screenReaderChanged', setLeitorAtivo);
  return () => sub.remove();
}, []);
```

**Idioma do conteúdo.** Texto em outro idioma no meio da tela (nome de música, termo em
inglês) pode receber `accessibilityLanguage="en-US"` para o leitor pronunciar certo.
Com i18n, os labels de acessibilidade também passam pelo `t()` (ver `i18n.md` §4).

**Lint.** Em projeto Expo, `eslint-plugin-react-native-a11y` pega `Pressable` sem role/label
e imagem sem descrição antes da revisão manual.

## 9. Como testar

- **Automático** (pega ~30–40%): axe DevTools / Lighthouse no web; `eslint-plugin-jsx-a11y`
  nos componentes DOM; `eslint-plugin-react-native-a11y` no Expo; `@testing-library` com `getByRole`
  (se não acha por role, está errado — ver `expo-app/references/testes.md`).
- **Manual, sempre**: navegar só com teclado; TalkBack (Android) e VoiceOver (iOS/macOS)
  na tela nova; zoom 200% / fonte máxima do sistema; modo escuro; reduzir movimento;
  checar contraste dos pares de cor novos.
