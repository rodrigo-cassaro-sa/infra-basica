# Versionamento, compatibilidade e depreciação

## Versão na URL

```text
/api/v1/
```

`v2` só existe quando há mudança incompatível que não pode conviver com a v1. Manter duas versões custa manutenção dobrada — antes de criar, verifique se dá para introduzir o novo comportamento de forma aditiva (campo novo, endpoint novo, parâmetro opcional).

## Classificação da mudança

| Compatível | Potencialmente incompatível |
|---|---|
| novo campo opcional na resposta | remover campo |
| novo endpoint | renomear campo |
| novo filtro opcional | alterar tipo de um campo |
| novo valor em enum **se** o cliente ignora desconhecidos | alterar semântica/unidade |
| | tornar campo de entrada obrigatório |
| | mudar status HTTP retornado |
| | mudar ou remover um `code` de erro |

Atenção ao caso do enum: se o app Expo faz `switch` sobre os valores, valor novo quebra a tela. Verifique com quem consome antes de classificar como compatível.

## API pública x interna

**Pública** (integradores, parceiros, clientes) exige compromisso forte com versionamento, compatibilidade, documentação, rate limits, segurança e processo de depreciação anunciado.

**Interna** (só o app Expo da própria casa) ainda precisa ser organizada e documentada, mas pode ter ciclo coordenado com seus consumidores — desde que o deploy do backend e do frontend seja combinado. Atenção: app nativo publicado na loja fica meses em versões antigas — para iOS/Android trate a API como **pública** (compatibilidade para trás obrigatória). Registre em qual categoria cada endpoint está; a diferença muda o custo de qualquer alteração.

## Depreciação

Não remova contrato em uso sem comunicar. Sequência:

1. marcar como deprecated no OpenAPI (`@extend_schema(deprecated=True)`) e na documentação;
2. documentar o substituto, com exemplo de migração;
3. definir janela de migração com data;
4. monitorar uso (log por rota/consumidor) para saber quem ainda chama;
5. avisar os consumidores restantes;
6. remover só depois da janela e com uso zerado.

Adicionar header `Deprecation` / `Sunset` ajuda integrações automatizadas a detectarem o prazo.

## Migração de campo sem quebrar

Padrão expand/contract:

1. adicione o campo novo junto do antigo, ambos preenchidos;
2. documente o antigo como deprecated;
3. migre os consumidores;
4. remova o antigo em janela combinada (ou em `/api/v2/`, se for público).
