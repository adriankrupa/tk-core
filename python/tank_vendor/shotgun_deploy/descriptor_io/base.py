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
from .. import constants
from ... import yaml
from ..errors import ShotgunDeployError

class IODescriptorBase(object):
    """
    An app descriptor describes a particular version of an app, engine or core component.
    It also knows how to access metadata such as documentation, descriptions etc.

    Several AppDescriptor classes exists, all deriving from this base class, and the
    factory method descriptor_factory() manufactures the correct descriptor object
    based on a location dict, that is found inside of the environment config.

    Different App Descriptor implementations typically handle different source control
    systems: There may be an app descriptor which knows how to communicate with the
    Tank App store and one which knows how to handle the local file system.
    """

    _instances = dict()

    def __new__(cls, bundle_cache_root, location_dict, *args, **kwargs):
        """
        Handles caching of descriptors.

        Executed prior to __init__ being executed.

        Since all our normal descriptors are immutable - they represent a specific,
        read only and cached version of an app, engine or framework on disk, we can
        also cache their wrapper objects.

        :param bundle_cache_root: Root location for bundle cache
        :param location_dict: Location dictionary describing the bundle
        :return: Descriptor instance
        """
        instance_cache = cls._instances

        # The cache is keyed based on the location dict and the bundle install root
        cache_key = (bundle_cache_root, str(location_dict))

        # Instantiate and cache if we need to, otherwise just return what we
        # already have stored away.
        if cache_key not in instance_cache:
            # If the bundle install path isn't in the cache, then we are
            # starting fresh. Otherwise, check to see if the app (by name)
            # is cached, and if not initialize its specific cache. After
            # that we instantiate and store by version.
            instance_cache[cache_key] = super(IODescriptorBase, cls).__new__(
                cls,
                bundle_cache_root,
                location_dict,
                *args,
                **kwargs
            )

        return instance_cache[cache_key]

    def __init__(self, bundle_cache_root, location_dict):
        """
        Constructor

        :param bundle_cache_root: Root location for bundle cache storage
        :param location_dict: dictionary describing the location
        """
        self._bundle_cache_root = bundle_cache_root
        self._location_dict = location_dict
        self.__manifest_data = None

    def __repr__(self):
        class_name = self.__class__.__name__
        return "<%s %s %s>" % (class_name, self.get_system_name(), self.get_version())

    def _get_local_location(self, descriptor_name, name, version):
        """
        Calculate the local location for an item. This is a convenience method
        that can be used by implementing classes if they want to stash the code
        payload in a standardized location in the file system.
        """
        # examples:
        # /studio/tank/install/app_store/tk-nuke/v0.2.3
        # /studio/tank/install/app_store/NAME/VERSION
        return os.path.join(self._bundle_cache_root, descriptor_name, name, version)

    def get_manifest(self):
        """
        Returns the info.yml metadata associated with this descriptor.
        Note that this call involves deep introspection; in order to
        access the metadata we normally need to have the code content
        local, so this method may trigger a remote code fetch if necessary.
        """
        if self.__manifest_data is None:
            # make sure payload exists locally
            if not self.exists_local():
                # @todo - at this point add to a metadata cache for performance
                # note - cannot cache dev descriptors - these do not have an immutal info.yml

                self.download_local()

            # get the metadata
            bundle_root = self.get_path()
            file_path = os.path.join(bundle_root, constants.BUNDLE_METADATA_FILE)

            if not os.path.exists(file_path):
                raise ShotgunDeployError("Toolkit metadata file '%s' missing." % file_path)

            try:
                file_data = open(file_path)
                try:
                    metadata = yaml.load(file_data)
                finally:
                    file_data.close()
            except Exception, exp:
                raise ShotgunDeployError("Cannot load metadata file '%s'. Error: %s" % (file_path, exp))

            # cache it
            self.__manifest_data = metadata

        return self.__manifest_data


    def get_location(self):
        """
        Returns the location dict associated with this descriptor
        """
        return self._location_dict

    def get_deprecation_status(self):
        """
        Returns (is_deprecated (bool), message (str)) to indicate if this item is deprecated.
        """
        # only some descriptors handle this. Default is to not support deprecation, e.g.
        # always return that things are active.
        return False, ""


    ###############################################################################################
    # stuff typically implemented by deriving classes
    
    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk
        """
        raise NotImplementedError
    
    def get_version(self):
        """
        Returns the version number string for this item.
        """
        raise NotImplementedError    
    
    def get_path(self):
        """
        returns the path to the folder where this item resides
        """
        raise NotImplementedError
        
    def get_changelog(self):
        """
        Returns information about the changelog for this item.
        Returns a tuple: (changelog_summary, changelog_url). Values may be None
        to indicate that no changelog exists.
        """
        return (None, None)
    
    def exists_local(self):
        """
        Returns true if this item exists in a locally accessible form
        """
        raise NotImplementedError

    def is_developer(self):
        """
        Returns true if this item is intended for development purposes
        """
        return False

    def is_immutable(self):
        """
        Returns true if this items content never changes
        """
        return True

    def ensure_local(self):
        if not self.exists_local():
            self.download_local()

    def download_local(self):
        """
        Retrieves this version to local repo.
        """
        raise NotImplementedError

    def find_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.
        
        :param constraint_pattern: If this is specified, the query will be constrained
        by the given pattern. Version patterns are on the following forms:
        
            - v1.2.3 (means the descriptor returned will inevitably be same as self)
            - v1.2.x 
            - v1.x.x

        :returns: descriptor object
        """
        raise NotImplementedError

