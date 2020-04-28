# -*- coding:utf-8 -*-

import os
import logging

try:
    import mutils
    import mutils.gui
    import maya.cmds
except ImportError as error:
    print(error)

from studiolibrarymaya import baseitem
from studiolibrarymaya import mayafileitem

logger = logging.getLogger(__name__)

def save(path, *args, **kwargs):
    """Convenience function for saving an ModelItem."""
    ModelItem(path).save(*args, **kwargs)


def load(path, *args, **kwargs):
    """Convenience function for loading an ModelItem."""
    ModelItem(path).load(*args, **kwargs)


class ModelItem(mayafileitem.MayaFileItem):
    
    NAME              = "Model"
    TYPE              = NAME
    EXTENSION         = ".model"
    ICON_PATH         = os.path.join(os.path.dirname(__file__), "icons", "model.png")
    TRANSFER_CLASS    = mutils.Model
    TRANSFER_BASENAME = "model.json"

    def __init__(self, *args, **kwargs):
        """
        Create a new instance of the pose item from the given path.

        :type path: str
        :type args: list
        :type kwargs: dict
        """
        super(ModelItem, self).__init__(*args, **kwargs)
