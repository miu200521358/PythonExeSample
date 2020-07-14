# -*- coding: utf-8 -*-
#

import logging
from time import sleep
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from service.MOptions import MOptions
from utils.MException import MLogicException, MKilledException
from utils.MLogger import MLogger # noqa

logger = MLogger(__name__)


class LongLogicService():
    def __init__(self, options: MOptions):
        self.options = options

    def execute(self):
        logging.basicConfig(level=self.options.logging_level, format="%(message)s [%(module_name)s]")

        # 【Point.13】全体をtry-exceptで囲み、エラー内容を出力する
        try:
            # 普通にロジックを載せてもOK
            self.execute_inner(-1)
            
            logger.info("--------------")

            # 並列タスクで分散させてもOK
            futures = []
            # 【Point.14】並列タスクには名前を付けておく
            with ThreadPoolExecutor(thread_name_prefix="long_logic", max_workers=self.options.max_workers) as executor:
                for n in range(self.options.loop_cnt):
                    futures.append(executor.submit(self.execute_inner, n))

            #【Point.15】並列タスクは、一括発行後、終了を待つ
            concurrent.futures.wait(futures, timeout=None, return_when=concurrent.futures.FIRST_EXCEPTION)

            for f in futures:
                if not f.result():
                    return False

            logger.info("長いロジック処理終了", decoration=MLogger.DECORATION_BOX, title="ロジック終了")

            return True
        except MKilledException:
            # 中断オプションによる終了の場合、そのまま結果だけ返す
            return False
        except MLogicException as se:
            # データ不備エラー
            logger.error("処理が処理できないデータで終了しました。\n\n%s", se.message, decoration=MLogger.DECORATION_BOX)
            return False
        except Exception as e:
            # それ以外のエラー
            logger.critical("処理が意図せぬエラーで終了しました。", e, decoration=MLogger.DECORATION_BOX)
            return False
        finally:
            logging.shutdown()

    def execute_inner(self, n: int):
        for m in range(5):
            logger.info("n: %s - m: %s", n, m)
            sleep(1)
        
        return True
