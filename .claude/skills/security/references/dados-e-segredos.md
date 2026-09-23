# Dados, segredos e observabilidade

Índice: segredos · rotação · criptografia · dados pessoais e sensíveis · minimização · logs · mascaramento · auditoria · alertas.

---

## Segredos

Nunca versione:

```text
senha · token · API key · private key · SECRET_KEY · credencial de banco
```

Use variáveis de ambiente, secret manager ou o cofre da plataforma de deploy.

**`.env.example`** contém nomes de variáveis. Nunca valores reais — nem "de desenvolvimento", porque eles costumam virar os de produção.

Segredo não aparece em: log, URL, analytics, mensagem de erro, payload de fila, prompt de LLM, artefato de CI, imagem Docker ou bundle de frontend.

---

## Rotação

Projete o sistema para trocar API key, senha, certificado e client secret **sem quebrar**. Se a rotação exige downtime ou deploy coordenado, ela não vai acontecer quando for urgente — e é justamente quando um segredo vaza que ela precisa ser imediata.

Quando um segredo já esteve em um repositório, considere-o comprometido: rotacione, não apenas remova o commit.

---

## Criptografia

**Em trânsito**: produção usa HTTPS/TLS. Evite tráfego sensível em HTTP puro, inclusive entre serviços internos quando a rede não for confiável.

**Em repouso**: avalie conforme a sensibilidade — disco, storage, backup, campos específicos.

Não invente criptografia própria. Use as primitivas e bibliotecas do ecossistema.

**Chaves** não ficam guardadas junto do dado criptografado sem controle adequado — isso anula o controle.

---

## Dados pessoais e sensíveis

Para dado pessoal aplique: **minimização, finalidade, controle de acesso, retenção, auditoria**.

Para dado sensível — saúde, financeiro, identidade, credenciais — a revisão é mais rigorosa: menos pessoas com acesso, mais auditoria, retenção mais curta, criptografia mais provável.

---

## Minimização

```text
guardar somente o necessário
trafegar somente o necessário
expor somente o necessário
reter somente pelo tempo necessário
```

É o controle mais barato que existe: dado que não foi coletado não vaza, não precisa ser criptografado e não aparece em incidente.

---

## Logs

Nunca registre:

```text
senha · token · cookie · API key · chave privada
dados pessoais desnecessários
payload completo de requisição sensível
```

Logs têm acesso restrito. Observabilidade não pode virar canal de vazamento — o APM, o agregador de logs e o rastreamento de erro costumam ter menos controle de acesso que o banco, e recebem os mesmos dados.

**Não logue prompt completo de IA por padrão** se ele puder conter PII ou segredo.

---

## Mascaramento

Quando a visualização parcial for necessária:

```text
CPF: ***.***.***-12
Token: ****abcd
```

Mascare na geração do log, não na exibição — o que chega ao log já não deve ter o valor completo.

---

## Auditoria

Operações críticas registram **quem, o quê, quando, qual recurso, qual resultado**.

Auditoria não substitui log técnico: ela responde a perguntas de responsabilidade, não de depuração. Alvos típicos: mudança de permissão, exclusão, exportação, acesso a dado sensível, ação administrativa, login com sucesso e falha.

---

## Alertas de segurança

Considere alertar em:

```text
muitas falhas de login
mudança de permissão
elevação de privilégio
token inválido repetido
acesso suspeito ou fora do padrão
volume anormal de exportação
```

Alerta sem alguém para responder é apenas ruído — defina quem recebe e o que faz.
