# AirSense System Startup PowerShell Script
Write-Host "AirSense System Startup Script" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""

# Function to test Python installation with pip validation
function Test-PythonInstallation {
    param($PythonPath)
    
    # Check if path exists (for full paths) or command is available
    $pathExists = $false
    if ($PythonPath -match "^[A-Za-z]:\\") {
        # Full path - check if file exists
        $pathExists = Test-Path $PythonPath
    } else {
        # Command name - try to execute
        $pathExists = $true
    }
    
    if ($pathExists) {
        try {
            # Check Python version
            $versionResult = & $PythonPath --version 2>&1
            if ($LASTEXITCODE -ne 0) {
                return $false
            }
            
            # Check pip availability
            $pipResult = & $PythonPath -m pip --version 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  Python found but pip not available, skipping..." -ForegroundColor Yellow
                return $false
            }
            
            Write-Host "Found Python with pip:" -ForegroundColor Green
            Write-Host "  $versionResult" -ForegroundColor Green
            Write-Host "  pip: $pipResult" -ForegroundColor Green
            return $true
        } catch {
            # Python not working
            return $false
        }
    }
    return $false
}

# Function to start AirSense with specific Python
function Start-AirSense {
    param($PythonPath)
    
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    try {
        & $PythonPath -m pip install --upgrade pip
        & $PythonPath -m pip install -r requirements.txt
        
        Write-Host ""
        Write-Host "Starting AirSense system..." -ForegroundColor Yellow
        Write-Host "Dashboard will be available at: http://localhost:8501" -ForegroundColor Cyan
        Write-Host "API Documentation at: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        
        & $PythonPath -m src.main all
    } catch {
        Write-Host "Error running AirSense: $_" -ForegroundColor Red
    }
}

# Try different Python installations (user-installed first, bundled last)
$pythonPaths = @(
    "python",
    "py", 
    "python3",
    "C:\Program Files\PostgreSQL\18\pgAdmin 4\python.exe",
    "C:\Program Files (x86)\Nmap\zenmap\bin\python.exe"
)

foreach ($pythonPath in $pythonPaths) {
    Write-Host "Testing: $pythonPath" -ForegroundColor White
    if (Test-PythonInstallation -PythonPath $pythonPath) {
        Write-Host "Using Python: $pythonPath" -ForegroundColor Green
        Start-AirSense -PythonPath $pythonPath
        exit 0
    }
}

Write-Host ""
Write-Host "No Python installation with pip found!" -ForegroundColor Red
Write-Host ""
Write-Host "Please ensure Python 3.9+ is installed from https://python.org" -ForegroundColor Yellow
Write-Host "and that it is added to your system PATH." -ForegroundColor Yellow
Write-Host ""
Write-Host "To verify: Open a new PowerShell window and run 'python --version'" -ForegroundColor Cyan
Write-Host "Then check pip with: 'python -m pip --version'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
