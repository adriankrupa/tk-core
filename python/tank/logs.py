import logging

__log_location = None
__logger_instance = None

__output_handler = None


def get_logger(name=None):
    global __logger_instance
    if not __logger_instance:
        logger_instance = logging.getLogger("sgtk")
        logger_instance.propagate = False
        logger_instance.setLevel(logging.DEBUG)
        __logger_instance = logger_instance

    if not name:
        return logging.getLogger("sgtk")
    return logging.getLogger("sgtk.%s" % name)


def set_output_handler(handler):
    global __output_handler
    __output_handler = handler
    get_logger().addHandler(handler)


def get_output_handler():
    global __output_handler
    return __output_handler
