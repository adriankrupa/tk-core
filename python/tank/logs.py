import sys
import os
import logging
import datetime

__log_location = None
__logger_instance = None


def get_logger(name=None):
    global __logger_instance
    if not __logger_instance:
        logger_instance = logging.getLogger("sgtk")
        logger_instance.propagate = False
        __logger_instance = logger_instance

    if not name:
        return logging.getLogger("sgtk")
    return logging.getLogger("sgtk.%s" % name)
