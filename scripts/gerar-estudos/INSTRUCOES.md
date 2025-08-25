# Como Gerar Material de Estudo Automaticamente

Este script automatiza a criação de material de estudo em formato Markdown a partir de vídeos do YouTube, Vimeo, ou qualquer outra plataforma suportada pelo `yt-dlp`.

Ele possui dois modos de operação principais: `aula` e `avulso`.

---

## Estrutura do Comando

O script funciona com sub-comandos. A estrutura geral é:

```bash
python3 gerar_estudo.py [MODO] [ARGUMENTOS_DO_MODO] [OPÇÕES_GLOBAIS]
```

-   `[MODO]`: Pode ser `aula` ou `avulso`.
-   `[ARGUMENTOS_DO_MODO]`: São os parâmetros específicos para cada modo.
-   `[OPÇÕES_GLOBAIS]`: São parâmetros opcionais que funcionam em ambos os modos (ex: `--password`, `--model`).

---

## Modo 1: `aula`

Use este modo para vídeos que fazem parte de um curso estruturado (ex: Teologia Sistemática, Aula 5 de 19). Os arquivos gerados são organizados em pastas por tema.

### Argumentos

1.  `main_topic`: O nome do curso ou tema geral.
2.  `lesson_identifier`: O identificador da aula específica.
3.  `url`: A URL do vídeo.

### Exemplo Prático (Vimeo com Senha)

Suponha que você queira gerar o material para a quinta aula do curso "Teologia Sistemática III".

```bash
python3 gerar_estudo.py aula "Teologia Sistemática III" "Aula 5 de 19" "https://vimeo.com/483614236" --password "ts3neto"
```

**O que este comando faz:**
*   Usa o modo `aula`.
*   Cria (ou usa) a pasta `docs/teologia/temas/teologia_sistemática_iii/`.
*   Processa o vídeo e gera um prompt final para a IA criar o arquivo `.md` consolidado dentro dessa pasta.

---

## Modo 2: `avulso`

Use este modo para qualquer vídeo individual que não faça parte de uma série estruturada (ex: um sermão, uma palestra, um estudo temático único). Os arquivos são salvos diretamente em `docs/estudos/`.

### Argumentos

1.  `title`: O título que você quer dar ao estudo.
2.  `url`: A URL do vídeo.

### Exemplo Prático (YouTube sem Senha)

Suponha que você queira gerar um estudo sobre um vídeo do YouTube sobre a oração.

```bash
python3 gerar_estudo.py avulso "A Importância da Oração na Vida Cristã" "https://www.youtube.com/watch?v=FWAdfuPpLOc"
```

**O que este comando faz:**
*   Usa o modo `avulso`.
*   Verifica se o vídeo do YouTube tem legendas em português para acelerar o processo.
*   Processa o vídeo e gera um prompt final para a IA criar o arquivo `a_importancia_da_oracao_na_vida_crista.md` dentro da pasta `docs/estudos/`.

---

## Opções Globais (Opcionais)

Estas opções podem ser adicionadas no final de qualquer um dos comandos acima.

*   `--password "SUA_SENHA"`
    *   Use esta opção se o vídeo (geralmente no Vimeo) for protegido por senha.
*   `--model [MODELO]`
    *   Permite escolher o modelo do Whisper para a transcrição. O padrão é `large` (mais preciso e lento).
    *   **Opções:** `tiny`, `base`, `small`, `medium`, `large`.
    *   **Exemplo:** Adicione `--model medium` para usar um modelo mais rápido, mas menos preciso.

---
## Fluxo de Execução

Ao executar um comando, o script irá:
1.  Verificar se os arquivos intermediários (vídeo, áudio, transcrição) já existem na pasta `processing/`.
2.  Se um arquivo já existir, ele perguntará se você deseja **[S]obrescrever**, **[P]ular** ou **[A]bortar**.
3.  Listar todos os comandos que serão executados.
4.  Pedir sua confirmação final (`s/n`) antes de começar.
5.  Executar os passos e, ao final, gerar o prompt detalhado para ser usado pela IA.

```text
Olá! Por favor, siga as instruções abaixo para executar a automação completa de geração de material de estudo.

**Informações da Aula:**
*   **Tema Geral do Curso:** [TEMA]
*   **Identificador da Aula:** [AULA]
*   **URL do Vídeo:** [URL_DO_VIMEO]
*   **Senha (opcional):** [SENHA_ou_deixe_em_branco_s_não_houver]

**Sua Tarefa (Assistente de IA):**

**Fase 1: Executar o Script Local**
   - Usando suas ferramentas de terminal, execute o script `gerar_estudo.py` com os argumentos fornecidos acima. O comando será parecido com isto:
     ```bash
     python3 gerar_estudo.py "Tema Geral do Curso" "Identificador da Aula" "URL do Vídeo" --password "SENHA"
     ```
   - Deixe o script rodar completamente. Ele irá baixar os arquivos, transcrever o áudio e, ao final, imprimir um segundo prompt contendo a transcrição e as instruções detalhadas para você (a IA).

**Fase 2: Analisar e Criar os Arquivos**
   - O resultado da Fase 1 será um novo prompt detalhado, com a transcrição completa. Siga as instruções daquele prompt para:
     1. Identificar o tema específico da aula.
     2. Criar um único arquivo de estudo consolidado (`.md`) com artigo, perguntas e prova.
     3. Atualizar o arquivo de fontes central `docs/teologia/fontes_de_referencia/todas_as_fontes.md` (se necessário).

Por favor, inicie a Fase 1.
``` 