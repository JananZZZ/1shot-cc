# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/templates', 'app/templates'),
        ('static', 'static'),
        ('tutorials', 'tutorials'),
    ],
    hiddenimports=[
        # Flask & Jinja2
        'flask',
        'jinja2',

        # App core
        'app',
        'app.config',

        # Routes
        'app.routes',
        'app.routes.api_system',
        'app.routes.api_install',
        'app.routes.api_config',
        'app.routes.api_tutorial',

        # Services — detectors
        'app.services',
        'app.services.detector',

        # Services — installers
        'app.services.node_installer',
        'app.services.git_installer',
        'app.services.claude_installer',
        'app.services.ccswitch_installer',
        'app.services.colorcc_installer',

        # Services — utilities
        'app.services.config_writer',
        'app.services.error_resolver',
        'app.services.launcher',
        'app.services.proxy_helper',
        'app.services.system_checker',
        'app.services.uninstaller',
        'app.services.colorcc_installer',

        # Utils
        'app.utils',
        'app.utils.downloader',
        'app.utils.elevation',
        'app.utils.logger',
        'app.utils.path_helper',
        'app.utils.registry_reader',
        'app.utils.startup_checker',
        'app.utils.subprocess_runner',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'unittest', 'pydoc'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='1shot-CC',
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
    icon='static/img/logo.png' if False else None,
)
