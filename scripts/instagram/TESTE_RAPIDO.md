# Teste Rápido - Post DS598L0Dk2R

## URL do Post
https://www.instagram.com/p/DS598L0Dk2R/

## Shortcode
DS598L0Dk2R

## Como Executar

### Opção 1: Criar ambiente virtual (Recomendado)

```bash
cd scripts/instagram

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # No Mac/Linux
# ou
venv\Scripts\activate     # No Windows

# Instalar biblioteca
pip install instagrapi

# Executar o script
python pegar_comentarios.py \
  --url "https://www.instagram.com/p/DS598L0Dk2R/" \
  --user SEU_USUARIO_INSTAGRAM \
  --password SUA_SENHA \
  --output comentarios_DS598L0Dk2R.json
```

### Opção 2: Usar shortcode (mais simples)

```bash
cd scripts/instagram
source venv/bin/activate  # Se estiver usando venv

python pegar_comentarios.py \
  --shortcode DS598L0Dk2R \
  --user SEU_USUARIO_INSTAGRAM \
  --password SUA_SENHA \
  --output comentarios_DS598L0Dk2R.json
```

### Opção 3: Salvar em Markdown

```bash
python pegar_comentarios.py \
  --shortcode DS598L0Dk2R \
  --user SEU_USUARIO_INSTAGRAM \
  --password SUA_SENHA \
  --output comentarios_DS598L0Dk2R.md \
  --format markdown
```

## Substituir

- `SEU_USUARIO_INSTAGRAM` → seu usuário do Instagram (sem o @)
- `SUA_SENHA` → sua senha do Instagram

## Exemplo Real

```bash
python pegar_comentarios.py \
  --shortcode DS598L0Dk2R \
  --user joao_silva \
  --password minha_senha_secreta \
  --output comentarios.json
```

## Resultado

O script vai criar um arquivo `comentarios_DS598L0Dk2R.json` (ou `.md`) com todos os comentários do post.

