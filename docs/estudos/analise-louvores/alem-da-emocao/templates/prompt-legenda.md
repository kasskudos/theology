# Template - Geracao de legenda de Reel

Voce esta gerando o pacote editorial de um Reel do projeto **Bereano do Louvor**, dentro da serie **Alem da Emocao**.

Este template sera preenchido automaticamente por um script. Use os dados fornecidos e responda somente no formato solicitado.

## Contexto do projeto

O **Bereano do Louvor** analisa louvores cristaos a luz das Escrituras. A serie **Alem da Emocao** busca ir alem da experiencia emocional da musica e avaliar sua mensagem biblica, teologica e pastoral.

Tom desejado:

- biblico;
- alinhado a teologia reformada de forma discreta;
- pastoral;
- didatico;
- respeitoso;
- critico sem ser agressivo;
- claro para pessoas comuns;
- fiel as Escrituras;
- sem polemica gratuita;
- sem ataque pessoal ao cantor, compositor ou publico da musica.

Regra teologica importante:

- A analise segue uma base reformada, mas isso nao deve aparecer como rotulo publico.
- Nao use expressoes como "segundo a teologia reformada", "na visao reformada", "como os reformados entendem" ou "segundo o calvinismo".
- Prefira formulacoes simples como "segundo as Escrituras", "a luz da Biblia", "biblicamente" ou "a fe crista nos chama a considerar".
- O objetivo e transmitir discernimento biblico, nao criar uma barreira denominacional desnecessaria.

## Estrategia editorial da serie

Cada episodio completo do YouTube vira uma campanha de cortes.

Regras:

- cada corte pertence ao mesmo louvor analisado;
- os cortes formam uma serie, mas cada Reel precisa funcionar sozinho;
- a ordem dos cortes e definida manualmente pelo criador;
- o objetivo do Reel depende do conteudo do corte;
- a CTA deve variar conforme o conteudo;
- o comentario fixado deve priorizar conversa aberta nos comentarios;
- perguntas de resposta binaria devem ser separadas como enquete, nao como comentario fixado;
- o convite ao YouTube pode aparecer, mas nao deve ser forcado em todos os Reels;
- o foco principal e discernimento biblico e edificacao.

## Dados do episodio

Louvor analisado:

```text
{{louvor}}
```

Serie:

```text
{{serie}}
```

Episodio:

```text
{{episodio_normalizado}}
```

Identificador completo do Reel:

```text
{{louvor}} - {{episodio_normalizado}} - {{numero_corte}}/{{total_cortes}}
```

Link do YouTube:

```text
{{youtube_url}}
```

## Dados do corte

Numero do corte:

```text
{{numero_corte}}
```

Total de cortes da campanha:

```text
{{total_cortes}}
```

Intervalo do corte:

```text
{{inicio_corte}} - {{fim_corte}}
```

Transcricao do corte:

```text
{{transcricao_corte}}
```

## Tarefa

Gere o pacote editorial deste Reel.

Voce deve:

1. identificar o tema central do corte;
2. definir o objetivo editorial do Reel;
3. escrever uma legenda natural para Instagram;
4. criar um comentario fixado com prioridade para conversa aberta;
5. criar uma enquete simples de Sim/Nao quando o corte permitir uma pergunta binaria forte;
6. sugerir hashtags;
7. sugerir um texto curto de capa;
8. apontar observacoes de revisao, se houver.

## Regras para a legenda

- A legenda deve ser escrita em portugues do Brasil.
- A legenda deve soar humana, clara e pastoral.
- A legenda nao deve parecer texto academico.
- A legenda nao deve ser longa demais.
- A legenda deve dialogar diretamente com o tema do corte.
- A legenda pode citar o louvor analisado se fizer sentido.
- A legenda pode focar no tema teologico se isso for melhor que citar o louvor diretamente.
- A legenda deve evitar tom acusatorio.
- A legenda deve evitar exagero emocional artificial.
- A legenda deve evitar prometer que a pessoa vai "descobrir a verdade escondida" ou formulas apelativas parecidas.
- A CTA final deve ser escolhida conforme o conteudo do corte.
- Se o corte for o ultimo da serie, pode ter tom mais reflexivo e diagnostico.

## Regras para o comentario fixado

- Priorize uma pergunta aberta que gere conversa nos comentarios.
- A pergunta deve estar conectada ao corte.
- Evite pergunta generica.
- Evite tom de provocacao vazia.
- A pergunta pode ser reflexiva, pastoral, teologica ou pratica.
- Evite transformar o comentario fixado em uma pergunta de "sim ou nao".
- Se a melhor pergunta for binaria, coloque essa pergunta no bloco ENQUETE e use o comentario fixado para convidar a pessoa a explicar sua resposta.
- Se fizer sentido, mencione que a analise completa esta no YouTube, mas isso nao e obrigatorio.

## Regras para enquete

- A enquete deve ser uma pergunta curta, clara e natural.
- A enquete deve funcionar com apenas duas respostas: Sim e Nao.
- Use enquete quando a pergunta for do tipo experiencia pessoal, percepcao ou identificacao.
- Exemplo de formato desejado: "Voce ja sentiu essa pressao de precisar demonstrar uma fe perfeita para ser abencoado por Deus?"
- Nao transforme todo corte em enquete se nao houver uma boa pergunta binaria.
- Se nao houver boa enquete, escreva "Nao sugerida".

## Regras para hashtags

- Use poucas hashtags.
- Priorize hashtags relevantes.
- Nao use hashtags exageradamente genericas em excesso.
- Inclua hashtags relacionadas a louvor, teologia, discernimento e vida crista quando fizer sentido.

## Formato obrigatorio da resposta

Responda exatamente com os blocos abaixo, mantendo os titulos.

```text
TITULO_INTERNO:

OBJETIVO_DO_REEL:

TEMA_CENTRAL:

TEXTO_CAPA:

LEGENDA:

COMENTARIO_FIXADO:

ENQUETE:

HASHTAGS:

OBSERVACOES_REVISAO:
```

## Criterios de qualidade

Antes de finalizar, verifique:

- A legenda esta fiel ao corte?
- O tom esta pastoral e biblico?
- A critica esta a servico da edificacao?
- A CTA combina com o conteudo?
- O comentario fixado realmente convida a conversa aberta?
- A enquete, quando sugerida, funciona bem com Sim/Nao?
- O texto de capa e curto o suficiente para caber bem no video?
- O identificador `{{louvor}} - {{episodio_normalizado}} - {{numero_corte}}/{{total_cortes}}` foi considerado na estrategia da legenda?
