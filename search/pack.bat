@echo off
pushd "%~dp0"
set VERSION=%1
if "%VERSION%" == "" goto exit

::ntzip -r TheHologram-PythonCheat-%VERSION%.0.zip BepInEx\Console\Mods\Cheat
::7za a PythonCheatMod_v%VERSION%.7z BepInEx\Console\Mods\Cheat\*
::xcopy /D /Y /U BepInEx\Console\Mods\Cheat\* E:\Development\Gaming\DSP_Mods\cheat
::xcopy /D /Y /U BepInEx\Console\Mods\Cheat\* E:\Development\Gaming\DSP_Mods\thunder\PythonCheatMod\BepInEx\Console\Mods\Cheat 

pushd E:\Development\Gaming\DSP_Mods\thunder\PythonCheatMod
ntzip -r TheHologram-PythonCheat-%VERSION%.0.zip .
move TheHologram-PythonCheat-%VERSION%.0.zip ..
goto exit
:error
echo No Version specified
:exit
popd