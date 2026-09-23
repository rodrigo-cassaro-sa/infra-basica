# Performance

## Sumário
1. Medir antes de otimizar
2. Listas: FlatList → FlashList
3. Item de lista e memoização
4. Imagens com expo-image
5. Re-render: causas reais
6. Busca e filtros sem travar
7. Animação e thread JS
8. Checklist

---

## 1. Medir antes de otimizar

Regra 17: não otimize sem medir. E **meça em build de release**: o modo dev é várias vezes
mais lento e engana.

- **Preview build** (`eas build --profile preview`) ou `npx expo start --no-dev --minify` para sentir a performance real.
- **Performance Monitor** (menu de dev → "Perf Monitor"): FPS da UI e da thread JS.
- **React DevTools → Profiler** (tecla `j` no terminal do `expo start`): o que renderiza demais e por quê.
- **Produção**: EAS Observe / Sentry performance.
- Teste num Android intermediário. O iPhone do dev não é o aparelho do usuário.

| Sintoma | Causa provável | Seção |
|---|---|---|
| Rolagem engasga, células brancas | lista pesada ou item caro | 2, 3 |
| Digitar na busca trava | filtro pesado a cada tecla | 6 |
| Tela pisca/pula imagem | imagem sem tamanho, sem cache | 4 |
| Toda a tela re-renderiza ao mudar algo pequeno | estado alto demais, seletor de store amplo | 5 |
| Animação engasga durante carregamento | trabalho na thread JS | 7 |

## 2. Listas: FlatList → FlashList

- **Padrão: `FlatList`** para qualquer lista que possa crescer (regra 12). Nunca `ScrollView` + `.map()`.
- **`FlashList`** (`@shopify/flash-list`) quando houver problema **medido**: centenas/milhares
  de itens, item com imagem, feed, chat. Ela recicla células em vez de montar e desmontar.
  Registre a adoção no `docs/stack.md`.

```bash
npx expo install @shopify/flash-list
```

```tsx
import { FlashList } from "@shopify/flash-list";

<FlashList
  data={students}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => <StudentRow student={item} onPress={openStudent} />}
  ListEmptyComponent={<EmptyState title="Nenhum aluno ainda" description="Cadastre um aluno para começar." />}
  onRefresh={refetch}
  refreshing={isRefetching}
  onEndReached={() => hasNextPage && !isFetchingNextPage && fetchNextPage()}
  onEndReachedThreshold={0.4}
/>
```

- A API é quase a da `FlatList`: a troca é pequena. A v2 (New Architecture) dispensa
  `estimatedItemSize`; em versão anterior ele é obrigatório — confira a versão instalada.
- Itens de **tipos diferentes** (cabeçalho de seção, card, anúncio): `getItemType` para
  reciclar célula do tipo certo.
- **Reciclagem = estado local de item vaza** para outro item. Não guarde `useState` no item
  que dependa do dado (ex.: "expandido"); guarde por id no pai ou na store.

Ajustes úteis na `FlatList` antes de trocar de lib:
- Item de altura fixa → `getItemLayout` (pula a medição).
- `initialNumToRender` ≈ itens de uma tela; `windowSize` menor (ex.: 5) em listas pesadas.
- Paginação no backend (`useInfiniteQuery`, `dados-e-api.md` §8) resolve mais que qualquer ajuste de lista.

## 3. Item de lista e memoização

Com **React Compiler ativo** (padrão do template, `experiments.reactCompiler: true`), ele
memoiza sozinho. Não escreva `memo`/`useMemo`/`useCallback` manual sem medição mostrando
que o compilador não resolveu.

Sem compilador (ou caso medido), as três andam juntas: `memo` sem props estáveis não faz nada.

```tsx
export const StudentRow = memo(function StudentRow({ student, onPress }: StudentRowProps) {
  return <Pressable onPress={() => onPress(student.id)} /* ... */ />;
});

// na screen: um handler estável que recebe o id, em vez de um handler novo por item
const openStudent = useCallback((id: string) => router.push(`/alunos/${id}`), []);
```

Item leve: nada de formatação cara, filtro ou `new Intl.*` dentro do `renderItem` — formate
no mapper (DTO → modelo) ou crie o formatador uma vez fora do componente.

## 4. Imagens com expo-image

`expo-image` é o padrão da casa (cache em disco, placeholder, transição, formatos modernos).
Nunca `Image` do React Native para imagem remota.

```tsx
import { Image } from "expo-image";

<Image
  source={{ uri: student.photoUrl }}
  style={{ width: 48, height: 48, borderRadius: radius.full }}   // sempre com dimensão
  contentFit="cover"
  placeholder={{ blurhash: student.photoBlurhash }}               // se o backend fornecer
  transition={motion.fast}                                        // 0 se "reduzir movimento" estiver ativo
  recyclingKey={student.id}                                       // obrigatório em FlashList: evita imagem trocada
  accessibilityLabel={`Foto de ${student.name}`}                  // decorativa: accessible={false}
/>
```

- **Tamanho certo**: peça ao backend/MinIO a imagem no tamanho de exibição (ou variantes
  `thumb`/`medium`). Baixar 4000 px para mostrar 48 é o maior desperdício comum.
- **Prefetch** do que o usuário vai ver a seguir: `Image.prefetch(urls)`.
- `cachePolicy`: padrão (disco) serve para quase tudo; `"none"` só para imagem que muda com a mesma URL (prefira mudar a URL).
- Ícones e ilustrações simples: SVG ou fonte de ícones, não PNG grande.

## 5. Re-render: causas reais

Antes de memoizar, corrija a estrutura:
- **Estado alto demais**: estado do campo de busca no topo da tela re-renderiza a lista inteira.
  Desça o estado para o componente que usa.
- **Seletor amplo de store**: `useSessionStore()` inteiro re-renderiza em qualquer mudança.
  Sempre seletor: `useSessionStore((s) => s.user)`.
- **Context com objeto novo a cada render**: todo consumidor re-renderiza. Divida o contexto
  ou estabilize o `value`.
- **Query key instável** (objeto novo a cada render) → refetch em loop. Keys vêm do `query-keys.ts`.

## 6. Busca e filtros sem travar

- **Busca no servidor**: debounce (~300 ms, hook `use-debounce` em `src/hooks`) + termo na
  query key + `placeholderData: keepPreviousData` (a lista não pisca vazia entre termos).
- **Filtro local em lista grande**: `useDeferredValue(termo)` mantém o campo responsivo e
  filtra com prioridade baixa.

## 7. Animação e thread JS

- Animações com `react-native-reanimated` (rodam na thread de UI) ou `Animated` com
  `useNativeDriver: true`. Nada de animar com `setState` em intervalo.
- Durações vêm de `motion` (tema); respeite "reduzir movimento" (`AccessibilityInfo.isReduceMotionEnabled`).
- Trabalho pesado (parse grande, ordenação de milhares de itens) fora do caminho da animação:
  faça no backend, pagine, ou adie com `InteractionManager.runAfterInteractions`.

## 8. Checklist

```text
[ ] Problema medido em build de release, em Android intermediário
[ ] Lista longa em FlatList; FlashList só com problema medido (registrado no stack.md)
[ ] Item de lista leve; sem formatação/filtro no renderItem
[ ] memo/useMemo/useCallback só com medição (React Compiler ativo)
[ ] Imagens remotas com expo-image, dimensão definida, tamanho certo vindo do backend
[ ] recyclingKey em imagem dentro de FlashList
[ ] Seletores em toda leitura de store; query keys estáveis
[ ] Busca com debounce + keepPreviousData
```
