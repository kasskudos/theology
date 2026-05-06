# Instruções Globais do Claude

> Ao editar este arquivo: manter apenas como índice de referências.
> Nunca adicionar conteúdo detalhado aqui — criar arquivo separado em `~/.claude/` e referenciar abaixo.
> Cada entrada deve ter trigger claro descrevendo *quando* carregar o arquivo.
> O Claude deve ler o arquivo via Read antes de executar a tarefa quando o trigger casar — não tentar adivinhar o conteúdo.

## Idioma

- Sempre responder em português brasileiro, mesmo quando o usuário escrever em inglês.
- Código (comentários, docstrings, identificadores), mensagens de commit, descrições de PR e nomes de branch seguem o padrão do projeto, geralmente inglês. Não traduzir.

## Pontuação

- Nunca usar hífen ou travessão (`-`, `–`, `—`) como separador em texto gerado (respostas, mensagens, comentários, descrições de PR, commits). Sempre substituir por vírgula.
- Exceção: marcadores de lista (`- item`), palavras compostas hifenizadas naturais (ex.: "pré-commit", "follow-up") e identificadores de código.

## Processos disponíveis

- Code style: ao escrever, editar ou revisar código em qualquer linguagem (estilo, testes, dependências, formatação, logging) — ver `~/.claude/code-style.md`
- GitFlow / Subida de alterações: quando o usuário pedir para commitar, fazer push, abrir PR, criar branch ou subir alterações em qualquer projeto — ver `~/.claude/gitflow-meli.md`
- Lembretes: quando o usuário pedir para lembrar de algo, não esquecer, fazer follow-up ou agendar algo pra mais tarde — ver `~/.claude/reminders.md`
- Anotações: quando precisar documentar decisão, reunião, projeto ou tema relevante (Obsidian) — ver `~/.claude/obsidian.md`
- Reuniões: para agendar reuniões, enviar convites ou consultar Google Calendar — ver `~/.claude/calendar.md`
- Queries SQL: quando o usuário compartilhar uma query para salvar, documentar ou reutilizar — ver `~/.claude/sql-queries.md`
- Fury API: ao precisar autenticar no Fury ou buscar apps/recursos por time — ver `~/.claude/fury-api.md`
- Resumo Semanal: quando o usuário pedir "resumo semanal", "fechar a semana", "atualizar comentários dos épicos", "preparar pro 1:1 com Ariel" ou similar — ver `~/.claude/weekly-summary.md`
- Resumo Mensal: quando o usuário pedir "resumo mensal", "atualizar porotos", "fechar o mês", "comment mensal nos porotos" ou similar — ver `~/.claude/monthly-summary.md`
- Akita / agente questionador: quando o usuário pedir para você "ser o Akita", "atuar como Akita", "modo Akita" ou variação (papel de parceiro crítico que questiona/revisa, não implementa) — ver `~/.claude/akita.md`
- Jarvis / agente implementador: quando o usuário pedir para você "ser o Jarvis", "atuar como Jarvis", "modo Jarvis" ou variação (papel de implementador disciplinado que segue plano congelado, contraparte do Akita) — ver `~/.claude/jarvis.md`
- Review de PR: quando o usuário pedir para revisar uma PR, gerar comentários para postar em PR, ou variações ("faz o review", "revisa essa PR", "gera os comentários pra eu colar"), ver `~/.claude/pr-review.md`
- Multi-agente inbox/outbox: quando estiver em sessão Akita ou Jarvis
  e precisar entender o protocolo de comunicação entre as duas sessões
  (formato do inbox, formato do outbox, quando escrever, quando aguardar)
  — ver `~/.claude/multi-agent-setup.md`