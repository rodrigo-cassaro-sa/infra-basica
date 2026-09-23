# Workspace seguro no EasyPanel

O Code Server (só no DEV) não monta o checkout interno do EasyPanel como diretório gravável.

## Fluxo

1. `workspace-init` copia o checkout da branch do serviço para o volume `coder_workspace` apenas na primeira inicialização.
2. O Code Server abre `/home/coder/workspace`.
3. Em `RUN_MODE=dev`, Django e Expo usam o mesmo `coder_workspace`: mudanças feitas no Code Server aparecem no ambiente.
4. HOM e PROD (`RUN_MODE=server`, sem Code Server) constroem Django e Expo a partir do checkout controlado pelo EasyPanel/Git.
5. `git commit`, `pull` e `push` feitos no Code Server atuam na cópia privada, sem alterar ownership de `/etc/easypanel/.../code`.

Como a cópia só é feita uma vez, redeploy não atualiza o workspace: use `git pull` no Code Server. Para recomeçar do zero, apague o volume `coder_workspace` do serviço e reimplante.

## Se já ocorreu `dubious ownership`

O Compose evita que volte a ocorrer, mas o checkout atual do EasyPanel pode continuar com ownership antigo. Corrija uma vez no host ou recrie o checkout/deploy do projeto pelo EasyPanel.
