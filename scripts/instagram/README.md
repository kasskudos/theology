# Scripts para Instagram

Este diretório contém scripts para interagir com o Instagram usando web scraping não oficial.

## 📁 Arquivos

- `pegar_comentarios.py` - **Script principal** para extrair TODOS os comentários de qualquer post público
- `monitorar_respostas.py` - Monitora respostas aos seus comentários em posts de outras pessoas
- `comentar_post.py` - Script usando API oficial (apenas seus próprios posts)

---

# Pegar Comentários de Qualquer Post Público

Este script extrai **todos os comentários** de qualquer post público do Instagram.

## 🎯 Caso de Uso

Você quer analisar os comentários de um post específico, seja para:
- Análise teológica
- Estudo de engajamento
- Coleta de dados
- Qualquer outra análise

## ⚠️ AVISOS IMPORTANTES

1. **Este script usa web scraping não oficial** - Pode quebrar se o Instagram mudar sua interface
2. **Requer login** - Você precisa fazer login com sua conta (sessão é salva)
3. **Use com moderação** - Muitas requisições podem resultar em bloqueio temporário
4. **Apenas posts públicos** - Não funciona com posts privados (a menos que você siga a conta)
5. **Não é oficial** - Não é fornecido pela Meta/Facebook

## 📋 Pré-requisitos

1. **Python 3.7+**
2. **Biblioteca instagrapi**
   ```bash
   pip install instagrapi
   ```
   Ou use o arquivo requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

3. **Conta do Instagram**
   - Qualquer conta funciona (pessoal, Business, Creator)
   - Você precisa do usuário e senha (apenas na primeira vez)

## 🚀 Como Usar

### Instalação

```bash
cd scripts/instagram
pip install -r requirements.txt
```

### Exemplo Básico - Extrair Comentários

```bash
# Usando URL completa
python pegar_comentarios.py \
  --url "https://www.instagram.com/p/ABC123XYZ/" \
  --user seu_usuario \
  --password sua_senha \
  --output comentarios.json

# Usando apenas o shortcode
python pegar_comentarios.py \
  --shortcode ABC123XYZ \
  --user seu_usuario \
  --password sua_senha \
  --output comentarios.json
```

### Salvar em Markdown

```bash
python pegar_comentarios.py \
  --shortcode ABC123XYZ \
  --user seu_usuario \
  --password sua_senha \
  --output comentarios.md \
  --format markdown
```

### Após primeira vez (sessão salva)

Depois do primeiro login, a sessão é salva. Você pode omitir as credenciais:

```bash
python pegar_comentarios.py \
  --shortcode ABC123XYZ \
  --output comentarios.json
```

### Como obter o Shortcode?

O shortcode é a parte única da URL do post:
- URL: `https://www.instagram.com/p/ABC123XYZ/`
- Shortcode: `ABC123XYZ`

Basta copiar a parte que vem depois de `/p/`

---

# Monitorar Respostas aos Seus Comentários

Este script monitora os comentários que **você fez** em posts de outras pessoas e verifica se há novas respostas.

## 🎯 Caso de Uso

Você comenta em vários posts do Instagram, mas é difícil acompanhar quais comentários receberam respostas, especialmente quando a pessoa não marca seu @. Este script resolve isso!

## 🔧 Como Funciona

1. **Você comenta em um post** de outra pessoa no Instagram
2. **Adiciona o post para monitoramento** usando o shortcode (parte da URL)
3. **O script verifica periodicamente** se há novas respostas aos seus comentários
4. **Você recebe notificações** sobre novas respostas

## 🚀 Como Usar

### Passo 1: Adicionar Posts para Monitorar

Primeiro, você precisa adicionar os posts onde você comentou:

```bash
python monitorar_respostas.py \
  --add-post ABC123XYZ \
  --user seu_usuario \
  --password sua_senha
```

O script vai:
- Fazer login no Instagram
- Encontrar seus comentários no post
- Salvar o post na lista de monitoramento

### Passo 2: Verificar Respostas

#### Verificar um post específico:

```bash
python monitorar_respostas.py \
  --check-post ABC123XYZ \
  --user seu_usuario \
  --password sua_senha
```

#### Verificar todos os posts monitorados:

```bash
python monitorar_respostas.py \
  --check-all \
  --user seu_usuario \
  --password sua_senha
```

### Passo 3: Listar Posts Monitorados

```bash
python monitorar_respostas.py --list-posts
```

### Passo 4: Remover um Post

```bash
python monitorar_respostas.py \
  --remove-post ABC123XYZ
```

### Automação (Opcional)

Você pode criar um script que roda periodicamente:

```bash
# Adicionar ao crontab (Linux/Mac) para rodar a cada hora
0 * * * * cd /caminho/para/scripts/instagram && python monitorar_respostas.py --check-all --user SEU_USUARIO --password SUA_SENHA
```

---

## 🔐 Segurança das Credenciais

Para não expor sua senha no histórico do terminal, você pode:

1. **Usar variáveis de ambiente** (recomendado):
```bash
export INSTAGRAM_USER="seu_usuario"
export INSTAGRAM_PASS="sua_senha"

python pegar_comentarios.py --shortcode ABC123 \
  --user "$INSTAGRAM_USER" \
  --password "$INSTAGRAM_PASS"
```

2. **Criar um script wrapper** (mais seguro):
```bash
#!/bin/bash
# instagram.sh
python pegar_comentarios.py "$@" \
  --user "seu_usuario" \
  --password "sua_senha"
```

3. **Modificar o script** para ler de arquivo de configuração (não versionado no git)

## 📁 Arquivos Gerados

Os scripts criam alguns arquivos:

- `instagram_session.json` - Sessão salva (evita login repetido) ⚠️ **NÃO compartilhe!**
- `posts_monitorados.json` - Lista de posts sendo monitorados (apenas monitorar_respostas.py)
- `*.json` / `*.md` - Arquivos de saída com comentários

## 🔒 Segurança

⚠️ **NUNCA compartilhe seus arquivos de sessão ou senha!**

- O arquivo `instagram_session.json` contém tokens de autenticação
- Adicione `*.json` ao `.gitignore` (já está no `.gitignore` do diretório)
- Use variáveis de ambiente para credenciais em produção
- Mantenha os arquivos locais seguros

## ❓ Perguntas Frequentes

**P: Preciso fazer login toda vez?**
R: Não. Os scripts salvam a sessão no arquivo `instagram_session.json`. Você só precisa fazer login novamente se o token expirar.

**P: Posso usar para quantos posts quiser?**
R: Sim, mas use com moderação. Muitas requisições podem resultar em bloqueio temporário pelo Instagram.

**P: O script funciona com posts privados?**
R: Não. Você só pode acessar posts públicos ou posts de contas que você segue (se o perfil for privado).

**P: E se o Instagram mudar sua interface?**
R: Os scripts podem parar de funcionar. A biblioteca `instagrapi` é mantida pela comunidade e pode precisar de atualizações.

**P: Posso usar isso para spam ou automação de comentários?**
R: Não. Estes scripts são apenas para leitura/análise. Use com responsabilidade e respeite os Termos de Serviço do Instagram.

**P: Recebi um erro de login. O que fazer?**
R: 
- Verifique se suas credenciais estão corretas
- Se você tem 2FA ativado, o script vai pedir o código
- Tente deletar `instagram_session.json` e fazer login novamente
- Aguarde alguns minutos se houver muitas tentativas

## 📚 Recursos

- [Biblioteca instagrapi no GitHub](https://github.com/adw0rd/instagrapi)
- [Documentação do instagrapi](https://adw0rd.github.io/instagrapi/)
