# MCP Server — expor o backend para hosts de IA

Índice:
1. O que é e o que não é
2. Estrutura
3. Tools, resources e prompts
4. SDK e versionamento
5. Exemplos
6. Transportes e operação remota
7. Autenticação e autorização
8. Privilégio mínimo e read-only por padrão
9. Ações sensíveis e trabalho longo

---

## 1. O que é e o que não é

MCP é um protocolo padronizado para conectar aplicações de IA a dados e funcionalidades. O backend pode ser MCP Server, MCP Client ou ambos.

**MCP não substitui REST:**

```text
REST → app Expo (web, iOS, Android), integrações convencionais
MCP  → hosts, assistentes e agentes de IA
```

Os dois reutilizam os mesmos services e selectors. MCP é camada de apresentação/adaptação — nunca camada de domínio.

```text
                   DOMÍNIO
                     │
             ┌───────┴───────┐
             ▼               ▼
          REST/DRF          MCP
             │               │
             ▼               ▼
        Painel web       AI Hosts
```

## 2. Estrutura

```text
apps/mcp/
├── server.py
├── tools/
├── resources/
├── prompts/
├── auth.py
└── clients/
```

## 3. Tools, resources e prompts

**Tools** representam ações/capacidades executáveis, e cada uma chama um service ou selector do domínio:

```text
find_customer
get_campaign_status
create_opportunity
schedule_followup
```

**Resources** representam contexto legível, também sujeitos a autorização:

```text
customer://123
campaign://456
policy://sales
report://weekly/2026-38
```

**Prompts** expõem templates reutilizáveis: versionáveis, documentados, limitados ao escopo do produto e livres de segredos.

## 4. SDK e versionamento

Usar o SDK oficial Python, com versão fixada no `pyproject.toml`. Atualização de major version passa por:

```text
migration guide → testes → homologação → deploy controlado
```

Registrar também qual revisão do protocolo o servidor suporta.

## 5. Exemplos

Esqueleto conceitual (confirme a API exata na versão do SDK fixada no projeto):

```python
from mcp.server import MCPServer

mcp = MCPServer("backend")


@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

Em projeto real, a tool delega ao domínio e a autorização acontece **antes** de qualquer dado sair:

```python
@mcp.tool()
def get_customer(customer_id: int) -> dict:
    customer = get_customer_details(customer_id=customer_id)

    return {
        "id": customer.id,
        "name": customer.name,
    }
```

Note o retorno explícito: a tool devolve um dicionário controlado, não o objeto do ORM serializado inteiro. Expor `model_to_dict` é como expor a tabela.

## 6. Transportes e operação remota

```text
stdio            → desenvolvimento/local quando apropriado
Streamable HTTP  → servidor remoto
```

Compatibilidade adicional só com requisito real.

Servidor remoto opera com HTTPS, reverse proxy, auth, rate limiting, logs e observabilidade. Nunca expor servidor de desenvolvimento diretamente à Internet.

## 7. Autenticação e autorização

MCP remoto tem estratégia explícita de autenticação, usando os mecanismos previstos pela revisão vigente do protocolo, incluindo OAuth quando aplicável.

Autenticação não substitui autorização. Para cada tool/resource, verificar: identidade, tenant, escopo, permissão, objeto.

Como isso é feito sem duplicar regra:

- `apps/mcp/auth.py` só **autentica** o host e resolve `principal.user` (um `accounts.User` real ou técnico, com permissões mínimas).
- Permissão = `common.permissions.require_perm(user, "app.codename")` — a mesma do core. Sem função `require_permission` paralela.
- Tenant e objeto = selector do core chamado com `actor=user` (`scope_to_tenant`). A tool **nunca** passa `tenant_id` explícito.
- `DomainError` volta ao modelo como `{"error": exc.to_dict()}`.

## 8. Privilégio mínimo e read-only por padrão

Expor apenas as capacidades necessárias. Nunca publicar automaticamente todos os models, todas as tabelas ou todas as ações — gerador automático de tools a partir do ORM é anti-pattern.

Começar com tools e resources de leitura. Escrita entra depois, com política clara.

## 9. Ações sensíveis e trabalho longo

Escrita crítica:

```text
modelo solicita → servidor valida → PendingAction quando necessário → confirmação → service executa
```

Trabalho longo que pertence ao domínio não bloqueia a tool:

```text
MCP tool → service cria AIJob/Job → evento/task (BE-03) → worker → resultado persistido
```

A tool devolve o identificador do job; o host consulta o status depois.
