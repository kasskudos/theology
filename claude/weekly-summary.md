# Weekly Summary — Resumo Semanal pro Chefe

Pipeline pronto para gerar o resumo semanal do time **cross-fraud-data-services** (Jira project `PFDATSERV`):
- comentários narrativos por épico ativo no Jira (input pra futuro resumo mensal nos porotos)
- resumo executivo em Obsidian/markdown pra reunião com o gerente (Ariel)
- buckets separados de PRs órfãos e épicos sem mov

## Quando usar

Trigger quando o usuário pedir variações de:
- "gera resumo semanal"
- "resumo da semana pro chefe"
- "atualizar comentários dos épicos"
- "fechar a semana no Jira"
- "preparar pro 1:1 com Ariel"

> Para **resumo mensal** (atualizar porotos no projeto PRFRAUDE), ver `~/.claude/monthly-summary.md` — pipeline diferente.

## Onde está

**Projeto:** `/Users/lkudo/work/projects/fraud-scripts/automation/weekly-summary/`

**Documentação completa do pipeline:** ler `automation/weekly-summary/CLAUDE.md` antes de executar — tem todas as decisões de design (filtros de épico, hierarquia BFS, idempotência, fontes de dados, etc) que NÃO devem ser revisitadas sem motivo.

## Como executar

```bash
cd /Users/lkudo/work/projects/fraud-scripts/automation/weekly-summary
./run_weekly.sh                    # semana ISO anterior, automático
./run_weekly.sh 2026-W17           # semana específica
./run_weekly.sh --skip-collect     # re-gera só drafts (mantém data/)
./run_weekly.sh --post 2026-W17    # post manual depois de revisar drafts/
```

`run_weekly.sh` orquestra 5 etapas; o step 4 (gerar drafts) e o step 3b (Drive via MCP) usam `claude -p` em vez de chamada à API Anthropic — reusa a sessão local, não precisa de `ANTHROPIC_API_KEY`.

## Estilo dos drafts (importante)

Os comentários do Jira (`drafts/<WEEK>/epic-comments/<EPIC>.md`) **devem ser narrativos e executivos**, não bullet-list de tickets. Pessoa lendo (gerente) precisa entender o que andou, onde estamos e o que falta sem precisar abrir cada ticket.

Estilo definido em `prompts/summarize.md`. Em qualquer iteração futura sobre o pipeline, esse estilo é critério de aceite — bullet-list de tickets foi explicitamente rejeitado pelo Lucas em 2026-04-29.
