# -*- coding: utf-8 -*-
#

import wx
from utils.MLogger import MLogger # noqa

logger = MLogger(__name__)


class ConsoleCtrl(wx.TextCtrl):

    def __init__(self, parent):
        # 複数行可、読み取り専用、枠線ナシ、縦スクロールあり、横スクロールあり、キーイベント取得あり
        super().__init__(parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(-1, -1), \
                         wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE | wx.HSCROLL | wx.VSCROLL | wx.WANTS_CHARS)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        # キーボードイベントバインド
        self.Bind(wx.EVT_CHAR, lambda event: self.on_select_all(event, self.console_ctrl))

    # コンソール部分の出力処理【Point.07】        
    def write(self, text):
        try:
            wx.CallAfter(self.AppendText, text)
        except: # noqa
            pass

    # コンソール部分の全選択処理【Point.08】
    def on_select_all(event, target_ctrl):
        keyInput = event.GetKeyCode()
        if keyInput == 1:  # 1 stands for 'ctrl+a'
            target_ctrl.SelectAll()
        event.Skip()
