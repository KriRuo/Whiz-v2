# whiz.spec — PyInstaller build spec for Whiz Voice-to-Text
#
# Build with:  pyinstaller whiz.spec --clean --noconfirm
# Output:      dist\Whiz\Whiz.exe  (onedir bundle)
#
# onedir is used (not onefile) because ctranslate2 has many native DLLs that
# must live alongside the executable. onefile unpacks to a new temp dir on
# every launch, which is slow and blocked by some corporate AV policies.

import os
from pathlib import Path

block_cipher = None

# ---------------------------------------------------------------------------
# Data files — resources that must be accessible at runtime via _MEIPASS
# ---------------------------------------------------------------------------
datas = [
    ('assets', 'assets'),
    ('ui/styles/theme_dark.qss',  'ui/styles'),
    ('ui/styles/theme_light.qss', 'ui/styles'),
]

# Bundle local FFmpeg binaries if present
ffmpeg_exe = Path('ffmpeg/bin/ffmpeg.exe')
ffprobe_exe = Path('ffmpeg/bin/ffprobe.exe')
if ffmpeg_exe.exists():
    datas.append(('ffmpeg/bin/ffmpeg.exe', 'ffmpeg/bin'))
if ffprobe_exe.exists():
    datas.append(('ffmpeg/bin/ffprobe.exe', 'ffmpeg/bin'))

# ---------------------------------------------------------------------------
# Hidden imports — modules PyInstaller's static analysis misses
# ---------------------------------------------------------------------------
hidden_imports = [
    # Note: sip is handled automatically by PyInstaller's PyQt5 hook
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    # Audio / input
    'sounddevice',
    '_sounddevice_data',
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    'pyautogui',
    # Windows API (pywin32)
    'win32api',
    'win32con',
    'win32gui',
    'win32process',
    'pywintypes',
    # Transcription
    'faster_whisper',
    'ctranslate2',
    # Misc
    'psutil',
    'numpy',
]

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/pyi_rth_ctranslate2_first.py'],
    excludes=[
        # torch and friends — not needed (CPU path uses ctranslate2 directly)
        'torch', 'torchvision', 'torchaudio',
        # Other heavyweights never imported by Whiz
        'tensorflow', 'keras',
        'matplotlib', 'scipy',
        'PIL', 'Pillow',
        'IPython', 'jupyter',
        'pandas', 'sklearn',
        'tkinter',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # onedir: keep DLLs alongside exe
    name='Whiz',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/images/icons/app_icon_transparent.ico',
    manifest='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>''',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Whiz',
)
