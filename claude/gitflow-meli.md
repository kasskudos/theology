# GitFlow do Meli — Guidelines de Subida de Alterações

Baseado no **Fury Release Process** (documentação oficial em furydocs.io/release-process).

---

## 1. Branches disponíveis

| Tipo | Padrão de nome | Estável (protegida) | Releasável para produção |
|---|---|---|---|
| Principal | `master` | Sim | Sim |
| Desenvolvimento | `develop` | Sim | Não |
| Nova funcionalidade | `feature/.*` | Não | Não |
| Correção de bug | `fix/.*` ou `bugfix/.*` | Não | Não |
| Melhoria técnica | `enhancement/.*` | Não | Não |
| Release | `release/.*` | Não | Não |
| Emergência/produção | `hotfix/.*` | Não | Sim |
| Migração | `migration/.*` | Não | Não |
| Reversão | `revert-.*` | Não | Não |

> **Importante:** `master` e `develop` são protegidas — nunca fazer `git push` direto. Somente via PR.

---

## 2. Fluxo completo: "sobe as alterações"

Seguir **todos** os passos na ordem abaixo sempre que o usuário pedir para subir, commitar ou criar PR de alterações.

---

### Passo 1 — Diagnóstico da branch atual

```bash
git branch --show-current
git fetch origin
git status
```

**Cenário A: já está em uma branch de trabalho** (`feature/`, `fix/`, `bugfix/`, `enhancement/`, `hotfix/`, `migration/`)
→ Pular para o Passo 4 (commit)

**Cenário B: está em `develop`**
- Verificar se está atualizada: `git status` após o fetch
- Se desatualizada: `git pull origin develop`
- Se houver **conflitos**: **parar imediatamente** e pedir ao usuário para resolver antes de continuar
- Se atualizada: prosseguir para o Passo 2

**Cenário C: está em `master`**
- Só criar branch de trabalho se for um `hotfix`
- Para qualquer outro tipo de alteração: avisar o usuário e perguntar se deve fazer checkout em `develop` primeiro

---

### Passo 2 — Análise das alterações

```bash
git diff --name-only
git status
```

- Listar todos os arquivos modificados/staged
- Verificar se as alterações fazem parte do **mesmo contexto ou funcionalidade**
- Se forem **contextos muito diferentes** (ex: bug fix em módulo A + nova feature em módulo B):
  → Propor divisão em múltiplas branches e **pedir confirmação ao usuário** antes de continuar  Se esse for o cenário, para cada branch criada você deve fazer os passmos 3 ao 6
- Se forem do **mesmo contexto**: seguir com uma branch única

---

### Passo 3 — Criação da branch

Classificar o tipo de alteração e criar a branch a partir da base correta:

| Tipo | Nome da branch | Base |
|---|---|---|
| Nova funcionalidade | `feature/descricao-curta` | `develop` |
| Correção de bug | `fix/descricao-curta` | `develop` |
| Melhoria técnica | `enhancement/descricao-curta` | `develop` |
| Migração | `migration/descricao-curta` | `develop` |
| Emergência em produção | `hotfix/descricao-curta` | `master` |

**Regras para o nome:**
- Usar kebab-case (ex: `feature/add-fraud-score-validation`)
- Máximo 100 caracteres após a barra
- Ser descritivo mas conciso
- Em inglês

```bash
git checkout -b feature/nome-da-branch  # ou fix/, enhancement/, etc.
```

Se houver múltiplas branches: criar cada uma, fazer os passos 4–6 para cada, e depois retornar ao `develop` entre elas.

---

### Passo 4 — Commit

Gerar um commit com título e descrição baseados nas alterações reais:

**Formato do título:** `tipo: descrição breve em minúsculas`
- Exemplos: `feat: add fraud score endpoint`, `fix: handle null cpf on validation`, `chore: update pre-commit hooks`. Titulos sempre em inglês

**Descrição:** explicar **o quê** foi feito e **por quê**, em frases claras.

```bash
git add <arquivos específicos>
git commit -m "$(cat <<'EOF'
tipo: título breve

Descrição detalhada do que foi alterado e a motivação por trás da mudança.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

> Nunca usar `git add -A` sem antes verificar os arquivos. Evitar commitar `.env`, credenciais ou binários grandes.

---

### Passo 5 — Push

```bash
git push -u origin <nome-da-branch>
```

Se houver múltiplas branches, fazer o push de cada uma.

---

### Passo 6 — Criação do Pull Request

Definir o **target correto** baseado no tipo de branch:

| Branch | Base do PR |
|---|---|
| `feature/.*` | `develop` |
| `fix/.*` | `develop` |
| `bugfix/.*` | `develop` |
| `enhancement/.*` | `develop` |
| `migration/.*` | `develop` |
| `release/.*` | `master` |
| `hotfix/.*` | `master` |

**Criar o PR com:**
- Título descritivo e conciso (até 70 caracteres)
- Títulos sempre em inglês
- Corpo com: resumo das mudanças, motivação/contexto, checklist de teste

```bash
gh pr create --title "título do PR" --body "$(cat <<'EOF'
## Resumo
- bullet point com o que foi feito

## Motivação
Breve contexto de por que essa mudança foi necessária.

## Checklist de teste
- [ ] Item de validação 1
- [ ] Item de validação 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" --base develop  # ou master para hotfix/release
```

> Se o `gh pr create` falhar (autenticação, permissão, etc.), usar o MCP do GitHub (`mcp__github__create_pull_request`) como opção B.

**Após criar o PR**, sempre exibir o link completo no formato `https://github.com/<owner>/<repo>/pull/<number>`.
- Com `gh pr create`: capturar a URL retornada no stdout e exibi-la.
- Com o MCP: usar o campo `html_url` da resposta e exibi-lo.

**Parar aqui.** Não fazer merge, não criar release, não fazer deploy.

Após criar todos os PRs, voltar para a branch `develop`:

```bash
git checkout develop
```

---

## 3. Observações importantes

- **Commit signing** pode ser obrigatório na org `melisource` a partir do Q3 2025 — usar o plugin `fury scm` para configurar
- Após merge de `release/.*` ou `hotfix/.*` na `master`, o Fury abre automaticamente um **backport PR** para propagar as mudanças ao `develop`
- Se o projeto não usar o Fury Release Process (ex: repositório de scripts), aplicar o mesmo modelo de branches como boa prática, mas sem as verificações automáticas do CI/CD do Fury
- O `release/.*` é criado a partir de `develop` quando se quer congelar as mudanças para uma release; usar `fury create-version` para gerar a versão de teste antes do PR para `master`

---

## 4. Prompt reutilizável (copy-paste)

Use este prompt em qualquer conversa nova para acionar o fluxo completo:

```
Sobe as alterações deste projeto seguindo o processo de GitFlow do Meli.
Antes de começar, leia as instruções em ~/.claude/gitflow-meli.md e siga o fluxo completo descrito lá:
diagnóstico da branch atual, análise das alterações, criação de branch(es), commit(s), push e criação do(s) PR(s).
Pare após criar os PRs — não faça merge nem deploy.
```
