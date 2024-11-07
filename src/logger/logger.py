import datetime
from io import TextIOWrapper
import sys
from typing import Literal, Optional, Union
import unittest

Coloring = Literal["Disable", "OnLogType", "OnWholeMsg"]

class LogType:
    """Leveled log type, log level is auto assigned
    by the ascending order of initialization,
    later assignation means the more severe it is.
    e.g. `DEBUG.lv = 0`, `ERROR.lv = 3`
    """
    lv = 0
    msg_fmt = "{:}[{:}] {:}"
    
    def __init__(self, tp: str, color_code: int):
        self.tp = tp
        self.color_fmt = f"\033[{color_code}" + "m{:}\033[0m"
        self.lv = LogType.lv
        LogType.lv += 1  # increase log level in each construction
    
    def to_string(self, msg: str, coloring: Coloring, stamp: str):
        ret: str
        if coloring == "OnLogType":
            ret = self.color_fmt.format(self.tp)
            ret = self.msg_fmt.format(stamp, ret, msg)
        elif coloring == "OnWholeMsg":
            ret = self.msg_fmt.format(stamp, self.tp, msg)
            ret = self.color_fmt.format(ret)
        elif coloring == "Disable":
            ret = self.msg_fmt.format(stamp, self.tp, msg)
        else:
            raise ValueError(f"Invalid coloring: {coloring}")
        return ret

DEBUG = LogType("DEBG", 92)
INFO = LogType("INFO", 94)
WARN = LogType("WARN", 93)
ERROR = LogType("ERRO", 91)

class LogMsg:
    def __init__(self, tp: LogType, msg: str):
        self.tp = tp
        self.msg = msg
        self.stamp = datetime.datetime.now()
    
    def stamp2str(self, use_stamp: Union[bool, str] = True):
        if use_stamp != False:
            if use_stamp == True:
                stamp_str = self.stamp.isoformat(sep=" ")
            else:
                stamp_str = self.stamp.strftime(use_stamp)
            stamp_str += " "  # add a space as string seperator
        else:
            stamp_str = ""
        return stamp_str
    
    def to_cli(self, coloring: Coloring, use_stamp: Union[bool, str] = True):
        return self.tp.to_string(self.msg, coloring, self.stamp2str(use_stamp))
    
    def to_logfile(self, use_stamp: Union[bool, str] = True):
        return self.tp.to_string(self.msg, "Disable", self.stamp2str(use_stamp))

class Logger:
    def __init__(self,
                 level: LogType = DEBUG,
                 coloring: Coloring = "OnLogType",
                 f: TextIOWrapper = None,
                 use_stamp: Union[bool, str] = True):
        """Logger to log message to strerr and optionally `f` IO stream

        Args:
            level (LogType, optional): debug level. Defaults to LogType.DEBUG.
            coloring (Coloring, optional): coloring on console. Defaults to "OnLogType".
            f (TextIOWrapper, optional): ***opened*** log file. Defaults to None.
                If given io is closed, no log message will be logged to such IO.
        """
        self._cache: list[LogMsg] = []
        self._coloring = coloring
        self._use_stamp = use_stamp
        self.f = f
        self.set_level(level)
    
    def set_level(self, level: LogType):
        self.lv = level.lv
    
    def debug(self, msg: str):
        if self.lv <= DEBUG.lv:
            self._cache.append(LogMsg(DEBUG, msg))
    
    def info(self, msg: str):
        if self.lv <= INFO.lv:
            self._cache.append(LogMsg(INFO, msg))
    
    def warn(self, msg: str | Exception):
        if self.lv <= WARN.lv:
            self._cache.append(LogMsg(WARN, msg))
    
    def error(self, err: str | Exception):
        if self.lv <= ERROR.lv:
            self._cache.append(LogMsg(ERROR, err))

    def clear(self):
        """Clean up all cached log messages.
        Log messages are cached if no `flush` is called
        """
        self._cache = []

    def flush(self):
        """Flush all cached logs to strerr and optionally `f` IO stream
        """
        if self.f is not None and not self.f.closed:
            for lm in self._cache:
                print(lm.to_logfile(), file=self.f)
                print(lm.to_cli(self._coloring, self._use_stamp), file=sys.stderr)
        else:
            for lm in self._cache:
                print(lm.to_cli(self._coloring, self._use_stamp), file=sys.stderr)
        self._cache = []

    def __del__(self):
        """On deconstruction, cacheed log messages
        will be flushed automatically
        """
        if len(self._cache) > 0:
            self.flush()

logger = Logger()
"""Global logger
"""

class LoggedTestCase(unittest.TestCase):
    """Unit test integration

    `LoggedTestCase` is equivalent to `unittest.TestCase`
    which will print log message using the global `Logger`
    """
    def run(self, result: Optional[unittest.TestResult]):
        fail_cnt, err_cnt = len(result.failures), len(result.errors)
        res = super().run(result)
        if len(res.errors) > err_cnt:
            logger.error(f"{type(self).__name__}::{self._testMethodName} error occurs: {res.errors[-1][1]}")
        elif len(res.failures) > fail_cnt:
            logger.error(f"{type(self).__name__}::{self._testMethodName} failed: {res.failures[-1][1]}")
        else:
            logger.info(f"{type(self).__name__}::{self._testMethodName} passed")
        return res
