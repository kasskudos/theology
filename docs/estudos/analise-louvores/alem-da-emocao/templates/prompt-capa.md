# Template - Geracao de capa de Reel

Voce esta gerando a direcao de arte de uma capa para Reel do projeto **Bereano do Louvor**, dentro da serie **Alem da Emocao**.

Este template sera preenchido automaticamente por um script. Use os dados fornecidos e responda somente no formato solicitado.

## Contexto do projeto

O **Bereano do Louvor** analisa louvores cristaos a luz das Escrituras. A serie **Alem da Emocao** busca ir alem da experiencia emocional da musica e avaliar sua mensagem biblica, teologica e pastoral.

A capa deve comunicar o tema do corte de forma visual, seria e memoravel, sem parecer sensacionalista.

## Direcao teologica

A analise segue uma base reformada, mas isso nao deve aparecer como rotulo na capa.

Regras:

- nao usar expressoes como "teologia reformada", "visao reformada" ou "calvinismo" na arte;
- comunicar a ideia como discernimento biblico;
- quando houver texto teologico, preferir linguagem como "Biblia", "Escrituras", "cruz", "Evangelho", "Cristo" e "adoracao";
- evitar linguagem que afaste antes de explicar.

## Identidade visual

Estilo desejado:

- hand-drawn;
- sketch poster;
- whiteboard/grunge;
- preto e branco;
- vermelho como unica cor de destaque;
- fundo de papel envelhecido;
- tracos grossos;
- visual serio e teologico;
- composicao forte e simples;
- legivel em tela pequena;
- sem 3D;
- sem anime;
- sem fotografia como base principal;
- sem visual infantil;
- sem excesso de elementos;
- sem estetica de thumbnail apelativa.

Formato visual do video:

```text
4:5
```

Resolucao padrao:

```text
1080x1350
```

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

Identificador curto da capa:

```text
{{episodio_normalizado}} - {{numero_corte}}/{{total_cortes}}
```

Identificador completo do Reel:

```text
{{louvor}} - {{episodio_normalizado}} - {{numero_corte}}/{{total_cortes}}
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

Legenda gerada:

```text
{{legenda}}
```

Texto de capa sugerido pela etapa editorial:

```text
{{texto_capa_sugerido}}
```

## Tarefa

Gere a direcao de arte da capa deste Reel.

Voce deve:

1. identificar o conceito visual central;
2. sugerir uma metafora visual;
3. definir composicao;
4. definir texto final da capa;
5. definir onde entra o identificador curto;
6. gerar um prompt final de imagem;
7. gerar instrucoes negativas para evitar erros de estilo.

## Regras para o texto da capa

- Deve ser curto.
- Deve ser forte sem ser apelativo.
- Deve caber visualmente no formato 4:5.
- Deve funcionar como chamada visual do corte.
- Nao precisa explicar tudo.
- Nao deve ter frase longa.
- Nao deve usar muitas palavras abstratas ao mesmo tempo.
- Pode usar pergunta curta se isso combinar com o corte.
- Deve preservar o identificador curto `{{episodio_normalizado}} - {{numero_corte}}/{{total_cortes}}` em algum lugar discreto da capa.

## Regras para a composicao

- Priorize uma imagem central forte.
- Use poucos elementos.
- Use contraste alto.
- Use vermelho apenas como detalhe de enfase.
- A capa precisa continuar legivel no grid do Instagram.
- A capa nao deve depender de texto pequeno para funcionar.
- Evite poluir com muitos simbolos teologicos ao mesmo tempo.
- Evite representar pessoas reais, cantores ou rostos reconheciveis.

## Formato obrigatorio da resposta

Responda exatamente com os blocos abaixo, mantendo os titulos.

```text
CONCEITO_VISUAL:

METAFORA_VISUAL:

COMPOSICAO:

TEXTO_CAPA_FINAL:

POSICAO_IDENTIFICADOR:

PROMPT_IMAGEM:

NEGATIVE_PROMPT:

OBSERVACOES_REVISAO:
```

## Criterios de qualidade

Antes de finalizar, verifique:

- A capa representa o tema do corte?
- O texto da capa e curto e legivel?
- O identificador `{{episodio_normalizado}} - {{numero_corte}}/{{total_cortes}}` foi considerado?
- O estilo visual segue a identidade do Bereano do Louvor?
- O prompt evita 3D, anime, fotografia e excesso de elementos?
- A composicao funciona em 1080x1350?
