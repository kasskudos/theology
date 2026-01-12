# Como Usar - Guia Rápido

## 🚀 Passo a Passo

### 1. Instalar as Dependências

Abra o terminal e navegue até a pasta do script:

```bash
cd scripts/instagram
```

Instale a biblioteca necessária:

```bash
pip install instagrapi
```

Ou use o arquivo de requisitos:

```bash
pip install -r requirements.txt
```

### 2. Pegar Comentários de um Post

Você tem duas opções para identificar o post:

#### Opção A: Usando a URL completa

```bash
python pegar_comentarios.py \
  --url "https://www.instagram.com/p/ABC123XYZ/" \
  --user seu_usuario \
  --password sua_senha \
  --output comentarios.json
```

#### Opção B: Usando apenas o shortcode

O shortcode é a parte da URL que vem depois de `/p/`

**Exemplo:**
- URL: `https://www.instagram.com/p/CxYz123AbC/`
- Shortcode: `CxYz123AbC`

```bash
python pegar_comentarios.py \
  --shortcode CxYz123AbC \
  --user seu_usuario \
  --password sua_senha \
  --output comentarios.json
```

### 3. Primeira Execução

Na primeira vez, você precisará:
- Fornecer seu usuário do Instagram (`--user`)
- Fornecer sua senha (`--user`)
- O script vai fazer login e salvar a sessão

**Importante:** Se você tem autenticação de dois fatores (2FA) ativada, o script vai pedir o código de verificação.

### 4. Próximas Execuções

Depois da primeira vez, a sessão é salva. Você pode usar sem credenciais:

```bash
python pegar_comentarios.py \
  --shortcode ABC123 \
  --output comentarios.json
```

### 5. Salvar em Markdown

Se preferir salvar em formato Markdown (mais fácil de ler):

```bash
python pegar_comentarios.py \
  --shortcode ABC123 \
  --user seu_usuario \
  --password sua_senha \
  --output comentarios.md \
  --format markdown
```

### 6. Ver apenas um resumo (sem salvar arquivo)

Se você só quer ver um resumo no terminal:

```bash
python pegar_comentarios.py \
  --shortcode ABC123 \
  --user seu_usuario \
  --password sua_senha
```

## 📋 Exemplos Práticos

### Exemplo 1: Analisar comentários de um post específico

```bash
# 1. Copie a URL do post do Instagram
# Exemplo: https://www.instagram.com/p/CxYz123AbC/

# 2. Execute o script
python pegar_comentarios.py \
  --url "https://www.instagram.com/p/CxYz123AbC/" \
  --user meu_instagram \
  --password minha_senha \
  --output analise_comentarios.json

# 3. Abra o arquivo comentarios.json para ver os comentários
```

### Exemplo 2: Coletar comentários de vários posts

```bash
# Post 1
python pegar_comentarios.py --shortcode ABC123 --output post1.json --user usuario --password senha

# Post 2 (já tem sessão salva, não precisa de credenciais)
python pegar_comentarios.py --shortcode DEF456 --output post2.json

# Post 3
python pegar_comentarios.py --shortcode GHI789 --output post3.json
```

### Exemplo 3: Usar variáveis de ambiente (mais seguro)

Para não expor sua senha no histórico do terminal:

```bash
# No terminal (Linux/Mac)
export INSTAGRAM_USER="seu_usuario"
export INSTAGRAM_PASS="sua_senha"

# Agora use as variáveis
python pegar_comentarios.py \
  --shortcode ABC123 \
  --user "$INSTAGRAM_USER" \
  --password "$INSTAGRAM_PASS" \
  --output comentarios.json
```

## ⚠️ Problemas Comuns

### Erro: "instagrapi não está instalado"

**Solução:**
```bash
pip install instagrapi
```

### Erro: "Não autenticado"

**Solução:** Forneça suas credenciais na primeira vez:
```bash
python pegar_comentarios.py --shortcode ABC123 --user usuario --password senha --output comentarios.json
```

### Erro de login / Credenciais inválidas

**Solução:**
- Verifique se o usuário e senha estão corretos
- Se você tem 2FA, o script vai pedir o código
- Tente deletar `instagram_session.json` e fazer login novamente

### Post privado / Não consegue acessar

**Solução:**
- O script só funciona com posts públicos
- Ou posts de contas privadas que você segue
- Não é possível acessar posts totalmente privados

### Muitas requisições / Bloqueio temporário

**Solução:**
- Aguarde alguns minutos
- Use com moderação (não faça muitas requisições em pouco tempo)
- O Instagram pode bloquear temporariamente se detectar uso excessivo

## 💡 Dicas

1. **Use o shortcode**: É mais fácil copiar apenas o shortcode do que a URL completa
2. **Salve a sessão**: Após o primeiro login, você não precisa mais digitar credenciais
3. **Use Markdown**: Para leitura humana, o formato Markdown é mais legível
4. **Use JSON**: Para processamento automático ou análise programática
5. **Moderação**: Não faça muitas requisições seguidas para evitar bloqueios

## 📝 Onde encontrar o Shortcode?

1. Abra o post no Instagram (no navegador ou app)
2. Copie a URL
3. O shortcode é a parte depois de `/p/`

**Exemplos:**
- `https://www.instagram.com/p/CxYz123AbC/` → Shortcode: `CxYz123AbC`
- `https://instagram.com/p/ABC123/?utm_source=...` → Shortcode: `ABC123`
- `instagram.com/p/DEF456/` → Shortcode: `DEF456`

