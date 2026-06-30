# Passo 10 - Integracao com Meta/Instagram

## Objetivo

Deixar a implementacao pronta para publicar Reels no Instagram quando houver credenciais e URLs publicas dos arquivos.

## Ponto importante

A Instagram Graph API nao envia arquivos locais diretamente.

Para publicar um Reel, a API precisa receber:

- uma URL publica do video;
- uma URL publica da capa;
- legenda;
- access token;
- ID da conta profissional do Instagram.

Por isso, os arquivos locais em:

```text
C:\Users\PICHAU\Documents\Alem da Emocao\EP2
```

precisam estar tambem disponiveis publicamente em algum lugar acessivel pela Meta.

## Hospedagem pelo Google Drive

O fluxo escolhido e usar o Google Drive por API.

O script:

```text
drive_upload.py
```

faz:

1. recebe o episodio, por exemplo `EP02`;
2. encontra a pasta externa `C:\Users\PICHAU\Documents\Alem da Emocao\EP2`;
3. localiza `corte N.mp4` e `capa_NN.png`;
4. sobe os arquivos para uma pasta no Google Drive;
5. libera leitura publica por link;
6. gera `drive_urls.json` na pasta externa do episodio.

Esse arquivo vira a ponte entre Drive e Meta.

Formato resumido:

```json
{
  "1": {
    "video_file": "corte 1.mp4",
    "cover_file": "capa_01.png",
    "video_url": "https://drive.google.com/uc?export=download&id=...",
    "cover_url": "https://drive.google.com/uc?export=download&id=..."
  }
}
```

Observacao: Google Drive funciona para testes e automacao inicial. Se a Meta recusar algum arquivo por redirecionamento, tamanho ou tempo de processamento, a proxima opcao mais robusta sera usar um storage proprio como Cloudflare R2, S3 ou similar.

## Variaveis necessarias

Ver `.env.meta.example`:

```text
META_ACCESS_TOKEN=
META_IG_USER_ID=
META_PUBLIC_VIDEO_BASE_URL=
META_PUBLIC_COVER_BASE_URL=
META_GRAPH_VERSION=v23.0
```

Quando `drive_urls.json` existir, `META_PUBLIC_VIDEO_BASE_URL` e `META_PUBLIC_COVER_BASE_URL` sao opcionais.

## Script criado

```text
meta_publish.py
```

Ele faz:

1. le `legenda_XX.txt`;
2. le `comentario_fixado_XX.txt`;
3. le as URLs de `drive_urls.json` quando existir;
4. se nao houver `drive_urls.json`, monta as URLs pelas bases configuradas no `.env`;
5. cria o container do Reel;
6. publica o container;
7. comenta no post publicado.

## Comentario fixado

O script cria o comentario sugerido no post.

Fixar o comentario fica marcado como etapa manual caso a API da Meta nao disponibilize esse recurso para a conta/endpoint usado.

## Teste sem publicar

Depois de configurar as variaveis, rode:

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/meta_publish.py EP02 --cut 1 --dry-run
```

## Publicar um corte

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/meta_publish.py EP02 --cut 1
```

## Publicar todos os cortes encontrados

```powershell
py docs/estudos/analise-louvores/alem-da-emocao/meta_publish.py EP02
```

## O que ainda falta antes de usar de verdade

- criar/configurar app na Meta;
- obter access token valido;
- obter o ID da conta do Instagram;
- criar OAuth Client do Google Drive;
- rodar `drive_upload.py EP02`;
- testar com `--dry-run`;
- publicar um corte de teste;
- confirmar manualmente se comentario pode ser fixado pela interface.
