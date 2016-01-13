# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import logging

# Instance of the properly configured sgtk logger
__logger_instance = None
# Instance of the logging handler that outputs for the current process.
__output_handler = None


def get_logger(name=None):
    """
    Retrieves the logger with the given name.

    :param name: Name of the logger under the sgtk logger to retrieve. Can be empty.

    :returns: A logger instance rooted under the sgtk logger. If name was empty, returns the
        sgtk logger.
    """
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
    """
    Sets the output handler for the current process on the sgtk logger.

    :param handler: logging.Handler derived instance that can write logs for the
        current process.
    """
    global __output_handler
    __output_handler = handler
    get_logger().addHandler(handler)


def get_output_handler():
    """
    Retrieves the output handler for the current process.

    :returns: The output handler for the current process.
    """
    global __output_handler
    return __output_handler
