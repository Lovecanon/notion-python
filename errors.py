# -*- coding:utf-8 -*-
class Error(Exception):
    pass


class ApiKeyError(Error):
    """notion api key error"""
    pass


class ApiError(Error):
    """response status is not 200"""

    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return str(self.status)
        else:
            return "{} ({})".format(self.status, self.message)


class RequestError(Error):
    pass


class JsonDecodeError(ApiError):
    """json decode error"""
    pass


class ParameterError(Error):
    """request parameter error"""
    pass
