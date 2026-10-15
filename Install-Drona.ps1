$ErrorActionPreference = 'Stop'

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $projectDir '.venv'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'
$databaseDir = Join-Path $projectDir 'Database'
New-Item -ItemType Directory -Path $databaseDir -Force | Out-Null

Write-Host 'Drona setup' -ForegroundColor Cyan

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$pythonExecutable = $null
$pythonArguments = @()
if ($pythonCommand) {
    $pythonExecutable = $pythonCommand.Source
} else {
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        $pythonExecutable = $pyCommand.Source
        $pythonArguments = @('-3')
    }
}

if (-not $pythonExecutable) {
    throw "Python 3.10 or newer is required. Install it from https://www.python.org/downloads/ and enable Add Python to PATH, then run setup again."
}

$versionOutput = (& $pythonExecutable @pythonArguments --version 2>&1 | Out-String).Trim()
if ($versionOutput -notmatch 'Python\s+(\d+)\.(\d+)') {
    throw "Could not determine the Python version: $versionOutput"
}
$pythonMajor = [int]$Matches[1]
$pythonMinor = [int]$Matches[2]
if (($pythonMajor -lt 3) -or (($pythonMajor -eq 3) -and ($pythonMinor -lt 10))) {
    throw "Drona requires Python 3.10 or newer. Found $versionOutput"
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host 'Creating Drona Python environment...'
    & $pythonExecutable @pythonArguments -m venv $venvDir
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
}

Write-Host 'Installing Drona server packages...'
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Could not update pip in Drona's local environment." }
& $venvPython -m pip install fastapi uvicorn requests
if ($LASTEXITCODE -ne 0) { throw "Could not install Drona's Python packages." }

function Get-DronaGitCommand {
    $command = Get-Command git -ErrorAction SilentlyContinue
    if ($command) { return $command }

    $gitExeCandidates = @(
        (Join-Path $env:ProgramFiles 'Git\cmd\git.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Git\cmd\git.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Git\cmd\git.exe')
    )
    foreach ($gitExe in $gitExeCandidates) {
        if (Test-Path -LiteralPath $gitExe) {
            $gitDirectory = Split-Path -Parent $gitExe
            $env:Path = "$gitDirectory;$env:Path"
            return Get-Command git -ErrorAction SilentlyContinue
        }
    }
    return $null
}

$gitCommand = Get-DronaGitCommand
if (-not $gitCommand) {
    Write-Host 'Git is required by Drona and was not found. Installing Git for Windows...'
    $wingetCommand = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCommand) {
        & $wingetCommand.Source install --id Git.Git --exact --source winget --accept-source-agreements --accept-package-agreements --silent
        $gitCommand = Get-DronaGitCommand
    }

    if (-not $gitCommand) {
        Write-Host 'Installing Git using the official Git for Windows installer...'
        $gitInstaller = Join-Path $env:TEMP 'Drona-Git-Installer.exe'
        try {
            Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/latest/download/Git-64-bit.exe' -OutFile $gitInstaller
            $gitInstallProcess = Start-Process -FilePath $gitInstaller -ArgumentList '/VERYSILENT /NORESTART /SP-' -Wait -PassThru
            if ($gitInstallProcess.ExitCode -ne 0) {
                throw "The Git installer exited with code $($gitInstallProcess.ExitCode)."
            }
        } catch {
            throw "Git is required, but automatic installation failed. Install Git from https://git-scm.com/install/windows, then run this setup again. Details: $($_.Exception.Message)"
        } finally {
            if (Test-Path -LiteralPath $gitInstaller) { Remove-Item -LiteralPath $gitInstaller -Force }
        }
        $gitCommand = Get-DronaGitCommand
    }

    if (-not $gitCommand) {
        throw 'Git installation finished, but git.exe could not be found. Restart PowerShell and run Install-Drona.ps1 again.'
    }
    Write-Host 'Git is installed and ready.' -ForegroundColor Green
}

if ($gitCommand) {
    $setupGit = Read-Host "Set up Drona's GitHub push feature now? Enter y or press Enter to skip"
    if ($setupGit -match '^(y|yes)$') {
        while ($true) {
            $repoInput = (Read-Host 'Enter the full path to your Git repository').Trim().Trim('"').Trim("'")
            if (-not $repoInput) { break }

            $repoRootOutput = & $gitCommand.Source -C $repoInput rev-parse --show-toplevel 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Host 'That path is not a Git repository. Try again, or press Enter to skip.' -ForegroundColor Yellow
                continue
            }

            $repoRoot = ($repoRootOutput | Out-String).Trim()
            $remoteOutput = & $gitCommand.Source -C $repoRoot remote get-url origin 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "This repository has no origin remote. Drona's push action needs origin; try another path or press Enter to skip." -ForegroundColor Yellow
                continue
            }

            $currentBranch = (& $gitCommand.Source -C $repoRoot branch --show-current 2>$null | Out-String).Trim()
            if ($LASTEXITCODE -ne 0 -or $currentBranch -ne 'main') {
                Write-Host "Drona currently pushes the local main branch. Switch this repository to main, then run setup again." -ForegroundColor Yellow
                break
            }

            $settingsPath = Join-Path $databaseDir 'repo_settings.json'
            $settings = @{ category = 'Use folder category'; repo_path = $repoRoot }
            $settingsJson = $settings | ConvertTo-Json
            $utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
            [System.IO.File]::WriteAllText($settingsPath, $settingsJson, $utf8NoBom)
            Write-Host 'Git repository saved for this computer.' -ForegroundColor Green
            break
        }
    }
}

$vsixDirectory = Join-Path $projectDir 'drona-activity-tracker'
$vsixPackage = Get-ChildItem -LiteralPath $vsixDirectory -Filter '*.vsix' -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($vsixPackage) {
    $vsixPath = $vsixPackage.FullName
    $codeCommand = Get-Command code -ErrorAction SilentlyContinue
    if ($codeCommand) {
        Write-Host 'Installing the Drona VS Code extension...'
        & $codeCommand.Source --install-extension $vsixPath --force
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'Automatic extension installation failed. Install the VSIX manually from the VS Code Extensions menu.' -ForegroundColor Yellow
        }
    } else {
        Write-Host 'VS Code command-line tool not found. Install the extension from the VS Code Extensions menu using this file:' -ForegroundColor Yellow
        Write-Host $vsixPath
    }
} else {
    Write-Host 'The Drona VS Code extension package is missing. The dashboard works, but automatic coding-time tracking needs the extension.' -ForegroundColor Yellow
}

Write-Host ''
Write-Host 'Drona setup is complete. Run Start Drona.bat whenever you want to use the dashboard.' -ForegroundColor Green
Write-Host 'The server runs only on this computer. Keep its window open while using Drona.'
Read-Host 'Press Enter to close setup' | Out-Null
