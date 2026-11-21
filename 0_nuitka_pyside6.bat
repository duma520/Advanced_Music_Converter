cls
rem if exist build rmdir /s /q build
rem if exist dist rmdir /s /q dist
rem if exist dist rmdir /s /q dist_pyside6

nuitka --standalone ^
    --enable-plugin=pyside6 ^
    --enable-plugin=numpy ^
    --windows-console-mode=disable ^
    --include-package=mido ^
    --include-package=pygame ^
    --include-package=PySide6 ^
    --include-module=pygame.midi ^
    --follow-imports ^
    --jobs=4 ^
    --output-dir=build_output ^
    Advanced_Music_Converter.py