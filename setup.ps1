# Movie Emotion Recommender - Setup Script for Windows

Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Movie Emotion Recommender - Setup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Create folder structure
Write-Host "`nCreating folder structure..." -ForegroundColor Yellow

$folders = @(
    "app\services",
    "ml",
    "recommender",
    "quiz",
    "data",
    "models",
    "static\css",
    "static\js",
    "templates"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

# Create __init__.py files for Python modules
$initFiles = @(
    "app\__init__.py",
    "app\services\__init__.py",
    "ml\__init__.py",
    "recommender\__init__.py",
    "quiz\__init__.py"
)

foreach ($file in $initFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

Write-Host "✓ Folder structure created" -ForegroundColor Green

# Create Python virtual environment
Write-Host "`nCreating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "✓ Virtual environment created" -ForegroundColor Green

# Display activation instructions
Write-Host "`n===================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "`nNext steps:`n"
Write-Host "1. Activate the virtual environment:" -ForegroundColor Yellow
Write-Host "   .\venv\Scripts\Activate.ps1`n"
Write-Host "2. Install dependencies:" -ForegroundColor Yellow
Write-Host "   pip install -r requirements.txt`n"
Write-Host "3. Add your TMDB API key to .env (optional)`n" -ForegroundColor Yellow
Write-Host "4. Run the app:" -ForegroundColor Yellow
Write-Host "   python run.py`n"
Write-Host "===================================" -ForegroundColor Cyan
