# Publicação nas lojas

Regras e preços das lojas mudam. Este é o roteiro; confirme valores e exigências no console
de cada loja antes de prometer prazo ao cliente.

## Contas (fazer com antecedência)

- **Apple Developer Program**: anuidade. Conta de **empresa** exige D-U-N-S e a aprovação
  pode levar dias ou semanas; conta pessoal sai mais rápido, mas o app aparece com o nome da pessoa.
- **Google Play Console**: taxa única. Contas pessoais novas precisam de **teste fechado com
  número mínimo de testadores por período mínimo** antes de liberar produção (confira a regra vigente).

**Software house**: o ideal é o **cliente** ter as contas e adicionar a empresa como membro.
O app é dele; se o contrato acabar, ninguém transfere app entre contas.

## Credenciais

Deixe o EAS gerenciar (`eas credentials`). Não gere keystore local por conta própria: perder
a chave de upload do Android exige processo de reset com o Google.

Para `eas submit` sem intervenção:
- **iOS**: App Store Connect API Key (Users and Access → Integrations), informada ao EAS.
- **Android**: service account no Google Cloud com acesso no Play Console, JSON cadastrado
  no EAS. **O primeiro AAB de um app novo vai manual pelo Play Console**; a API só aceita
  envio depois que o app existe lá.

## Primeira publicação: o que vão pedir

Comum: ícone, nome, descrições, capturas de tela nos tamanhos exigidos, URL da política de
privacidade, formulário de dados coletados (Apple "App Privacy" / Google "Data safety")
coerente com o que o app e as libs coletam, classificação etária, e **conta de teste
funcionando** para o revisor quando há login.

Apple:
- App que permite **criar conta** precisa permitir **excluir a conta** dentro do app.
- Login social (Google etc.) geralmente obriga a oferecer **Sign in with Apple** (`seguranca.md`).
- App que é só um site embrulhado costuma ser rejeitado.
- Texto de permissão genérico ("precisamos da câmera") é reprovado: diga o porquê.

Google:
- Público-alvo (é voltado a crianças?), declaração de permissões sensíveis
  (localização em segundo plano, SMS...), link web para exclusão de conta.

## Fluxo de release

1. `eas build --profile production --platform all`
2. `eas submit --profile production --platform all --latest` (ou `--auto-submit` no build)
3. **iOS**: build cai no TestFlight → teste → envio para revisão no App Store Connect.
4. **Android**: `submit.production.android.track: "internal"` no `eas.json` → teste →
   promova para produção no console com **liberação gradual** (porcentagem).

Checklist de release: `qualidade.md` §9.
