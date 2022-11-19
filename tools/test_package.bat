echo "This is designed to run in Windows PowerShell."

pushd ".\dist"
for %%a in ("*.whl") do set WHEEL=".\dist\%%a"
popd

.\.winenv\Scripts\pip install pip install "%WHEEL%[test]"

echo " === Running tests WITHOUT package extras installed..."
.\.winenv\Scripts\python -m pytest --pyargs pathy._tests --cov=pathy
