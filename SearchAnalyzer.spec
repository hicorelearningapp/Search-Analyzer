# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('api', 'api'), ('services', 'services'), ('sources', 'sources'), ('utils', 'utils'), ('config.py', '.'), ('app_state.py', '.'), ('llm_summarizer.py', '.'), ('document_system.py', '.'), ('docx_generator.py', '.'), ('requirements.txt', '.')],
    hiddenimports=['fastapi', 'uvicorn', 'PyQt5', 'sentence_transformers', 'transformers', 'torch', 'python_dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SearchAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
