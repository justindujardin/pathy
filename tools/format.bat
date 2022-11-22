echo "This is designed to run in Windows PowerShell."

if not exist ".winenv" (
    echo "Making virtual environment (.winenv)"
    pip install virtualenv --upgrade
    python -m virtualenv .winenv -p python3
)

echo "Installing/updating dev requirements..."
.\.winenv\Scripts\pip install -r requirements.txt -r requirements-local.txt
echo "Sort imports one per line, so autoflake can remove unused imports"
.\.winenv\Scripts\python -m isort pathy --force-single-line-imports
.\.winenv\Scripts\python -m autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place main.py --exclude=__init__.py
.\.winenv\Scripts\python -m isort pathy
.\.winenv\Scripts\python -m black pathy