cls
rem if exist build rmdir /s /q build
rem if exist dist rmdir /s /q dist
rem if exist dist rmdir /s /q dist_pyside6

nuitka --standalone ^
    --enable-plugin=pyside6 ^
    --enable-plugin=numpy ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=icon.ico ^
    --include-data-files=icon.ico=icon.ico ^
    --include-package=mido ^
    --include-package=pygame ^
    --include-package=PySide6 ^
    --include-module=pygame.midi ^
    --follow-imports ^
    --jobs=4 ^
    --company-name="dumafu" ^
    --product-name="Advanced_Music_Converter" ^
    --file-version="3.1.2.0" ^
    --product-version=3.1.2.0 ^
    --file-description="Advanced_Music_Converter" ^
    --copyright="Copyright ©  2026 dumafu" ^
    --trademarks="dumafu" ^
    --output-dir=build_output ^
    Advanced_Music_Converter.py