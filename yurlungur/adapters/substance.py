# coding: utf-8
import sd
from sd.api.sdproperty import SDPropertyCategory

context = sd.getContext()
app = context.getSDApplication()
manager = app.getPackageMgr()

if getattr(app, "getUIMgr", False):
    graph = app.getUIMgr().getCurrentGraph()
    UndoGroup = sd.api.SDHistoryUtils.UndoGroup
    qt = app.getQtForPythonUIMgr()
else:
    graph = manager.getUserPackages()[0].getChildrenResources(True)[0]
