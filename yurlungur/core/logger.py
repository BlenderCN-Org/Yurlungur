# -*- coding: utf-8 -*-
import sys

try:
    from logging import (
        getLogger, Handler, INFO, WARNING, basicConfig
    )
    from pprint import pformat
    from yurlungur.core import env

except ImportError:
    Handler = object


class GuiLogHandler(Handler):
    def __init__(self, *args, **kwargs):
        super(GuiLogHandler, self).__init__(*args, **kwargs)

        if env.Maya():
            import maya.OpenMaya as om
            self.MGlobal = om.MGlobal

    def emit(self, record):
        from yurlungur.tool.meta import meta

        msg = self.format(record)
        if record.levelno > WARNING:
            if env.Maya():
                self.MGlobal.displayError(msg)
            elif env.Houdini():
                meta.ui.setStatusMessage(msg, severity=meta.severityType.Error)
            elif env.Unreal():
                meta.log_error(msg)
            elif env.Unity():
                meta.Debug.LogError(msg)
            elif env.Nuke():
                meta.error(msg)
            elif env.Max():
                meta.print_(msg, True, False)

        elif record.levelno > INFO:
            if env.Maya():
                self.MGlobal.displayWarning(msg)
            elif env.Houdini():
                meta.ui.setStatusMessage(msg, severity=meta.severityType.Warning)
            elif env.Unreal():
                meta.log_warning(msg)
            elif env.Unity():
                meta.Debug.LogWarning(msg)
            elif env.Nuke():
                meta.warning(msg)
            elif env.Max():
                meta.print_(msg, True, False)

        else:
            if env.Maya():
                self.MGlobal.displayInfo(msg)
            elif env.Houdini():
                meta.ui.setStatusMessage(msg, severity=meta.severityType.Message)
            elif env.Unreal():
                meta.log(msg)
            elif env.Unity():
                meta.Debug.Log(msg)
            elif env.Nuke():
                meta.debug(msg)
            elif env.Max():
                meta.print_(msg, False, True)


try:
    if env.Substance():
        import sd
        import sd.logger as slog

        logger = sd.getContext().getLogger()
        Warning = slog.LogLevel.Warning

    else:
        import yurlungur

        logger = getLogger(yurlungur.__name__)
        logger.setLevel(INFO)
        handler = GuiLogHandler()
        logger.addHandler(handler)
        basicConfig(level=INFO, stream=sys.stdout)
except:
    pass


def pprint(*msgs):
    logger.log(pformat(*msgs))
