echo "Removing build files..."

rmdir /S /Q "dist" 2>nul
rmdir /S /Q "build" 2>nul
rmdir /S /Q "htmlcov" 2>nul
rmdir /S /Q ".test-env" 2>nul
rmdir /S /Q "pathy.egg-info" 2>nul
