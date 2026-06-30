# Passo 05 - Estrutura de saida e automacoes

## Objetivo deste passo

Definir o que o pipeline deve gerar depois de ler o arquivo `EPXX.txt`, extrair os cortes e localizar os videos correspondentes na pasta externa do episodio.

A saida desejada nao e apenas uma pasta organizada. O objetivo final e que o script conduza o fluxo completo:

1. extrair a transcricao de cada corte;
2. gerar a legenda de cada corte;
3. gerar a capa de cada corte;
4. preparar ou realizar o agendamento dos posts;
5. lidar com o comentario fixado quando a publicacao permitir.

## Local de saida

Os arquivos gerados devem ser colocados na mesma pasta dos videos do episodio.

Exemplo:

```text
C:\Users\PICHAU\Documents\Alem da Emocao\EP2\
  Bencaos que nao tem Fim - Alem da Emocao - EP2.mp4
  corte 1.mp4
  corte 2.mp4
  transcricao_corte_01.txt
  transcricao_corte_02.txt
  pacote_editorial_01.txt
  pacote_editorial_02.txt
  legenda_01.txt
  legenda_02.txt
  comentario_fixado_01.txt
  comentario_fixado_02.txt
  enquete_01.txt
  enquete_02.txt
  texto_capa_01.txt
  texto_capa_02.txt
  prompt_capa_01.txt
  prompt_capa_02.txt
  capa_01.png
  capa_02.png
```

Os videos continuam fora do Git. Os arquivos gerados nessa pasta tambem podem ficar fora do Git, porque sao materiais de producao do episodio.

## Transcricoes dos cortes

Para cada corte definido no `EPXX.txt`, o script deve gerar um arquivo de transcricao correspondente.

Padrao:

```text
transcricao_corte_01.txt
transcricao_corte_02.txt
transcricao_corte_03.txt
```

Regras:

- o numero vem do bloco `Corte N` do arquivo `EPXX.txt`;
- o texto deve ser extraido da transcricao completa usando o inicio e o fim do corte;
- os timestamps devem ser preservados;
- a marca `>> ` deve ser removida do texto;
- o script deve manter o conteudo do corte fiel ao que esta na transcricao;
- a limpeza nao deve reescrever o argumento, apenas remover marcas mecanicas.

## Legendas dos videos

Depois de gerar a transcricao de um corte, o script deve gerar a legenda daquele corte.

Padrao:

```text
legenda_01.txt
legenda_02.txt
legenda_03.txt
```

Arquivos relacionados:

```text
pacote_editorial_01.txt
comentario_fixado_01.txt
enquete_01.txt
texto_capa_01.txt
codex_legenda_01.raw.txt
```

Para gerar cada legenda, o script deve chamar o Codex via CLI em uma sessao propria, passando:

- contexto do projeto;
- estrategia editorial da serie;
- identidade editorial e visual;
- dados do episodio;
- numero do corte;
- total de cortes;
- transcricao do corte;
- prompt editorial;
- instrucoes de formato da resposta.

Importante:

- a geracao deve ser feita **um corte por vez**;
- o script deve esperar a geracao de `legenda_01.txt` terminar antes de iniciar `legenda_02.txt`;
- isso reduz risco de rate limit e facilita revisar erro por erro;
- se uma chamada falhar, o script deve parar ou pedir confirmacao antes de continuar.

## Capas dos videos

Depois da legenda, o script deve gerar a capa de cada corte.

Padrao desejado:

```text
capa_01.png
capa_02.png
capa_03.png
```

Arquivos auxiliares recomendados:

```text
prompt_capa_01.txt
prompt_capa_02.txt
prompt_capa_03.txt
```

Para cada capa, o script deve chamar uma nova sessao do Codex via CLI, passando:

- contexto do projeto;
- identidade visual;
- dados do episodio;
- numero do corte;
- legenda gerada;
- transcricao do corte;
- prompt de direcao de arte;
- instrucoes para gerar a capa ou o prompt final da imagem.

Importante:

- a geracao das capas tambem deve acontecer **uma por vez**;
- o script deve esperar a capa ou prompt da capa terminar antes de seguir para o proximo corte;
- isso tambem evita rate limit.

Observacao tecnica:

- para gerar imagem de fato, o pipeline precisara de um backend de imagem disponivel;
- se o Codex CLI nao conseguir gerar o bitmap diretamente, ele deve pelo menos gerar `prompt_capa_XX.txt`;
- nesse caso, a geracao automatica de `capa_XX.png` fica para uma etapa posterior.

## Agendamento dos posts

O objetivo final e que o script consiga agendar os posts automaticamente.

Regra editorial:

- o dia atual deve ser considerado o dia do primeiro post;
- o primeiro corte vira `1/N`;
- os proximos cortes devem ser agendados para os dias seguintes;
- o horario padrao deve ser meio-dia;
- se houver mais ou menos que 7 cortes, o calendario deve se adaptar automaticamente.

Exemplo:

```text
Corte 1 -> hoje, 12:00
Corte 2 -> amanha, 12:00
Corte 3 -> depois de amanha, 12:00
```

O script deve gerar pelo menos um plano de agendamento.

Arquivo recomendado:

```text
agendamento.csv
```

Campos recomendados:

- numero do corte;
- data;
- horario;
- video;
- legenda;
- capa;
- comentario fixado;
- status;
- observacoes.

## Publicacao automatica

A publicacao/agendamento automatico no Instagram depende de integracao externa.

Essa etapa pode exigir:

- conta profissional do Instagram;
- pagina do Facebook vinculada;
- app/configuracao da Meta;
- tokens de acesso;
- permissoes;
- tratamento de expiracao de tokens;
- limites de API;
- regras especificas para Reels;
- verificacao do que a API permite em relacao a comentario fixado.

Por isso, o plano deve separar duas fases:

1. **Fase local:** gerar todos os arquivos e o `agendamento.csv`.
2. **Fase integrada:** tentar publicar/agendar automaticamente quando a integracao estiver validada.

## Comentario fixado

Cada post deve ter um comentario fixado ou, no minimo, um comentario sugerido.

Padrao de arquivo:

```text
comentario_fixado_01.txt
comentario_fixado_02.txt
comentario_fixado_03.txt
enquete_01.txt
enquete_02.txt
enquete_03.txt
```

Regra editorial:

- o comentario fixado deve priorizar uma pergunta que gere conversa;
- pode variar conforme o conteudo do corte;
- pode apontar para outro trecho, para a serie ou para a analise completa quando fizer sentido.

Regra tecnica:

- se a API permitir publicar e fixar comentario automaticamente, o script pode fazer isso;
- se nao permitir ou se a integracao ainda nao estiver pronta, o script deve deixar o comentario pronto para uso manual.

## Ordem de execucao desejada

Para cada episodio:

1. Ler `EPXX.txt`.
2. Identificar dados do episodio.
3. Identificar cortes.
4. Localizar pasta externa do episodio.
5. Validar videos `corte N.mp4`.
6. Gerar `transcricao_corte_XX.txt`.
7. Chamar Codex CLI para gerar `legenda_XX.txt`.
8. Chamar Codex CLI para gerar `comentario_fixado_XX.txt` e `enquete_XX.txt`.
9. Chamar Codex CLI ou backend de imagem para gerar `prompt_capa_XX.txt` e/ou `capa_XX.png`.
10. Gerar `agendamento.csv`.
11. Se houver integracao com a Meta, agendar/publicar posts.
12. Se houver suporte, publicar/fixar comentarios.

## Comportamento em caso de excecao

O padrao editorial e 7 cortes, mas o pipeline deve aceitar excecoes.

Regras:

- o arquivo `EPXX.txt` e a fonte principal da verdade;
- se o TXT tiver 6 cortes, a campanha tem 6 posts;
- se o TXT tiver 8 cortes, a campanha tem 8 posts;
- se faltar um video `corte N.mp4`, o script deve avisar;
- se houver video extra sem corte correspondente, o script deve avisar;
- a geracao deve continuar apenas quando os arquivos essenciais existirem.

## Criterio de conclusao do Passo 5

Este passo esta concluido quando estiver definido:

- onde os arquivos gerados ficam;
- quais arquivos cada corte deve produzir;
- como as legendas serao geradas;
- como as capas serao geradas;
- como evitar rate limit;
- como o calendario/agendamento sera criado;
- como lidar com mais ou menos de 7 cortes;
- qual parte e local e qual parte depende de integracao externa.
