# Monthly Summary — Resumo Mensal pros Porotos

Pipeline pra gerar comentários **em inglês** nos porotos (projeto Jira `PRFRAUDE`) consolidando 4-5 semanas de trabalho do time **cross-fraud-data-services** (épicos do `PFDATSERV`).

## Quando usar

Trigger quando o usuário pedir variações de:
- "gera resumo mensal"
- "atualizar porotos"
- "fechar o mês"
- "comment mensal nos porotos"
- "consolidar mês X nos porotos"

## Onde está

**Projeto:** `/Users/lkudo/work/projects/fraud-scripts/automation/monthly-summary/`

**Documentação completa:** ler `automation/monthly-summary/CLAUDE.md` antes de executar — tem todas as decisões (detecção poroto via inlineCard ADF scan, janela flexível, idioma EN obrigatório, tom executivo sem ticket IDs).

## Como executar

```bash
cd /Users/lkudo/work/projects/fraud-scripts/automation/monthly-summary
./run_monthly.sh                              # rolling 35d até hoje
./run_monthly.sh --month 2026-04              # mês específico, flex 5 dias
./run_monthly.sh --start 2026-03-27 --end 2026-04-29
./run_monthly.sh --skip-collect --label X     # re-gera drafts
./run_monthly.sh --post --label 2026-04       # post manual depois de revisar
```

## Diferenças críticas vs weekly

- **Idioma e destino — DOIS posts por épico ativo c/ poroto:**
  - **EN** vai no **poroto (PRFRAUDE)** subtask do nosso subteam → audiência externa (time solicitante + gerência/diretoria). Tag `[monthly-summary YYYY-MM]`.
  - **PT-BR** vai no **épico (PFDATSERV)** do nosso time → audiência interna (Ariel + time). Tag `[resumo-mensal YYYY-MM]`.
  - Mesmo conteúdo, traduzido naturalmente. Comentários no poroto sempre em inglês (regra dura — diretoria externa lê).
- **Sem ticket IDs no corpo:** nada de `PFDATSERV-XXXX` ou `PRFRAUDE-XXXX` no narrative — audiência externa não navega
- **Fontes:** Jira **não** é source of truth (Lucas só começou agora a atualizar weekly). Cruzar com Obsidian + Drive + drafts locais semanais. Decisões importantes saem em reuniões e nunca chegam ao Jira.
- **Janela flexível:** evitar cravar 1º a último dia do mês — trabalho do time não respeita virada de mês
- **Tag idempotência:** `[monthly-summary YYYY-MM]` (em inglês também)
- **Onde posta:** o comment vai numa **subtask** do epic do poroto, não no epic. Hierarquia: Epic (poroto) → Tarefa (nome do time, "Detection Platform" ou "Arquitectura/Cross") → Subtarefa (subteam "Fraud - Data Engineering | Pangea & Data Platform"). O script resolve essa cadeia automaticamente.
- **Tom executivo:** 4-8 parágrafos, narrativo, foco em marcos entregues + quanto falta + ETA só se existir nos dados (nunca inventar)

## Relação com o weekly

Mensal **consome** os comments semanais (postados nos épicos do PFDATSERV pelo pipeline weekly) **+ todas as outras fontes**. Idealmente roda no início do mês seguinte, depois de já ter ~4 weeklies postados.
