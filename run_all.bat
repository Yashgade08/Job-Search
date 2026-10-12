@echo off
echo ========================================================
echo   Launching Job Market Intelligence Platform
echo ========================================================
echo.
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Job Intelligence FastAPI Backend" cmd /k "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting Streamlit Dashboard on http://localhost:8501 ...
start "Job Intelligence Streamlit Dashboard" cmd /k "python -m streamlit run dashboard/app.py --server.port 8501"

echo.
echo Both servers have been launched in separate windows!
echo - Dashboard: http://localhost:8501
echo - API Docs:  http://127.0.0.1:8000/docs
echo ========================================================
pause
