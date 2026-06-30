# Alem da Emocao - Pipeline de Reels

Esta pasta concentra o planejamento e a primeira ferramenta local para transformar episodios do **Alem da Emocao** em cortes de Reels.

## Estrutura principal

```text
alem-da-emocao/
  episodios/
    EP02.example.txt
  templates/
    prompt-legenda.md
    prompt-capa.md
  pipeline.py
  drive_upload.py
  meta_publish.py
  plano-macro.md
```

## Entrada

Os arquivos de episodio ficam em:

```text
episodios/
  EP02.txt
  EP03.txt
```

O arquivo deve conter:

- titulo do louvor, serie e episodio na primeira linha;
- link do YouTube, se houver;
- transcricao completa;
- cortes no final, usando `Corte 1`, `Corte 2`, etc.

Os videos ficam fora do Git, na pasta:

```text
C:\Users\PICHAU\Documents\Alem da Emocao\EP2\
```

Padrao dos videos:

```text
corte 1.mp4
corte 2.mp4
```

## Rodar o pipeline

No Windows, use o launcher `py`.

Tambem existe um atalho/script interativo:

```text
rodar-pipeline.ps1
testar-etapa.ps1
```

Ele pergunta o numero do episodio e roda o pipeline completo.
O `testar-etapa.ps1` pergunta qual parte voce quer testar: transcricoes, legendas, capa, Drive, Meta ou pipeline completo.

Comando normal:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02
```

Esse comando faz o fluxo completo:

- gera/atualiza transcricoes dos cortes;
- gera/atualiza `agendamento.csv`;
- chama Codex CLI para gerar legendas;
- chama Codex CLI para gerar comentarios fixados;
- chama Codex CLI para gerar prompts de capa;
- sobe videos e capas para o Google Drive, se `google_client_secret.json` ja existir;
- processa um corte por vez.

Para testar sem escrever arquivos:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --dry-run
```

Para sobrescrever arquivos ja existentes:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --overwrite
```

Para informar uma data inicial especifica do agendamento:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --start-date 2026-07-05
```

Para testar ou retomar apenas um corte:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --only-cut 3
```

Para gerar apenas transcricoes e agenda, sem chamar Codex:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --skip-legends --skip-cover-prompts
```

## Testar partes individualmente

Use o menu interativo:

```powershell
powershell -ExecutionPolicy Bypass -File docs/estudos/analise-louvores/alem-da-emocao/testar-etapa.ps1
```

Ou rode direto:

```powershell
# So transcricoes e agenda
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --skip-legends --skip-cover-prompts --skip-drive-upload

# So legenda/comentario de um corte
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --only-cut 1 --skip-cover-prompts --skip-drive-upload

# So prompt de capa de um corte
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --only-cut 1 --skip-legends --skip-drive-upload

# So Drive em dry-run
py docs/estudos/analise-louvores/alem-da-emocao/drive_upload.py EP02 --cut 1 --dry-run

# So Meta em dry-run
py docs/estudos/analise-louvores/alem-da-emocao/meta_publish.py EP02 --cut 1 --dry-run
```

Para forcar o upload para o Google Drive:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --upload-drive
```

Para rodar o pipeline sem tentar upload para o Drive:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --skip-drive-upload
```

Para publicar no Instagram ao final, depois de configurar `.env.meta` e gerar `drive_urls.json`:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --publish-meta
```

Para testar a publicacao sem postar:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --publish-meta --meta-dry-run
```

## Saida

O pipeline gera, na pasta externa do episodio:

```text
transcricao_corte_01.txt
transcricao_corte_02.txt
agendamento.csv
pacote_editorial_01.txt
legenda_01.txt
comentario_fixado_01.txt
enquete_01.txt
texto_capa_01.txt
codex_legenda_01.raw.txt
prompt_capa_01.txt
```

Nesta fase, o pipeline gera o prompt/direcao de arte da capa. A geracao automatica do arquivo de imagem `capa_01.png` fica para uma etapa posterior.

## Observacao sobre Codex CLI

As chamadas ao Codex CLI podem usar autenticacao/rede. Para evitar rate limit, o pipeline processa um corte por vez e espera a resposta terminar antes de seguir para o proximo.

## Publicacao no Instagram

A camada de publicacao usa dois scripts:

```text
drive_upload.py
meta_publish.py
```

O primeiro sobe videos e capas para o Google Drive e gera `drive_urls.json`.
O segundo publica no Instagram usando as URLs desse arquivo.

Veja:

```text
.env.meta.example
passo-10-integracao-meta.md
```

Importante: a API da Meta precisa de URLs publicas dos videos/capas. Ela nao publica direto a partir de arquivos locais.

## Upload para Google Drive

Instale as dependencias uma vez:

```powershell
py -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

No Google Cloud, crie um OAuth Client do tipo **Desktop app** e salve o JSON nesta pasta como:

```text
google_client_secret.json
```

Depois rode direto pelo pipeline:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/pipeline.py EP02 --upload-drive
```

Ou rode apenas a etapa de upload:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/drive_upload.py EP02
```

Na primeira execucao, o navegador vai abrir para autorizar o acesso ao Drive. O script cria/salva um `google_token.json` local e gera, na pasta externa do episodio:

```text
drive_urls.json
```

Para testar antes de subir:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/drive_upload.py EP02 --dry-run
```

Para reenviar arquivos ja mapeados:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/drive_upload.py EP02 --overwrite
```

## Publicar usando URLs do Drive

Depois de gerar `drive_urls.json`, configure `META_ACCESS_TOKEN` e `META_IG_USER_ID` no ambiente ou em `.env.meta`.
Voce pode copiar `.env.meta.example` para `.env.meta` e preencher so essas duas linhas quando estiver usando Drive.

Tambem existe um configurador interativo:

```powershell
powershell -ExecutionPolicy Bypass -File docs/estudos/analise-louvores/alem-da-emocao/configurar-meta.ps1
```

Teste um corte:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/meta_publish.py EP02 --cut 1 --dry-run
```

Diagnosticar token/permissoes sem publicar:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/meta_diagnose.py
```

Publicar um corte:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/meta_publish.py EP02 --cut 1
```

## Enquetes

O pipeline gera `enquete_XX.txt` com pergunta e opcoes Sim/Nao.

A API atual usada para publicar Reels permite legenda, capa, publicacao e comentario, mas nao permite anexar automaticamente um sticker de enquete interativa ao Reel. Por isso, a enquete fica pronta como arquivo editorial para uso manual em story/repost, ate a Meta disponibilizar esse recurso por API.

## Agendamento

Agendamento, neste projeto, significa publicar automaticamente em nuvem no horario definido, sem depender do PC ligado.

O fluxo atual usa GitHub Actions:

```text
.github/workflows/alem-da-emocao-publish.yml
```

Ele roda diariamente as 15:00 UTC, que corresponde a 12:00 em America/Sao_Paulo.

A agenda do EP02 fica em:

```text
docs/estudos/analise-louvores/alem-da-emocao/schedules/EP02.json
```

Para o EP02, como os cortes 1 e 2 ja foram publicados, a fila cloud contem os cortes 3 a 12.

Secrets necessarios no GitHub:

```text
META_ACCESS_TOKEN
META_IG_USER_ID
GOOGLE_DRIVE_API_KEY
```

Eles devem ser cadastrados em:

```text
GitHub repo > Settings > Secrets and variables > Actions > New repository secret
```

Depois de cadastrar os secrets e subir estes arquivos para o GitHub, o workflow publica automaticamente o corte cuja data bater com o dia da execucao.

Tambem da para testar manualmente no GitHub em:

```text
Actions > Alem da Emocao Publish > Run workflow
```

Use `dry_run=true` para testar sem publicar.
