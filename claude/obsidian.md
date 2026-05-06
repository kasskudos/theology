# Obsidian — Anotações e Documentação

Vault principal: `/Users/lkudo/work/obs/meli/`

## Estrutura de pastas

```
reunioes/
  cerimonias/   — dailys e cerimônias do time
  one-a-one/    — 1:1s e alinhamentos bilaterais
  syncs/        — syncs recorrentes com times
  outras/       — reuniões que não se encaixam nas demais
tasks/          — uma nota por task (geradas das reuniões)
recursos/       — decisões técnicas e notas de referência
pessoas/        — observações sobre colaboradores para feedback
arquivo/        — notas inativas ou concluídas
templates/      — templates Templater (ex: Marcar como Done)
TaskNotes/
  Views/
    Kanban Board.md   — board Kanban com colunas TODO / WIP / DONE
    Kanban Tasks.base — view alternativa em tabela (Obsidian Bases)
```

---

## Propriedades das notas de reunião

```yaml
participantes:
  - Nome Completo
tipo: daily | alinhamento | sync | análise | conversa | decisão | observação
tema: freshness | pangea | modelos-ml | datasets | infraestrutura | time | ferramentas | genai | pf
```

Valores de `tipo`:
- `daily` — standup diário do time
- `alinhamento` — reunião para alinhar decisão ou direção
- `sync` — check-in recorrente com pessoa ou time
- `análise` — deep-dive em problema ou tema técnico
- `conversa` — troca informal (Slack, 1:1 leve)
- `decisão` — registro de decisão técnica
- `observação` — nota sobre colaborador para feedback futuro

---

## Formato de notas de reunião

Estrutura obrigatória:

- **TL;DR** — resumo breve do assunto principal e do que foi definido/decidido
- **Pontos principais discutidos** — pontos e decisões em lista
- **Próximos passos** — ações de **outras pessoas** (não Lucas), em lista, com responsável no final de cada item separado por `—`. Ex: `- Atualizar planilha com novos critérios — Jade`
- **Minhas ações** — bloco DataviewJS que busca automaticamente as tasks geradas desta reunião. **Nunca usar lista de checkboxes** — as tasks vivem em `tasks/` e o status é lido de lá em tempo real.
- **Outros comentários** — observações adicionais relevantes

> Nunca usar tabelas — listas são mais fáceis de compartilhar no Slack.

> A distinção entre "Próximos passos" e "Minhas ações" é crítica: "Próximos passos" é para acompanhar o que outros precisam fazer; "Minhas ações" mostra as tasks do vault vinculadas a esta reunião, com status em tempo real.

O bloco "Minhas ações" deve sempre ser exatamente:

~~~markdown
## Minhas ações

```dataviewjs
const tasks = dv.pages('"tasks"')
  .where(p => String(p.origem).includes(dv.current().file.name));
dv.table(
  ["Task", "Status", "Priority", "Due", "Requester"],
  tasks.map(p => [p.file.link, p.status, p.priority, p.due, p.requester])
);
```
~~~

> `origem` nos arquivos de task deve ter aspas: `origem: "[[YYYY-MM-DD nome da reunião]]"` — sem aspas o YAML interpreta `[[` como array aninhado e quebra o link.
> Usar DataviewJS (não DQL puro) — o DQL falha na comparação de wikilinks com `this.file.link`.
> Requer plugin Dataview com "Enable JavaScript Queries" ativo nas configurações.

---

## Convenção de nome de arquivo

- Reuniões: `YYYY-MM-DD descrição curta.md`
- Tasks: nome descritivo simples em kebab-case (ex: `relatorio-latencia-phs.md`)

---

## Formato de tasks

Cada task é uma nota individual em `tasks/`. Frontmatter completo:

```yaml
---
title: "Título completo da task"
status: todo | wip | done
completed: YYYY-MM-DD        # preenchido automaticamente pelo template ao marcar done
priority: high | medium | low
tema: freshness | pangea | modelos-ml | datasets | infraestrutura | time | ferramentas | genai | pf
origem: "[[YYYY-MM-DD nome da reunião de origem]]"
participantes:
  - Lucas Kudo
due: YYYY-MM-DD              # prazo de entrega — obrigatório, sempre preencher com base no contexto da reunião
requester: Nome Completo     # quem pediu/solicitou a task
---
```

> `scheduled` foi removido — só existe `due` (prazo de entrega).
> `due` é **obrigatório**. Se a reunião não definiu prazo explícito, inferir pelo contexto (urgência, próxima reunião sobre o tema, etc.) e registrar.

O **corpo da task** tem duas seções obrigatórias:

```
## Contexto

Toda a informação de fundo necessária para retomar a task sem precisar abrir a reunião de origem,
independentemente de quanto tempo passou. Inclui: qual é o problema, qual a situação atual,
quem está envolvido, quais decisões já foram tomadas, qual é o risco ou impacto se não for feito,
e qualquer detalhe técnico ou de negócio relevante mencionado na reunião.

## O que fazer

Lista clara e objetiva das ações concretas a executar, com datas quando mencionadas.
```

---

## Kanban Board

**Arquivo:** `TaskNotes/Views/Kanban Board.md`
**Plugin:** Kanban (mgmeyers/obsidian-kanban)
**Colunas:** TODO | WIP | DONE

Cada card no board tem:
- Tags de prioridade: `#high`, `#medium`, `#low`
- Tags de tema: `#freshness`, `#pangea`, `#modelos-ml`, etc.
- `📅 YYYY-MM-DD` para tasks com prazo
- Link wikilink para o arquivo da task: `[[nome-arquivo|Título legível]]`

Formato de um card:
```
- [ ] [[nome-arquivo|Título da task]] #high #freshness 📅 2026-04-11
```

---

## Marcar task como done (Templater)

Template: `templates/Marcar como Done.md`

Ao executar o template no arquivo de uma task, ele:
1. Seta `status: done`
2. Preenche `completed:` com a data de hoje (YYYY-MM-DD)

Configuração necessária no Templater:
- Template folder: `templates`
- Associar o template `Marcar como Done` a um hotkey (ex: `Cmd+Shift+D`)

Após executar o template, mover o card no Kanban Board manualmente para a coluna DONE.

---

## Processando notas de reunião (qualquer tipo)

Quando o usuário pedir para processar/anotar qualquer reunião (daily, sync, 1:1, alinhamento, etc.) — geralmente compartilha um arquivo com a transcrição do Meet:

> **Regra geral:** antes de escrever qualquer arquivo, montar um plano de execução explícito (TodoWrite ou lista numerada na resposta) cobrindo todos os passos abaixo. Ao final, antes de declarar pronto, reler o plano e confirmar item por item que cada passo foi feito de fato (não basta ter "tentado"). Se algum passo foi pulado, voltar e executar antes de entregar. Esse checkpoint é obrigatório porque o atalho clássico é assumir que `search_files` substitui `read_file_content`, ou que a comparação com o doc do Drive é decorativa, e não é.

1. **Buscar o doc oficial da reunião no Google Drive antes de escrever a nota.** O Meet gera automaticamente um doc de anotações ("Notas da reunião" / "Meeting notes") que costuma capturar pontos que a transcrição bruta perde (resumo, decisões, action items destacados pelo Gemini).
   - Usar `mcp__claude_ai_Google_Drive__search_files` com query pela data e/ou pelo nome do evento (ex: `daily`, `sync rollout`, `1:1 Ariel`, data da reunião).
   - **Ler obrigatoriamente com `mcp__claude_ai_Google_Drive__read_file_content`** — o `contentSnippet` retornado pelo `search_files` é truncado e NÃO substitui a leitura completa. Se o plano de execução marcar este passo como feito sem ter chamado `read_file_content`, o passo não foi feito.
   - Se não encontrar, seguir só com a transcrição e avisar o usuário que o doc do Drive não foi localizado.
2. **Combinar as duas fontes ao montar a nota:** transcrição traz fala literal e nuances; doc do Drive traz estrutura, decisões e action items consolidados. Comparar item por item — divergências entre as duas fontes (nomes próprios, nomes de produtos, ações que só uma das fontes capturou) são o sinal mais comum de que a transcrição da IA errou em algum ponto. Trazer essas divergências para o usuário antes de fechar a nota.
3. Seguir o formato padrão de nota de reunião (TL;DR, Pontos principais, Próximos passos, Minhas ações, Outros comentários).
4. Extrair tasks do Lucas para `tasks/` conforme seção abaixo.
5. **Checkpoint final antes de entregar:** reler os passos 1, 2, 3, 4 e confirmar explicitamente o que foi feito de cada um. Se em algum momento foi possível responder "não cheguei a fazer X porque Y", o passo não foi cumprido — voltar e executar.

---

## Extraindo tasks de reuniões

Ao processar uma nota de reunião e identificar ações atribuídas a Lucas:
1. Criar um arquivo em `tasks/` com nome descritivo em kebab-case
2. Preencher todo o frontmatter (status: todo, requester = quem pediu, origem = link para a reunião)
3. Escrever corpo com 5–10 linhas de contexto
4. Adicionar o card no `TaskNotes/Views/Kanban Board.md` na coluna TODO com tags de prioridade e tema

---

## Observações

- Vault de trabalho (`meli`) é separado do pessoal
- Plugin Reminder instalado para lembretes dentro do vault
- Tasks são exclusivamente ações que Lucas precisa executar — não incluir tasks delegadas a outros
