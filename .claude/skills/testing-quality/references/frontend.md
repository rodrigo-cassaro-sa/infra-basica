# Trilha frontend

Leia quando a mudança tocar componentes, formulários, navegação, estados de tela, usabilidade, acessibilidade, responsividade ou mobile.

## Índice

1. [O que o frontend prova e o que não prova](#1-o-que-o-frontend-prova-e-o-que-não-prova)
2. [Componentes](#2-componentes)
3. [Formulários](#3-formulários)
4. [Navegação](#4-navegação)
5. [Estados de tela](#5-estados-de-tela)
6. [Erro, retry e concorrência](#6-erro-retry-e-concorrência)
7. [Usabilidade](#7-usabilidade)
8. [Acessibilidade](#8-acessibilidade)
9. [Responsividade e compatibilidade](#9-responsividade-e-compatibilidade)
10. [Mobile](#10-mobile)
11. [Visual e snapshots](#11-visual-e-snapshots)

---

## 1. O que o frontend prova e o que não prova

Prova: que a interface reage corretamente ao que o backend responde — mostra erro, bloqueia ação, exibe vazio, redireciona.

Não prova: autorização. Botão escondido não é permissão. O teste real de permissão vive no backend (`references/backend.md`, seção 6). Esconder o botão **e** negar no servidor são dois requisitos, com dois testes.

---

## 2. Componentes

Teste componentes que têm comportamento próprio — não os que só repassam props.

```text
renderização com os dados esperados
estado interno
interação (click, change, submit)
validação
erro
loading
disabled
```

Teste pelo que o usuário percebe (texto, papel, rótulo acessível), não por detalhes internos de implementação. Teste amarrado a estrutura interna quebra a cada refatoração sem indicar defeito real.

---

## 3. Formulários

```text
[ ] campos obrigatórios
[ ] validação por campo
[ ] mensagem de erro visível e clara
[ ] envio
[ ] loading durante envio
[ ] sucesso
[ ] falha (erro de API, erro de validação do servidor)
```

Erro do servidor precisa aparecer no campo certo quando a API indicar campo — não só um toast genérico.

---

## 4. Navegação

```text
rota carrega a tela certa
redirecionamento
acesso autenticado
acesso não autorizado → para onde vai
fluxo entre telas
```

---

## 5. Estados de tela

Toda tela relevante considera:

```text
loading
success
error
empty
disabled
offline quando aplicável
```

O estado vazio é o mais esquecido e o mais visível para o usuário novo. Trate-o como requisito, não como sobra.

---

## 6. Erro, retry e concorrência

**Erro de API**: a tela mostra estado de erro adequado — não quebra, não fica em loading infinito, não mostra tela em branco.

**Retry**: quando existir, manual ou automático, testar que refaz a chamada e recupera o estado.

**Submit duplicado**: quando a ação pode gerar duplicidade relevante (pagamento, criação, envio), testar a proteção — botão desabilitado durante envio, guard de requisição em voo, ou o que o projeto adotar.

---

## 7. Usabilidade

Quando a história tem interface, registre no mapa de testes os cenários de usabilidade aplicáveis:

```text
clareza da ação principal
validação e mensagens de erro
loading
sucesso
estado vazio
confirmação de ação destrutiva
navegação
responsividade
acessibilidade
```

Usabilidade aqui não é avaliação estética. Cada item vira teste com **comportamento observável e resultado esperado**:

| Ruim | Bom |
|---|---|
| "a tela está confusa" | "ao excluir item, aparece confirmação com nome do item e ação de cancelar" |
| "o erro é feio" | "e-mail inválido exibe mensagem abaixo do campo e impede o envio" |

---

## 8. Acessibilidade

Validar quando aplicável, especialmente em interface pública:

```text
labels associados aos campos
navegação por teclado
contraste
semântica (headings, landmarks, roles)
foco visível e gerenciado após ação/modal
leitores de tela
```

---

## 9. Responsividade e compatibilidade

Testar pontos relevantes do layout:

```text
mobile
tablet quando aplicável
desktop
```

Matriz de compatibilidade definida pelo produto (Chrome, Firefox, Safari, Edge, Android, iOS). Não testar plataforma fora do escopo sem necessidade — custo sem risco correspondente.

---

## 10. Mobile

Validar quando aplicável:

```text
navegação
permissões do dispositivo
estado offline
deep links
armazenamento local
integração com API
layout
```

Offline só é testado quando a funcionalidade exige operar sem conexão.

---

## 11. Visual e snapshots

QA-01 verifica comportamento, estados, responsividade básica e consistência com `docs/guia-visual.md`.

Snapshots: use com cuidado. Nunca aceitar atualização de snapshot sem revisar a mudança — snapshot aprovado no automático transforma regressão visual em commit silencioso.

Visual regression automatizado pode ser adotado para interface estável e crítica. Não é obrigatório no início do projeto.
