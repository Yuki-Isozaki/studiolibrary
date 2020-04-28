# -*- coding:utf-8 -*-

import os
import logging

import mutils

try:
    import maya.cmds
except ImportError:
    import traceback
    traceback.print_exc()


__all__ = ["MayaFile", "saveMayaFile", "loadMayaFile"]

logger = logging.getLogger(__name__)

_mayafile_ = None


def saveMayaFile(path, objects, fileType, metadata=None, **kwargs):
    mayafile = mutils.MayaFile.fromObjects(objects)

    if metadata:
        mayafile.updateMetadata(metadata)

    logger.debug("Save MayaFile:{0} Format:{1}".format(path, fileType))
    mayafile.save(path, fileType, **kwargs)

    return mayafile


def loadMayaFile(path, *args, **kwargs):
    global _mayafile_

    if not _mayafile_ or _mayafile_.path() != path:
        _mayafile_ = MayaFile.fromPath(path)

    _mayafile_.load(*args, **kwargs)

    return _mayafile_


class MayaFile(mutils.TransferObject):

    DEFAULT_FILE_FORMAT = "mayaBinary"
    FILE_FORMATS = {
            "mayaAscii"  : ".ma",
            "mayaBinary" : ".mb",
        }
    DEFAULT_GROUPING_OPTION = True
    DEFAULT_NAMESPACE_OPTION = True

    def __init__(self):
        mutils.TransferObject.__init__(self)
        self.scene_attrs = []

    def createObjectData(self, name):
        """
        Create the object data for the given object name.

        :type name: str
        :rtype: dict
        """
        attrs = self.scene_attrs
        attrs = list(set(attrs))
        attrs = [mutils.Attribute(name, attr) for attr in attrs]

        data = {"attrs": self.attrs(name)}

        for attr in attrs:
            if attr.isValid():
                if attr.value() is None:
                    msg = "Cannot save the attribute %s with value None."
                    logger.warning(msg, attr.fullname())
                else:
                    data["attrs"][attr.attr()] = {
                         "type"  : attr.type(),
                         "value" : attr.value()
                    }

        return data

    def select(self, objects=None, namespaces=None, **kwargs):
        """
        Select the objects contained in the model file.

        :type objects: list[str] or None
        :type namespaces: list[str] or None
        :rtype: None
        """
        selectionSet = mutils.SelectionSet.fromPath(self.path())
        selectionSet.load(objects=objects, namespaces=namespaces, **kwargs)


    def attrs(self, name):
        """
        Return the attribute for the given name.

        :type name: str
        :rtype: dict
        """
        return self.object(name).get("attrs", {})

    def attr(self, name, attr):
        """
        Return the attribute data for the given name and attribute.

        :type name: str
        :type attr: str
        :rtype: dict
        """
        return self.attrs(name).get(attr, {})

    def attrType(self, name, attr):
        """
        Return the attribute type for the given name and attribute.

        :type name: str
        :type attr: str
        :rtype: str
        """
        return self.attr(name, attr).get("type", None)

    def attrValue(self, name, attr):
        """
        Return the attribute value for the given name and attribute.

        :type name: str
        :type attr: str
        :rtype: str | int | float
        """
        return self.attr(name, attr).get("value", None)


    @mutils.timing
    def load(self, **kwargs):
        """
        Load the scene.
        """
        logger.debug("Loading Args:{0} ".format(kwargs))

        mayafilename     = kwargs.get("filename")
        objects          = kwargs.get("objects")
        loadtype         = kwargs.get("loadtype")
        grouping         = kwargs.get("grouping", self.DEFAULT_GROUPING_OPTION)
        usenamespace     = kwargs.get("namespace", self.DEFAULT_NAMESPACE_OPTION)

        options = {}
        options["op"]  = "v=0;"

        #FileType
        filetype = ""
        filepath = os.path.abspath(os.path.join(os.path.dirname(self.path()), mayafilename))
        if mayafilename.lower().endswith(".ma"):
            filetype = "mayaAscii"
        elif mayafilename.lower().endswith(".mb"):
            filetype = "mayaBinary"
        options["typ"] = filetype

        #Import or Reference
        if loadtype.lower() == "import":
            options["i"]  = True
            logger.info("Imoort scene: %s" % filepath)
        elif loadtype.lower() == "reference":
            options["r"]  = True
            logger.info("Reference scene: %s" % filepath)
        else:
            raise ValueError("loadtype : {} is not defined".format(loadtype))

        #NameSpace
        namespace =""
        namespace_ptn = "{0}{1:03}"
        idx = 0
        while True:
            namespace = namespace_ptn.format(mayafilename.split(".")[0], idx)
            if not maya.cmds.namespace(exists=namespace):
                break
            idx += 1
        if usenamespace:
            options["namespace"]  = namespace

        #Grouping
        options["groupReference"] = False
        if grouping:
            options["groupReference"] = True
            options["groupName"] = namespace + "_grp"
 
        logger.debug("Loading Options:{0} ".format(options))
        maya.cmds.file(filepath, **options )
        maya.cmds.setFocus("MayaWindow")



    @mutils.showWaitCursor
    def save(self, path, fileType="", **kwargs):
        logger.info("Saving MayaFile: %s" % path)

        objects = self.objects().keys()
        fileType = fileType or MayaFile.DEFAULT_FILE_FORMAT
        if fileType not in MayaFile.FILE_FORMATS:
            raise ValueError("{0} is not supported format.".format(fileType))

        maya.cmds.select(clear=True)
        maya.cmds.select(objects)

        basename = os.path.basename(os.path.dirname(path)).split(".")[0]
        fileName = basename + MayaFile.FILE_FORMATS.get(fileType)
        mayaPath = os.path.join(os.path.dirname(path), fileName)

        self.setMetadata("mayafilename", fileName)
        self.setMetadata("fileType", fileType)

        logger.info("Saving mayafile: %s" % mayaPath)

        maya.cmds.file(mayaPath, force=True, options='v=0', type=fileType, uiConfiguration=False, exportSelected=True)

        super(MayaFile, self).save(path)

        logger.info("Saved MayaFile: %s" % path)