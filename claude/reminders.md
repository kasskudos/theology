# Criar lembretes nativos no macOS

## 1. Lembrete pontual

Usar o app nativo **Reminders** via `osascript`:

```bash
osascript -e 'tell app "Reminders" to make new reminder with properties {name:"TÍTULO", due date:date "DD/MM/YYYY HH:MM:SS", remind me date:date "DD/MM/YYYY HH:MM:SS"}'
```

- Sempre verificar a hora atual com `date "+%H:%M"` antes de criar
- Formato de data: `DD/MM/YYYY HH:MM:SS`

## 2. Lembrete recorrente (qualquer tipo)

Usar **launchd user agent** — é a abordagem padrão para recorrências no macOS.

> ⚠️ cron NÃO funciona para abrir apps/popups GUI. O launchd roda na sessão do usuário e tem acesso à tela.

### Popup via In Your Face

```bash
/usr/bin/open 'inyourface://showAlert?title=TÍTULO&notes=NOTAS'
```

### Criar o plist em `~/Library/LaunchAgents/com.lkudo.NOME.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lkudo.NOME</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>inyourface://showAlert?title=TÍTULO&notes=NOTAS</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <!-- Repetir um dict por dia da semana (1=seg, 2=ter, ..., 5=sex) -->
        <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>30</integer><key>Weekday</key><integer>1</integer></dict>
    </array>
</dict>
</plist>
```

### Carregar o agent

```bash
launchctl load ~/Library/LaunchAgents/com.lkudo.NOME.plist
```

### Testar imediatamente

```bash
launchctl kickstart -k gui/$(id -u)/com.lkudo.NOME
```

### Descarregar (desativar)

```bash
launchctl unload ~/Library/LaunchAgents/com.lkudo.NOME.plist
```

## 3. Recorrência complexa (primeiro dia útil, última sexta, etc.)

Criar um script Python em `~/.claude/scripts/reminder_recorrente.py` que:
1. Calcula se hoje é o dia correto para a regra
2. Se sim, dispara o In Your Face via `subprocess.run(["/usr/bin/open", "inyourface://..."])`

E um launchd agent que roda todo dia de manhã chamando o script.

## Observações

- As opções de snooze (1 hora, hoje à noite, amanhã) são fixas do macOS, não configuráveis
- Agents launchd sobrevivem a reboots automaticamente
- Agents existentes: `com.lkudo.tickets.morning`, `com.lkudo.tickets.afternoon`, `com.lkudo.tickets.evening`
