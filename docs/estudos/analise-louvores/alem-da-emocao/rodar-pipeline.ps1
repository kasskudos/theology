Add-Type -AssemblyName Microsoft.VisualBasic

$episodeInput = [Microsoft.VisualBasic.Interaction]::InputBox(
    "Digite o numero do episodio. Exemplo: 2, 02 ou EP02",
    "Alem da Emocao - Pipeline",
    "EP02"
)

if ([string]::IsNullOrWhiteSpace($episodeInput)) {
    Write-Host "Operacao cancelada."
    Start-Sleep -Seconds 2
    exit 0
}

$episodeInput = $episodeInput.Trim()

if ($episodeInput -match '^(?i:EP)?0*(\d+)$') {
    $episode = "EP{0:D2}" -f [int]$Matches[1]
} else {
    Write-Host "Entrada invalida: $episodeInput"
    Write-Host "Use algo como 2, 02 ou EP02."
    Read-Host "Pressione Enter para fechar"
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pipelinePath = Join-Path $scriptDir "pipeline.py"

Write-Host ""
Write-Host "Rodando pipeline para $episode..."
Write-Host ""

py $pipelinePath $episode
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "Pipeline concluido com sucesso."
} else {
    Write-Host "Pipeline terminou com erro. Codigo: $exitCode"
}

Read-Host "Pressione Enter para fechar"
exit $exitCode
