# Agendar reuniões via Google Calendar (Composio)

## Ferramenta

`mcp__composio__COMPOSIO_MULTI_EXECUTE_TOOL` com `tool_slug: "GOOGLECALENDAR_CREATE_EVENT"`

## Schema

```json
{
  "tool_slug": "GOOGLECALENDAR_CREATE_EVENT",
  "arguments": {
    "summary": "Título da reunião",
    "description": "Descrição e contexto da reunião",
    "start_datetime": "YYYY-MM-DDTHH:MM:SS",
    "timezone": "America/Sao_Paulo",
    "event_duration_hour": 0,
    "event_duration_minutes": 30,
    "attendees": ["email1@mercadolivre.com", "email2@mercadolivre.com"],
    "calendar_id": "primary"
  }
}
```

## Observações

- `session_id`: usar `"open"`
- Duração: separar em `event_duration_hour` e `event_duration_minutes`
- Google Meet é criado automaticamente
- Padrão de email do Meli: `firstname.lastname@mercadolivre.com`
- O organizador (lucas.kudo@mercadolivre.com) é adicionado automaticamente
- sempre manda o titulo e a descrição do email antes para aprovação

## Time do Lucas

Quando o usuário pedir para marcar uma reunião com "o meu time" ou "o time", usar o e-mail de grupo:

- **fraud-dq-br@mercadolivre.com** — time Fraud DQ BR

Fluxo para marcar reunião com o time:
1. Verificar agenda com `GOOGLECALENDAR_FIND_FREE_SLOTS` + `GOOGLECALENDAR_EVENTS_LIST` para a semana desejada
2. Identificar os melhores slots livres (>=1h) dentro do horário comercial
3. Propor título e descrição para aprovação do usuário
4. Criar o evento com `GOOGLECALENDAR_CREATE_EVENT` incluindo `fraud-dq-br@mercadolivre.com` nos `attendees`
