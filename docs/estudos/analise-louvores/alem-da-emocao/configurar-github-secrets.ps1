Add-Type -AssemblyName Microsoft.VisualBasic

$ErrorActionPreference = "Stop"

function Require-Gh {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $gh) {
        throw "GitHub CLI (gh) nao encontrado."
    }
}

function Set-GitHubSecret {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Valor vazio para $Name."
    }

    $Value | gh secret set $Name --repo kasskudos/theology
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao configurar secret $Name."
    }
}

function Read-SecretText {
    param([string]$Name)

    Write-Host ""
    Write-Host "Cole o valor de $Name."
    Write-Host "Ele nao sera exibido enquanto voce digita."
    $secure = Read-Host $Name -AsSecureString
    if ($secure.Length -eq 0) {
        throw "Valor vazio para $Name."
    }

    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }
}

try {
    Require-Gh

    Write-Host "Configurando GitHub Secrets para kasskudos/theology"
    Write-Host ""
    Write-Host "Voce vai informar tres valores:"
    Write-Host "1. META_ACCESS_TOKEN"
    Write-Host "2. META_IG_USER_ID"
    Write-Host "3. GOOGLE_DRIVE_API_KEY"
    Write-Host ""

    $metaAccessToken = Read-SecretText "META_ACCESS_TOKEN"

    $igUserId = [Microsoft.VisualBasic.Interaction]::InputBox(
        "Informe o META_IG_USER_ID.",
        "Alem da Emocao - GitHub Secrets",
        "27356910893993006"
    )
    if ([string]::IsNullOrWhiteSpace($igUserId)) {
        throw "META_IG_USER_ID vazio."
    }

    $googleDriveApiKey = Read-SecretText "GOOGLE_DRIVE_API_KEY"

    Set-GitHubSecret "META_ACCESS_TOKEN" $metaAccessToken
    Set-GitHubSecret "META_IG_USER_ID" $igUserId.Trim()
    Set-GitHubSecret "GOOGLE_DRIVE_API_KEY" $googleDriveApiKey

    Write-Host ""
    Write-Host "Secrets configurados com sucesso."
    Write-Host ""
    Write-Host "Proximo teste no GitHub:"
    Write-Host "Actions > Alem da Emocao Publish > Run workflow"
    Write-Host "cut: 3"
    Write-Host "dry_run: true"
    Read-Host "Pressione Enter para fechar"
    exit 0
} catch {
    Write-Host ""
    Write-Host "ERRO: $($_.Exception.Message)"
    Read-Host "Pressione Enter para fechar"
    exit 1
}
