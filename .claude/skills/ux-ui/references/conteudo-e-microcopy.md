# Conteúdo e microcopy (pt-BR)

## Sumário
1. Tom
2. Botões e ações
3. Mensagens de sucesso, erro e confirmação
4. Estados vazios
5. Vocabulário oficial
6. Datas, horas, números e moeda
7. Notificações e permissões
8. Tabela rápida: ruim → bom

---

## 1. Tom

Simples, direto, curto, humano, específico. Voz ativa, frases em caixa normal (nada de
TÍTULO EM CAIXA ALTA), sem jargão técnico, sem enrolação, sem pedir desculpas em excesso.
Fale na linguagem de quem usa ("alunos", "turmas", "mensalidade"), não na de quem
programou ("registros", "entidades", "webhook"). Cada texto faz um trabalho só.

## 2. Botões e ações

- Verbo (+ objeto): **Salvar · Criar usuário · Enviar proposta · Confirmar pagamento ·
  Cancelar campanha**.
- Evite **OK / Continuar / Confirmar / Sim / Enviar** quando o resultado não é óbvio.
- Mesmo verbo do começo ao fim: botão "Arquivar" → toast "Arquivado" → filtro "Arquivados".
- Links dizem o destino ("Ver histórico de pagamentos"), nunca "clique aqui".

## 3. Mensagens

**Sucesso** — curto e específico: "Usuário criado." em vez de "Operação realizada com sucesso."

**Erro** — o que houve + o que fazer, sem culpar o usuário, sem código:
- Campo: "Digite um CPF válido (11 números)."
- Tela: "Não foi possível salvar este aluno. Tente novamente. Se continuar, fale com o suporte."
- Permissão: "Você não tem permissão para editar este usuário."
- Rede: "Sem conexão. Verifique sua internet e tente novamente."
Nunca: "Error 500", "Foreign key violation", "Falha desconhecida", "Ops! Algo deu errado :("
sem próximo passo. Detalhe técnico vai para o log.

**Confirmação** — pergunta específica + consequência + verbo no botão:
"Excluir campanha Vacinação ABC? As 120 doses agendadas serão canceladas. [Cancelar] [Excluir campanha]"
Nunca "Deseja proceder?".

## 4. Estados vazios

Título que diz o estado + frase que diz o próximo passo + ação:
"Nenhuma turma ainda · Crie uma turma para começar a matricular alunos. · [Criar turma]"

## 5. Vocabulário oficial

A mesma entidade tem **um nome** no produto inteiro (telas, botões, e-mails, notificações,
API de documentação para o usuário). Não alterne "Cliente" / "Empresa" / "Contratante" se é
a mesma coisa. O vocabulário do domínio fica em `docs/produto.md` (fonte única, usada também pelas
Histórias e pela API); termos só de interface ficam no `docs/guia-visual.md` §5. Siga-os em
toda tela gerada. Termo novo? Adicione lá antes de usar.

## 6. Datas, horas, números e moeda

UI e armazenamento não usam a mesma representação: banco/API em ISO (`2026-09-18`,
`2026-09-18T14:30:00-03:00`); UI em pt-BR.

| Tipo | Formato UI | Observação |
|---|---|---|
| Data | `18/09/2026` | se houver ambiguidade (público estrangeiro): `18 set 2026` |
| Data relativa | "hoje, 14:30" · "ontem" · "há 5 min" | com data completa acessível |
| Hora | `14:30` (24h) | indicar fuso quando houver mais de um |
| Número | `1.250` | |
| Moeda | `R$ 1.250,00` | |
| Percentual | `10,5%` | |
| Telefone | `(14) 99999-9999` | |
| CPF / CNPJ | `000.000.000-00` / `00.000.000/0000-00` | |

Use `Intl.DateTimeFormat('pt-BR')` / `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })`
— os templates `format.ts` das skills de stack já fazem isso. Nunca formate na mão.
Projeto multi-idioma: o locale vem do idioma atual e o fuso do aparelho; ver `i18n.md` §5.

## 7. Notificações e permissões

**Notificação**: contexto + informação + ação. "Aula remarcada — Forró iniciante de quinta
passou para 20h. [Ver agenda]". Nunca "Você possui uma nova notificação."

**Pedido de permissão (pré-prompt)**: por que + benefício, antes do prompt do sistema.
"Para enviar lembretes de aula, precisamos da permissão de notificações." [Permitir] [Agora não]

**Ação sensível**: o quê, em quem, impacto. "Desativar João Silva? Ele perderá acesso
ao sistema imediatamente."

## 8. Ruim → bom

| Ruim | Bom |
|---|---|
| Operação realizada com sucesso. | Aluno matriculado. |
| Deseja proceder? | Cancelar a matrícula de Ana? |
| OK | Salvar alterações |
| Buscar... | Buscar alunos por nome ou telefone |
| Erro 403 | Você não tem permissão para ver os pagamentos. |
| Nenhum resultado. | Nenhum aluno em "Inativos". [Limpar filtros] |
| Excluir selecionados? | Excluir 27 alunos? |
| ↑ 8% | ↑ 8% vs. agosto |
| Campo inválido | Digite a data no formato dd/mm/aaaa. |
