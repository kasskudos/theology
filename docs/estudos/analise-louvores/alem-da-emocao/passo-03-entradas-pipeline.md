# Passo 03 - Entradas do pipeline

## Objetivo deste passo

Definir quais arquivos o pipeline recebe e onde cada informacao deve estar.

A regra principal e: a entrada precisa ser simples para o criador. O script deve fazer o trabalho pesado de interpretar e estruturar os dados.

## Arquivo principal do episodio

Cada episodio tera um unico arquivo TXT dentro do projeto.

Pasta:

```text
docs/estudos/analise-louvores/alem-da-emocao/episodios/
```

Padrao de nome:

```text
EP02.txt
EP03.txt
EP10.txt
```

O nome do arquivo deve usar o episodio normalizado com dois digitos.

Exemplo:

- arquivo: `EP02.txt`;
- primeira linha pode conter `EP2`;
- o sistema normaliza para `EP02`.

## Estrutura geral do arquivo

O arquivo `EPXX.txt` deve conter:

1. linha inicial com nome do louvor, nome da serie e episodio;
2. link do YouTube, quando houver;
3. cabecalho da transcricao vindo do plugin;
4. transcricao completa com timestamps;
5. lista de cortes no final.

Exemplo:

```text
Bencaos que nao tem Fim - Alem da Emocao - EP2
YouTube: https://youtu.be/exemplo
Time	Subtitle
0s	Sejam muito bem-vindos a mais um episodio do Alem da Emocao, nosso
4s	programa semanal de analise biblica e teologica de louvores cristaos.
9s	>> Ola, pessoal. E muito bom estar aqui de novo.

Corte 1
0s	Sejam muito bem-vindos a mais um episodio do Alem da Emocao, nosso
1:27	grande tensao da nossa conversa, porque quando os numeros sao tao gigantes

Corte 2
22:52	>> Fizemos. Mas e ai? Diante de tudo isso, o que a gente faz na pratica?
25:50	>> E amarrar o subjetivo no objetivo absoluto. Sensacional.
```

## Cabecalho do episodio

A primeira linha util deve seguir este padrao humano:

```text
Nome do louvor - Alem da Emocao - EP2
```

O script deve extrair:

- `louvor`: texto antes do primeiro ` - `;
- `serie`: texto entre o primeiro e o segundo ` - `;
- `episodio`: `EP2`, `EP02`, etc.;
- `episodio_normalizado`: `EP02`, `EP03`, `EP10`, etc.

## Link do YouTube

O link do YouTube pode aparecer no cabecalho:

```text
YouTube: https://youtu.be/exemplo
```

Regras:

- se existir, o script deve guardar o link nos metadados;
- se nao existir, o pipeline deve continuar;
- a geracao de legenda deve receber o link quando ele estiver disponivel.

## Transcricao completa

A transcricao vem do plugin e pode conter uma linha de cabecalho:

```text
Time	Subtitle
```

Essa linha deve ser ignorada pelo script.

Depois dela, cada linha da transcricao tem um timestamp e o texto correspondente.

Exemplo:

```text
0s	Sejam muito bem-vindos...
4s	programa semanal...
1:00	mundo cantando.
```

## Lista de cortes

A lista de cortes fica no final do mesmo arquivo.

Nao sera usado marcador especial como `=== CORTES ===`.

O inicio da lista de cortes e identificado pela primeira linha no padrao:

```text
Corte 1
```

Cada corte deve ter:

- linha `Corte N`;
- primeira linha copiada da transcricao completa, indicando o inicio;
- ultima linha copiada da transcricao completa, indicando o fim.

Exemplo:

```text
Corte 1
22:52	>> Fizemos. Mas e ai? Diante de tudo isso, o que a gente faz na pratica?
25:50	>> E amarrar o subjetivo no objetivo absoluto. Sensacional.
```

O texto dessas duas linhas serve como referencia humana. Para o script, o que importa principalmente sao os timestamps:

- primeiro timestamp do bloco: inicio do corte;
- segundo timestamp do bloco: fim do corte.

O script deve voltar para a transcricao completa e extrair todo o recheio entre esses tempos.

## Pasta externa dos videos

Os videos nao ficam no Git.

Eles ficam na pasta externa padrao:

```text
%USERPROFILE%\Documents\Alem da Emocao\
```

O episodio define a subpasta:

```text
EP02 -> %USERPROFILE%\Documents\Alem da Emocao\EP2\
EP03 -> %USERPROFILE%\Documents\Alem da Emocao\EP3\
EP12 -> %USERPROFILE%\Documents\Alem da Emocao\EP12\
```

Ou seja:

- para exibicao e arquivos de texto, usar `EP02`;
- para encontrar a pasta externa, remover zero a esquerda e usar `EP2`.

## Videos dos cortes

O padrao oficial dos videos e:

```text
corte 1.mp4
corte 2.mp4
corte 3.mp4
```

Regras:

- `Corte 1` no TXT corresponde a `corte 1.mp4`;
- `Corte 2` no TXT corresponde a `corte 2.mp4`;
- nao precisa aceitar variacoes como `corte1.mp4`, `reel_01.mp4` ou `corte_1.mp4`;
- se faltar um video esperado, o script deve avisar.

## Quantidade de cortes

O padrao editorial e 7 cortes, mas pode haver excecoes.

Regras:

- o arquivo `EPXX.txt` e a fonte principal da verdade;
- se o TXT tiver 6 cortes, a campanha tem 6 Reels;
- se o TXT tiver 8 cortes, a campanha tem 8 Reels;
- se a pasta tiver videos extras, o script deve avisar;
- se a pasta nao tiver video para um corte listado, o script deve avisar.

## Formato dos videos

O formato padrao do projeto e:

```text
1080x1350
```

Proporcao:

```text
4:5
```

O script pode validar esse formato quando `ffprobe` estiver disponivel.

Se o video estiver fora do formato esperado, o script deve avisar, mas nao precisa bloquear automaticamente.

## Criterio de conclusao do Passo 3

Este passo esta concluido quando:

- existe uma pasta `episodios/`;
- existe um exemplo `EP02.example.txt`;
- o formato do arquivo de entrada esta claro;
- a relacao entre `EPXX.txt` e a pasta externa de videos esta definida;
- o script sabe como associar cada `Corte N` ao video `corte N.mp4`.
