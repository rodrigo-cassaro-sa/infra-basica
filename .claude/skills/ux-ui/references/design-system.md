# Design system

## Sumário
1. Camadas de tokens
2. Cores e cores semânticas
3. Contraste
4. Tipografia
5. Espaçamento, proximidade e alinhamento
6. Bordas, raio e sombras (elevação)
7. Ícones
8. Movimento (tokens de duração)
9. Dark mode
10. Formato de arquivo (DTCG) e pipeline

---

## 1. Camadas de tokens

O design system é a fonte das decisões visuais. Nenhuma tela define valor arbitrário.

```text
Primitivo            →  Semântico               →  Componente
blue.600                color.action.primary       button.primary.background
gray.900                color.text.primary         input.text
space.4 (16)            space.inset.md             card.padding
```

- **Primitivo**: a paleta crua. Existe, mas componente **não consome** direto.
- **Semântico**: o papel (`text.primary`, `surface`, `error`). É o que telas e componentes usam.
- **Componente**: só quando um componente precisa divergir do semântico. Não crie por hábito.

Categorias: `color · typography · spacing · radius · border · shadow/elevation · size · breakpoint · motion · icon`.

Por que: trocar marca, criar dark mode ou variante de alto contraste passa a ser trocar a
camada semântica — nenhum componente muda.

## 2. Cores e cores semânticas

Cor tem significado, não enfeite. Conjunto mínimo de papéis:

```text
primary · primaryHover · primaryPressed · onPrimary
secondary
background · surface · surfaceVariant
textPrimary · textSecondary · textDisabled
border · divider · focus
success · warning · error · info   (+ on* e *Surface quando usados como fundo)
```

Nos arquivos de tema o papel `error` chama-se `danger` e `textPrimary`/`textSecondary`
chamam-se `text`/`textMuted` (convenção da `expo-app`, mantida em `tokens.json`).

Semântica fixa no produto inteiro:

| Papel | Uso | Exemplo |
|---|---|---|
| `success` | concluído, aprovado | Pagamento aprovado |
| `warning` | atenção, prazo | Documento vence em 3 dias |
| `error` | falha, bloqueio, destrutivo | Falha ao salvar |
| `info` | neutro informativo | Novo recurso disponível |

- `error` também é a cor do botão destrutivo. Não use vermelho decorativo.
- Cor **complementa** texto/ícone, nunca substitui: `● Concluído`, não `●` verde.
- Uma cor de marca forte basta. Espalhe a marca pela ação principal e pelo estado
  selecionado — não por fundos inteiros.

## 3. Contraste (WCAG 2.2 AA)

| Elemento | Mínimo |
|---|---|
| Texto normal | 4,5:1 |
| Texto grande (≥ 24px regular ou ≥ 18,66px bold) | 3:1 |
| Ícones essenciais, bordas de input, foco, gráficos (1.4.11) | 3:1 contra o adjacente |
| Texto desabilitado / decorativo | isento, mas precisa parecer desabilitado |

Pontos cegos comuns: placeholder cinza-claro, texto secundário sobre `surface`, erro
vermelho sobre fundo escuro, texto sobre imagem/gradiente, estado de foco. Verifique os
pares **nos dois temas**. `textSecondary` tem de passar 4,5:1 sobre `background` **e** `surface`.

## 4. Tipografia

Uma família principal (duas no máximo, claramente distintas). Fonte simples e legível para
produto; personalidade tipográfica forte fica para marketing (ver `frontend-web`).

Escala padrão (projeto novo):

| Token | Tamanho | Uso |
|---|---|---|
| display | 40 | números de destaque, hero |
| h1 | 32 | título de página (web) |
| h2 | 28 | |
| h3 | 24 | título de tela (app) / seção |
| h4 | 20 | título de card/modal |
| bodyLarge | 18 | leitura longa |
| body | 16 | **padrão** — nunca menos que 16 em input no iOS (evita zoom automático no Safari) |
| bodySmall | 14 | secundário, tabela densa |
| caption | 12 | metadado; nunca para informação essencial |

- Line-height ≈ 1,4–1,5 para corpo; 1,2–1,3 para títulos. Linha de leitura ≤ 80 caracteres.
- Pesos: 400 regular · 500 medium · 600 semibold · 700 bold. **Peso também é hierarquia**;
  bold em tudo = nada em destaque.
- Escala menor no app que no web desktop é normal; defina no tema, não por tela.
- Texto respeita a escala de fonte do sistema (Dynamic Type/fonte do Android). Não trave
  `allowFontScaling`; limite com `maxFontSizeMultiplier` só em elementos que realmente quebram.

Exemplo de hierarquia:
```text
Usuários                           ← h1
Gerencie quem acessa o sistema     ← body / textSecondary
Rodrigo Silva                      ← body medium
Administrador                      ← bodySmall / textSecondary
```

## 5. Espaçamento, proximidade e alinhamento

Grade de **4**: `4 · 8 · 12 · 16 · 24 · 32 · 40 · 48 · 64`. Os mais usados: **8, 16, 24, 32**.
Nada de `13px`, `19px`, `23px` sem motivo.

- **Proximidade comunica relação**: label↔campo 4–8; campo↔ajuda 4–8; campo↔próximo campo
  16–24; seção↔seção 32–48.
- **Alinhamento**: grid/flex/containers; elementos relacionados compartilham a mesma
  linha visual (títulos, inputs, cards, colunas, botões).
- Padding de tela: 16 no celular, 24 no tablet, 24–32 no desktop.
- Hierarquia por espaço antes de bordas e caixas.

## 6. Bordas, raio e sombras

**Bordas**: `border.default · border.strong · border.focus · border.error`. Use quando
separar ajuda. Prefira, nesta ordem: espaço → hierarquia → fundo (`surface`) → divisor → borda.
Evite caixa dentro de caixa dentro de caixa.

**Raio** (padrão novo): `sm 4 · md 8 · lg 12 · xl 16 · full 9999`. Um raio por nível
(input/botão `md`, card `lg`, modal/sheet `xl`, avatar/chip `full`). Aninhado: raio interno =
raio externo − padding (cantos concêntricos, como o iOS 26 faz).

**Sombra = elevação**, não enfeite: `shadow.sm` (dropdown), `shadow.md` (popover, card
arrastável), `shadow.lg` (modal). Card comum em lista: sem sombra, ou `sm`. No dark mode
sombra quase não aparece — eleve com `surface` mais clara.

## 7. Ícones

Uma família só (outline **ou** filled, não misturar), mesmo traço, tamanhos `16 · 20 · 24`.
Ícone sem significado universal leva texto ou tooltip (web) / `accessibilityLabel` (app).
Ícone decorativo ao lado de texto é escondido do leitor de tela.

Convenções que não se reinventam: `← Voltar · × Fechar · ⋮ Mais opções · 🔍 Buscar ·
⚙ Configurações · 🗑 Excluir · ✎ Editar · ＋ Adicionar`.

## 8. Movimento (tokens)

```text
motion.duration.fast    100–150ms   microinteração (pressed, toggle)
motion.duration.base    200–250ms   transição comum (expandir, toast)
motion.duration.slow    300–400ms   entrada de modal/sheet, navegação
(máx. ~500ms para transições complexas)
motion.easing.standard  ease-out para entrar, ease-in para sair
```
Detalhes e "reduzir movimento" em `acessibilidade.md` §7.

## 9. Dark mode

Não é inverter branco e preto. São dois conjuntos semânticos com **as mesmas chaves**:

- `background` não é `#000` puro; use cinza muito escuro. `text` não é `#FFF` puro em
  bloco grande de texto (cansa); use ~90% de luminosidade.
- Elevação por clareamento de superfície (`surface` > `background`), não por sombra.
- Dessature cores de marca/semânticas no escuro para não vibrar; revalide contraste.
- Imagens e ilustrações com fundo branco precisam de versão ou moldura.
- Componente consome token; nunca `isDark ? '#111' : '#fff'` dentro do componente.
- Respeite a preferência do sistema; ofereça escolha manual (Sistema / Claro / Escuro)
  quando o produto for usado todos os dias.

Padrão da casa (skill `expo-app`): tema escuro é o default quando o projeto não define.

## 10. Formato de arquivo e pipeline

Mantenha os tokens em **um arquivo fonte** no formato do W3C Design Tokens Community Group
(DTCG, versão estável 2025.10: `$value`, `$type`, aliases `{color.brand.600}`), exportável
do Figma Variables e lido pelo Style Dictionary v4. Desse arquivo saem `tokens.css` (web) e
`theme` (Expo/React Native).

Nesta skill: `assets/tokens/tokens.json` (ponto de partida) + `scripts/build-tokens.py`:

```bash
python3 <skill>/scripts/build-tokens.py tokens/tokens.json --ts src/theme/tokens.ts --check          # Expo
python3 <skill>/scripts/build-tokens.py tokens/tokens.json --css src/styles/tokens.css --check       # web
```

O `src/theme/index.ts` da `expo-app` já consome o `tokens.ts` gerado (`useTheme()`); a web
importa o `tokens.css` uma vez no ponto de entrada. `tokens.ts`/`tokens.css` são gerados:
nunca edite à mão.

**Fonte no app**: RN usa um arquivo de fonte por peso. Carregue com `expo-font` e registre o
nome carregado em `font.native` (`"400": "Inter_400Regular"`, `"600": "Inter_600SemiBold"`…);
`"system"` mantém a fonte do sistema. O tema aplica a família certa por peso.
