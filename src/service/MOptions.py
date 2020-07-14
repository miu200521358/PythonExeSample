# -*- coding: utf-8 -*-
#

class MOptions():

    def __init__(self, version_name: str, logging_level: int, loop_cnt: int, max_workers: int):
        self.version_name = version_name
        self.logging_level = logging_level
        self.loop_cnt = loop_cnt
        self.max_workers = max_workers
    


