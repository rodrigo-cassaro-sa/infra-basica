# Testes, gate e Definition of Done

Índice: threat modeling · abuse cases · critérios de aceite · mapa de testes · testes automatizados · security gate · exceção de risco · checklists de revisão · DoD.

---

## Threat modeling

Para histórias críticas, quatro perguntas bastam na maior parte dos casos:

```text
o que pode dar errado?
quem poderia abusar disso?
qual ativo está em risco?
qual controle reduz o risco?
```

**Ativos** típicos: credenciais, dados pessoais, dinheiro, permissões, documentos, segredos, serviços.

Quando a análise formal for útil, percorra STRIDE — spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege.

---

## Abuse cases

O abuse case é o cenário do atacante escrito como teste. Ele é o produto mais valioso desta skill, porque transforma "tem que ter autorização" em algo verificável.

Cenários base, aplicáveis a quase toda história:

```text
usuário não autenticado tenta acessar recurso privado
usuário autenticado sem permissão tenta ler o recurso
usuário autenticado sem permissão tenta alterar o recurso
usuário tenta acessar objeto de outro tenant pelo ID
payload tenta alterar campo não permitido (tenant_id, is_admin, status, preço)
resposta expõe campo desnecessário
upload inválido (tamanho, tipo, conteúdo, nome) é enviado
arquivo privado é acessado sem autorização
rate limit é excedido
token expirado ou revogado é reutilizado
webhook duplicado é reenviado
```

---

## Critérios de aceite de segurança

A história pode carregar critérios verificáveis, como:

```text
usuário sem permissão recebe 403
token expira após X
arquivo privado não é acessível sem autorização
tenant B não vê recurso do tenant A
```

Critério de segurança bem escrito tem sujeito, ação e resultado observável.

---

## Mapa de testes

Os cenários derivados da história são registrados em:

```text
docs/mapa-de-testes.md
```

Com rastreabilidade:

```text
T-xxx → H-xxx → controle de segurança
```

Divisão de responsabilidade: **a SEC-01 define os cenários e valida se a cobertura de segurança é suficiente; a QA-01 automatiza e executa.** Um cenário que existe no mapa mas nunca foi executado não conta como controle.

---

## Testes automatizados

Priorize testes de autorização sobre testes de "caminho feliz autenticado" — a falha real quase nunca é "não consigo entrar", é "consigo ver o que não é meu".

Para cada endpoint novo, o par mínimo é: usuário autorizado consegue, usuário de outro tenant ou sem permissão recebe 403/404.

---

## Security gate

A mudança não segue para produção se houver:

```text
vulnerabilidade crítica conhecida
secret exposto
autenticação quebrada
isolamento de tenant quebrado
controle essencial ausente
teste crítico de segurança pendente, falho ou bloqueado sem decisão explícita
```

A DAH-01 bloqueia a conclusão da história enquanto um risco crítico estiver aberto.

---

## Exceção de risco

Se o risco for aceito temporariamente, registre:

```text
qual é o risco
por que está sendo aceito
qual mitigação está no lugar
qual é o prazo
quem decidiu
```

Risco aceito e documentado é uma decisão de engenharia. Risco ignorado em silêncio é uma dívida que alguém vai pagar sem saber que assinou.

Mudança estrutural de segurança vira decisão no mapa de decisões (ex.: `D-021 usar sessão HttpOnly em vez de token em localStorage`).

---

## Checklists de revisão

**Por história:**

```text
[ ] novos dados sensíveis?
[ ] nova permissão?
[ ] nova rota?
[ ] nova integração?
[ ] novo upload?
[ ] nova ação destrutiva?
[ ] novo segredo?
[ ] novo provider?
[ ] novo acesso entre tenants?
[ ] nova tool de IA/MCP?
```

**Autenticação:**

```text
[ ] login seguro
[ ] logout invalida sessão/token
[ ] reset de senha seguro
[ ] token expira
[ ] brute force mitigado
[ ] mensagens não expõem demais
```

**Autorização:**

```text
[ ] deny by default
[ ] permissão de ação
[ ] permissão por objeto
[ ] tenant isolation
[ ] admin restrito
[ ] frontend não é fonte de verdade
```

**API:**

```text
[ ] auth
[ ] permission
[ ] validation
[ ] rate limit quando necessário
[ ] paginação
[ ] sem dados excessivos
[ ] sem mass assignment
[ ] erro seguro
```

**Frontend:** ver `frontend.md`. **Integração e IA/MCP:** ver `integracoes-ia-mcp.md`. **Infra:** ver `infra-pipeline.md`.

**Antes do deploy:**

```text
[ ] auth  [ ] permissions  [ ] secrets  [ ] TLS  [ ] CORS  [ ] CSRF
[ ] headers  [ ] debug  [ ] logs  [ ] uploads  [ ] dependências  [ ] dados sensíveis
```

---

## Definition of Done — SEC-01

A segurança está aprovada quando:

1. a autenticação é adequada ao caso de uso;
2. a autorização existe no backend;
3. permissões por objeto foram avaliadas;
4. o isolamento de tenant foi validado quando aplicável;
5. as entradas são validadas no servidor;
6. os secrets estão fora do código e fora do bundle;
7. dados sensíveis foram minimizados e protegidos;
8. a API não expõe dados excessivos;
9. CORS/CSRF estão corretos para a estratégia adotada;
10. uploads e arquivos possuem controles;
11. integrações externas possuem auth, timeout e validação;
12. webhooks possuem assinatura e idempotência quando aplicável;
13. IA/MCP respeitam least privilege;
14. dependências críticas foram revisadas;
15. produção não usa debug;
16. logs não vazam segredos;
17. vulnerabilidades críticas conhecidas não estão sendo ignoradas;
18. os testes de segurança aplicáveis estão registrados no mapa de testes;
19. os testes de segurança funcionais relevantes passam;
20. nenhum teste crítico está pendente, falho ou bloqueado sem decisão explícita;
21. os controles de infraestrutura necessários estão definidos;
22. qualquer risco aceito está documentado.
