# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

from .base import IODescriptorBase
from ..errors import ShotgunDeployError

class IODescriptorPath(IODescriptorBase):
    """
    Represents a local item on disk. This item is never downloaded
    into the local storage, you interact with it directly::

        {"type": "path", "path": "/path/to/app"}

    Optional parameters are possible::

        {"type": "path", "path": "/path/to/app", "name": "my-app"}

        {"type": "path",
         "linux_path": "/path/to/app",
         "windows_path": "d:\foo\bar",
         "mac_path": "/path/to/app" }

    String urls are on the following form::

        sgtk:path:[name]:local_path
        sgtk:path3:[name]:win_path:linux_path:mac_path

        sgtk:path:my-app:/tmp/foo/bar
        sgtk:path3::c%3A%0Coo%08ar:/tmp/foo/bar:

    Name is optional and if not specified will be determined based on folder path.
    If name is not specified and path is /tmp/foo/bar, the name will set to 'bar'
    """
    
    def __init__(self, bundle_cache_root, location_dict):
        """
        Constructor

        :param bundle_cache_root: Location on disk where items are cached
        :param location_dict: Location dictionary describing the bundle
        :return: Descriptor instance
        """

        super(IODescriptorPath, self).__init__(bundle_cache_root, location_dict)

        self._validate_locator(
            location_dict,
            required=["type"],
            optional=["name", "version", "linux_path", "mac_path", "path", "windows_path"]
        )

        # platform specific location support
        platform_key = {
            "linux2": "linux_path",
            "darwin": "mac_path",
            "win32": "windows_path"}[sys.platform]

        if "path" in location_dict:
            # first look for 'path' key
            self._path = location_dict["path"]
        elif platform_key in location_dict:
            # if not defined, look for os specific key
            self._path = location_dict[platform_key]
        else:
            raise ShotgunDeployError(
                "Invalid descriptor! Could not find a path or a %s entry in the "
                "location dict %s." % (platform_key, location_dict)
            )

        # lastly, resolve environment variables
        self._path = os.path.expandvars(self._path)
        
        # and normalise:
        self._path = os.path.normpath(self._path)
        
        # if there is a name defined in the location dict then lets use
        # this, otherwise we'll fall back to the folder name:
        self._name = location_dict.get("name")
        if not self._name:
            # fall back to the folder name
            bn = os.path.basename(self._path)
            self._name, _ = os.path.splitext(bn)

    def __repr__(self):
        """
        Low level string representation
        """
        class_name = self.__class__.__name__
        return "<%s %s>" % (class_name, self._path)

    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk, e.g. 'tk-maya'
        """
        return self._name

    def get_version(self):
        """
        Returns the version number string for this item
        """
        # version number does not make sense for this type of item
        # so a fixed string is returned
        return "v0.0.0"

    def get_path(self):
        """
        returns the path to the folder where this item resides
        """
        return self._path

    def get_platform_path(self, platform):
        """
        Returns the path to the descriptor on the given platform.
        If the location is not known, None is returned.

        The call ``get_platform_path(sys.platform)`` is equivalent to ``get_path()``

        :param platform: sys.platform-style operating system string, e.g.
                         'win32', 'linux2', 'darwin'
        :returns: Path to the given platform or None if not known.
        """
        if platform == sys.platform:
            # current os
            return self.get_path()

        else:
            platform_key = {
                "linux2": "linux_path",
                "darwin": "mac_path",
                "win32": "windows_path"}[platform]
            if platform_key in self.get_location():
                return self.get_location()[platform_key]
            else:
                return None

    def download_local(self):
        """
        Retrieves this version to local repo
        """
        # do nothing!

    def is_immutable(self):
        """
        Returns true if this items content never changes
        """
        return False

    def get_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: descriptor object
        """
        # we are always the latest version :)
        return self


