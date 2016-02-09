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
import re
import uuid
import tempfile

from ..zipfilehelper import unzip_file
from .base import IODescriptorBase

from .. import constants, util

from ..errors import ShotgunDeployError
from ...shotgun_base import ensure_folder_exists

log = util.get_shotgun_deploy_logger()

class IODescriptorUploadedConfig(IODescriptorBase):
    """
    Represents a pipeline configuration configuration attachment.

    This descriptor operates on pipeline configuration entities which have
    an attachment field containing an uploaded config zip file. Other
    configurations will not be supported.

    Note that it only makes sense to use this descriptor in conjunction with
    bundle type configuration

    {type: shotgun_uploaded_configuration, project_id: 123, name: primary, attachment_id: 456}
    """

    def __init__(self, bundle_cache_root, location_dict, sg_connection):
        """
        Constructor

        :param bundle_cache_root: Location on disk where items are cached
        :param location_dict: Location dictionary describing the bundle
        :param sg_connection: Shotgun connection to associated site
        :return: Descriptor instance
        """
        super(IODescriptorUploadedConfig, self).__init__(bundle_cache_root, location_dict)

        self._sg_connection = sg_connection
        self._name = location_dict.get("name")
        self._project_id = location_dict.get("project_id")
        self._attachment_id = location_dict.get("attachment_id")

        if self._name is None or self._project_id is None:
            raise ShotgunDeployError("Descriptor is not valid: %s" % str(location_dict))


    def get_system_name(self):
        """
        Returns a short name, suitable for use in configuration files
        and for folders on disk.

        In this case, this corresponds to the name of the pipeline configuration,
        usually 'primary'. Note that the value is sanitized for filesystem use.
        """
        return util.create_valid_filename("p%s_%s" % (self._project_id, self._name))

    def get_version(self):
        """
        Returns the version number string for this item.

        In this case, this is the shotgun attachment id that is linked with the
        """
        return "v%s" % self._attachment_id

    def get_path(self):
        """
        returns the path to the folder where this item resides
        """
        return self._get_local_location("sg_pc", self.get_system_name(), self.get_version())

    def download_local(self):
        """
        Retrieves this version to local repo.
        Will exit early if app already exists local.
        """
        if self.exists_local():
            # nothing to do!
            return

        target = self.get_path()
        ensure_folder_exists(target)

        # and now for the download.
        # @todo: progress feedback here - when the SG api supports it!
        # sometimes people report that this download fails (because of flaky connections etc)
        try:
            bundle_content = self._sg_connection.download_attachment(self._attachment_id)
        except Exception, e:
            # retry once
            log.warning("Download of attachment failed, retrying once. Error reported: %s" % e)
            bundle_content = self._sg_connection.download_attachment(self._attachment_id)

        zip_tmp = os.path.join(tempfile.gettempdir(), "%s_tank.zip" % uuid.uuid4().hex)
        fh = open(zip_tmp, "wb")
        fh.write(bundle_content)
        fh.close()

        # unzip core zip file to app target location
        unzip_file(zip_tmp, target)


    #############################################################################
    # searching for other versions

    def get_latest_version(self, constraint_pattern=None):
        """
        Returns a descriptor object that represents the latest version.

        This method is useful if you know the name of an app (after browsing in the
        app store for example) and want to get a formal "handle" to it.

        :param constraint_pattern: If this is specified, the query will be constrained
               by the given pattern. Version patterns are on the following forms:

                - v0.1.2, v0.12.3.2, v0.1.3beta - a specific version
                - v0.12.x - get the highest v0.12 version
                - v1.x.x - get the highest v1 version

        :returns: descriptor object
        """
        if constraint_pattern:
            raise ShotgunDeployError("%s does not support version constraint patterns." % constraint_pattern)

        log.debug("Finding latest version of %s..." % self)

        # in the case of a pipeline configuration, simply fetch the current pipeline configuration attachment
        # and build a descriptor based on that

        project_entity = None if self._project_id is None else {"type": "Project", "id": self._project_id}

        pc = self._sg_connection.find_one(
            constants.PIPELINE_CONFIGURATION_ENTITY,
            [["project", "is", project_entity],
             ["code", "is", self._name]],
            [constants.SHOTGUN_PIPELINECONFIG_ATTACHMENT_FIELD]
        )

        # attachment field is on the following form in the case a file has been
        # uploaded:
        #  {'name': 'v1.2.3.zip',
        #  'url': 'https://sg-media-usor-01.s3.amazonaws.com/...',
        #  'content_type': 'application/zip',
        #  'type': 'Attachment',
        #  'id': 139,
        #  'link_type': 'upload'}

        if pc is None:
            raise ShotgunDeployError("Cannot find a pipeline configuration named '%s'!" % self._name)

        if pc[constants.SHOTGUN_PIPELINECONFIG_ATTACHMENT_FIELD].get("link_type") != "upload":
            raise ShotgunDeployError("Latest version of pipeline configuration is not an uploaded file: %s" % pc)

        attachment_id = pc[constants.SHOTGUN_PIPELINECONFIG_ATTACHMENT_FIELD]["id"]

        # make a location dict
        location_dict = {"type": "shotgun_uploaded_configuration",
                         "name": self._name,
                         "project_id": self._project_id,
                         "attachment_id": attachment_id}

        # and return a descriptor instance
        desc = IODescriptorUploadedConfig(self._bundle_cache_root, location_dict, self._sg_connection)
        log.debug("Latest version resolved to %s" % desc)
        return desc




