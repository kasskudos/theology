# Plano macro - Alem da Emocao

Este documento organiza o projeto em passos grandes e claros.

A ideia e que cada passo abaixo possa virar, depois, um **plano micro** proprio. Ou seja: primeiro definimos o caminho geral; depois pegamos um passo por vez e planejamos os detalhes.

## Objetivo geral

Criar um fluxo de producao para transformar cada episodio completo do programa **Alem da Emocao** em uma campanha semanal de conteudo para o **Bereano do Louvor**.

Cada episodio deve gerar:

- 1 video completo para o YouTube;
- 7 cortes em formato de Reels;
- legendas e comentarios para cada corte;
- textos de capa;
- prompts de arte/capa;
- calendario de publicacao;
- arquivos organizados para revisao;
- agendamento dos posts quando a integracao externa estiver disponivel.

O projeto sera dividido em fases. Primeiro, o pipeline deve gerar todos os arquivos locais. Depois, quando a integracao com a Meta/Instagram estiver validada, ele pode publicar/agendar automaticamente e lidar com comentarios fixados.

## Passo 1 - Definir a estrategia editorial da serie

**Objetivo:** deixar claro como cada episodio completo vira uma campanha semanal.

Precisamos definir:

- como o episodio completo sera apresentado no YouTube;
- quantos Reels sairao por episodio;
- como os Reels serao numerados;
- como cada Reel apontara para a serie completa;
- qual sera a chamada para o perfil, YouTube e link da bio;
- qual sera o padrao de publicacao semanal.

Entregavel deste passo:

- documento com a estrategia editorial da serie.

Criterio de conclusao:

- saber exatamente como um episodio do YouTube se transforma em uma sequencia de Reels.

## Passo 2 - Definir a identidade editorial e visual

**Objetivo:** estabelecer o tom do conteudo e o estilo visual das capas/artes.

Precisamos definir:

- tom teologico;
- tom pastoral;
- nivel de critica permitido;
- linguagem das legendas;
- linguagem dos comentarios fixados;
- estilo das capas;
- cores;
- elementos visuais permitidos;
- elementos visuais proibidos.

Direcao inicial:

- biblico;
- reformado;
- pastoral;
- didatico;
- respeitoso;
- critico sem ser agressivo;
- claro para pessoas comuns;
- fiel as Escrituras.

Direcao visual inicial:

- hand-drawn;
- sketch poster;
- whiteboard/grunge;
- preto e branco;
- vermelho como cor de destaque;
- fundo de papel envelhecido;
- tracos grossos;
- serio e teologico;
- sem 3D;
- sem anime;
- sem fotografia como base principal.

Entregavel deste passo:

- guia de identidade editorial e visual.

Criterio de conclusao:

- conseguir avaliar se uma legenda, capa ou prompt esta dentro ou fora do estilo do projeto.

## Passo 3 - Definir as entradas do pipeline

**Objetivo:** decidir quais informacoes o sistema precisa receber para processar um episodio.

Precisamos definir:

- onde ficam os arquivos de entrada no projeto;
- nome padrao dos arquivos de episodio;
- formato geral do arquivo `EPXX.txt`;
- como o episodio informa titulo, serie e numero;
- como o link do YouTube sera informado;
- como a lista de cortes aparece no final do mesmo arquivo;
- onde ficam os videos fora do repositorio;
- como associar cada `Corte N` ao arquivo `corte N.mp4`.

Entrada principal pensada:

```text
episodios/
  EP02.txt
  EP03.txt
  EP10.txt
```

Exemplo de inicio do arquivo:

```text
Bencaos que nao tem Fim - Alem da Emocao - EP2
YouTube: https://youtu.be/exemplo
Time	Subtitle
0s	Sejam muito bem-vindos a mais um episodio...
4s	programa semanal de analise biblica e teologica...
```

Exemplo da lista de cortes no final do mesmo arquivo:

```text
Corte 1
22:52	>> Fizemos. Mas e ai? Diante de tudo isso...
25:50	>> E amarrar o subjetivo no objetivo absoluto...

Corte 2
3:40	>> Texto inicial do corte...
5:12	Texto final do corte...
```

Os videos nao serao commitados no Git. Eles ficarao em uma pasta externa padrao:

```text
%USERPROFILE%\Documents\Alem da Emocao\EP2\
  corte 1.mp4
  corte 2.mp4
```

Entregavel deste passo:

- documento `passo-03-entradas-pipeline.md`;
- pasta `episodios/`;
- arquivo de exemplo `EP02.example.txt`.

Criterio de conclusao:

- conseguir criar um arquivo `EP02.txt` simples, humano e versionavel, sem precisar preencher JSON ou YAML.

## Passo 4 - Definir o formato da transcricao

**Objetivo:** garantir que a transcricao completa possa ser lida e dividida automaticamente pelos cortes.

Precisamos definir:

- formatos de timestamp aceitos;
- como o texto aparece ao lado de cada timestamp;
- como lidar com linhas quebradas pelo plugin de transcricao;
- como lidar com marcas como `>> `;
- como converter tempos para segundos;
- como extrair o texto entre inicio e fim de cada Reel.

Formato oficial esperado:

```text
0s	Texto inicial...
4s	Continua a fala...
55s	Outro trecho...
1:10	Texto depois de um minuto...
10:17	Texto depois de dez minutos...
```

Regras iniciais:

- ate 59 segundos, usar `0s`, `1s`, `10s`, `55s`;
- a partir de 1 minuto, usar `1:10`, `3:40`, `10:17`, `20:30`;
- os tempos devem ser preservados para processamento;
- a marca `>> ` pode ser removida do texto quando o pipeline limpar a transcricao;
- os cortes no final do arquivo usam o mesmo formato de linha da transcricao.

Entregavel deste passo:

- documento com o formato aceito da transcricao.

Criterio de conclusao:

- conseguir pegar uma transcricao completa e extrair automaticamente o trecho de cada Reel pelo tempo inicial e final.

## Passo 5 - Definir a estrutura de saida

**Objetivo:** decidir exatamente quais arquivos e automacoes serao gerados para cada Reel.

Precisamos definir:

- onde os arquivos gerados serao salvos;
- nome dos arquivos;
- conteudo de cada arquivo;
- como gerar transcricoes de corte;
- como gerar legendas chamando Codex CLI;
- como gerar capas ou prompts de capa;
- como gerar comentarios fixados;
- como gerar calendario/agendamento;
- quais partes sao locais e quais dependem de integracao externa.

Estrutura inicial pensada:

```text
%USERPROFILE%\Documents\Alem da Emocao\EP2\
  corte 1.mp4
  corte 2.mp4
  transcricao_corte_01.txt
  transcricao_corte_02.txt
  legenda_01.txt
  legenda_02.txt
  comentario_fixado_01.txt
  comentario_fixado_02.txt
  prompt_capa_01.txt
  prompt_capa_02.txt
  capa_01.png
  capa_02.png
  agendamento.csv
```

Regras iniciais:

- as legendas devem ser geradas uma por vez para evitar rate limit;
- as capas tambem devem ser geradas uma por vez;
- o comando normal deve ser simples: informar apenas o episodio, exemplo `EP02`;
- parametros extras devem servir apenas para testes, retomadas e excecoes;
- o calendario deve usar o dia atual como primeiro post e meio-dia como horario padrao;
- se houver mais ou menos de 7 cortes, o calendario deve se adaptar;
- publicacao automatica e comentario fixado dependem de integracao externa com a Meta/Instagram.

Entregavel deste passo:

- documento `passo-05-estrutura-saida.md`.

Criterio de conclusao:

- saber exatamente o que o pipeline deve criar, gerar e tentar agendar para cada Reel.

## Passo 6 - Criar o template mestre de legenda

**Objetivo:** criar o template operacional que o pipeline usa para transformar a transcricao de um corte em legenda e comentario fixado.

O template deve gerar:

- titulo interno;
- resumo do tema;
- legenda para Instagram;
- comentario fixado;
- hashtags;
- CTA adequada ao numero do Reel;
- texto curto sugerido para capa;
- observacoes de revisao.

O template precisa considerar:

- contexto geral do episodio;
- transcricao do corte;
- numero do Reel;
- total de Reels;
- nome do louvor;
- link ou referencia ao YouTube;
- tom biblico, reformado, pastoral e didatico.

O arquivo deve usar variaveis para o script preencher, por exemplo:

```text
{{louvor}}
{{serie}}
{{episodio_normalizado}}
{{numero_corte}}
{{total_cortes}}
{{inicio_corte}}
{{fim_corte}}
{{youtube_url}}
{{transcricao_corte}}
```

Entregavel deste passo:

- arquivo `templates/prompt-legenda.md`.

Criterio de conclusao:

- o script conseguir preencher o template e chamar o Codex CLI para gerar `legenda_XX.txt` e `comentario_fixado_XX.txt`.

## Passo 7 - Criar o template mestre de capa

**Objetivo:** criar o template operacional que o pipeline usa para transformar o tema do corte em direcao de arte, prompt de imagem e capa.

O template deve gerar:

- conceito visual;
- ideia visual principal;
- metafora visual;
- composicao da imagem;
- texto final de capa;
- posicao do identificador curto;
- prompt final para gerador de imagem;
- instrucoes negativas do que evitar.

O estilo deve seguir:

- hand-drawn;
- sketch poster;
- whiteboard/grunge;
- preto e branco;
- vermelho como destaque;
- papel envelhecido;
- tracos grossos;
- serio e teologico;
- sem 3D;
- sem anime;
- sem fotografia.

O arquivo deve usar variaveis para o script preencher, por exemplo:

```text
{{louvor}}
{{serie}}
{{episodio_normalizado}}
{{numero_corte}}
{{total_cortes}}
{{inicio_corte}}
{{fim_corte}}
{{transcricao_corte}}
{{legenda}}
{{texto_capa_sugerido}}
```

Entregavel deste passo:

- arquivo `templates/prompt-capa.md`.

Criterio de conclusao:

- o script conseguir preencher o template e chamar o Codex CLI ou backend de imagem para gerar `prompt_capa_XX.txt` e, quando possivel, `capa_XX.png`.

## Passo 8 - Criar a primeira versao tecnica do pipeline

**Objetivo:** construir a ferramenta local que le o episodio, extrai os cortes e gera os primeiros arquivos na pasta externa do episodio.

Nesta primeira versao, o pipeline deve:

- ler um arquivo `EPXX.txt` em `episodios/`;
- extrair dados do cabecalho;
- ler a transcricao completa;
- identificar a lista de cortes no final do arquivo;
- interpretar os timestamps;
- extrair os cortes;
- localizar videos externos em `%USERPROFILE%\Documents\Alem da Emocao\EPX\`;
- associar `Corte N` a `corte N.mp4`;
- validar se os videos esperados existem;
- validar, quando possivel, resolucao 1080x1350;
- gerar `transcricao_corte_XX.txt` na pasta externa do episodio;
- gerar `agendamento.csv` inicial;
- registrar erros simples.

Nesta etapa, a ferramenta ainda nao precisa chamar Codex CLI, gerar legenda, gerar capa ou publicar nada. Ela deve preparar a base confiavel para as proximas etapas.

Entregavel deste passo:

- primeira versao do pipeline local.
- `pipeline.py`;
- documentacao curta de uso.

Criterio de conclusao:

- rodar o pipeline em um episodio de teste e ver `transcricao_corte_XX.txt` e `agendamento.csv` gerados corretamente na pasta externa do episodio.

## Passo 9 - Integrar Codex CLI para legendas e capas

**Objetivo:** fazer o pipeline usar os templates do Passo 6 e Passo 7 para gerar automaticamente legendas, comentarios fixados e direcao de arte/capas.

Precisamos implementar:

- preenchimento de `templates/prompt-legenda.md`;
- chamada sequencial do Codex CLI para cada corte;
- geracao de `legenda_XX.txt`;
- geracao de `comentario_fixado_XX.txt`;
- preenchimento de `templates/prompt-capa.md`;
- chamada sequencial do Codex CLI ou backend de imagem para cada capa;
- geracao de `prompt_capa_XX.txt`;
- geracao de `capa_XX.png` quando houver ferramenta de imagem disponivel;
- controle para esperar uma geracao terminar antes da proxima;
- tratamento de falhas e logs.

Precisamos definir:

- comando exato do Codex CLI;
- como passar contexto para cada chamada;
- como salvar e separar os blocos da resposta;
- como retomar a partir de um corte especifico;
- como evitar sobrescrever arquivos ja revisados sem confirmacao.

Entregavel deste passo:

- pipeline gerando legendas, comentarios fixados e prompts/capas em fila sequencial.

Criterio de conclusao:

- rodar o pipeline em um episodio e obter `legenda_XX.txt`, `comentario_fixado_XX.txt` e `prompt_capa_XX.txt` para cada corte.

## Passo 10 - Integrar agendamento e publicacao

**Objetivo:** conectar o pipeline ao fluxo real de publicacao dos Reels.

Esta etapa pode ter duas fases:

1. gerar um plano de agendamento para uso manual;
2. integrar com API/ferramenta externa para publicar ou agendar automaticamente.

Precisamos definir:

- se a primeira versao usara Meta Business Suite manualmente;
- se usaremos API oficial da Meta;
- como autenticar;
- onde guardar tokens com seguranca;
- como agendar cada corte;
- como anexar video, legenda e capa;
- como publicar ou preparar comentario fixado;
- como lidar com limites, erros e expiracao de token.

Regra editorial:

- o dia atual e o primeiro post;
- o horario padrao e meio-dia;
- cada corte seguinte vai para o proximo dia;
- se houver mais ou menos cortes, o calendario se adapta.

Entregavel deste passo:

- agendamento manual confiavel ou integracao automatica validada.

Criterio de conclusao:

- conseguir transformar os arquivos gerados em posts agendados/publicados sem retrabalho relevante.

## Passo 11 - Testar com um episodio real

**Objetivo:** validar o fluxo inteiro com um episodio completo.

Precisamos fazer:

- escolher um episodio real;
- exportar os cortes;
- preparar a transcricao;
- criar o arquivo `EPXX.txt`;
- rodar o pipeline;
- gerar transcricoes de corte;
- gerar legendas;
- gerar comentarios fixados;
- gerar prompts/capas;
- gerar agendamento;
- revisar tudo;
- agendar ou publicar os Reels.

Entregavel deste passo:

- primeira campanha completa gerada pelo fluxo.

Criterio de conclusao:

- ter todos os Reels do episodio prontos, revisados e agendados/publicados.

## Passo 12 - Avaliar e melhorar o fluxo

**Objetivo:** aprender com o primeiro uso real e ajustar o sistema.

Precisamos avaliar:

- o que deu trabalho demais;
- o que ficou confuso;
- quais arquivos faltaram;
- quais textos precisaram de muita revisao;
- se o calendario funcionou;
- se a saida na pasta externa ajudou;
- se os prompts produziram boas respostas.

Entregavel deste passo:

- lista de melhorias priorizadas.

Criterio de conclusao:

- saber exatamente o que precisa mudar antes do segundo episodio.

## Passo 13 - Evoluir para ferramenta interna

**Objetivo:** transformar o pipeline em uma ferramenta mais confortavel e reutilizavel.

Possiveis evolucoes:

- interface simples;
- cadastro visual dos cortes;
- pre-visualizacao dos pacotes;
- geracao automatica de legendas;
- geracao automatica de prompts de capa;
- suporte a YouTube Shorts;
- suporte a Threads;
- integracao com geracao de imagens;
- integracao parcial com agendamento;
- painel interno do Bereano do Louvor.

Entregavel deste passo:

- plano de evolucao da ferramenta.

Criterio de conclusao:

- decidir quais melhorias realmente valem entrar depois da primeira versao funcional.

## Ordem recomendada

1. Passo 1 - Definir a estrategia editorial da serie.
2. Passo 2 - Definir a identidade editorial e visual.
3. Passo 3 - Definir as entradas do pipeline.
4. Passo 4 - Definir o formato da transcricao.
5. Passo 5 - Definir a estrutura de saida.
6. Passo 6 - Criar o template mestre de legenda.
7. Passo 7 - Criar o template mestre de capa.
8. Passo 8 - Criar a primeira versao tecnica do pipeline.
9. Passo 9 - Integrar Codex CLI para legendas e capas.
10. Passo 10 - Integrar agendamento e publicacao.
11. Passo 11 - Testar com um episodio real.
12. Passo 12 - Avaliar e melhorar o fluxo.
13. Passo 13 - Evoluir para ferramenta interna.

## Como vamos usar este plano

Quando formos trabalhar em um item, escolhemos apenas um passo.

Exemplo:

> Agora vamos fazer o plano micro do Passo 3.

Entao criamos um plano menor, com tarefas concretas, arquivos a criar, decisoes a tomar e criterio de conclusao daquele passo especifico.
