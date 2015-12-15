import sys
import os
import logging
import datetime

__log_location = None


def get_logger(name=None):
    if not name:
        return logging.getLogger("sgtk")
    return logging.getLogger("sgtk.%s" % name)


def __get_log_root():
    """
    Returns an OS specific log location.

    :returns: Path to the OS specific log folder.
    """
    if sys.platform == "darwin":
        root = os.path.expanduser("~/Library/Logs/Shotgun")
    elif sys.platform == "win32":
        root = os.path.join(os.environ["APPDATA"], "Shotgun", "logs")
    elif sys.platform.startswith("linux"):
        root = os.path.expanduser("~/.shotgun/logs")
    return root


def install_file_handler(context, directory=None):
    global __log_location

    # If there is already a file handler installed, don't accept another one.
    if __log_location:
        logging.getLogger().warning("A file handler has already been installed Toolkit.")

    # Make sure the folder exists.
    log_root = directory or __get_log_root()
    if not os.path.exists(log_root):
        os.makedirs(log_root)

    __log_location = os.path.join(
        log_root,
        "%s_%s.log" % (context, datetime.datetime.now().strftime("%Y-%m-%d-%Hh%Mm%Ss%fms"))
    )

    # Create an handler and install it at the sgtk level.
    handler = logging.FileHandler(__log_location)
    formatter = logging.Formatter('%(asctime)s [%(name)s.%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    # Let the handlers decide how much stuff they want to log.
    get_logger().setLevel(logging.DEBUG)
    get_logger().addHandler(handler)


def get_log_file_location():
    return __log_location
