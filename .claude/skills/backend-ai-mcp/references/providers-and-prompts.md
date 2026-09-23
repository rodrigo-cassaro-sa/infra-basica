# Providers, modelos, AI services e prompts

Índice:
1. Abstração de provider
2. Catálogo de modelos
3. Modelo por caso de uso
4. AI Services
5. Output estruturado
6. Falha de parsing
7. Prompts são código
8. System prompt e separação instrução/dados
9. Timeout, retry e fallback
10. Cache
11. Context budget e histórico
12. Custos e orçamentos
13. AI Run

---

## 1. Abstração de provider

O domínio nunca importa SDK de provider. Ele conhece só a interface interna:

```python
from typing import Protocol


class LLMProvider(Protocol):
    def generate(
        self,
        *,
        messages: list[dict],
        model: str,
        temperature: float | None = None,
    ) -> str:
        ...
```

Cada provider tem seu adapter em `apps/ai/providers/`: `base.py`, `openai.py`, `anthropic.py`, `gemini.py`, `ollama.py`. O adapter traduz erros do SDK para `AITransientError`/`AIPermanentError` (`apps/ai/providers/base.py`), que herdam da hierarquia única da família (`common.errors.TransientError`/`PermanentError`). Assim a task da BE-03 (`autoretry_for=(TransientError,)`) e o handler da API (503/502) tratam IA igual a qualquer integração, sem conhecer classes de biblioteca externa.

Providers de LLM/embeddings são **desta skill**, não da backend-integrations. Registro por settings, sem dict hardcoded:

```python
AI_PROVIDERS = {"anthropic": "apps.ai.providers.anthropic.AnthropicProvider"}   # nome → dotted path
AI_MODELS = {"message_classify": {"provider": "anthropic", "model": "...", "timeout": 20}}
```

Motivo prático: trocar de provider por preço, região ou política de dados é um evento normal na vida de um produto. Se o SDK estiver espalhado, a troca vira refactor.

## 2. Catálogo de modelos

Nomes de modelo não ficam espalhados no código. Centralize um catálogo em settings:

```text
AI_MODELS                    (chave = nome do caso de uso, igual ao do AI service)
├── message_classify
├── contract_extract
├── docs_answer
├── embeddings
└── ...
```

Cada entrada pode conter: `provider`, `model`, `timeout`, `max_output_tokens`, `temperature`, `fallback`.

O código pede `get_llm_provider("message_classify")`, nunca a string do modelo.

## 3. Modelo por caso de uso

Não usar um único modelo para tudo:

```text
classificação simples  → modelo econômico
extração               → modelo econômico com structured output
raciocínio complexo    → modelo mais capaz
embeddings             → modelo específico de embedding
visão                  → modelo multimodal
```

## 4. AI Services

Serviços explícitos, um por caso de uso:

```python
def message_classify(*, actor, text: str) -> MessageClassification:
    """require_perm + tenant do actor dentro do service; nunca em transaction.atomic."""
    ...
```

Evite `llm.generate()` genérico espalhado pelo sistema — é o equivalente a fazer SQL cru dentro de views. O AI Service é o lugar onde prompt, modelo, schema, validação e instrumentação ficam juntos.

## 5. Output estruturado

Quando a saída alimenta código, ela precisa ser validável:

```python
from pydantic import BaseModel


class MessageClassification(BaseModel):
    category: str
    confidence: float
    reason: str | None = None
```

Fluxo:

```text
LLM → JSON/structured output → Pydantic → regra de domínio → uso
```

Quando usar cada forma:

| Texto livre | Estrutura |
| --- | --- |
| resumo, redação, explicação | classificação, extração |
| mensagem, conteúdo criativo | roteamento, parâmetros de tool, dados que vão ao banco |

## 6. Falha de parsing

Tratar explicitamente: JSON inválido, campo ausente, enum desconhecido, tipo incorreto, valor fora do limite.

Nunca salvar dado inválido só porque veio de um modelo. Falhar de forma controlada, com código de erro estável (MAIÚSCULAS: `AI_OUTPUT_INVALID`) que o app Expo saiba exibir.

## 7. Prompts são código

Prompts relevantes são versionados em arquivo:

```text
prompts/
├── message_classify/
│   ├── v1.txt
│   ├── v2.txt
│   └── metadata.yaml
└── contract_extract/
```

Em toda execução, registrar `prompt_name`, `prompt_version`, `provider`, `model`. Sem isso é impossível explicar por que a qualidade caiu na terça-feira.

Evolução de prompt:

```text
v1 em produção → v2 → avaliação offline → canary → comparação → promoção
```

Rollback deve ser trivial (trocar a versão ativa em config, não redeploy de emergência).

## 8. System prompt e separação instrução/dados

O system prompt define papel, objetivo, limites, formato de saída e comportamento diante de informação insuficiente. Ele **não** substitui permissão nem regra de negócio.

Estruture o contexto de forma que a fronteira seja visível:

```text
INSTRUÇÕES
...

DADOS DO USUÁRIO
...

CONTEXTO RECUPERADO
...
```

Conteúdo externo é dado, não instrução privilegiada. Ver `security.md`.

## 9. Timeout, retry e fallback

Toda chamada de LLM tem timeout. Trabalho longo vai para a BE-03. **Uma camada de retry:** em task, quem repete é a task; o adapter do provider não faz retry próprio (desligar o retry embutido do SDK, ex.: `max_retries=0`).

Retry só para falha transitória: timeout, 429, 502, 503, falha de conexão. Nunca repetir automaticamente: prompt inválido, schema inválido persistente, autorização negada, erro de negócio.

Fallback de provider/modelo é decisão deliberada, considerando política de dados, custo, recursos disponíveis, compatibilidade de schema, região e qualidade. **Fallback silencioso é anti-pattern**: mandar dado de cliente para outro provider sem política definida é incidente, não resiliência.

## 10. Cache

Cabe quando a entrada é estável, staleness é aceitável, a privacidade permite e o resultado é reutilizável.

A chave precisa considerar: `use_case`, `prompt_version`, `model/config`, input normalizado. Cache que ignora a versão do prompt serve resposta velha depois de um deploy.

## 11. Context budget e histórico

Prioridade do que ocupa contexto:

```text
1. instruções
2. dados essenciais
3. histórico recente
4. RAG relevante
5. contexto adicional
```

Corte de baixo para cima. Histórico de conversa não vai inteiro para sempre: use janela recente, resumo acumulado, memória estruturada ou recuperação seletiva.

## 12. Custos e orçamentos

Medir quando possível: input tokens, output tokens, embeddings, retries, custo estimado, provider, modelo, caso de uso.

Limites podem existir por requisição, usuário, tenant, funcionalidade, dia e mês. Agente **sempre** tem limite de custo.

## 13. AI Run

Para operações relevantes, persistir metadados:

```text
AIRun
├── id
├── use_case
├── provider
├── model
├── prompt_version
├── status
├── input_tokens
├── output_tokens
├── latency_ms
├── estimated_cost
├── created_at
└── error_code
```

Não é obrigatório salvar prompt e output completos — e muitas vezes é indesejável por privacidade e retenção. Ver `security.md`.

## 14. Frameworks

LangChain, LlamaIndex e similares entram quando reduzem complexidade real, e nunca definem o domínio:

```text
domínio → interfaces próprias → framework externo
```

Stack mínima recomendada para começar: SDK do provider, Pydantic, Django services, PostgreSQL, pgvector quando necessário, SDK de MCP quando necessário. Adicionar mais só com benefício comprovado.
