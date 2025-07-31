# Windows PowerShell version (format.ps1)
# Run .\format.ps1 in bash
.\.oilvenv\Scripts\black . --exclude .oilvenv
.\.oilvenv\Scripts\isort . --skip .oilvenv
.\.oilvenv\Scripts\python.exe -m flake8 . --exclude=.oilvenv
if (Get-ChildItem -Recurse -Filter *.ipynb) {
  Write-Host "Formatting notebooks with black and isort via nbqa..."
  .\.oilvenv\Scripts\python.exe -m nbqa black . --line-length=88 --exclude .oilvenv
  .\.oilvenv\Scripts\python.exe -m nbqa isort . --skip .oilvenv
  Write-Host "Linting notebooks with flake8 via nbqa..."
  .\.oilvenv\Scripts\python.exe -m nbqa flake8 . --exclude .oilvenv --exit-zero
} else {
  Write-Host "No notebooks found - skipping nbQA."
}
