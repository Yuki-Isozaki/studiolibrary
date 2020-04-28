# Copyright 2019 by Kurt Rathjen. All Rights Reserved.
#
# This library is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. This library is distributed in the
# hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.
"""
NOTE: Make sure you register this item in the config.
"""

import os
import logging

import maya.cmds

from studiolibrarymaya import baseitem
import mutils
from mutils import MayaFile

logger = logging.getLogger(__name__)

def save(path, *args, **kwargs):
    """Convenience function for saving an MayaFileItem."""
    MayaFileItem(path).save(*args, **kwargs)


def load(path, *args, **kwargs):
    """Convenience function for loading an MayaFileItem."""
    MayaFileItem(path).load(*args, **kwargs)

class MayaFileItem(baseitem.BaseItem):

    NAME              = "MayaFile"
    TYPE              = NAME
    EXTENSION         = ".mayafile"
    ICON_PATH         = os.path.join(os.path.dirname(__file__), "icons", "file.png")
    TRANSFER_CLASS    = mutils.MayaFile
    TRANSFER_BASENAME = "mayafile.json"

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of the pose item from the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        super(MayaFileItem, self).__init__(*args, **kwargs)

    def loadSchema(self, **kwargs):
        """
        Get the schema used for loading the example item.

        :rtype: list[dict]
        """
        schema = super(MayaFileItem, self).loadSchema()
      
        mayafile = mutils.MayaFile.fromPath(self.transferPath())
        mayafilename = mayafile.metadata().get("mayafilename", "")
        schema.insert(2, {"name": "mayafile", 
                          "value": mayafilename})
        revision = -1 #fstat.revision
        schema.insert(3, {"name": "revison", 
                          "value": "#{0}".format(revision) })

        #Remove Namespace Options
        schema = schema[:-3]

        schema.extend([
            {
                "name": "optionsGroup",
                "title": "Options",
                "type": "group",
                "order": 2,
            },
            {
                "name": "loadType",
                "title": "LoadType",
                "type": "radio",
                "value": "Reference",
                "items": ["Import", "Reference"],
                "persistent": True,
            },
            {
                "name": "grouping",
                "type": "bool",
                "default": mutils.MayaFile.DEFAULT_GROUPING_OPTION,
                "layout": "horizontal"
            },
            {
                "name": "namespace",
                "type": "bool",
                "default": mutils.MayaFile.DEFAULT_NAMESPACE_OPTION,
                "layout": "horizontal"
            },
        ])

        return schema

    def load(self, **kwargs):
        """
        Load the animation for the given objects and options.

        :type kwargs: dict
        """
        logger.info("Loading %s %s", self.path(), str(kwargs))
        kwargs.pop("objects")

        mayafile = mutils.MayaFile.fromPath(self.transferPath())

        mayafile.load(
            filename   = kwargs.pop("mayafile"),
            objects    = mayafile.objects().keys(),
            loadtype   = kwargs.pop("loadType"),
            grouping   = kwargs.pop("grouping"),
            namespace  = kwargs.pop("namespace"),
            **kwargs
        )

    def saveSchema(self):
        """
        Get the schema for saving an animation item.

        :rtype: list[dict]
        """
        return [
            {
                "name": "folder",
                "type": "path",
                "layout": "vertical",
                "visible": False,
            },
            {
                "name": "name",
                "type": "string",
                "layout": "vertical"
            },
            {
                "name": "fileType",
                "type": "enum",
                "layout": "vertical",
                "default": mutils.MayaFile.DEFAULT_FILE_FORMAT,
                "items": mutils.MayaFile.FILE_FORMATS.keys(),
                "persistent": True
            },
            {
                "name": "comment",
                "type": "text",
                "layout": "vertical"
            },
            {
                "name": "objects",
                "type": "objects",
                "label": {
                    "visible": True
                }
            },
        ]

    def save(self, **kwargs):
        """
        The save method is called with the user values from the save schema.

        :type kwargs: dict
        """
        logger.info("Saving %s %s", self.path(), kwargs)

        super(MayaFileItem, self).save(**kwargs)

        filetype = kwargs.pop("fileType")
        objects  = kwargs.pop("objects")

        mutils.saveMayaFile(
            path     = self.transferPath(),
            objects  = objects,
            fileType = filetype,
            metadata = {"description": kwargs.pop("comment", "")},
            **kwargs
        )