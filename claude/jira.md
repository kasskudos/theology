# Processos Jira

## Perfil
Sou Project Leader de um time de Desenvolvimento de Software. Trabalho com Jira para gestão de tarefas do time.

---

## Buscar tasks ativas do time (para daily, relatórios, etc.)

Usar o endpoint `/rest/api/3/search/jql` via POST com status IDs (status names com acentos não funcionam via JQL).

**Status IDs ativos do projeto PFDATSERV:**
- `12834` — Em andamento
- `11400` — Blocked
- `12890` — Em análise
- `10000` / `12880` — Tarefas pendentes

**Query padrão:**

```python
import subprocess, json, os

payload = {
    "jql": "project = PFDATSERV AND status in (12834, 11400, 12890, 10000, 12880) AND assignee is not EMPTY ORDER BY assignee",
    "fields": ["summary", "status", "assignee"],
    "maxResults": 100
}

with open('/tmp/jql-search.json', 'w') as f:
    json.dump(payload, f, ensure_ascii=False)

result = subprocess.run([
    'curl', '-s', '-X', 'POST',
    '-u', f'{os.environ["JIRA_EMAIL"]}:{os.environ["JIRA_TOKEN"]}',
    '-H', 'Content-Type: application/json; charset=utf-8',
    '-d', '@/tmp/jql-search.json',
    f'{os.environ["JIRA_BASE_URL"]}/rest/api/3/search/jql'
], capture_output=True, text=True)

d = json.loads(result.stdout)
issues = d.get('issues', [])
```

**Importante:** Sempre usar Python com `ensure_ascii=False` e salvar em arquivo — passar o JSON direto via shell quebra os caracteres especiais.

**Membros do time (displayName no Jira):**
- Richer Severino Da Silva Santos
- Murilo Araujo Casmala
- Giuseppe Cortez Giovanelli
- Eduardo Januario Gomes
- Bruno Luiz Viana
- Breno De Almeida Jacubovski
- Romulo Puliafico Artur
- Gabriel Furtado Neves

Para filtrar só o time (excluindo Lucas e Tomás), adicionar ao JQL:
```
AND assignee in ("Richer Severino Da Silva Santos", "Murilo Araujo Casmala", "Giuseppe Cortez Giovanelli", "Eduardo Januario Gomes", "Bruno Luiz Viana", "Breno De Almeida Jacubovski", "Romulo Puliafico Artur", "Gabriel Furtado Neves")
```

## Fluxo

### 1. Gerar a task estruturada

A partir do contexto fornecido, gerar:

**Título:** Resumo claro e direto do objetivo da tarefa.

**Descrição:**
- **Objetivo:** O que precisa ser alcançado.
- **Contexto:** Cenário ou background que torna a tarefa necessária.
- **O que fazer:** Passos específicos ou requisitos para concluir a tarefa.
- **Stakeholders/Impactados:** Quem é afetado ou precisa ser notificado (se aplicável).
- **Links:** Documentos, screenshots ou fontes externas relevantes (se houver no contexto).
- **Dependências:** Se a tarefa depende de outras ou outras dependem dela (se aplicável).

**Critérios de Aceitação:**
- Lista dos critérios que devem ser atendidos para considerar a tarefa concluída (Definition of Done).
- Enviado no campo dedicado `customfield_22442`.

**Tipo de Tarefa:** Inferir do contexto. Confirmar se ambíguo. Usar sempre o **ID numérico** no payload (nomes em português e inglês podem ser rejeitados):

| Tipo | ID |
|------|----|
| Epic | 10000 |
| História (Story) | 10100 |
| Tarefa (Task) | 10101 |
| Subtarefa (Subtask) | 10102 |
| Bug | 10103 |
| Melhoria | 10200 |
| Spike | 11216 |
| Support | 11217 |

Exemplo: `"issuetype": {"id": "10101"}` — **nunca usar `{"name": "Task"}` ou `{"name": "Tarefa"}`**.

**Prioridade:** Indicada no contexto. Se não informada, perguntar.

**Data de Conclusão:** Se houver data limite no contexto, incluir no formato YYYY-MM-DD. Caso contrário, deixar em branco.

**Epic:** Se informado, vincular a task ao épico usando o campo `parent`.

### 2. Mostrar preview

Antes de criar no Jira, apresentar a task estruturada e perguntar:
> "Quer criar essa task no Jira, ajustar algo, ou cancelar?"

### 3. Criar no Jira via curl

Após aprovação, usar curl com as variáveis de ambiente:
- `$JIRA_BASE_URL`, `$JIRA_EMAIL`, `$JIRA_TOKEN`, `$JIRA_DEFAULT_PROJECT`

#### Passo a passo:

**3.1. Montar o payload JSON** com ADF e salvar em `/tmp/jira-payload-<timestamp>.json`:

```json
{
  "fields": {
    "project": {"key": "PFDATSERV"},
    "summary": "Título da task",
    "issuetype": {"id": "10101"},  // sempre usar ID, não name
    "parent": {"key": "EPIC_KEY"},
    "priority": {"name": "Medium"},
    "duedate": "YYYY-MM-DD",
    "description": {
      "version": 1,
      "type": "doc",
      "content": [
        {
          "type": "heading",
          "attrs": {"level": 3},
          "content": [{"type": "text", "text": "Objetivo"}]
        },
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": "..."}]
        }
      ]
    },
    "customfield_22442": {
      "version": 1,
      "type": "doc",
      "content": [
        {
          "type": "bulletList",
          "content": [
            {
              "type": "listItem",
              "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Critério 1"}]}]
            }
          ]
        }
      ]
    }
  }
}
```

Omitir `priority`, `duedate`, `parent` e `customfield_22442` se não informados.

**3.2. Criar a issue:**

```bash
curl -s -X POST \
  "$JIRA_BASE_URL/rest/api/3/issue" \
  -u "$JIRA_EMAIL:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/jira-payload-<timestamp>.json
```

**3.3. Retornar o link:** `$JIRA_BASE_URL/browse/{KEY}` (KEY vem no campo `key` da resposta)

---

## Ler uma issue

```bash
curl -s "$JIRA_BASE_URL/rest/api/3/issue/{KEY}" \
  -u "$JIRA_EMAIL:$JIRA_TOKEN"
```

Útil para buscar descrição, status, subtasks e links antes de gerar comentários ou atualizar uma task.

---

## Adicionar comentário em uma issue

**Cabeçalho obrigatório em comentários gerados por IA:**

Todo comentário gerado por Claude deve iniciar com o seguinte parágrafo antes do conteúdo:

```
🤖 Comentário gerado por IA — pode conter imprecisões. Revise antes de considerar oficial.
```

Em ADF:

```json
{
  "type": "paragraph",
  "content": [
    {
      "type": "text",
      "text": "🤖 Comentário gerado por IA — pode conter imprecisões. Revise antes de considerar oficial.",
      "marks": [{"type": "em"}]
    }
  ]
}
```

**1. Montar o payload** em `/tmp/comment-{KEY}.json`:

```json
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [{"type": "text", "text": "Texto do comentário."}]
      }
    ]
  }
}
```

Para bullet list dentro do comentário:

```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Item 1"}]}]
    }
  ]
}
```

**2. Postar o comentário:**

```bash
curl -s -X POST \
  "$JIRA_BASE_URL/rest/api/3/issue/{KEY}/comment" \
  -u "$JIRA_EMAIL:$JIRA_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/comment-{KEY}.json
```

O campo `id` na resposta confirma que o comentário foi criado.
