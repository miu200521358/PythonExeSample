# -*- coding: utf-8 -*-
#

from time import sleep
from worker.LongLogicWorker import LongLogicWorker
from form.ConsoleCtrl import ConsoleCtrl
from utils.MLogger import MLogger

import os
import sys
import wx
import wx.lib.newevent

logger = MLogger(__name__)
TIMER_ID = wx.NewId()

(LongThreadEvent, EVT_LONG_THREAD) = wx.lib.newevent.NewEvent()

# メインGUI
class MainFrame(wx.Frame):

    def __init__(self, parent, version_name: str, logging_level: int):
        self.version_name = version_name
        self.logging_level = logging_level
        self.elapsed_time = 0
        self.worker = None

        # 初期化
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"c01 Long Logic {0}".format(self.version_name), \
                          pos=wx.DefaultPosition, size=wx.Size(600, 650), style=wx.DEFAULT_FRAME_STYLE)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # 処理回数
        self.loop_cnt_ctrl = wx.SpinCtrl(self, id=wx.ID_ANY, size=wx.Size(100, -1), value="2", min=1, max=999, initial=2)
        self.loop_cnt_ctrl.SetToolTip(u"処理回数")
        self.sizer.Add(self.loop_cnt_ctrl, 0, wx.ALL, 5)

        # 並列処理有無チェックボックス
        self.multi_process_ctrl = wx.CheckBox(self, id=wx.ID_ANY, label="並列処理を実行したい場合、チェックを入れて下さい")
        self.sizer.Add(self.multi_process_ctrl, 0, wx.ALL, 5)

        # ボタン用Sizer
        self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 実行ボタン
        self.exec_btn_ctrl = wx.Button(self, wx.ID_ANY, u"長いロジック処理開始", wx.DefaultPosition, wx.Size(200, 50), 0)
        # マウス左クリックイベントとのバインド　【Point.01】
        self.exec_btn_ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_exec_click)
        # マウス左ダブルクリックイベントとのバインド　【Point.03】
        self.exec_btn_ctrl.Bind(wx.EVT_LEFT_DCLICK, self.on_doubleclick)
        self.btn_sizer.Add(self.exec_btn_ctrl, 0, wx.ALIGN_CENTER, 5)

        # 中断ボタン
        self.kill_btn_ctrl = wx.Button(self, wx.ID_ANY, u"長いロジック処理中断", wx.DefaultPosition, wx.Size(200, 50), 0)
        # マウス左クリックイベントとのバインド
        self.kill_btn_ctrl.Bind(wx.EVT_LEFT_DOWN, self.on_kill_click)
        # マウス左ダブルクリックイベントとのバインド
        self.kill_btn_ctrl.Bind(wx.EVT_LEFT_DCLICK, self.on_doubleclick)
        # 初期状態は非活性
        self.kill_btn_ctrl.Disable()
        self.btn_sizer.Add(self.kill_btn_ctrl, 0, wx.ALIGN_CENTER, 5)

        self.sizer.Add(self.btn_sizer, 0, wx.ALIGN_CENTER | wx.SHAPED, 0)

        # コンソール【Point.06】
        self.console_ctrl = ConsoleCtrl(self)
        self.sizer.Add(self.console_ctrl, 1, wx.ALL | wx.EXPAND, 5)

        # print出力先はコンソール【Point.05】
        sys.stdout = self.console_ctrl

        # 進捗ゲージ
        self.gauge_ctrl = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
        self.gauge_ctrl.SetValue(0)
        self.sizer.Add(self.gauge_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # イベントバインド【Point.05】
        self.Bind(EVT_LONG_THREAD, self.on_exec_result)

        self.SetSizer(self.sizer)
        self.Layout()

        # 画面中央に表示する
        self.Centre(wx.BOTH)

    # ダブルクリック無効化処理
    def on_doubleclick(self, event: wx.Event):
        self.timer.Stop()
        logger.warning("ダブルクリックされました。", decoration=MLogger.DECORATION_BOX)
        event.Skip(False)
        return False

    # 実行1クリックした時の処理
    def on_exec_click(self, event: wx.Event):
        # タイマーで若干遅らせて起動する（ダブルクリックとのバッティング回避）【Point.04】
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.StartOnce(200)
        self.Bind(wx.EVT_TIMER, self.on_exec, id=TIMER_ID)

    # 中断1クリックした時の処理
    def on_kill_click(self, event: wx.Event):
        self.timer = wx.Timer(self, TIMER_ID)
        self.timer.StartOnce(200)
        self.Bind(wx.EVT_TIMER, self.on_kill, id=TIMER_ID)

    # 処理実行
    def on_exec(self, event: wx.Event):
        self.timer.Stop()

        if not self.worker:
            # コンソールクリア
            self.console_ctrl.Clear()
            # 実行ボタン無効化
            self.exec_btn_ctrl.Disable()
            # 中断ボタン有効化
            self.kill_btn_ctrl.Enable()

            # 別スレッドで実行【Point.09】
            self.worker = LongLogicWorker(self, LongThreadEvent, self.loop_cnt_ctrl.GetValue(), self.multi_process_ctrl.GetValue())
            self.worker.start()
            
        event.Skip(False)

    # 中断処理実行
    def on_kill(self, event: wx.Event):
        self.timer.Stop()

        if self.worker:
            # 停止状態でボタン押下時、停止
            self.worker.stop()

            logger.warning("長いロジック処理を中断します。", decoration=MLogger.DECORATION_BOX)

            # ワーカー終了
            self.worker = None
            # 実行ボタン有効化
            self.exec_btn_ctrl.Enable()
            # 中断ボタン無効化
            self.kill_btn_ctrl.Disable()
            # プログレス非表示
            self.gauge_ctrl.SetValue(0)

        event.Skip(False)
    
    # 長いロジックが終わった後の処理
    def on_exec_result(self, event: wx.Event):
        # 【Point.12】ロジック終了が明示的に分かるようにする
        self.sound_finish()
        # 実行ボタン有効化
        self.exec_btn_ctrl.Enable()
        # 中断ボタン無効化
        self.kill_btn_ctrl.Disable()

        if not event.result:
            event.Skip(False)
            return False
        
        self.elapsed_time += event.elapsed_time
        logger.info("\n処理時間: %s", self.show_worked_time())

        # ワーカー終了
        self.worker = None
        # プログレス非表示
        self.gauge_ctrl.SetValue(0)

    def sound_finish(self):
        # 終了音を鳴らす
        if os.name == "nt":
            # Windows
            try:
                import winsound
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            except Exception:
                pass

    def show_worked_time(self):
        # 経過秒数を時分秒に変換
        td_m, td_s = divmod(self.elapsed_time, 60)

        if td_m == 0:
            worked_time = "{0:02d}秒".format(int(td_s))
        else:
            worked_time = "{0:02d}分{1:02d}秒".format(int(td_m), int(td_s))

        return worked_time
    

