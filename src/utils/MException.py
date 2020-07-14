# -*- coding: utf-8 -*-
#


class MLogicException(Exception):
    def __init__(self, message):
        self.message = message


class MParseException(MLogicException):
    def __init__(self, message):
        self.message = message


class MKilledException(MLogicException):
    def __init__(self):
        self.message = None

