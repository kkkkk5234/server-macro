@echo off
title TOI UU TU DONG THEO CAU HINH MAY
echo ===============================
echo   TOI UU HE THONG TU DONG
echo ===============================

:: KIEM TRA SSD HAY HDD
for /f "tokens=2 delims==" %%a in ('wmic diskdrive get model^,MediaType /format:value ^| find "="') do set mediatype=%%a

echo.
if /i "%mediatype%"=="SSD" (
  echo ✔ Phat hien O DIA: SSD  → se toi uu che do TRIM
  fsutil behavior set DisableDeleteNotify 0 >nul
) else (
  echo ✔ Phat hien O DIA: HDD  → se toi uu chong phan manh
  defrag C: /O >nul
)

:: KIEM TRA DUNG LUONG RAM
for /f "tokens=2 delims==" %%b in ('wmic computersystem get totalphysicalmemory /format:value ^| find "="') do set ram=%%b

if %ram% LSS 6000000000 (
  echo ✔ RAM THAP → toi uu giai phong RAM
  wevtutil cl System >nul 2>&1
  wevtutil cl Application >nul 2>&1
  ipconfig /flushdns >nul
) else (
  echo ✔ RAM DU → giam dich vu nen khong can giai phong RAM
)

:: BAT CHE DO ULTIMATE PERFORMANCE
echo.
echo ✔ Bat che do Ultimate Performance
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1

:: TOI UU CPU & DICH VU NEN
echo.
echo ✔ Toi uu CPU, tat dich vu nang khong can thiet
sc stop "SysMain" >nul 2>&1
sc config "SysMain" start=disabled >nul 2>&1
sc stop "DiagTrack" >nul 2>&1
sc config "DiagTrack" start=disabled >nul 2>&1

:: TOI UU MANG & FPS ONLINE
echo.
echo ✔ Toi uu mang giam ping
netsh int tcp set global autotuninglevel=normal >nul
netsh int tcp set global rss=enabled >nul

echo.
echo ===============================
echo   ✅ TOI UU HOAN TAT
echo   → Khuyen nghi Restart may
echo ===============================
pause