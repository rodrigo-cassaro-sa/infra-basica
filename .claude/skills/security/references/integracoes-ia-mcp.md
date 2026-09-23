# Integrações, IA e MCP

Índice: integrações externas · SSRF · webhooks · OAuth · OTP e canais · pagamentos · fornecedores e disponibilidade · IA · RAG · tools e MCP.

---

## Integrações externas

Aplique sempre:

```text
TLS · timeout · retry controlado · auth · validação de schema
proteção do secret · allowlist de destino · scope mínimo
```

Resposta de terceiro é entrada não confiável: valide o schema antes de usar, mesmo que o provider seja conhecido e o contrato esteja documentado.

Sem timeout, a indisponibilidade do terceiro vira indisponibilidade sua.

---

## SSRF

O backend nunca busca URL arbitrária fornecida por usuário, integração ou modelo sem validar:

```text
scheme · host · IP resolvido · porta · redirects seguidos · DNS (rebinding)
```

Bloqueie a rede interna e os endpoints de metadata da cloud quando não forem necessários. Valide o IP **depois** da resolução e **a cada** redirect — validar só a string da URL não protege.

Superfícies comuns esquecidas: importação por URL, preview de link, webhook de saída configurável pelo cliente, geração de PDF a partir de HTML, avatar por URL, e fetch feito por agente de IA.

---

## Webhooks

**Recebendo**, valide:

```text
assinatura · timestamp (janela) · event_id · replay · schema
```

**Idempotência**: entrega duplicada não pode duplicar efeito. Provedores reenviam por design — duplicar cobrança, estoque ou e-mail é falha de segurança operacional, não só bug.

Webhook financeiro sempre valida assinatura e idempotência.

---

## OAuth

```text
state · PKCE quando aplicável · scope mínimo · redirect URI fixa
```

Nunca aceite redirect URI arbitrária — é o caminho clássico para roubo de código de autorização.

---

## OTP e canais

OTP por e-mail, SMS ou WhatsApp deve expirar, ter limite de tentativas e não ser reutilizável.

Não confie em links recebidos por e-mail automaticamente — e não construa fluxos que treinem o usuário a confiar neles.

---

## Pagamentos

Nunca confie apenas no retorno do frontend para confirmar pagamento — confirme com o provider.

O valor final é calculado e validado no backend. O frontend exibe; não decide.

---

## Fornecedores e disponibilidade

Avalie o risco do fornecedor quando a integração tratar dado sensível: contrato, retenção, região, política, necessidade real.

Indisponibilidade externa afeta segurança. Defina o comportamento antes que aconteça — provider de identidade fora do ar, por exemplo. Para controle de segurança, **fail closed** é geralmente preferível:

```text
permission service falhou → negar
```

não:

```text
permission service falhou → permitir
```

---

## IA

**O LLM nunca decide autorização.** A permissão é verificada em código, antes e depois da chamada ao modelo.

**Prompt injection**: todo conteúdo externo — documento, página, e-mail, resultado de ferramenta, campo preenchido por outro usuário — é instrução potencialmente hostil. Trate conteúdo como dado, nunca como comando.

**Dados enviados ao modelo**: aplique minimização. Nunca envie secret. Antes de mandar dado sensível a um provider externo, avalie contrato, retenção, região, política e necessidade.

**Logs de IA**: não registre prompt completo por padrão se ele puder conter PII ou segredo.

---

## RAG

Aplique a permissão **antes do retrieval**: o índice retorna apenas o que aquele usuário e aquele tenant podem ver.

Nunca recupere globalmente e peça ao modelo para ignorar o que não pode mostrar. Isso não é um controle — é uma sugestão, e o modelo não é o limite de segurança.

Cuide também do índice: embeddings e chunks carregam o dado original e herdam a mesma classificação de sensibilidade.

---

## Tools e MCP

O agente tem apenas as tools necessárias — least privilege vale para tools como vale para usuários.

MCP remoto exige:

```text
auth · authorization · least privilege · tool allowlist · logs · TLS
```

Regras duras:

- **Não exponha SQL genérico** ao agente. Exponha operações específicas e parametrizadas.
- **Não exponha shell genérico** sem sandbox forte e justificativa explícita.
- **Não permita fetch arbitrário** sem mitigação de SSRF.
- Toda tool que escreve, apaga, gasta dinheiro ou envia mensagem para fora precisa de confirmação ou de escopo estritamente limitado.
- A tool valida seus argumentos como valida os de qualquer entrada — o chamador é um modelo influenciável por conteúdo externo.

A combinação perigosa é: acesso a dado privado + exposição a conteúdo não confiável + capacidade de comunicação externa. Quando as três coexistem, reduza uma delas.

---

## Checklists

**Integração:**

```text
[ ] TLS
[ ] timeout
[ ] secret protegido
[ ] schema validado
[ ] webhook autenticado
[ ] idempotência
[ ] SSRF mitigado
[ ] scope mínimo
```

**IA/MCP:**

```text
[ ] LLM não decide permissão
[ ] RAG filtra por acesso antes do retrieval
[ ] tools em allowlist
[ ] sem shell/SQL genérico
[ ] prompt injection considerada
[ ] dados minimizados
[ ] secrets não enviados
[ ] MCP autenticado
```
