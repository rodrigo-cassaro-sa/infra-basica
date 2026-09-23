# Workspace seguro no EasyPanel

O Code Server não monta mais o checkout interno do EasyPanel como diretório gravável.

## Fluxo

1. `workspace-init` copia o repositório do EasyPanel para `coder_workspace` apenas na primeira inicialização.
2. O Code Server abre `/home/coder/workspace`.
3. Django DEV e Expo DEV usam o mesmo `coder_workspace`, portanto mudanças feitas no Code Server aparecem no ambiente DEV.
4. HOM e PROD continuam sendo construídos a partir do checkout controlado pelo EasyPanel/Git.
5. `git commit`, `pull` e `push` feitos no Code Server atuam na cópia privada, sem alterar ownership de `/etc/easypanel/.../code`.

## Se já ocorreu `dubious ownership`

O Compose novo evita que volte a ocorrer, mas o checkout atual do EasyPanel pode continuar com ownership antigo. Corrija uma vez no host ou recrie o checkout/deploy do projeto pelo EasyPanel antes de usar o novo Compose.
