# Configurar GitHub Secrets

O workflow cloud precisa destes secrets no GitHub:

```text
META_ACCESS_TOKEN
META_IG_USER_ID
GOOGLE_DRIVE_API_KEY
```

Abra:

```text
GitHub repo > Settings > Secrets and variables > Actions
```

Crie um secret por vez em **New repository secret**.

Os valores estao no arquivo local:

```text
docs/estudos/analise-louvores/alem-da-emocao/.env.meta
```

Mapeamento:

```text
META_ACCESS_TOKEN  <- linha META_ACCESS_TOKEN=...
META_IG_USER_ID    <- linha META_IG_USER_ID=...
GOOGLE_DRIVE_API_KEY <- linha GOOGLE_DRIVE_API_KEY=...
```

Depois de cadastrar, va em:

```text
GitHub repo > Actions > Alem da Emocao Publish
```

Use **Run workflow** com:

```text
cut: 3
dry_run: true
```

Se o dry-run passar, o workflow diario publica automaticamente o corte previsto nos arquivos de agenda:

```text
docs/estudos/analise-louvores/alem-da-emocao/schedules/EPxx.json
```
