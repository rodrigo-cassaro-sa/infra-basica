# Agentes e tools

Índice:
1. Quando usar agente
2. Agente controlado
3. Tools de leitura e escrita
4. Schema e granularidade de tool
5. Tools perigosas
6. Validação de tool
7. Human-in-the-loop
8. Confiança e determinismo
9. Observabilidade de agentes

---

## 1. Quando usar agente

Agente é um modelo capaz de escolher ações/tools em múltiplos passos.

Em processo empresarial crítico:

```text
workflow determinístico  >  agente irrestrito
```

Se você consegue desenhar o fluxo como uma máquina de estados, implemente a máquina de estados. Agente é para quando o caminho realmente depende de interpretação e o espaço de ações é grande demais para enumerar.

## 2. Agente controlado

Todo agente tem, sem exceção:

```text
objetivo
tools permitidas (allowlist)
max_steps
timeout
budget
escopo de dados
condição de parada
```

`max_steps = 8` é um ponto de partida razoável. Ao atingir o limite, finalizar de forma controlada e registrar o motivo de parada — nunca loop indefinido.

Cada agente enxerga apenas as tools do seu caso de uso, mesmo que o servidor exponha mais:

```text
agente X → tool A, B, C
```

## 3. Tools de leitura e escrita

Separar explicitamente:

```text
READ TOOLS    → padrão, expostas primeiro
WRITE TOOLS   → exigem justificativa e controles adicionais
```

Começar todo agente e todo MCP server com leitura. Escrita entra com caso de uso e política claros, atrás de feature flag (`MCP_WRITE_TOOLS_ENABLED`, `AI_AGENT_V2_ENABLED`).

## 4. Schema e granularidade de tool

Toda tool tem entrada explícita e validável:

```python
class CancelInvoiceInput(BaseModel):
    invoice_id: int
    reason: str
```

Tools pequenas e específicas:

```text
✅ find_customer, get_invoice, cancel_invoice, create_followup
❌ execute_anything, run_sql, run_shell, manage_database
```

Tool específica é auditável, testável e permissionável. Tool genérica é uma porta aberta com nome bonito.

## 5. Tools perigosas

Não expor genericamente: shell, filesystem arbitrário, SQL livre, `eval`, `exec`, HTTP para qualquer URL, admin universal.

Se execução de código for requisito real do produto: sandbox isolado, sem segredos, sem rede por padrão, limites de CPU/RAM/tempo, filesystem descartável.

## 6. Validação de tool

Mesmo que o modelo escolha a tool, a ordem é sempre:

```text
schema → autenticação → autorização → escopo → regra de negócio → execução
```

O modelo escolhe a intenção; o backend decide se pode. Ações devem ser idempotentes sempre que possível, porque retry acontece.

## 7. Human-in-the-loop

Ações de maior impacto exigem confirmação humana: apagar dados, enviar comunicação em massa, cancelar cobrança, aprovar pagamento, alterar permissões, qualquer ação irreversível.

```text
agente propõe → PendingAction → humano confirma → service executa
```

No backend desacoplado, `PendingAction` (model em `assets/templates/models_airun.py`, dono: esta skill) é um recurso normal da API: o app lista as pendências, mostra o que o agente quer fazer e com qual argumento, e o usuário confirma. O agente nunca executa a ação sensível diretamente.

```text
POST /api/v1/ai/pending-actions/{id}/confirm/
  → service pending_action_confirm(actor=request.user, pending_action_id=...)
      → valida status/expiração (select_for_update)
      → chama o service do core registrado para `action` com **arguments + actor=quem confirmou
        (o require_perm do core vale para o humano que confirmou, não para o agente)
      → marca confirmed
```

O mapa `action` → service fica explícito em `settings.AI_CONFIRMABLE_ACTIONS = {"invoice_cancel": "apps.billing.services.invoice_cancel"}` — ação fora do mapa é recusada. Este é o padrão único de confirmação para ação pedida por IA (o `confirmed: bool` no service não é usado).

## 8. Confiança e determinismo

Score de confiança gerado pelo próprio modelo não é probabilidade calibrada. Se confiança for crítica: medir, calibrar, definir threshold e permitir revisão humana abaixo dele.

Quando reprodutibilidade importa: versionar prompt e modelo, controlar parâmetros, registrar a configuração, usar output estruturado e manter dataset de teste. Ainda assim, modelos variam — o sistema precisa tolerar isso.

Conteúdo gerado não é dado validado:

```text
LLM → extração → validação → confirmação quando necessária → persistência
```

## 9. Observabilidade de agentes

Medir: passos executados, tools chamadas, erros, tempo total, custo, motivo de parada, ações bloqueadas, confirmações humanas.

Correlacionar `correlation_id`, `ai_run_id`, `job_id`, `tool_call_id`, `mcp_request_id` para conseguir reconstruir um incidente.

Registrar o necessário para operar — inputs permitidos, outputs úteis, tools, métricas, decisões explícitas do workflow — e não depender de raciocínio interno do modelo como se fosse log de sistema.
