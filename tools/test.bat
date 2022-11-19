echo "This is designed to run in Windows PowerShell."

echo "Run tests..."
.\.winenv\Scripts\python -m pytest pathy/_tests --cov=pathy
