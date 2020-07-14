# -*- coding: utf-8 -*-
#

import os
import wx
import time
from worker.BaseWorker import BaseWorker, task_takes_time
from service.MOptions import MOptions
from service.LongLogicService import LongLogicService

class LongLogicWorker(BaseWorker):

    def __init__(self, frame: wx.Frame, result_event: wx.Event, loop_cnt: int, is_multi_process: bool):
        # 処理回数
        self.loop_cnt = loop_cnt
        # マルチプロセスで実行するか
        self.is_multi_process = is_multi_process

        super().__init__(frame, result_event)

    @task_takes_time
    def thread_event(self):
        start = time.time()

        # パラとかオプションとか詰め込み
        # max_workersの最大値は、Python3.8のデフォルト値に基づく
        options = MOptions(self.frame.version_name, self.frame.logging_level, self.loop_cnt, max_workers=(1 if not self.is_multi_process else min(32, os.cpu_count() + 4)))
        
        # ロジックサービス実行
        LongLogicService(options).execute()

        # 経過時間
        self.elapsed_time = time.time() - start

    def post_event(self):
        # ロジック処理が終わった後のイベントを呼び出して実行する【Point.11】
        wx.PostEvent(self.frame, self.result_event(result=self.result and not self.is_killed, elapsed_time=self.elapsed_time))
