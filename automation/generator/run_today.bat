@echo off
REM ==========================================
REM mold-factory: 오늘 발행 + Hugo 빌드 원클릭
REM ==========================================

REM 1) 스크립트가 있는 폴더로 이동
cd /d C:\sites\mold-factory\automation\generator

echo.
echo [1/2] 오늘 발행할 포스트 처리 (daily_publish.py) ...
echo.

python daily_publish.py

echo.
echo [2/2] Hugo 빌드 실행 (build_site.py) ...
echo.

python build_site.py

echo.
echo === 모든 작업이 끝났습니다. 창을 닫으려면 아무 키나 누르세요. ===
pause
