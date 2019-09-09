::@echo off
:: enable delayed expansion - used to resolve variable in loop
:: variable has to be used with '!' instead of '%'
setlocal ENABLEDELAYEDEXPANSION

::::::::::::::::::::::::::::::::::::::::::::
:: User Configuration
::::::::::::::::::::::::::::::::::::::::::::

:: adapt this path to your needs
set gptPath="C:\Program Files\snap\bin\gpt.exe"

::::::::::::::::::::::::::::::::::::::::::::
:: Command line handling
::::::::::::::::::::::::::::::::::::::::::::

:: first parameter is a path to the graph xml
set graphXmlPath=%1

:: second parameter is a path to a parameter file
set parameterFilePath=%2

:: use third parameter for path to source products
set sourceDirectory=%3
:: if sourceDirectory ends with '\' remove it
if %sourceDirectory:~-1%==\ set sourceDirectory=%sourceDirectory:~0,-1%

:: use third parameter for path to target products
set targetDirectory=%4
:: if targetDirectory ends with '\' remove it
if %targetDirectory:~-1%==\ set targetDirectory=%targetDirectory:~0,-1%

:: the fourth parameter is a file prefix for the target product name, 
:: typically indicating the type of processing
set targetFilePrefix=%5

:: Create the target directory
md %targetDirectory%

::::::::::::::::::::::::::::::::::::::::::::
:: Main processing
::::::::::::::::::::::::::::::::::::::::::::

:: double '%' in batch file and only a single '%' on command line
:: '/D' is for directories like Sentinel data. Remove '/D' when you open files.
for /D /R %sourceDirectory% %%F in (S2*.SAFE) do (
  echo.
  :: '~fF' means abolute path of 'F'
  set sourceFile=%%~fF
  echo Processing !sourceFile!
  :: '~nF' means filename without extension of 'F'
  set targetFile=%targetDirectory%\%targetFilePrefix%_%%~nF.dim
  set procCmd=%gptPath% %graphXmlPath% -e -p %parameterFilePath% -t "!targetFile!" "!sourceFile!"
  call !procCmd! 
)
