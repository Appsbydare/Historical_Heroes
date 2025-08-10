@echo off
setlocal

REM 1. Create build_release folder
if not exist build_release mkdir build_release

REM 2. Copy all needed .py files
copy backend\app.py build_release\app.py
copy backend\extraction_manager.py build_release\extraction_manager.py
copy wikipedia_extractor.py build_release\wikipedia_extractor.py
REM Optionally copy any other .py files from backend
for %%f in (backend\*.py) do copy %%f build_release\

REM 3. Create empty data folder
if not exist build_release\data mkdir build_release\data

REM 4. Install pyinstaller if not present
pip show pyinstaller >nul 2>&1
if errorlevel 1 pip install pyinstaller

REM 5. Build the EXE
cd build_release
pyinstaller --onefile --noconsole --name WikipediaExtractor app.py

REM 6. Copy data folder to dist
xcopy data dist\data /E /I /Y

REM 7. Print output location
cd dist
@echo.
@echo Build complete! Your EXE is at: %cd%\WikipediaExtractor.exe
@echo The data folder is at: %cd%\data
pause 