# Template e exemplos por campo

## Template obrigatório

```md
# <Nome>

**Código:** H-000

**Status:** rascunho

**Versão:** 1

**Capítulo:** <Capítulo>

**Contexto:** <Contexto>

**Local:** <Local>

## Atores

- Ator 1: <Ator>
- Ator 2: <Ator>

## O que acontece

1. <Passo 1>
2. <Passo 2>
3. <Passo 3>

## O que não pode acontecer

- <Restrição 1>
- <Restrição 2>

## Resultados possíveis

- **Sucesso:** <Estado final verificável>.
- **Falha 1:** <Estado final verificável da falha>.

**Histórias relacionadas:** <H-XXX, H-YYY ou Nenhuma>
```

Com um único ator, liste apenas `Ator 1`. Sem falha relevante, mantenha só o Sucesso. Não altere este formato sem pedido explícito.

---

## 1. Nome

Ação de negócio ou interação observável.

| Bom | Ruim |
|---|---|
| Criar novo usuário | Criar tabela usuário |
| Reservar vaga | Implementar endpoint |
| Cancelar matrícula | Fazer backend |
| Confirmar e-mail | Corrigir tela |

## 2. Código

`H-001`, `H-002`, `H-003`… Sequencial, único, permanente.

O Código identifica a História e **não representa a posição dela no fluxo funcional**. A sequência funcional vem de `Histórias relacionadas`. Uma História descoberta depois recebe o próximo Código livre mesmo que funcionalmente aconteça no meio de outras.

## 3. Status

| Valor | Significado |
|---|---|
| `rascunho` | Ainda pode mudar |
| `aprovada` | Validada; serve de referência para desenvolvimento |
| `implementada` | Desenvolvida e validada |
| `cancelada` | Fora do escopo ativo |

Estes quatro e mais nenhum.

## 4. Versão

Inteiro desde `1`: `1` → `2` → `3`. Incrementa a cada mudança funcional depois da primeira versão. Correção puramente ortográfica que não altera sentido não exige incremento.

## 5. Capítulo

Área funcional. Os capítulos do projeto ficam listados em `docs/produto.md` — ex.: `Acesso`, `Perfil`, `Agenda`, `Pagamentos`, `Administração / Usuários`.

Reutilize o Capítulo existente. Capítulo novo entra primeiro no `docs/produto.md`. Não crie dois nomes para o mesmo conceito.

## 6. Contexto

Condição inicial. Responde: em que estado o ator está, o que permite iniciar a História, que intenção levou ao início.

```
Usuário ainda não cadastrado acessa o fluxo de credenciamento e deseja criar um novo usuário.
```

Não coloque no Contexto o que pertence aos passos de **O que acontece**.

## 7. Local

Onde a interação principal acontece, em termos funcionais: tela, página, área, fluxo, ambiente.

| Bom | Ruim |
|---|---|
| `Tela de criação de usuário` | `Componente React CreateUser.tsx` |
| `Administração > Canais de comunicação > Configuração de e-mail` | `/admin/email-config` |

Liste mais de um Local apenas quando for necessário para entender o comportamento.

## 8. Atores

```md
## Atores

- Ator 1: Usuário não cadastrado
- Ator 2: Sistema
```

Os papéis do projeto ficam em `docs/produto.md` (ex.: `Usuário não cadastrado`, `Usuário cadastrado`, `Administrador`, `Sistema`). Cada ator é um papel funcional claro. Use o vocabulário oficial e não multiplique atores para o mesmo papel.

`Sistema` é o produto inteiro — nunca separe `App` e `Backend` como atores: isso é decisão de arquitetura, não de comportamento.

Um ator pode ser serviço externo quando ele age de forma observável no fluxo — ex.: `Ator 3: Provedor de e-mail`, `Ator 3: Gateway de pagamento`. Prefira o papel ao nome do fornecedor; o fornecedor pode mudar sem a História mudar.

## 9. O que acontece

Fluxo principal de sucesso, numerado, na ordem real. Cada passo é ação ou resposta observável, referindo o ator pelo identificador definido.

```md
1. Ator 1 informa o e-mail.
2. Ator 1 informa a senha.
3. Ator 1 solicita a criação do usuário.
4. Ator 2 valida as informações.
5. Ator 2 cria o usuário.
6. Ator 2 informa o resultado.
```

Validação que precisa ocorrer antes de uma mudança de estado aparece **antes** dela. Sem SQL, classe, arquivo, framework, endpoint ou comando técnico.

## 10. O que não pode acontecer

Restrições, validações, estados inválidos, comportamentos proibidos. Objetivos e verificáveis.

```md
- Não cria o usuário sem e-mail.
- Não cria o usuário sem senha.
- Não cria o usuário se a senha e a confirmação forem diferentes.
- Não cria o usuário se já existir outro usuário com o mesmo e-mail.
```

Evite termo subjetivo sem definição no projeto (`senha forte`, `valor adequado`, `prazo razoável`, `dado válido`). Quando o projeto já definiu, escreva a definição — Ex.: em vez de "senha forte", escreva "Não aceita senha com menos de 8 caracteres" e as demais regras concretas.

Quando a restrição exigir resposta específica do sistema, essa resposta vai em **Resultados possíveis**. Não repita o fluxo principal em forma negativa.

## 11. Resultados possíveis

Estados finais observáveis.

```md
- **Sucesso:** existe um usuário com status não confirmado e um código de confirmação foi enviado ao e-mail informado.
- **Falha 1:** se houver erro de preenchimento ou validação, o usuário não é criado e o motivo é apresentado.
- **Falha 2:** se o e-mail já estiver cadastrado e o usuário estiver validado, o usuário não é criado e é oferecida a recuperação de senha.
- **Falha 3:** se o e-mail já estiver cadastrado e o usuário não estiver validado, o usuário não é criado e é oferecido o reenvio do código.
```

Falhas podem ser: erro de preenchimento, erro de validação, estado incompatível, registro já existente, falta de permissão, falha de comunicação, indisponibilidade de serviço externo. Condições de falha com comportamentos diferentes ficam separadas.

Descreva o estado final e a resposta observável. Nunca `Operação realizada com sucesso.`

## 12. Histórias relacionadas

`H-002, H-010` — ou `Nenhuma`.

A primeira deve ser, sempre que existir, a **continuação natural do fluxo**. As demais representam alternativa, recuperação, dependência funcional ou fluxo complementar.

Não invente código inexistente. Quando a História necessária ainda não existir, registre fora da História como `História a criar: <nome sugerido>` e atualize o campo depois que ela receber Código oficial.

---

## Quando algo é História

Precisa ter: pelo menos um ator, um contexto inicial, um local funcional quando aplicável, uma ação, uma mudança observável de estado ou resposta, e ao menos um resultado verificável.

Não é História: criar tabela, instalar biblioteca, configurar servidor, criar endpoint isoladamente, alterar CSS sem necessidade funcional, criar classe, refatorar, configurar pipeline. São tarefas técnicas.

## Granularidade — exemplo

Evite a História gigante:

```
Usuário compra produto, paga, recebe nota, acompanha entrega e avalia pedido.
```

Prefira dividir:

```
H-010 Usuário adiciona produto ao carrinho
H-011 Usuário finaliza pedido
H-012 Usuário realiza pagamento
H-013 Usuário acompanha entrega
H-014 Usuário avalia pedido
```

## Acervo existente

Se o acervo tiver formatação mista (separadores `;` e `,`, marcadores `-` e `*`), não normalize em massa sem pedido — gera ruído em arquivos aprovados. Em arquivo novo, use `,` e `-`.
