# Checklists e Definition of Done

Use o checklist correspondente ao que foi implementado, antes de abrir o PR. Em revisão de código, use o mesmo checklist como roteiro e aponte os itens ausentes.

---

## Novo caso de uso de IA

```text
[ ] IA é realmente necessária?
[ ] regra determinística foi separada?
[ ] caso de uso está definido e nomeado?
[ ] provider está abstraído?
[ ] modelo é configurável (catálogo, não string solta)?
[ ] prompt está versionado?
[ ] output estruturado quando necessário?
[ ] resposta é validada?
[ ] dados foram minimizados?
[ ] dados sensíveis foram revisados?
[ ] timeout definido?
[ ] retry definido (só para falha transitória)?
[ ] custo conhecido?
[ ] limite de tokens definido?
[ ] métricas definidas (AIRun)?
[ ] testes adversariais considerados?
```

## RAG

```text
[ ] fonte identificada
[ ] original preservado em MinIO/S3
[ ] hash/versionamento definido
[ ] metadata suficiente (tenant, permission_scope); retrieval recebe actor
[ ] chunking testado
[ ] embedding versionado
[ ] vector store definido
[ ] autorização antes do retrieval
[ ] tenant filtrado por SQL
[ ] top-k avaliado
[ ] ausência de evidência tratada (AI_INSUFFICIENT_CONTEXT)
[ ] referências disponíveis na resposta
[ ] avaliação de retrieval criada
```

## Agente

```text
[ ] agente é necessário?
[ ] workflow determinístico não seria melhor?
[ ] objetivo explícito
[ ] tools em allowlist
[ ] write tools separadas
[ ] permissões verificadas no backend
[ ] max_steps
[ ] timeout
[ ] budget
[ ] condição de parada
[ ] ação sensível exige confirmação (PendingAction)?
[ ] logs/tracing
[ ] idempotência das ações
[ ] prompt injection testada
```

## MCP Server

```text
[ ] SDK oficial utilizado
[ ] versão fixada no pyproject.toml
[ ] revisão do protocolo conhecida
[ ] tools representam o domínio
[ ] resources possuem autorização
[ ] prompts não contêm segredos
[ ] autenticação definida
[ ] autorização por tool/resource
[ ] least privilege
[ ] write tools justificadas
[ ] sem SQL/shell genérico
[ ] HTTPS quando remoto
[ ] rate limiting
[ ] logs
[ ] métricas
[ ] testes com MCP client
```

## MCP Client

```text
[ ] servidor está em allowlist
[ ] URL validada
[ ] autenticação segura
[ ] credencial fora do código
[ ] tools permitidas definidas
[ ] timeout
[ ] retry
[ ] output validado por schema
[ ] dados externos tratados como não confiáveis
[ ] prompt injection considerada
[ ] logs/tracing
```

## Segurança

```text
[ ] modelo não decide autorização
[ ] nenhum segredo enviado ao LLM
[ ] tools respeitam permissões
[ ] RAG respeita tenant
[ ] URLs externas controladas
[ ] SQL gerado não executado diretamente
[ ] código gerado não usa eval/exec
[ ] arquivos validados
[ ] outputs validados
[ ] retenção definida
[ ] logs não vazam dados desnecessários
```

## Backend desacoplado do app (Expo)

```text
[ ] nenhuma chave de provider acessível ao front
[ ] contrato da API não expõe provider/modelo/prompt
[ ] permissão checada no DRF antes do AI Service
[ ] operação longa devolve job (202 + id), não request de 90s
[ ] erros de IA têm códigos estáveis MAIÚSCULOS; provider → AITransientError/AIPermanentError (common.errors)
[ ] streaming respeita auth, limites, cancelamento e logs
[ ] REST e MCP reutilizam os mesmos services/selectors
```

---

## Definition of Done — BE-04

Uma implementação de IA/MCP está pronta quando:

1. IA está separada do domínio;
2. regras determinísticas continuam no backend;
3. providers estão encapsulados;
4. prompts importantes estão versionados;
5. outputs usados por código são validados;
6. permissões nunca dependem do LLM;
7. dados enviados ao provider foram minimizados;
8. segredos não entram em prompts;
9. custo e limites foram considerados;
10. timeouts e retries estão definidos;
11. RAG respeita autorização e tenant;
12. modelo, embedding e índice são versionados;
13. agentes possuem tools limitadas, timeout, steps e budget;
14. ações sensíveis possuem controle adicional;
15. MCP reutiliza services/selectors do domínio;
16. MCP não expõe SQL, shell ou ORM genérico;
17. MCP remoto possui autenticação e autorização;
18. clientes MCP usam allowlist;
19. logs e métricas permitem investigação;
20. testes cobrem outputs inválidos, falhas e permissões;
21. avaliações existem para casos relevantes;
22. feature flags/rollback existem para mudanças de maior risco.
