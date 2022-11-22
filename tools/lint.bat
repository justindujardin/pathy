echo "This is designed to run in Windows PowerShell."

if not exist ".winenv" (
    echo "Making virtual environment (.winenv)"
    pip install virtualenv --upgrade
    python -m virtualenv .winenv -p python3
)

echo "Installing/updating dev requirements..."
.\.winenv\Scripts\pip install -r requirements.txt -r requirements-dev.txt

echo "========================= mypy"
.\.winenv\Scripts\python.exe -m mypy pathy
echo "========================= flake8"
.\.winenv\Scripts\python.exe -m flake8 pathy
echo "========================= black"
.\.winenv\Scripts\python.exe -m black pathy --check
echo "========================= pyright"
npx pyright --version
npx pyright pathy