# PR Review, formato e tom

Guia para quando o usuário pedir review de PR (via MCP do GitHub, gh CLI ou similar). Define o formato dos comentários, o tom esperado e os passos obrigatórios de verificação antes de gerar qualquer texto.

## Princípios gerais

1. O usuário lê uma explicação técnica detalhada e copia um comentário curto pra postar na PR. São duas coisas diferentes, não confundir.
2. Como o agente não tem o contexto completo da tarefa, o comentário na PR é sempre questionador, tirando dúvidas. Nunca prescritivo, nunca sugerindo "faça X" ou "altere Y".
3. Comentários informais. Sem cumprimentos ("e aí", "olá"), sem dois pontos depois de "queria entender", sem firulas. Direto ao ponto.
4. Nada de copia e cola gigante. Cada finding é um comentário independente, separado por divisor.
5. Sem emojis, sem tabelas, sem headers de severidade tipo "🔴 Blocker". Texto corrido funciona melhor.

## Antes de gerar qualquer comentário

### Verificar se a descrição tem link pro ticket do Jira

Conferir se a descrição da PR contém link pro ticket do Jira associado ao tema (URL pra `mercadolibre.atlassian.net` ou ID no formato `PROJETO-1234`). Se não tiver, gerar um comentário geral (não inline) pedindo o link, é muito comum o time esquecer.

Quando tiver link, validar consistência: o ID do ticket na descrição deve bater com o nome do branch (ex.: `feature/PFDATSERV-4318` → link pra `PFDATSERV-4318`). Se houver divergência (link aponta pra ticket diferente do branch/título), levantar como finding pra confirmar qual é o ticket certo.

### Verificar comentários de review já existentes

Antes de gerar qualquer finding, listar os comentários inline já feitos por outros revisores na PR, para não duplicar. Usar `gh api repos/<owner>/<repo>/pulls/<num>/comments --jq '.[] | {user: .user.login, path: .path, line: .line, body: .body}'`. Se um finding seu coincide em tema/linha com algo já comentado, descartar (ou consolidar mencionando que reforça o ponto do outro revisor, se houver algo a acrescentar). Reportar de volta ao usuário quais foram filtrados, pra ele saber que viu o estado real da PR.

### Verificar linhas reais no branch da PR

Nunca confiar só no diff pra inferir números de linha. O diff mostra hunks, não o estado final do arquivo. Sempre buscar o conteúdo real do arquivo no branch da PR via `gh api`:

```bash
gh api "repos/<owner>/<repo>/contents/<path>?ref=<branch>" --jq '.content' | base64 -d | nl -ba
```

(Atenção: zsh interpreta `?` como glob, sempre quotar a URL.)

Conferir as linhas exatas e capturar o conteúdo literal de cada linha referenciada. Errar uma linha (especialmente quando o arquivo tem hunks múltiplos) invalida o comentário.

### Verificar o estado atual antes de classificar como bug

Não declarar que algo está "faltando" só porque não aparece no diff. O diff só mostra o que mudou. Se uma config, dependência ou método já existe no arquivo (de commit anterior, mesmo branch ou base), o diff não mostra. Sempre ler o arquivo final antes de afirmar "X está faltando".

Caso real: declarei "configurações YAML faltando" como blocker olhando só o diff, mas as 8 propriedades já estavam todas no `application.yml` em linhas que não foram modificadas pelo PR.

### Filtrar findings teóricos sem cenário real

Antes de soltar um finding, perguntar: esse caso acontece de verdade no contexto do time/projeto? Coisas como `Locale.ROOT` em `toLowerCase()` (locale turco), micro otimizações de alocação, hardening contra cenários que exigem configuração exótica de ambiente, são corretos em manual mas o time não opera nesses cenários. Soltar findings desse tipo polui o review e treina o usuário a ignorar comentários. Se o cenário é hipotético e ninguém do time vai bater nele, descartar.

Casos que valem mesmo sendo "teóricos": vulnerabilidade de segurança real (mesmo que improvável), corrupção de dado silencioso, comportamento que diverge do que o código aparenta fazer. Casos que não valem: defesa contra locales improváveis, hardening de input que já é validado upstream, micro perfs sem benchmark.

### Ser preciso em afirmações técnicas

Ao explicar comportamento de API/framework, não simplificar a ponto de gerar afirmação errada. Exemplo: dizer "writableStackTrace=false suprime o stack trace" é meia verdade, na realidade só suprime o stack da exception específica, o cause original (quando passado) preserva o próprio stack. A explicação deve refletir essa nuance.

### Não invocar autoridade que pode não existir

Diretrizes em `.claude/rules/` ou `.cursor/rules/` são guias locais do repo, não policies formais corporativas. Não falar "a regra de segurança da empresa proíbe X" quando na verdade é uma rule do agente. Linkar o arquivo e linha específica da rule, deixar o usuário decidir o peso.

## Estrutura de cada comentário

Para cada finding, gerar nesta ordem:

```
### `<NomeDoArquivo.ext>` linha N (ou linhas N a M)

Conteúdo da linha (ou linhas):
```linguagem
<conteúdo literal exato copiado do arquivo>
```

<Explicação técnica detalhada para o usuário ler. Pode ser longa, completa, contextualizada. Sem prefixos tipo "Explicação para você:". Direto ao ponto. Pode mencionar a regra interna que o caso violaria, citando arquivo e linha da rule.>

> <comentário curto e informal pra colar na PR. Sem cumprimentos. Sem "queria entender:". Em forma de pergunta. Não sugerir ações específicas, só tirar dúvida.>
```

Sem prefixos "Explicação pra você:" nem "Comentário pra colar:". O usuário já sabe que a primeira parte é pra ler e o blockquote é pra colar.

Path do arquivo só vai no header se necessário pra desambiguar (arquivos com mesmo nome em diretórios diferentes). Padrão é só o nome do arquivo.

## Tom do comentário

Modelos do que NÃO fazer:
- "e ai, queria entender uma coisa: ..."
- "Olá, fiquei na dúvida sobre ..."
- "Sugestão: extrair como constante e ..."
- "Recomendo adicionar @Transactional ..."
- "Você precisa validar o input ..."

Modelos do que fazer:
- "esse `@Modifying` não precisaria de um `@Transactional` junto?"
- "tem motivo pra esses timeouts serem `long`?"
- "essa URL tá repetida nos três testes, faz sentido extrair como constante ou tem motivo pra deixar inline?"
- "teve motivo específico pra `writableStackTrace=false`?"

Padrão geral: pergunta curta, em minúsculas (sem capitalizar a primeira letra para reforçar informalidade), termina com interrogação. Pode ter mais de uma frase, separadas por vírgula. Não usar dois pontos para introduzir explicação.

## Workflow recomendado

1. Listar PRs abertos via MCP do GitHub ou `gh pr list`.
2. Pegar o diff e os arquivos via `mcp__github__get_pull_request_diff` / `get_pull_request_files`, ou `gh pr diff <num>`.
3. Para cada finding candidato, buscar o arquivo completo no branch da PR via `gh api .../contents/<path>?ref=<branch>` e validar a linha exata e seu conteúdo.
4. Confirmar com o estado real do repo se a alegação ainda procede (ex.: configs já existem em outro arquivo, método já tem caller correto, etc).
5. Gerar a estrutura "header + linha + conteúdo + explicação + comentário" para cada finding.
6. Separar findings com `---`.

## Iterações comuns

O usuário tipicamente vai pedir para:
- Reformatar (tirar emojis, headers, tabelas).
- Tornar o comentário mais informal.
- Confirmar a linha exata mostrando o conteúdo.
- Justificar referências a regras (mostrar o arquivo e linha da rule).
- Refinar afirmações técnicas imprecisas.

Antecipar essas iterações desde a primeira tentativa.
