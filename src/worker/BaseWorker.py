# -*- coding: utf-8 -*-
#
import wx
import wx.xrc
from abc import ABCMeta, abstractmethod
from threading import Thread
from functools import wraps
import time
import threading

from utils.MLogger import MLogger # noqa

logger = MLogger(__name__)


# https://wiki.wxpython.org/LongRunningTasks
# https://teratail.com/questions/158458
# http://nobunaga.hatenablog.jp/entry/2016/06/03/204450
class BaseWorker(metaclass=ABCMeta):

    """Worker Thread Class."""
    def __init__(self, frame, result_event):
        """Init Worker Thread Class."""
        # 親GUI
        self.frame = frame
        # 経過時間
        self.elapsed_time = 0
        # スレッドが終わった後の呼び出しイベント
        self.result_event = result_event
        # 進捗ゲージ
        self.gauge_ctrl = frame.gauge_ctrl
        # 処理成功可否
        self.result = True
        # 停止命令有無
        self.is_killed = False

    # スレッド開始
    def start(self):
        self.run()

    # スレッド停止
    def stop(self):
        # 中断FLGをONにする
        self.is_killed = True

    def run(self):
        # スレッド実行
        self.thread_event()

        # 後処理実行
        self.post_event()
    
    def post_event(self):
        wx.PostEvent(self.frame, self.result_event(result=self.result))
    
    @abstractmethod
    def thread_event(self):
        pass


# https://doloopwhile.hatenablog.com/entry/20090627/1275175850
class SimpleThread(Thread):
    """ 呼び出し可能オブジェクト（関数など）を実行するだけのスレッド """
    def __init__(self, base_worker, acallable):
        # 別スレッド内の処理
        self.base_worker = base_worker
        # 関数デコレータ内で動かすメソッド
        self.acallable = acallable
        # 関数デコレータの結果
        self._result = None
        # 中断FLG=OFFの状態で初期化する
        super(SimpleThread, self).__init__(name="simple_thread", kwargs={"is_killed": False})
    
    def run(self):
        self._result = self.acallable(self.base_worker)
    
    def result(self):
        return self._result


def task_takes_time(acallable):
    """
    関数デコレータ【Point.10】
    acallable本来の処理は別スレッドで実行しながら、
    ウィンドウを更新するwx.YieldIfNeededを呼び出し続けるようにする
    """
    @wraps(acallable)
    def f(base_worker):
        t = SimpleThread(base_worker, acallable)
        # デーモンで、親が死んだら子も殺す
        t.daemon = True
        t.start()
        # スレッドが生きている間中、ウィンドウ描画を更新し続ける
        while t.is_alive():
            # 進捗ゲージをクルクル回す
            base_worker.gauge_ctrl.Pulse()
            # 必要ならばウィンドウを更新する
            wx.YieldIfNeeded()
            # 少しだけ待機
            time.sleep(0.01)

            if base_worker.is_killed:
                # 【Point.23】呼び出し元から停止命令が出ている場合、自分(GUI)以外の全部のスレッドに終了命令
                for th in threading.enumerate():
                    if th.ident != threading.current_thread().ident and "_kwargs" in dir(th):
                        th._kwargs["is_killed"] = True
                break
        
        return t.result()
    return f

