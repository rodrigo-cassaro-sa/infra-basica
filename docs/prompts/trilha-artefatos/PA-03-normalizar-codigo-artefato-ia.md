# PA-03 — Normalizar e Integrar Código de Artefato de IA

## Tipo

```text
PROMPT AVULSO
```

Conteúdo técnico extraído do antigo PA-01 v2 (seções 24–38).

---

# Pré-requisito

Executar **somente** para comportamentos que já têm H-xxx oficial aprovada:

```text
PA-01 → PA-02 → revisão humana → P-01 → P-02 oficial → PA-03 → P-05
```

Se não houver H-xxx aprovada: parar e indicar o fluxo acima.

Comando:

```text
PA-03 H-027 (origem: A-001)
```

---

# 1. Entradas

```text
história oficial H-xxx
história provisória A-xxx correspondente
analise-artefato/inventario.md
artefato original
AGENTS.md
docs/modelo-de-dados.md
docs/contratos-de-api.md
docs/guia-visual.md
docs/mapa-de-decisoes.md
```

---

# 2. Stack oficial prevalece

Não adotar a stack do artefato silenciosamente.

```text
Exemplo:
Artefato: React + Firebase
Projeto:  Expo + Django + PostgreSQL

extrair comportamento → preservar interface útil → adaptar à stack oficial
```

A H-xxx oficial é a especificação. O artefato é só referência de implementação.

---

# 3. Frontend

Identificar componentes reutilizáveis, rotas, layout, interações, mock data, APIs falsas, dependências e assets. Não copiar cegamente.

Conversão React Web → Expo (sempre semântica, nunca substituição textual):

```text
div → View
p / span → Text
button → Pressable
input → TextInput
img → Image
```

Tratar navegação, estilos (CSS → StyleSheet/tema oficial) e eventos caso a caso.

---

# 4. Backend

Normalizar para a arquitetura oficial:

```text
Django / DRF
models
services
selectors
permissions
tasks
integrations
```

---

# 5. Banco

Se o artefato usar Firebase, Supabase, SQLite, MongoDB, JSON ou localStorage, extrair:

```text
entidades, campos, relações, constraints, estados
```

Comparar com `docs/modelo-de-dados.md`. Divergências precisam de decisão humana antes de migration.

---

# 6. API

Comparar endpoints com `docs/contratos-de-api.md`:

```text
compatível / parcial / incompatível / não documentado
```

Endpoint não documentado não entra sem atualizar o contrato via fluxo oficial.

---

# 7. Mocks

Identificar e remover ou substituir:

```text
dados hardcoded, setTimeout, Promise.resolve, JSON local, usuário fictício, API fake
```

Mock não é backend.

---

# 8. Dependências

Analisar `package.json`, `requirements.txt`, `pyproject.toml` e lockfiles.

Importar só o que a implementação oficial usa. Não trazer dependências órfãs. Nova dependência relevante → registrar decisão.

---

# 9. Secrets

Nunca importar senha, token, API key, private key ou credential. Substituir por variável de ambiente e documentar em `.env.example`.

---

# 10. Segurança

Código de IA não é presumido seguro. Acionar **SEC-01** quando houver autenticação, permissões, upload, pagamento, dados pessoais ou integração externa.

---

# 11. Validação técnica

```text
lint
typecheck
tests
build
```

Expo: `npx expo-doctor`
Django: `python manage.py check` e `pytest`

---

# 12. Registros oficiais

- Decisões relevantes → `docs/mapa-de-decisoes.md`
- Diário → só quando a importação afeta o projeto oficial
- Cronograma → só via H-xxx (A-xxx nunca entra)

---

# 13. Relação com P-05

```text
PA-03 normaliza → P-05 testa e conclui
```

PA-03 nunca substitui P-05 e nunca marca história como concluída.

---

# Regra final

```text
PA-03 SÓ TOCA EM CÓDIGO DEPOIS QUE A H-xxx EXISTE.
A HISTÓRIA OFICIAL MANDA. O ARTEFATO É REFERÊNCIA.
STACK OFICIAL PREVALECE. MOCK NÃO É BACKEND. SECRET NUNCA ENTRA.
```
