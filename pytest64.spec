# -*- coding: utf-8 -*-
# -*- mode: python -*-
# PythonExeサンプル 64bit版

block_cipher = None


a = Analysis(['src\\executor.py'],
             pathex=[],
             binaries=[],
             datas=[],
             # 隠蔽されたライブラリインポート
             hiddenimports=['wx._adv', 'wx._html', 'pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             # 除外するライブラリ
             excludes=['mkl','libopenblas'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          # アプリ名
          name='PythonExeSample.exe',
          # exeにする際のデバッグログ表示有無
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          # コンソールの表示有無
          console=False )
