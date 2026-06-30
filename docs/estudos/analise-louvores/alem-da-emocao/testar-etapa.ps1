Add-Type -AssemblyName Microsoft.VisualBasic

function Normalize-Episode {
    param([string]$Value)

    $clean = $Value.Trim()
    if ($clean -match '^(?i:EP)?0*(\d+)$') {
        return "EP{0:D2}" -f [int]$Matches[1]
    }

    throw "Entrada invalida: $Value. Use algo como 2, 02 ou EP02."
}

function Ask-Episode {
    $episodeInput = [Microsoft.VisualBasic.Interaction]::InputBox(
        "Digite o numero do episodio. Exemplo: 2, 02 ou EP02",
        "Alem da Emocao - Testar etapa",
        "EP02"
    )

    if ([string]::IsNullOrWhiteSpace($episodeInput)) {
        Write-Host "Operacao cancelada."
        exit 0
    }

    return Normalize-Episode $episodeInput
}

function Ask-Cut {
    param([string]$Message)

    $cutInput = [Microsoft.VisualBasic.Interaction]::InputBox(
        $Message,
        "Alem da Emocao - Corte opcional",
        ""
    )

    if ([string]::IsNullOrWhiteSpace($cutInput)) {
        return $null
    }

    $cutInput = $cutInput.Trim()
    if ($cutInput -match '^\d+$') {
        return [int]$cutInput
    }

    throw "Corte invalido: $cutInput. Use apenas numero, exemplo: 1."
}

function Ask-YesNo {
    param(
        [string]$Message,
        [string]$Default = "S"
    )

    $answer = [Microsoft.VisualBasic.Interaction]::InputBox(
        "$Message`nDigite S para sim ou N para nao.",
        "Alem da Emocao - Confirmacao",
        $Default
    )

    if ([string]::IsNullOrWhiteSpace($answer)) {
        return $false
    }

    return $answer.Trim().ToUpper().StartsWith("S")
}

function Add-CutArg {
    param(
        [System.Collections.Generic.List[string]]$Args,
        [Nullable[int]]$Cut
    )

    if ($null -ne $Cut) {
        $Args.Add("--only-cut")
        $Args.Add([string]$Cut)
    }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pipelinePath = Join-Path $scriptDir "pipeline.py"
$drivePath = Join-Path $scriptDir "drive_upload.py"
$metaPath = Join-Path $scriptDir "meta_publish.py"

$menu = @"
Escolha a etapa para testar:

1 - Transcricoes e agenda
2 - Legendas e comentarios
3 - Prompts de capa
4 - Upload Google Drive
5 - Meta/Instagram dry-run
6 - Meta/Instagram publicar
7 - Pipeline completo dry-run
8 - Pipeline completo real
"@

try {
    $choice = [Microsoft.VisualBasic.Interaction]::InputBox(
        $menu,
        "Alem da Emocao - Testar etapa",
        "1"
    )

    if ([string]::IsNullOrWhiteSpace($choice)) {
        Write-Host "Operacao cancelada."
        Start-Sleep -Seconds 2
        exit 0
    }

    $choice = $choice.Trim()
    $episode = Ask-Episode
    $argsList = [System.Collections.Generic.List[string]]::new()
    $commandLabel = ""

    switch ($choice) {
        "1" {
            $argsList.Add($pipelinePath)
            $argsList.Add($episode)
            $argsList.Add("--skip-legends")
            $argsList.Add("--skip-cover-prompts")
            $argsList.Add("--skip-drive-upload")
            $commandLabel = "Transcricoes e agenda"
        }
        "2" {
            $cut = Ask-Cut "Digite o numero do corte para testar, ou deixe vazio para todos."
            $argsList.Add($pipelinePath)
            $argsList.Add($episode)
            $argsList.Add("--skip-cover-prompts")
            $argsList.Add("--skip-drive-upload")
            Add-CutArg $argsList $cut
            $commandLabel = "Legendas e comentarios"
        }
        "3" {
            $cut = Ask-Cut "Digite o numero do corte para testar, ou deixe vazio para todos."
            $argsList.Add($pipelinePath)
            $argsList.Add($episode)
            $argsList.Add("--skip-legends")
            $argsList.Add("--skip-drive-upload")
            Add-CutArg $argsList $cut
            $commandLabel = "Prompts de capa"
        }
        "4" {
            $cut = Ask-Cut "Digite o numero do corte para testar upload, ou deixe vazio para todos."
            $dryRun = Ask-YesNo "Rodar apenas dry-run, sem enviar arquivos ao Drive?" "S"
            $argsList.Add($drivePath)
            $argsList.Add($episode)
            if ($null -ne $cut) {
                $argsList.Add("--cut")
                $argsList.Add([string]$cut)
            }
            if ($dryRun) {
                $argsList.Add("--dry-run")
            }
            $commandLabel = "Upload Google Drive"
        }
        "5" {
            $cut = Ask-Cut "Digite o numero do corte para testar Meta, ou deixe vazio para todos."
            $argsList.Add($metaPath)
            $argsList.Add($episode)
            $argsList.Add("--dry-run")
            if ($null -ne $cut) {
                $argsList.Add("--cut")
                $argsList.Add([string]$cut)
            }
            $commandLabel = "Meta/Instagram dry-run"
        }
        "6" {
            $cut = Ask-Cut "Digite o numero do corte para publicar, ou deixe vazio para todos."
            $confirmed = Ask-YesNo "Isso pode publicar de verdade no Instagram. Confirmar?" "N"
            if (-not $confirmed) {
                Write-Host "Publicacao cancelada."
                Start-Sleep -Seconds 2
                exit 0
            }
            $argsList.Add($metaPath)
            $argsList.Add($episode)
            if ($null -ne $cut) {
                $argsList.Add("--cut")
                $argsList.Add([string]$cut)
            }
            $commandLabel = "Meta/Instagram publicar"
        }
        "7" {
            $argsList.Add($pipelinePath)
            $argsList.Add($episode)
            $argsList.Add("--dry-run")
            $commandLabel = "Pipeline completo dry-run"
        }
        "8" {
            $confirmed = Ask-YesNo "Rodar o pipeline completo real para $episode?" "N"
            if (-not $confirmed) {
                Write-Host "Pipeline cancelado."
                Start-Sleep -Seconds 2
                exit 0
            }
            $argsList.Add($pipelinePath)
            $argsList.Add($episode)
            $commandLabel = "Pipeline completo real"
        }
        default {
            throw "Opcao invalida: $choice"
        }
    }

    Write-Host ""
    Write-Host "Etapa: $commandLabel"
    Write-Host "Episodio: $episode"
    Write-Host "Comando:"
    Write-Host ("py " + ($argsList -join " "))
    Write-Host ""

    & py @argsList
    $exitCode = $LASTEXITCODE

    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "Etapa concluida com sucesso."
    } else {
        Write-Host "Etapa terminou com erro. Codigo: $exitCode"
    }

    Read-Host "Pressione Enter para fechar"
    exit $exitCode
} catch {
    Write-Host ""
    Write-Host "ERRO: $($_.Exception.Message)"
    Read-Host "Pressione Enter para fechar"
    exit 1
}
