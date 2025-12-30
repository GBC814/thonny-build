@echo off

set BUILDDIR=build
del %BUILDDIR% /Q
rmdir %BUILDDIR% /S /Q
mkdir %BUILDDIR%

@echo ............... COPYING PYTHON ...................................
xcopy D:\Python314\* %BUILDDIR% /S /E /K>NUL
@echo ............... COPYING OTHER STUFF ...................................
copy ThonnyRunner314\x64\Release\thonny.exe %BUILDDIR% /Y
copy thonny_python.ini %BUILDDIR%

@echo ............... INSTALLING DEPS ...................................

set PIP_INDEX_URL=http://mirrors.aliyun.com/pypi/simple/
set PIP_TRUSTED_HOST=mirrors.aliyun.com

%BUILDDIR%\python -s -m pip install --no-warn-script-location --no-cache-dir --upgrade pip wheel setuptools

%BUILDDIR%\python -s -m pip install --no-warn-script-location --no-cache-dir -U --only-binary Pillow,lxml,numpy,scipy,matplotlib,pandas -r ..\requirements-regular-bundle-314.txt

@rem Clean up zipp which might be pulled in by some older packages but is not needed in 3.14
%BUILDDIR%\python -s -m pip uninstall -y zipp
if exist %BUILDDIR%\Lib\site-packages\zipp rmdir %BUILDDIR%\Lib\site-packages\zipp /S /Q
if exist %BUILDDIR%\Lib\site-packages\zipp-*.dist-info rmdir %BUILDDIR%\Lib\site-packages\zipp-*.dist-info /S /Q

@echo ............... INSTALLING THONNY ...................................
%BUILDDIR%\python -s -m pip install --no-warn-script-location --pre --no-cache-dir ..\..\
@rem %BUILDDIR%\python -s -m pip install --no-warn-script-location ..\setuptools\thonny-4.0.0b4.dev1-py3-none-any.whl

@echo ............... CLEANING PYTHON ............................
@rem remove following 3 files to avoid confusion (user may think they're Thonny license etc.)
move %BUILDDIR%\LICENSE.txt %BUILDDIR%\PYTHON_LICENSE.txt
move %BUILDDIR%\README.txt %BUILDDIR%\PYTHON_README.txt
move %BUILDDIR%\NEWS.txt %BUILDDIR%\PYTHON_NEWS.txt

@rem Remove legacy dll if exists
if exist %BUILDDIR%\python310.dll del %BUILDDIR%\python310.dll /Q

del /S "%BUILDDIR%\*.pyc">NUL
@rem del /S "%BUILDDIR%\*.lib">NUL
del /S "%BUILDDIR%\tcl\*.lib">NUL
del /S "%BUILDDIR%\*.a">NUL
del /S "%BUILDDIR%\*.chm">NUL

rmdir %BUILDDIR%\Doc /S /Q>NUL
@rem rmdir %BUILDDIR%\include /S /Q>NUL
@rem rmdir %BUILDDIR%\libs /S /Q>NUL
rmdir %BUILDDIR%\Tools /S /Q>NUL
del "%BUILDDIR%\Scripts\*" /Q>NUL

copy .\pip.bat "%BUILDDIR%\Scripts\pip.bat"
copy .\pip.bat "%BUILDDIR%\Scripts\pip3.bat"
copy .\pip.bat "%BUILDDIR%\Scripts\pip3.14.bat"

rmdir %BUILDDIR%\lib\test /S /Q>NUL

del %BUILDDIR%\tcl\*.sh /Q>NUL
del %BUILDDIR%\tcl\tcl8.6\clock.tcl>NUL
del %BUILDDIR%\tcl\tcl8.6\safe.tcl>NUL
rmdir %BUILDDIR%\tcl\tix8.4.3\demos /S /Q>NUL

rmdir %BUILDDIR%\tcl\tk8.6\demos /S /Q>NUL
rmdir %BUILDDIR%\tcl\tk8.6\msgs /S /Q>NUL

rmdir %BUILDDIR%\tcl\tcl8.6\opt0.4 /S /Q>NUL
rmdir %BUILDDIR%\tcl\tcl8.6\msgs /S /Q>NUL
rmdir %BUILDDIR%\tcl\tcl8.6\tzdata /S /Q>NUL

rmdir %BUILDDIR%\lib\site-packages\pylint\test /S /Q>NUL
rmdir %BUILDDIR%\lib\site-packages\mypy\test /S /Q>NUL


@echo ............... ADDING LICENSES ...................................
copy ..\..\LICENSE.txt %BUILDDIR% /Y>NUL
mkdir %BUILDDIR%\licenses
xcopy ..\..\licenses\* %BUILDDIR%\licenses /S /E /K>NUL

@echo ............... ADDING OTHER STUFF ...................................
copy ..\..\CHANGELOG.rst %BUILDDIR% /Y>NUL
copy ..\..\CREDITS.rst %BUILDDIR% /Y>NUL
copy ..\..\README.rst %BUILDDIR% /Y>NUL


@echo ............... CREATING INSTALLER ..........................
set /p VERSION=<%BUILDDIR%\Lib\site-packages\thonny\VERSION
"D:\Inno Setup 6\iscc" /dInstallerPrefix=thonny /dAppVer=%VERSION% /dSourceFolder=build inno_setup.iss > installer_building.log

@echo ............... CREATING ZIP ..........................
SET PATH=%PATH%;D:\7-Zip
copy ..\portable_thonny.ini %BUILDDIR%
cd %BUILDDIR%
7z a -tzip ..\dist\thonny-%VERSION%-windows-portable.zip *
del portable_thonny.ini
cd ..

@echo ............... XXL ..........................
@echo Note: Some XXL packages may fail to install on Python 3.14 due to missing wheels.
%BUILDDIR%\python -s -m pip install --no-cache-dir -U --only-binary Pillow,lxml,numpy,scipy,matplotlib,pandas -r ..\requirements-xxl-bundle-314.txt
if %ERRORLEVEL% NEQ 0 (
    @echo Some XXL packages failed to install, trying without strict version locks for some...
    %BUILDDIR%\python -s -m pip install --no-cache-dir -U --only-binary Pillow,lxml,numpy,scipy,matplotlib,pandas -r ..\requirements-xxl-bundle-314.txt || rem
)

del /S "%BUILDDIR%\*.pyc">NUL

@rem no point in keeping exe-s in Scripts, as they contain absolute path to the interpreter
del "%BUILDDIR%\Scripts\*.exe" /Q>NUL
del "%BUILDDIR%\Scripts\*.manifest" /Q>NUL


"D:\Inno Setup 6\iscc" /dInstallerPrefix=thonny-xxl /dAppVer=%VERSION% /dSourceFolder=build inno_setup.iss > xxl_installer_building.log

rmdir %BUILDDIR% /S /Q
rem pause
