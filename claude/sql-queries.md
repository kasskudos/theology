# SQL Queries — Organização no Obsidian

Vault: `/Users/lkudo/work/obs/meli/`
Pasta de queries: `queries/`
Template: `templates/sql-query.md`
BigQuery projeto padrão: `warehouse-cross-pf` (usar quando o usuário não especificar)

---

## Quando usar este fluxo

Sempre que o usuário compartilhar uma query SQL para salvar, documentar ou reutilizar.

---

## Fluxo ao receber uma nova query

1. **Analisar o que a query faz**
   - Identificar tabelas, filtros, agregações e o resultado esperado
   - Inferir finalidade a partir da estrutura, mesmo sem contexto explícito

2. **Executar com o MCP do BigQuery Analyzer** (quando aplicável)
   - Rodar a query original com `mcp__bigquery_analizer__execute_query`
   - Testar variações úteis: janelas de tempo diferentes, filtros alternativos, limites de amostragem
   - Capturar amostras representativas do resultado (3–5 linhas)
   - Verificar custo com `dry_run_query` antes de executar queries pesadas

3. **Registrar exemplos de saída**
   - Incluir amostra real ou comportamento observado na seção "Exemplo de execução"

4. **Salvar no Obsidian**
   - Criar arquivo em `queries/` com nome no padrão: `YYYY-MM-DD nome-descritivo.md`
   - Usar o template `templates/sql-query.md` como base
   - Preencher todos os campos do frontmatter

5. **Documentar contexto completo**
   - O que faz, por que existe, quando usar
   - Observações sobre cuidados, limitações ou custo
   - Fonte: quem compartilhou, quando e onde (Slack, reunião, PR, etc.)

---

## Padrão de nomeação de arquivos

```
YYYY-MM-DD nome-descritivo.md
```

- Data = dia em que a query foi registrada
- Nome = kebab-case, descritivo, sem redundância com a pasta
- Exemplos:
  - `2026-04-20 latencia-inferencia-por-modelo.md`
  - `2026-04-20 contagem-itens-freshness-por-site.md`

---

## Estrutura da pasta de queries

```
queries/
  README.md          — índice com dataview de todas as queries
  YYYY-MM-DD *.md    — uma nota por query
  <tema>/            — subpastas por tema, quando o volume justificar
```

---

## Template de nota de query

Campos obrigatórios:
- `titulo` — nome legível da query
- `tema` — área/domínio (freshness, pangea, datasets, etc.)
- `fonte` — sistema ou contexto de origem (ex: BigQuery, Hive, Redshift)
- `autor` — quem compartilhou ou escreveu a query
- `data` — data de registro

Seções obrigatórias do corpo:
- **Query SQL** — código completo
- **O que faz** — descrição em 2–4 linhas
- **Contexto de uso** — quando e por que usar
- **Exemplo de execução** — amostra real ou comportamento esperado
- **Observações** — cuidados, limites, custo, filtros críticos
- **Fonte** — quem compartilhou, quando e onde
