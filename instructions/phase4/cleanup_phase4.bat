@echo off
REM Phase 4 Folder Cleanup Script
REM Deletes redundant documentation files
REM Keeps only essential execution prompts

cd /d C:\ClaudeDesktop_Projects\Trade2026\instructions\phase4

echo Cleaning up Phase 4 folder...
echo.

REM Delete redundant documentation files
del /F /Q PHASE4_ALL_PROMPTS_READY.md
del /F /Q PHASE4_CREATION_COMPLETE.md
del /F /Q PHASE4_DELIVERY_STATUS.md
del /F /Q PHASE4_FINAL_STATUS.md
del /F /Q PHASE4_HANDOFF.md
del /F /Q PHASE4_INDEX.md
del /F /Q PHASE4_PROMPTS_04-13_SPECIFICATIONS.md
del /F /Q PHASE4_PROMPTS_SUMMARY.md

echo.
echo Cleanup complete!
echo.
echo Remaining files:
dir /B PHASE4*.md
dir /B README.md
echo.
echo Essential files kept:
echo   - PHASE4_PROMPT00_VALIDATION_GATE.md
echo   - PHASE4_PROMPT01_LIBRARY_SERVICE_DATABASE.md
echo   - PHASE4_PROMPT03_NATS_INTEGRATION.md
echo   - PHASE4_PROMPT04_ENTITY_CRUD_ENDPOINTS.md
echo   - PHASE4_PROMPT05_DEPLOYMENT_LIFECYCLE.md
echo   - PHASE4_PROMPT06_HOTSWAP_ENGINE.md
echo   - PHASE4_PROMPTS_06-13_CONSOLIDATED.md
echo   - PHASE4_EXECUTION_GUIDE.md
echo   - README.md
echo.
pause
