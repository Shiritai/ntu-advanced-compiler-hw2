import datetime
from time import sleep
from logger import DEBUG, ERROR, INFO, WARN, LogType, Logger


def test():
    def test_fmt(stamp_fmt: str):
        l = Logger(use_stamp=stamp_fmt)
        l.debug("Meow")
        l.info("Meow")
        l.warn("Meow")
        l.error("Meow")
        for m in l._cache:
            test_str = " ".join(m.to_logfile(use_stamp=stamp_fmt).split(" ")[:-2])
            golden = m.stamp.strftime(stamp_fmt)
            assert datetime.datetime.strptime(test_str, stamp_fmt) == datetime.datetime.strptime(golden, stamp_fmt), "bad time stamp formatting"
        l.clear()
    
    def test_level_interval(level: LogType, exp_cnt: int):
        l = Logger(level)
        interval = 0.05
        l.debug("Debug Meow")
        sleep(interval)
        l.info("Info Meow")
        sleep(interval)
        l.warn("Warn Meow")
        sleep(interval)
        l.error("Error Meow")
        assert len(l._cache) == exp_cnt, \
            f"Invalid logger level system on level {level.tp}"
        m = l._cache[0]
        for _m in l._cache[1:]:
            diff = (_m.stamp - m.stamp).total_seconds()
            assert diff >= interval, f"Invalid time stamp interval ({diff})"
            m = _m
        l.clear() # to avoid showing log on deconstruction

    test_level_interval(DEBUG, 4)
    test_level_interval(INFO, 3)
    test_level_interval(WARN, 2)
    test_level_interval(ERROR, 1)
    test_fmt("%m/%d/%Y %I:%M:%S %p")
    test_fmt("%I:%M:%S %p")
    test_fmt("%I:%M:%S")
    test_fmt("%m/%d/%Y")

    assert DEBUG.lv < INFO.lv < WARN.lv < ERROR.lv, "Invalid log level value"

    logger = Logger(DEBUG, "OnWholeMsg")
    logger.debug(f"{type(logger).__name__} self test ends successfully")
    
if __name__ == '__main__':
    test()
