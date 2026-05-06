---
name: Fury API - Listar apps por time
description: Como buscar aplicações do time no Fury via API, incluindo auth e endpoint correto
type: reference
originSessionId: 0a90322e-2eb0-422d-86a7-48068f303a85
---
## Autenticação

Usar o header `X-Tiger-Token` com o valor completo `Bearer <token>`:

```bash
TOKEN=$(fury get-token 2>/dev/null | tail -1)
curl -H "X-Tiger-Token: $TOKEN" ...
```

> O header `Authorization: Bearer` **não funciona** nesse contexto — retorna 401.

## Buscar apps por projeto

### Opção 1 — `/api/proxy/fury/applications` (retorna lista plana)
```bash
TOKEN=$(fury get-token 2>/dev/null | tail -1)
curl -s -H "X-Tiger-Token: $TOKEN" \
  "https://web.furycloud.io/api/proxy/fury/applications?projects=<project_code>"
```

Retorna array de apps diretamente.

### Opção 2 — `/api/proxy/puma/v2/applications` (paginado, mais campos)
```bash
curl -s -H "X-Tiger-Token: $TOKEN" \
  "https://web.furycloud.io/api/proxy/puma/v2/applications?project_code=<project_code>"
```

Resposta: `{ "applications": [...] }`. Suporta também `?limit=80&only_favorites=true` para buscar favoritos.

### Como descobrir o project_code do time
Buscar uma app conhecida do time e inspecionar o campo `project_code`:

```bash
curl -s -H "X-Tiger-Token: $TOKEN" \
  "https://api.furycloud.io/applications/pangea-serving" | jq .project_code
# "cross-fp-data-services-pre-compute"
```

## Buscar meus projetos

```bash
TOKEN=$(fury get-token 2>/dev/null | tail -1)
curl -s -H "X-Tiger-Token: $TOKEN" \
  "https://web.furycloud.io/api/proxy/acme/projects/my-projects?with_counts=true&all=true"
```

Retorna lista paginada com `name`, `description`, `status`, `team` e `apps_count`.

## Buscar projetos de um time específico

```bash
TOKEN=$(fury get-token 2>/dev/null | tail -1)
curl -s -H "X-Tiger-Token: $TOKEN" \
  "https://web.furycloud.io/api/proxy/acme/projects?team=<team-code>"
```

Exemplo: `?team=cross-fraud-data-services` retorna os 6 projetos do time.

## Buscar meus times

```bash
TOKEN=$(fury get-token 2>/dev/null | tail -1)
curl -s -H "X-Tiger-Token: $TOKEN" \
  "https://web.furycloud.io/api/proxy/acme/legacy/my-teams"
```

Retorna lista com `id`, `name`, `code` e `description` de cada time.

## Contexto do time

- **Time:** cross-fraud-data-services
- **project_code:** `cross-fp-data-services-pre-compute`
- **Apps (11):** pangea-serving, fraud-pangea-challenger, pangea-dedup-service, fraud-airflow-dags-configs, fraud-pangea-features-dags, fraud-pangea-features-jobs, fraud-pangea-admin, deduplication-data-service, cciac-feature-store-pangea, fraud-pangea-metrics-service, migration-new-pangea-scripts

## Notas

- `GET https://api.furycloud.io/applications` retorna todas as 59k apps sem suporte a filtro por query param
- O endpoint v2 (`web.furycloud.io/api/proxy/puma/v2/applications`) suporta filtro server-side via `project_code`
- Descoberto inspecionando as chamadas de rede do `web.furycloud.io` no DevTools do browser
