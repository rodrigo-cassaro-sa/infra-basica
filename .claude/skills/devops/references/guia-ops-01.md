# OPS-01 — devops

## Identificação

- **Código:** OPS-01
- **Nome:** devops
- **Categoria:** Qualidade transversal
- **Escopo:** backend, frontend, banco de dados, filas, storage, observabilidade, deploy e operação
- **Dependências:** DAH-01 project-governance + QA-01 testing-quality + SEC-01 security
- **Objetivo:** garantir que o sistema possa ser construído, publicado, monitorado, atualizado, recuperado e operado de forma previsível

---

# 1. Objetivo

Esta skill define o padrão operacional para todos os projetos.

Ela deve orientar:

- ambientes;
- Docker;
- Docker Compose;
- containers;
- imagens;
- registry;
- CI/CD;
- build;
- deploy;
- rollback;
- migrations;
- PostgreSQL;
- Redis;
- Celery;
- MinIO;
- reverse proxy;
- HTTPS;
- DNS;
- health checks;
- readiness;
- observabilidade;
- logs;
- métricas;
- alertas;
- backups;
- restore;
- secrets;
- configuração;
- escalabilidade;
- disponibilidade;
- capacidade;
- manutenção;
- runbooks;
- incidentes;
- custos operacionais.

A OPS-01 é transversal.

Ela cuida de como o sistema roda, não da regra de negócio.

---

# 2. Princípio central

```text
CÓDIGO
  ↓
BUILD
  ↓
TESTE
  ↓
ARTEFATO
  ↓
DEPLOY
  ↓
OBSERVAÇÃO
  ↓
OPERAÇÃO
  ↓
RECUPERAÇÃO
```

---

# 3. Regra de ouro

```text
SE NÃO PODE SER
REPRODUZIDO,
OBSERVADO
E RECUPERADO,
AINDA NÃO ESTÁ PRONTO
PARA PRODUÇÃO.
```

---

# 4. Relação com DAH

Quando uma história exigir alteração operacional, a OPS-01 deve verificar impacto em:

```text
deploy
migration
worker
fila
storage
secret
DNS
proxy
ambiente
monitoramento
backup
capacidade
```

---

# 5. Quando OPS-01 deve ser acionada

Obrigatoriamente quando a história envolver:

```text
nova infraestrutura
novo serviço
novo banco
nova fila
novo storage
novo domínio
novo secret
migration relevante
novo worker
nova integração operacional
nova necessidade de escalabilidade
```

---

# 6. Ambientes

Padrão:

```text
dev
hom
prod
```

## dev

Desenvolvimento.

Pode possuir:

```text
debug
hot reload
dados sintéticos
serviços locais
```

## hom

Homologação.

Deve ser próximo de produção.

Usado para:

```text
integração
QA
teste de deploy
migration
smoke
```

## prod

Produção.

Deve possuir:

```text
DEBUG=False
HTTPS
secrets seguros
backup
logs
monitoramento
alertas
```

---

# 7. Isolamento entre ambientes

Nunca compartilhar por padrão:

```text
banco
Redis
fila
bucket
secret
credencial externa
```

entre:

```text
dev
hom
prod
```

---

# 8. Configuração por ambiente

Usar configuração externa ao código.

Exemplo:

```text
DATABASE_URL
REDIS_URL
CELERY_BROKER_URL
SECRET_KEY
MINIO_ENDPOINT
```

---

# 9. `.env`

`.env` pode ser usado localmente.

Produção deve preferir secrets/configuração da plataforma.

Nunca versionar `.env` real.

---

# 10. `.env.example`

Deve listar variáveis esperadas.

Exemplo:

```text
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
```

Sem valores sensíveis.

---

# 11. Infraestrutura mínima

Padrão:

```text
Django
PostgreSQL
Redis
```

Adicionar somente quando necessário:

```text
Celery
MinIO
Prometheus
Grafana
Loki
```

---

# 12. Simplicidade operacional

Não criar infraestrutura antes da necessidade.

Exemplo:

```text
projeto pequeno
↓
1 web
1 postgres
1 redis
```

é preferível a:

```text
15 containers
```

sem motivo.

---

# 13. Docker

Todo projeto deve poder ser executado de forma reproduzível.

Docker deve conter:

```text
versão de runtime
dependências
comando
filesystem esperado
```

---

# 14. Dockerfile

Boas práticas:

```text
imagem oficial
imagem versionada
camadas simples
cache eficiente
usuário não-root quando possível
sem secrets
sem arquivos desnecessários
```

---

# 15. `.dockerignore`

Excluir:

```text
.git
.env
node_modules
.venv
logs
backups
dados locais
```

---

# 16. Multi-stage build

Usar quando reduzir imagem ou separar build/runtime.

Especialmente útil em frontend.

---

# 17. Imagem imutável

O mesmo artefato deve ser promovido entre ambientes quando possível.

Evitar rebuild diferente para produção sem necessidade.

---

# 18. Tag de imagem

Preferir:

```text
commit SHA
version
release tag
```

Evitar depender apenas de:

```text
latest
```

---

# 19. Registry

Artefatos devem ser publicados em registry confiável.

Exemplo:

```text
GitHub Container Registry
Docker Hub
registry privado
```

---

# 20. Docker Compose

Bom para:

```text
desenvolvimento
homologação simples
single server
EasyPanel
```

---

# 21. EasyPanel

Quando utilizado:

- manter serviços separados;
- configurar env/secrets;
- usar volumes persistentes;
- revisar health checks;
- configurar proxy/HTTPS;
- registrar processo de deploy.

---

# 22. Containers efêmeros

Não guardar dado importante dentro do filesystem do container.

Persistir em:

```text
PostgreSQL
MinIO
volume adequado
storage externo
```

---

# 23. PostgreSQL

Produção deve usar volume/storage persistente.

Monitorar:

```text
conexões
disco
locks
queries lentas
replicação quando existir
```

---

# 24. Redis

Usar para:

```text
cache
broker
locks
fila
```

conforme arquitetura.

Não usar como fonte principal de verdade do negócio.

---

# 25. MinIO

Usar para arquivos quando necessário.

Monitorar:

```text
disco
bucket
erros
capacidade
```

---

# 26. Celery

Workers devem ser processos separados do web.

Exemplo:

```text
web
worker
beat
```

---

# 27. Celery Beat

Rodar apenas uma instância responsável por cada agenda.

---

# 28. Filas

Separar quando necessário:

```text
default
integrations
long-running
ai
```

---

# 29. Worker scaling

Escalar baseado em:

```text
backlog
latência
CPU
RAM
tempo de task
```

---

# 30. Frontend

Frontend pode ser:

```text
container
CDN/static hosting
platform hosting
```

conforme stack.

---

# 31. Reverse proxy

Padrão:

```text
Traefik
```

quando aplicável.

Responsável por:

```text
routing
HTTPS
certificados
headers
```

---

# 32. HTTPS

Produção deve usar HTTPS.

Certificados devem possuir renovação automática quando possível.

---

# 33. DNS

Registrar:

```text
domínio
subdomínio
serviço
ambiente
```

Evitar apontamentos manuais sem documentação.

---

# 34. Health check

Todo serviço relevante deve possuir health check.

Exemplo:

```text
/health/
```

---

# 35. Liveness

Responde:

```text
processo está vivo?
```

---

# 36. Readiness

Responde:

```text
aplicação está pronta para receber tráfego?
```

---

# 37. Health check não deve ser pesado

Evitar:

```text
consultar 10 integrações externas
```

em cada health check.

---

# 38. Startup check

Pode validar:

```text
configuração essencial
banco
migration
secret obrigatório
```

sem transformar startup em operação frágil.

---

# 39. Graceful shutdown

Containers devem encerrar corretamente.

Especialmente:

```text
web
worker
```

---

# 40. Timeout de shutdown

Configurar tempo suficiente para finalizar requests/tasks críticas.

---

# 41. CI/CD

Pipeline deve automatizar:

```text
lint
tests
build
security checks
artifact
deploy
smoke
```

---

# 42. Ordem recomendada

```text
checkout
 ↓
install
 ↓
lint
 ↓
unit tests
 ↓
integration tests
 ↓
build
 ↓
security checks
 ↓
publish artifact
 ↓
deploy
 ↓
smoke
```

---

# 43. Quality gate

Deploy deve bloquear quando:

```text
build falha
teste crítico falha
security gate falha
migration inválida
```

---

# 44. Deploy manual ou automático

Pode ser:

```text
automático
manual aprovado
```

conforme maturidade.

Produção pode exigir aprovação explícita.

---

# 45. Deploy reproduzível

Não executar sequência manual obscura.

Deve existir processo documentado.

---

# 46. Deploy sem edição manual no servidor

Evitar:

```text
ssh
editar arquivo
reiniciar manualmente
```

como fluxo principal.

---

# 47. Artifact promotion

Preferir:

```text
mesma imagem
dev → hom → prod
```

---

# 48. Migrations

Toda migration deve ser:

```text
versionada
revisada
testada
```

---

# 49. Migration antes ou depois do deploy

Definir estratégia.

Para compatibilidade:

```text
migration backward-compatible
 ↓
deploy app
 ↓
cleanup posterior
```

---

# 50. Expand and contract

Para mudanças complexas:

```text
1. adicionar novo campo
2. app suporta ambos
3. migrar dados
4. remover antigo
```

---

# 51. Migration destrutiva

Exige cuidado adicional.

Exemplo:

```text
drop column
rename incompatível
alteração de tipo
```

---

# 52. Backup antes de migration crítica

Quando risco justificar:

```text
backup
↓
migration
↓
validação
```

---

# 53. Migration data-heavy

Grandes migrations devem evitar bloquear produção.

Pode exigir:

```text
batch
background migration
janela
```

---

# 54. Rollback

Todo deploy relevante deve considerar:

```text
como voltar?
```

---

# 55. Rollback de aplicação

Pode usar imagem anterior.

---

# 56. Rollback de migration

Nem sempre é simples.

Por isso:

```text
compatibilidade
backup
migration reversível
```

devem ser avaliados.

---

# 57. Blue/green

Pode ser adotado quando necessidade de disponibilidade justificar.

---

# 58. Canary

Pode ser usado para rollout gradual.

Não é obrigatório no início.

---

# 59. Feature flags

Podem reduzir risco de deploy.

Permitem:

```text
deploy código
↓
ativar funcionalidade depois
```

---

# 60. Zero-downtime deploy

Avaliar quando requisito exigir.

Depende de:

```text
proxy
containers
migration compatível
graceful shutdown
```

---

# 61. Observabilidade

Todo sistema de produção deve permitir responder:

```text
está funcionando?
está lento?
está falhando?
onde?
desde quando?
```

---

# 62. Logs

Logs devem ser:

```text
estruturados
centralizados
pesquisáveis
```

quando maturidade justificar.

---

# 63. Loki

Pode ser usado para logs centralizados.

---

# 64. Métricas

Monitorar:

```text
request rate
error rate
latency
CPU
RAM
disk
DB connections
queue backlog
worker status
```

---

# 65. Prometheus

Pode coletar métricas.

---

# 66. Grafana

Pode apresentar:

```text
dashboards
alertas
tendências
```

---

# 67. Tracing

Pode ser adicionado quando sistema distribuído exigir.

Não obrigatório inicialmente.

---

# 68. Golden signals

Monitorar:

```text
latency
traffic
errors
saturation
```

---

# 69. Alertas

Alertar quando há ação necessária.

Evitar alertar por tudo.

---

# 70. Alerta útil

Exemplo:

```text
API 5xx > limite
```

---

# 71. Alert fatigue

Muitos alertas inúteis reduzem atenção.

---

# 72. Dashboard

Cada serviço crítico pode possuir:

```text
disponibilidade
latência
erro
recursos
fila
```

---

# 73. SLO

Quando maturidade justificar, definir:

```text
disponibilidade
latência
taxa de sucesso
```

---

# 74. SLA

Não confundir SLA contratual com SLO interno.

---

# 75. Capacity planning

Monitorar crescimento de:

```text
disco
banco
fila
storage
tráfego
```

---

# 76. CPU

Não escalar somente por CPU sem entender workload.

---

# 77. RAM

Aplicações Python podem exigir atenção à memória por worker.

---

# 78. Disk

Monitorar especialmente:

```text
PostgreSQL
MinIO
logs
backups
```

---

# 79. Database connections

Evitar esgotar conexões.

Pode usar:

```text
PgBouncer
```

quando necessário.

---

# 80. PgBouncer

Adicionar quando volume de conexões justificar.

---

# 81. PostgreSQL tuning

Não otimizar prematuramente.

Monitorar antes.

---

# 82. Query performance

Queries lentas podem causar incidente operacional.

Coordenar com BE-01/QA-01.

---

# 83. Backup

Deve existir para dados importantes.

Padrão:

```text
PostgreSQL
MinIO
configuração crítica
```

---

# 84. Backup não é suficiente

Deve haver teste de restore.

---

# 85. Regra de ouro de backup

```text
BACKUP NÃO TESTADO
=
BACKUP NÃO CONFIÁVEL
```

---

# 86. Frequência

Definir com base em:

```text
RPO
```

---

# 87. RPO

Quanto dado pode ser perdido?

Exemplo:

```text
1 hora
24 horas
```

---

# 88. RTO

Quanto tempo pode levar para recuperar?

---

# 89. Retenção

Definir:

```text
diário
semanal
mensal
```

conforme necessidade.

---

# 90. Backup off-site

Para risco relevante, manter cópia fora do mesmo servidor.

---

# 91. Backup criptografado

Quando contém dado sensível.

---

# 92. Restore test

Executar periodicamente.

---

# 93. Disaster recovery

Para sistemas críticos, definir:

```text
servidor perdido
banco corrompido
storage perdido
```

---

# 94. Single point of failure

Identificar:

```text
um único servidor
um único banco
um único storage
```

Aceitar conscientemente conforme estágio do projeto.

---

# 95. Alta disponibilidade

Adicionar quando necessidade justificar.

Não por padrão.

---

# 96. PostgreSQL replica

Pode ser usada para:

```text
HA
read scaling
```

quando necessário.

---

# 97. Redis persistence

Configurar conforme uso.

Broker/cache possuem necessidades diferentes.

---

# 98. MinIO replication

Avaliar apenas quando necessidade justificar.

---

# 99. CDN

Pode ser usada para:

```text
assets
download
frontend
```

quando necessário.

---

# 100. Cache

Aplicar onde medição justificar.

---

# 101. Cache invalidation

Toda estratégia de cache deve explicar:

```text
quando expira?
quando invalida?
```

---

# 102. Secrets

Produção deve usar armazenamento seguro de secrets.

---

# 103. Secret rotation

Operação deve prever rotação.

---

# 104. Secret expiry

Monitorar quando credencial expira.

---

# 105. Certificados

Monitorar expiração.

---

# 106. Third-party credentials

Registrar dono e finalidade.

---

# 107. Runbook

Serviço crítico deve possuir procedimento para falhas comuns.

Pode estar no próprio sistema de gestão operacional ou documentação existente.

Não criar documento extra sem necessidade.

---

# 108. Runbook mínimo

Responder:

```text
o que aconteceu?
como verificar?
como mitigar?
como recuperar?
```

---

# 109. Incidente

Fluxo:

```text
detectar
 ↓
conter
 ↓
restaurar
 ↓
investigar
 ↓
corrigir
 ↓
registrar decisão quando necessário
```

---

# 110. Diário de bordo

Incidente relevante deve ser registrado no diário.

---

# 111. Mapa de decisões

Mudança operacional estrutural deve virar decisão.

Exemplo:

```text
D-031
adotar PgBouncer
```

---

# 112. Postmortem

Para incidente grave, registrar:

```text
causa
impacto
linha do tempo
ação corretiva
```

Pode ser incorporado ao diário/mapa de decisões se a técnica DAH não quiser novo documento.

---

# 113. Manutenção

Planejar:

```text
updates
patches
vacuum
backups
certificados
storage
```

---

# 114. Janela de manutenção

Definir quando necessário.

---

# 115. Atualizações

Não deixar stack envelhecer indefinidamente.

---

# 116. Patch security

Correções críticas têm prioridade.

---

# 117. Dependências operacionais

Mapear:

```text
DNS
registry
cloud
provider
email
storage
```

---

# 118. External dependency outage

Definir comportamento.

Exemplo:

```text
provider de e-mail fora
→ fila acumula
→ sistema principal continua
```

---

# 119. Graceful degradation

Quando possível, sistema continua parcialmente funcional.

---

# 120. Feature disable

Capacidade problemática pode ser desligada via flag/configuração.

---

# 121. Cost awareness

Monitorar:

```text
CPU
RAM
storage
egress
providers
logs
IA
```

---

# 122. Cost anomaly

Aumento inesperado pode indicar:

```text
bug
abuso
loop
ataque
```

---

# 123. Dev environment

Deve ser simples de subir.

Idealmente:

```text
docker compose up
```

ou fluxo equivalente.

---

# 124. Bootstrap

Novo desenvolvedor/agente deve conseguir iniciar projeto com poucos passos.

---

# 125. Seed

Dados sintéticos podem facilitar desenvolvimento.

---

# 126. Homologação

Deve permitir:

```text
QA
integração real/sandbox
migration test
deploy test
```

---

# 127. Produção

Mudança deve ser controlada.

---

# 128. Change management

Deploy relevante deve indicar:

```text
história
versão
migration
risco
rollback
```

---

# 129. Versionamento

Pode usar:

```text
semantic versioning
release tags
commit SHA
```

conforme produto.

---

# 130. Changelog

Não criar documento extra obrigatoriamente.

Pode ser derivado do Git/histórias quando necessário.

---

# 131. Git

Branch por história pode facilitar rastreabilidade.

Exemplo:

```text
feat/H-023-visualizar-permissoes
```

---

# 132. Merge

Exigir quality/security gates conforme criticidade.

---

# 133. Production access

Acesso à produção deve ser restrito.

---

# 134. SSH

Usar chave, não senha, quando possível.

---

# 135. Root

Evitar uso rotineiro de root.

---

# 136. Firewall

Expor apenas portas necessárias.

---

# 137. Private network

Banco/Redis/MinIO devem preferir rede privada.

---

# 138. Monitoring network

Endpoints internos de métricas não precisam ser públicos.

---

# 139. Prometheus endpoint

Restringir conforme arquitetura.

---

# 140. Logs retention

Definir retenção para evitar:

```text
disco cheio
custo excessivo
dados armazenados demais
```

---

# 141. Log rotation

Configurar quando logs locais existirem.

---

# 142. Structured logging

Preferir campos:

```text
timestamp
level
service
request_id
message
```

---

# 143. Request ID

Propagar entre:

```text
web
worker
integration
```

---

# 144. Clock synchronization

Servidores devem manter horário correto.

---

# 145. Timezone

Infra geralmente opera em UTC.

Aplicação converte para apresentação.

---

# 146. Scheduling

Tarefas recorrentes devem considerar timezone.

---

# 147. Celery Beat timezone

Deve estar coerente com Django.

---

# 148. Cron

Evitar cron espalhado em servidor se Celery Beat já governa tarefas da aplicação.

---

# 149. Jobs operacionais

Backups podem usar scheduler separado apropriado.

---

# 150. Temporary files

Devem ser limpos.

---

# 151. Disk pressure

Alertar antes de atingir 100%.

---

# 152. Queue backlog

Monitorar tamanho e idade.

---

# 153. Worker failures

Monitorar:

```text
crash
restart
timeout
retry excessivo
```

---

# 154. Restart policy

Configurar containers críticos.

---

# 155. Restart loop

Detectar e não mascarar causa.

---

# 156. Resource limits

Containers podem possuir:

```text
CPU
RAM
```

quando plataforma permitir.

---

# 157. OOM

Monitorar reinícios por falta de memória.

---

# 158. Scaling web

Escalar quando:

```text
latência
CPU
requests
```

justificarem.

---

# 159. Scaling worker

Escalar baseado em fila.

---

# 160. Scaling database

Última etapa após otimização e tuning.

---

# 161. Load test

Antes de escala importante, QA-01 pode executar carga.

OPS-01 interpreta capacidade.

---

# 162. Deployment strategy

Padrão simples:

```text
rolling/restart controlado
```

Estratégias mais complexas só quando necessárias.

---

# 163. EasyPanel deploy

Quando usar EasyPanel:

```text
build/pull image
configure env
persistent volumes
health check
domain
HTTPS
deploy
smoke
```

---

# 164. EasyPanel backups

Não depender apenas da plataforma sem validar restore.

---

# 165. Observabilidade mínima

Projeto em produção deve possuir pelo menos:

```text
logs
health check
uptime
backup
```

---

# 166. Observabilidade madura

Adicionar:

```text
metrics
dashboards
alerts
tracing
```

---

# 167. Uptime monitor

Pode verificar endpoint externo.

---

# 168. Synthetic monitoring

Pode testar fluxo real simples.

Exemplo:

```text
login de usuário sintético
```

quando necessário.

---

# 169. Deploy smoke test

Após deploy:

```text
health
API crítica
frontend
login
```

---

# 170. Rollback trigger

Definir quando rollback automático/manual deve ocorrer.

Exemplo:

```text
erro 5xx dispara muito
health falha
```

---

# 171. Migration failure

Deploy deve parar se migration falhar.

---

# 172. Partial deploy

Evitar estado em que:

```text
frontend novo
backend antigo incompatível
```

sem estratégia de compatibilidade.

---

# 173. Backward compatibility

Planejar quando frontend/backend deployam separadamente.

---

# 174. API compatibility

Coordenação com BE-02.

---

# 175. Data migration

Coordenação com BE-01.

---

# 176. Async migration

Coordenação com BE-03.

---

# 177. Integration config

Coordenação com BE-05.

---

# 178. IA infrastructure

Coordenação com BE-04.

---

# 179. QA

QA-01 define testes.

OPS-01 garante execução no pipeline/ambiente.

---

# 180. Security

SEC-01 define controles.

OPS-01 aplica:

```text
TLS
secrets
firewall
network
container
```

---

# 181. Governança

DAH-01 decide se a história está operacionalmente concluída.

---

# 182. Operational readiness

Antes de produção:

```text
[ ] build
[ ] tests
[ ] security
[ ] migration
[ ] secrets
[ ] health
[ ] logs
[ ] backup
[ ] rollback
[ ] smoke
```

---

# 183. Checklist ambiente

```text
[ ] env separado
[ ] secrets corretos
[ ] banco correto
[ ] Redis correto
[ ] storage correto
[ ] domínio correto
[ ] HTTPS
```

---

# 184. Checklist Docker

```text
[ ] imagem versionada
[ ] sem secrets
[ ] usuário não-root quando possível
[ ] .dockerignore
[ ] health check
[ ] volume correto
[ ] comando correto
```

---

# 185. Checklist banco

```text
[ ] backup
[ ] restore testado
[ ] conexão protegida
[ ] migrations aplicadas
[ ] espaço em disco
[ ] monitoramento
```

---

# 186. Checklist Celery

```text
[ ] broker
[ ] worker
[ ] beat quando necessário
[ ] filas
[ ] health
[ ] backlog monitorado
```

---

# 187. Checklist MinIO

```text
[ ] bucket
[ ] credencial
[ ] acesso privado
[ ] volume
[ ] backup
```

---

# 188. Checklist deploy

```text
[ ] artifact identificado
[ ] config validada
[ ] migration revisada
[ ] backup quando necessário
[ ] deploy
[ ] smoke
[ ] logs
[ ] métricas
[ ] rollback disponível
```

---

# 189. Checklist observabilidade

```text
[ ] logs
[ ] uptime
[ ] error rate
[ ] latency
[ ] CPU
[ ] RAM
[ ] disk
[ ] DB
[ ] queue
```

---

# 190. Checklist backup

```text
[ ] banco
[ ] storage
[ ] frequência
[ ] retenção
[ ] off-site quando necessário
[ ] restore testado
```

---

# 191. Checklist produção

```text
[ ] DEBUG=False
[ ] HTTPS
[ ] secrets
[ ] health
[ ] logs
[ ] backup
[ ] monitoramento
[ ] firewall
[ ] rollback
```

---

# 192. Definition of Done — OPS-01

A operação está pronta quando:

1. ambientes estão separados;
2. configuração está externalizada;
3. build é reproduzível;
4. imagem/artefato está versionado;
5. deploy possui processo definido;
6. migrations foram revisadas;
7. rollback foi considerado;
8. secrets estão protegidos;
9. banco possui persistência e backup;
10. restore foi testado quando criticidade exigir;
11. serviços possuem health check;
12. logs permitem investigação;
13. métricas básicas estão disponíveis quando necessário;
14. alertas críticos estão definidos;
15. workers/filas são monitorados;
16. storage está persistente;
17. HTTPS está ativo em produção;
18. smoke test é executado após deploy;
19. capacidade e recursos estão adequados;
20. a DAH-01 pode considerar a história operacionalmente pronta.

---

# 193. Regra final

```text
DEVOPS NÃO É SÓ DEPLOY.

É GARANTIR QUE O SISTEMA:
SUBA,
FUNCIONE,
SEJA OBSERVADO,
SEJA ATUALIZADO,
E POSSA SER RECUPERADO.
```

---

# 194. Arquitetura transversal

```text
                       DAH-01
                          │
                          ▼
                       HISTÓRIA
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
      BACKEND          FRONTEND          INFRA
         │                │                │
         └────────────────┼────────────────┘
                          ▼
                       OPS-01
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
       BUILD            DEPLOY          OPERAR
         │                │                │
         └────────────────┼────────────────┘
                          ▼
                     OBSERVAR
                          │
                          ▼
                     RECUPERAR
                          │
                          ▼
                       DAH-01
```

---

# 195. Resultado esperado

Ao executar a OPS-01 deve ser possível responder:

```text
como o sistema sobe?
como é construído?
como é publicado?
como migrations são aplicadas?
como rollback funciona?
onde ficam secrets?
como o banco é protegido?
como workers são operados?
como arquivos são persistidos?
como saber se algo falhou?
como recuperar de falha?
como restaurar backup?
o sistema está pronto para produção?
```

Esse é o propósito da **OPS-01 — devops**.
