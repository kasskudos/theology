Add-Type -AssemblyName Microsoft.VisualBasic

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path $scriptDir ".env.meta"

$igUserId = [Microsoft.VisualBasic.Interaction]::InputBox(
    "Cole o ID da conta profissional do Instagram.",
    "Alem da Emocao - Configurar Meta",
    "17841422410235525"
)

if ([string]::IsNullOrWhiteSpace($igUserId)) {
    Write-Host "Configuracao cancelada."
    Start-Sleep -Seconds 2
    exit 0
}

Write-Host ""
Write-Host "Cole o access token da Meta."
Write-Host "Ele nao sera exibido enquanto voce digita."
$secureToken = Read-Host "META_ACCESS_TOKEN" -AsSecureString

if ($secureToken.Length -eq 0) {
    Write-Host "Configuracao cancelada: token vazio."
    Start-Sleep -Seconds 2
    exit 0
}

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
try {
    $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

$content = @"
META_ACCESS_TOKEN=$token
META_IG_USER_ID=$($igUserId.Trim())
META_GRAPH_VERSION=v23.0
"@

Set-Content -LiteralPath $envPath -Value $content -Encoding UTF8

Write-Host ""
Write-Host "Arquivo criado:"
Write-Host $envPath
Write-Host ""
Write-Host "Importante: esse arquivo esta no .gitignore e nao deve ser commitado."
Read-Host "Pressione Enter para fechar"
