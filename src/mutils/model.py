# -*- coding:utf-8 -*-

import os
import logging

import mutils

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()


__all__ = ["Model", "saveModel", "loadModel"]

logger = logging.getLogger(__name__)

_model_ = None


def saveModel(path, objects, fileType, metadata=None, **kwargs):
    model = mutils.MayaFile.fromObjects(objects)

    if metadata:
        model.updateMetadata(metadata)

    logger.debug("Save MayaFile:{0} Format:{1}".format(path, fileType))
    model.save(path, fileType, **kwargs)

    return model


def loadModel(path, *args, **kwargs):
    global _model_

    if not _model_ or _model_.path() != path:
        _model_ = Model.fromPath(path)

    _model_.load(*args, **kwargs)

    return _model_


class Model(mutils.MayaFile):

    def __init__(self):
        mutils.TransferObject.__init__(self)
