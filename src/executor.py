# -*- coding: utf-8 -*-
#

import wx
import argparse
import numpy as np
import multiprocessing

from form.MainFrame import MainFrame
from utils.MLogger import MLogger

VERSION_NAME = "ver1.00"

# 指数表記なし、有効小数点桁数6、30を超えると省略あり、一行の文字数200
np.set_printoptions(suppress=True, precision=6, threshold=30, linewidth=200)

# Windowsマルチプロセス対策
multiprocessing.freeze_support()


if __name__ == '__main__':
    # 引数解釈
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", default=20, type=int)
    args = parser.parse_args()
    
    # ロガー初期化
    MLogger.initialize(level=args.verbose, is_file=False)

    # GUI起動
    app = wx.App(False)
    frame = MainFrame(None, VERSION_NAME, args.verbose)
    frame.Show(True)
    app.MainLoop()

