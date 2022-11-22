echo "This is designed to run in Windows PowerShell."

if not exist ".winenv" (
    echo "Making virtual environment (.winenv)"
    pip install virtualenv --upgrade
    python -m virtualenv .winenv -p python3
)

echo "Cleaning output folders"
call .\tools\clean.bat

echo "Build python package..."
.\.winenv\Scripts\python setup.py sdist bdist_wheel
