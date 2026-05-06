# Setup Multi-Agente: Akita + Jarvis

> Documentação de configuração do fluxo de duas sessões Claude Code
> comunicando via arquivos inbox/outbox.

---

## Estrutura de arquivos por projeto

```
<raiz-do-projeto>/
└── .claude/
    ├── jarvis_inbox.md    ← Akita escreve aqui
    └── jarvis_outbox.md   ← Jarvis escreve aqui
```

Esses arquivos são por projeto — cada repo tem o seu par.
Recomendado adicionar ao `.gitignore` se o projeto for compartilhado:

```
# .gitignore
.claude/jarvis_inbox.md
.claude/jarvis_outbox.md
```

---

## Script de inicialização

Salve como `~/bin/start-agents` (ou qualquer pasta no seu PATH)
e dê permissão de execução: `chmod +x ~/bin/start-agents`

```bash
#!/bin/bash
# start-agents — inicializa sessões Akita e Jarvis para um projeto
# Uso: start-agents [caminho-do-projeto]
# Se não passar caminho, usa o diretório atual.

PROJECT_DIR="${1:-$(pwd)}"
CLAUDE_DIR="$PROJECT_DIR/.claude"

# Garante que a pasta .claude existe
mkdir -p "$CLAUDE_DIR"

# Inicializa os arquivos de comunicação se não existirem
if [ ! -f "$CLAUDE_DIR/jarvis_inbox.md" ]; then
  echo "<!-- inbox vazio — aguardando Akita -->" > "$CLAUDE_DIR/jarvis_inbox.md"
  echo "✓ Criado: $CLAUDE_DIR/jarvis_inbox.md"
fi

if [ ! -f "$CLAUDE_DIR/jarvis_outbox.md" ]; then
  echo "<!-- outbox vazio — aguardando Jarvis -->" > "$CLAUDE_DIR/jarvis_outbox.md"
  echo "✓ Criado: $CLAUDE_DIR/jarvis_outbox.md"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Projeto: $PROJECT_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Abra dois terminais e rode:"
echo ""
echo "  Terminal 1 (Akita):"
echo "  cd $PROJECT_DIR"
echo "  claude --allowedTools 'Read,Write,Edit' \\"
echo "         --disallowedTools 'Bash' \\"
echo "         --add-dir $HOME/.claude"
echo ""
echo "  Terminal 2 (Jarvis):"
echo "  cd $PROJECT_DIR"
echo "  claude --allowedTools 'Read,Write,Edit,Bash'"
echo ""
echo "Depois, em cada sessão, ative o modo com:"
echo "  Akita:  'modo Akita'"
echo "  Jarvis: 'modo Jarvis'"
echo ""
echo "Arquivos de comunicação:"
echo "  Inbox:  $CLAUDE_DIR/jarvis_inbox.md"
echo "  Outbox: $CLAUDE_DIR/jarvis_outbox.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

---

## Passo a passo de uso

### 1. Inicializar o projeto

```bash
cd /caminho/do/projeto
start-agents
```

O script cria a pasta `.claude/` com os arquivos vazios e imprime
os comandos exatos para abrir cada sessão.

### 2. Abrir as sessões

**Terminal 1 — Akita:**
```bash
cd /caminho/do/projeto
claude --allowedTools 'Read,Write,Edit' \
       --disallowedTools 'Bash' \
       --add-dir $HOME/.claude
```

> `--disallowedTools 'Bash'` impede o Akita de executar comandos
> no sistema — coerente com o contrato do modo Akita (não toca
> no código, só lê e escreve nos arquivos de comunicação).
> `Read,Write,Edit` permite ler docs do projeto e escrever no inbox.

**Terminal 2 — Jarvis:**
```bash
cd /caminho/do/projeto
claude --allowedTools 'Read,Write,Edit,Bash'
```

> Jarvis tem acesso ao Bash porque precisa executar comandos,
> rodar testes, fazer commits, etc.

### 3. Ativar os modos

Em cada sessão, após abrir, envie a mensagem de ativação:

- Akita: `modo Akita`
- Jarvis: `modo Jarvis`

O Claude Code vai ler os arquivos correspondentes em `~/.claude/`
e ativar o comportamento correto.

### 4. Monitorar os arquivos (opcional mas recomendado)

Abra um terceiro terminal para acompanhar a troca em tempo real:

```bash
# Monitora inbox e outbox simultaneamente
watch -n 2 'echo "=== INBOX ===" && cat .claude/jarvis_inbox.md && echo "" && echo "=== OUTBOX ===" && cat .claude/jarvis_outbox.md'
```

Ou, se preferir mais granular com destaque de diff:

```bash
# Apenas o outbox (o mais útil para acompanhar progresso)
tail -f .claude/jarvis_outbox.md
```

---

## Como intervir durante a execução

Você pode interromper o Akita a qualquer momento digitando
diretamente na sessão dele. Exemplos:

- **Corrigir direção:** "Para. O Jarvis foi por um caminho errado,
  veja o outbox — precisamos ajustar a abordagem antes de continuar."
- **Adicionar contexto:** "Antes de mandar o próximo prompt,
  considera que X é uma restrição do ambiente de produção."
- **Forçar pausa:** "Não manda mais nada pro inbox agora, preciso
  revisar o que foi feito."

O Akita trata sua intervenção como input do Stark — prioridade máxima.

---

## Configuração do `~/.claude/CLAUDE.md` (global)

Adicione a entrada do multi-agente ao seu índice global existente:

```markdown
- Multi-agente inbox/outbox: quando estiver em sessão Akita ou Jarvis
  e precisar entender o protocolo de comunicação entre as duas sessões
  (formato do inbox, formato do outbox, quando escrever, quando aguardar)
  — ver `~/.claude/multi-agent-setup.md`
```

---

## Troubleshooting

**Jarvis não está lendo o inbox:**
Verifique se o arquivo existe e tem o header `[AKITA → JARVIS]`.
O Jarvis ignora o arquivo se estiver com o placeholder inicial.

**Akita está tentando executar código:**
O `--disallowedTools 'Bash'` impede isso. Se estiver acontecendo,
verifique se abriu com os flags corretos.

**As sessões estão perdendo contexto:**
Normal em sessões muito longas. Sinal de que é hora do handoff.
O próprio prompt do Akita detecta isso e orquestra a transição.

**Inbox com dois prompts ao mesmo tempo:**
Não deve acontecer — o Akita só escreve novo prompt após o Jarvis
responder no outbox. Se acontecer, o Jarvis deve sinalizar no outbox
qual prompt está executando e ignorar o segundo até terminar.