@echo off
title The Galactic Dream Engine
echo =================================================
echo THE GALACTIC DREAM ENGINE - INITIALIZATION PROTOCOL
echo =================================================
echo.
echo Starting FastAPI Backend...
start cmd /k run_backend.bat

echo Starting React Vite Frontend...
start cmd /k run_frontend.bat

echo.
echo =================================================
echo SIMULATION ONLINE AND EXPLORABLE AT:
echo http://localhost:5173
echo =================================================
