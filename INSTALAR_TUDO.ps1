# Instalador automático do DET Robot para Windows (PowerShell)
# Execute com: .\INSTALAR_TUDO.ps1

# Verificar se está rodando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Clear-Host

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "           DET ROBOT - INSTALAÇÃO AUTOMÁTICA" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script vai instalar tudo automaticamente."
Write-Host "Você não precisa fazer nada, apenas aguardar!"
Write-Host ""

if (-not $isAdmin) {
    Write-Host "⚠️  AVISO: Executando sem privilégios de administrador" -ForegroundColor Yellow
    Write-Host "   Algumas operações podem falhar. Recomenda-se executar como administrador." -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Pressione ENTER para começar a instalação"

$erro = $false

# Passo 1: Verificar Python
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSO 1/5: Verificando Python" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python instalado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTALE O PYTHON:" -ForegroundColor Yellow
    Write-Host "  Baixe em: https://www.python.org/downloads/"
    Write-Host ""
    Write-Host "IMPORTANTE: Marque 'Add Python to PATH' durante instalação" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione ENTER para sair"
    exit 1
}

# Passo 2: Verificar pip
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSO 2/5: Verificando pip" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

try {
    python -m pip --version | Out-Null
    Write-Host "✅ pip instalado" -ForegroundColor Green
} catch {
    Write-Host "⚠️  pip não encontrado, instalando..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# Passo 3: Verificar navegador
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSO 3/5: Verificando navegador" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$navegadorEncontrado = $false

$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

$firefoxPaths = @(
    "C:\Program Files\Mozilla Firefox\firefox.exe",
    "C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
)

foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        Write-Host "✅ Google Chrome encontrado" -ForegroundColor Green
        $navegadorEncontrado = $true
        break
    }
}

if (-not $navegadorEncontrado) {
    foreach ($path in $firefoxPaths) {
        if (Test-Path $path) {
            Write-Host "✅ Firefox encontrado" -ForegroundColor Green
            $navegadorEncontrado = $true
            break
        }
    }
}

if (-not $navegadorEncontrado) {
    Write-Host "⚠️  AVISO: Nenhum navegador suportado encontrado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Instale um dos seguintes:"
    Write-Host "  1. Google Chrome: https://www.google.com/chrome/"
    Write-Host "  2. Firefox: https://www.mozilla.org/firefox/"
    Write-Host ""
    Read-Host "Pressione ENTER depois de instalar um navegador"
}

# Passo 4: Instalar dependências
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSO 4/5: Instalando dependências Python" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Atualizando pip..."
python -m pip install --upgrade pip --quiet

Write-Host ""
Write-Host "Instalando pacotes necessários (pode demorar alguns minutos)..."
Write-Host ""

$pacotes = @(
    "selenium",
    "webdriver-manager",
    "pydantic",
    "streamlit",
    "plotly",
    "typer",
    "rich",
    "openpyxl",
    "pandas"
)

foreach ($pacote in $pacotes) {
    Write-Host "  Instalando $pacote..." -NoNewline
    try {
        python -m pip install $pacote --quiet 2>&1 | Out-Null
        Write-Host " ✅" -ForegroundColor Green
    } catch {
        Write-Host " ❌" -ForegroundColor Red
        $erro = $true
    }
}

# Instalar requirements.txt se existir
if (Test-Path "requirements.txt") {
    Write-Host ""
    Write-Host "Instalando demais dependências do arquivo requirements.txt..."
    python -m pip install -r requirements.txt --quiet
}

# Passo 5: Testar instalação
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "PASSO 5/5: Testando instalação" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$testScript = @"
import sys

print('Verificando módulos...')

modulos = {
    'selenium': 'Automação web',
    'webdriver_manager': 'Gerenciador de drivers',
    'streamlit': 'Interface web',
    'pydantic': 'Validação de dados',
}

todos_ok = True

for modulo, desc in modulos.items():
    try:
        __import__(modulo)
        print(f'  ✅ {modulo} ({desc})')
    except ImportError:
        print(f'  ❌ {modulo} ({desc})')
        todos_ok = False

if todos_ok:
    print('\n✅ Todos os módulos instalados corretamente!')
    sys.exit(0)
else:
    print('\n❌ Alguns módulos faltando')
    sys.exit(1)
"@

$testScript | Out-File -FilePath "teste_temp.py" -Encoding UTF8

python teste_temp.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Teste de módulos passou!" -ForegroundColor Green
} else {
    Write-Host "❌ Alguns módulos não instalaram corretamente" -ForegroundColor Red
    $erro = $true
}

Remove-Item "teste_temp.py"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan

if (-not $erro) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "            ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 O DET Robot está pronto para usar!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "COMO USAR:" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Execute um destes comandos:"
    Write-Host ""
    Write-Host "  .\USAR_DET_ROBOT.bat" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  (ou)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  python run_det_robot.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "         ⚠️  INSTALAÇÃO TEVE ALGUNS PROBLEMAS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Verifique os erros acima e tente corrigir."
    Write-Host ""
    Write-Host "Se precisar de ajuda, veja: SOLUCAO_PROBLEMAS_DET.md"
}

Write-Host ""
Read-Host "Pressione ENTER para finalizar"
