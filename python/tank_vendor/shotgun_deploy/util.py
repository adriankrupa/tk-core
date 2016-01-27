# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

from distutils.version import LooseVersion
import os
from .errors import ShotgunDeployError
from ..shotgun_base import get_sgtk_logger

def get_shotgun_deploy_logger():
    """
    Returns a logger object suitable for the shotgun deploy module
    :return:
    """
    return get_sgtk_logger("deploy")

def execute_git_command(cmd):
    """
    Wrapper around git execution.
    
    Tries to execute a git command. 
    First probes to check if the git executable exists. Next 
    executes the given command. Any output generated by the command
    will not be captured but will get emitted to stdout/stderr.
    
    :raises: Will raise a TankError on failure
    :param cmd: git command to execute (e.g. 'clone foo.git')
    """
    # first probe to check that git exists in our PATH
    try:
        git_version_info = subprocess_check_output("git --version", shell=True)
    except:
        raise ShotgunDeployError(
            "Cannot execute the 'git' command. Please make sure that git is "
            "installed on your system and that the git executable has been added to the PATH."
        )
        
    status = os.system("git %s" % cmd)
    if status != 0:
        raise ShotgunDeployError(
            "Error executing git operation. The git command '%s' "
            "returned error code %s." % (cmd, status)
        )


################################################################################################
# py26 compatible subprocess.check_output call
# from http://stackoverflow.com/questions/2924310/whats-a-good-equivalent-to-pythons-subprocess-check-call-that-returns-the-cont

import subprocess

class SubprocessCalledProcessError(Exception):

    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)


def subprocess_check_output(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise SubprocessCalledProcessError(retcode, cmd, output=output)
    return output

