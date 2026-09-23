# Segurança operacional (aplicação dos controles da SEC-01)

- **Secrets:** envs do EasyPanel (por ambiente) e GitHub Environments. Nunca no repo, na
  imagem, em log ou em mensagem de commit. Cofre de senhas da equipe guarda o inventário.
- **Inventário de credenciais de terceiros** no `docs/deploy.md`: para quê, dono, ambiente,
  onde está cadastrada, quando expira.
- **Rotação:** ao sair alguém da equipe, ao suspeitar de vazamento e anualmente para as críticas.
- **Rede:** Postgres, Redis, MinIO (API interna) e métricas só na rede privada do projeto.
  Firewall da VPS: 22 (restrito), 80, 443. Painel do EasyPanel com 2FA.
- **SSH:** chave, sem senha, sem root rotineiro. SSH é para emergência, não para deploy.
- **TLS:** Traefik/EasyPanel com renovação automática; monitorar expiração.
- **Container:** usuário não-root, imagem oficial com versão fixa, rebuild mensal para patches
  de segurança do sistema base (o pipeline pega a imagem base nova).
- **Dependências:** audit no CI (`pip-audit`/`uv`, `npm audit`), correção crítica tem prioridade.
- **Acesso a prod:** mínimo de pessoas; aprovação do environment `prod` restrita.
- **Horário:** servidores em UTC com NTP; aplicação converte para `America/Sao_Paulo`.
