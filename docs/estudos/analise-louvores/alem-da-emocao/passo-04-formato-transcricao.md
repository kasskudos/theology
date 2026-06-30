# Passo 04 - Formato da transcricao

## Objetivo deste passo

Definir como o pipeline deve ler a transcricao completa, identificar timestamps e extrair o texto de cada corte.

## Origem da transcricao

A transcricao vem de um plugin e pode conter marcas mecanicas.

Exemplo:

```text
Time	Subtitle
0s	Sejam muito bem-vindos a mais um episodio do Alem da Emocao, nosso
4s	programa semanal de analise biblica e teologica de louvores cristaos. [musica]
9s	>> Ola, pessoal. E muito bom estar aqui de novo para mais um mergulho profundo com
14s	voces hoje. >> E olha, o mergulho de hoje e sobre um
```

O pipeline deve aceitar essa transcricao como ela vier, sem exigir edicao manual previa.

## Formato oficial dos timestamps

Ate 59 segundos:

```text
0s
1s
10s
55s
```

A partir de 1 minuto:

```text
1:00
1:10
3:40
9:33
10:17
20:30
33:50
```

Regras:

- nao precisa aceitar `00:01:10`;
- nao precisa aceitar `[00:01:10]`;
- nao precisa aceitar multiplos formatos alternativos;
- o parser deve focar no formato real exportado pelo plugin.

## Linha de transcricao

Cada linha valida da transcricao deve comecar com um timestamp.

Exemplos:

```text
0s	Texto...
1:10	Texto...
20:30	Texto...
```

O separador pode ser uma tabulacao ou espacos. O script deve separar o timestamp inicial do restante da linha.

## Conversao para segundos

O script deve converter timestamps para segundos.

Exemplos:

```text
0s -> 0
55s -> 55
1:00 -> 60
1:10 -> 70
10:17 -> 617
33:50 -> 2030
```

## Extracao dos cortes

Cada `Corte N` informa duas linhas:

- linha inicial do corte;
- linha final do corte.

Exemplo:

```text
Corte 1
22:52	>> Fizemos. Mas e ai? Diante de tudo isso, o que a gente faz na pratica?
25:50	>> E amarrar o subjetivo no objetivo absoluto. Sensacional.
```

O script deve:

1. ler o timestamp da primeira linha do corte;
2. ler o timestamp da segunda linha do corte;
3. procurar na transcricao completa todas as linhas com tempo entre inicio e fim;
4. incluir a linha de inicio;
5. incluir a linha de fim;
6. gerar a transcricao do corte com esse intervalo.

## Limpeza do texto

Os timestamps devem ser preservados.

A limpeza deve atuar apenas no texto da fala.

Regra inicial:

- remover `>> ` do texto;
- se aparecer `>>` sem espaco, remover tambem;
- normalizar espacos duplicados depois da remocao.

Exemplo:

Entrada:

```text
14s	voces hoje. >> E olha, o mergulho de hoje e sobre um
```

Saida:

```text
14s	voces hoje. E olha, o mergulho de hoje e sobre um
```

Observacao:

- os timestamps continuam no arquivo de transcricao do corte;
- a limpeza nao deve reescrever ideias;
- a limpeza nao deve transformar o texto em legenda final;
- a limpeza serve apenas para remover marcas mecanicas do plugin.

## Marcadores como [musica]

O marcador `[musica]` pode aparecer na transcricao.

Decisao inicial:

- nao remover automaticamente nesta etapa;
- manter o texto fiel ao material extraido;
- decidir depois, nos templates ou na revisao, se esse marcador deve influenciar a legenda.

## Criterio de conclusao do Passo 4

Este passo esta concluido quando o pipeline consegue:

- reconhecer timestamps no formato real do plugin;
- separar transcricao completa da lista de cortes;
- converter tempos para segundos;
- extrair o trecho correto de cada corte;
- preservar os timestamps;
- remover `>> ` sem alterar o conteudo teologico ou argumentativo.
