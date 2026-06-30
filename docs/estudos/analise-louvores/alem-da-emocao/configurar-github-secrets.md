# Configurar GitHub Secrets

O workflow cloud precisa destes secrets no GitHub:

```text
META_ACCESS_TOKEN
META_IG_USER_ID
GOOGLE_DRIVE_API_KEY
```

Abra:

```text
https://github.com/kasskudos/theology/settings/secrets/actions
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
https://github.com/kasskudos/theology/actions/workflows/alem-da-emocao-publish.yml
```

Use **Run workflow** com:

```text
cut: 3
dry_run: true
```

Se o dry-run passar, o workflow diario publica automaticamente o corte previsto no arquivo:

```text
docs/estudos/analise-louvores/alem-da-emocao/schedules/EP02.json
```
