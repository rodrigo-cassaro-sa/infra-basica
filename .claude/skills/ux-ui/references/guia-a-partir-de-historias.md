# Derivar e manter o guia visual a partir das Histórias

As Histórias descrevem necessidades de interação. O `docs/guia-visual.md` transforma essas
necessidades em **padrões reutilizáveis do projeto**. Ele não descreve uma tela: define o
que as telas usam.

```text
Histórias / RN-xx → necessidades → padrões recorrentes → GV-* no guia → mapa de telas → código
```

Exemplo: "usuário pode excluir permissão", "admin pode excluir usuário" e "usuário pode
remover documento" são **uma** necessidade — confirmação de ação destrutiva — e viram
**um** `GV-CMP-020`, não três modais.

## Sumário
1. O que vai no guia do projeto (e o que não vai)
2. Entrada e saída
3. IDs `GV-*`
4. Necessidade × padrão × decisão de marca
5. Processo
6. Consistência, rastreabilidade e conflitos
7. Rodar de novo sem destruir decisões
8. Validação final

---

## 1. O que vai no guia do projeto (e o que não vai)

As regras universais — princípios, estados de tela, feedback, acessibilidade, hierarquia,
densidade, microcopy — **já estão nesta skill** e valem para todos os projetos. O guia do
projeto **não copia essas regras**. Ele registra só o que é deste produto:

| Vai no `guia-visual.md` | Não vai (já está na `ux-ui`) |
|---|---|
| Identidade: marca, fonte, logo, tema padrão, densidade | Princípios gerais de UX |
| Valores dos tokens (resumo; valor real em `tokens.json`) | Lista de estados de tela e como tratá-los |
| Componentes base com nome no código e variantes | Regras de contraste, foco, alvo de toque |
| Padrões do projeto `GV-*` derivados das Histórias | Anatomia genérica de botão, campo, modal |
| Termos de interface, decisões por plataforma | Regras de microcopy · vocabulário do domínio (fica no `docs/produto.md`) |
| Exceções aprovadas, pendências e conflitos | |

Guia enxuto é guia que a IA lê inteiro antes de cada tela. Guia de 21 seções repetindo a
skill vira texto que ninguém atualiza.

## 2. Entrada e saída

Leia nesta ordem: `docs/historias/` (skill `dah-historia`; ou `spec.md` do Spec Kit) →
`docs/produto.md` (vocabulário) → `docs/mapa-de-telas.md` → `docs/guia-visual.md` existente
→ `docs/mapa-de-fluxos.md`.

- Histórias determinam as necessidades.
- O mapa de telas mostra onde os padrões são usados.
- O guia existente guarda decisões já tomadas: prevalece sobre qualquer inferência nova.

Saída: `docs/guia-visual.md` (template em `assets/templates/docs/guia-visual.md`) e, se mudou
valor, `tokens/tokens.json` + `build-tokens.py --check`.

Ignore: índices, README, backups, temporários e Histórias com status `cancelada`.

## 3. IDs `GV-*`

```text
GV-CMP-###  componente do projeto        GV-FOR-###  padrão de formulário
GV-EST-###  estado específico do projeto GV-NAV-###  navegação
GV-LAY-###  layout de página             GV-ACS-###  decisão de acessibilidade do projeto
```

- Cor, tipografia, espaçamento e raio **não recebem GV-ID**: são tokens, e o nome do token
  já é o identificador (`colors.primary`, `space[4]`, `radius.md`).
- Todo `GV-CMP` aponta para o nome no código (`GV-CMP-001 → Button`), para a IA não criar
  outro componente com o mesmo papel.
- IDs nunca são renumerados nem reaproveitados. Novo elemento recebe o próximo livre;
  removido fica marcado `OBSOLETO` com a data.

O mapa de telas cita os IDs na seção **Componentes** de cada tela T- (formato da skill `dah-documentacao`).

## 4. Necessidade × padrão × decisão de marca

| Camada | Vem de | Exemplo |
|---|---|---|
| **Necessidade** | A História revela | ação principal |
| **Padrão** | O guia consolida | `GV-CMP-001 → Button` variante `primary` |
| **Decisão de marca** | O cliente/dono decide | cor de marca `#235AFF`, fonte Inter |

- **Pode inferir necessidade funcional**: "pesquisar alunos pelo nome" → campo de busca.
- **Não pode inventar decisão de marca**: cor de marca, fonte, logo, ilustração, tom da
  marca. Sem informação → `PENDENTE_DE_DEFINICAO` no guia.
- **Valor estrutural não fica pendente**: espaçamento, raio, tipografia, estados, contraste,
  alvo de toque usam o padrão da casa (`assets/tokens/tokens.json`) até alguém decidir outro.
  O app nunca fica sem funcionar por falta de decisão.

Enquanto a marca estiver pendente, o `tokens.json` usa o valor padrão da casa e o guia
registra `PENDENTE_DE_DEFINICAO (usando padrão da casa)`. Quando o valor chegar, atualize
o guia, o `tokens.json` e rode `--check`.

## 5. Processo

1. **Ler as Histórias** e achar a função real de cada elemento citado — não crie um
   componente por palavra encontrada.
2. **Agrupar** necessidades recorrentes entre Histórias diferentes.
3. **Ler o guia existente inteiro** antes de mudar qualquer coisa.
4. **Classificar** cada necessidade:

| Classificação | Quando | Ação |
|---|---|---|
| `REUTILIZAR` | Já existe componente base ou `GV-*` com esse papel | Citar o ID no mapa de telas |
| `ALTERAR` | Existe, mas falta variante/estado | Acrescentar variante; registrar versão e motivo |
| `CRIAR` | Necessidade recorrente sem padrão | Novo `GV-*` com Histórias relacionadas |
| `PENDENTE` | Depende de decisão de marca ou de negócio | `PENDENTE_DE_DEFINICAO` na seção de pendências |
| `OBSOLETO` | Nenhuma História ativa usa mais | Marcar, não apagar o ID |
| `SEM IMPACTO` | História não muda a interface | Nada |

Ordem de preferência: **reutilizar → variante → criar**. Antes de criar, confira os
componentes base da `expo-app` (`Button`, `FormInput`, `components/feedback`, `Screen`):
a maioria das necessidades cabe neles.

5. **Incorporar só o necessário** e atualizar o mapa de telas com os IDs.

Formato de um padrão do projeto:

```md
### GV-CMP-020 — Confirmação de ação destrutiva
- **Código:** `ConfirmDialog` (`components/ui/confirm-dialog.tsx`)
- **Finalidade:** confirmar ação irreversível ou de alto impacto
- **Estrutura:** título com a ação · consequência em uma frase · Cancelar · botão `danger` com o verbo ("Excluir aluno")
- **Variantes / estados:** carregando no botão de confirmar; erro inline no diálogo
- **Não usar:** ação reversível → prefira desfazer (`estados-e-feedback.md`)
- **Histórias:** H-020, H-022, H-031
```

## 6. Consistência, rastreabilidade e conflitos

- **Um papel, um padrão.** "Botão principal", "botão confirmar", "botão salvar azul" e
  "CTA" são `Button primary`. Diferença legítima vira **variante**, não componente novo.
- **Rastreabilidade:** todo `GV-*` lista as Histórias que o originaram. Elemento universal
  pode usar `Uso global`. Mudança grande registra `Alterado em <data>` e `Motivo`.
- **Conflito:** Histórias que pedem comportamentos incompatíveis não se resolvem
  escolhendo um lado. Registre em "Pendências e conflitos":

```md
- CONFLITO_VISUAL_OU_INTERACAO — H-014 pede confirmação antes de excluir; H-066 pede exclusão imediata sem confirmação. Decisão: PENDENTE.
```

- **Fronteira com o domínio:** **se** o usuário pode executar a ação é regra de negócio
  (RN-xx, backend). **Como** a indisponibilidade aparece (ocultar × desabilitar com
  motivo) é guia visual. A História não define cor, fonte, padding ou raio; o guia resolve.

Fora do escopo aqui: regra de negócio, banco, endpoint, algoritmo, arquitetura e código.

## 7. Rodar de novo sem destruir decisões

O processo roda a cada leva de Histórias. Decisões já registradas — cores, fontes,
identidade, logo, exceções aprovadas, decisões de UX — são preservadas. Uma História nova
não sobrescreve decisão global sem evidência explícita; se parecer que deveria, registre
como conflito e pergunte.

## 8. Validação final

- **Consistência:** algum `GV-*` duplica um componente base ou outro `GV-*`? Nome
  diferente para o mesmo papel? Variante que virou componente?
- **Cobertura:** toda necessidade recorrente tem padrão? Toda tela do mapa cita seus `GV-*`?
- **Pendências:** toda decisão de marca ausente está como `PENDENTE_DE_DEFINICAO`, com o
  padrão da casa em uso?
- **Rastreabilidade:** todo `GV-*` novo tem Histórias relacionadas?
- **Tokens:** mudou valor? `tokens.json` atualizado e `--check` passou?
