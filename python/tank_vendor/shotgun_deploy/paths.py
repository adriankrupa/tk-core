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
import datetime

from .. import shotgun_base


def get_bundle_cache_root():
    """
    Returns the cache location for the global bundle cache.
    Ensures that this folder exists.

    :returns: path on disk
    """
    bundle_cache_root = os.path.join(shotgun_base.get_cache_root(), "bundle_cache")
    shotgun_base.ensure_folder_exists(bundle_cache_root)
    return bundle_cache_root


def get_configuration_cache_root(site_url, project_id, pipeline_configuration_id):
    """
    Calculates the location of a cached configuration.
    Ensures that this folder exists.

    :param project_id: The shotgun id of the project to store caches for
    :param pipeline_configuration_id: The shotgun pipeline config id to store caches for
    :returns: path on disk
    """
    config_cache_root = os.path.join(
            shotgun_base.get_pipeline_config_cache_root(
                    site_url,
                    project_id,
                    pipeline_configuration_id),
            "config"
    )
    shotgun_base.ensure_folder_exists(config_cache_root)

    return config_cache_root

def get_configuration_backup(site_url, project_id, pipeline_configuration_id):
    """
    Calculates the location of a cached configuration backup.
    Ensures that this folder exists.

    :param project_id: The shotgun id of the project to store caches for
    :param pipeline_configuration_id: The shotgun pipeline config id to store caches for
    :returns: path on disk
    """

    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    config_cache_root = os.path.join(
            shotgun_base.get_pipeline_config_cache_root(
                    site_url,
                    project_id,
                    pipeline_configuration_id),
            "config.bak",
            date_str
    )
    shotgun_base.ensure_folder_exists(config_cache_root)

    return config_cache_root
