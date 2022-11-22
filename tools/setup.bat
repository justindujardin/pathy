echo "This is designed to run in Windows PowerShell."

if not exist ".winenv" (
    echo "Making virtual environment (.winenv)"
    pip install virtualenv --upgrade
    python -m virtualenv .winenv -p python3
)

echo "Installing/updating requirements..."
.\.winenv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
.\.winenv\Scripts\pip install -e ".[all]"