# -*- coding: utf-8 -*-
import sys

try:
    import time
    import traceback
    import functools
    import threading
    import contextlib
    import multiprocessing
except ImportError:
    pass

from yurlungur.tool.meta import meta
from yurlungur.core import env, logger

# assign UndoGroup
if env.Houdini():
    UndoGroup = meta.undos.group

if env.Unreal():
    UndoGroup = meta.ScopedEditorTransaction

if env.Max():
    UndoGroup = functools.partial(meta.undo, True)

if env.Nuke():
    UndoGroup = meta.Undo

if env.Substance():
    UndoGroup = meta.sd.UndoGroup


class UndoGroup(object):
    """
    undoGroup with script
.
    >>> import yurlungur
    >>> with yurlungur.UndoGroup("undo group"):
    >>>     for node in "hoge", "fuga", "piyo":
    >>>         yurlungur.YNode(node).delete()
    """

    def __init__(self, label):
        if env.Photoshop():
            self.label = meta.activeDocument.ActiveHistoryState
        else:
            self.label = label

    def __enter__(self):
        if env.Maya():
            meta.undoInfo(ock=1)
        elif env.Blender():
            self.undo = meta.context.user_preferences.edit.use_global_undo
            meta.context.user_preferences.edit.use_global_undo = False
        elif env.Davinci():
            meta.fusion.StartUndo()
        elif env.Photoshop():
            self.label = meta.activeDocument.activeHistoryState

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if env.Maya():
            meta.undoInfo(cck=1)
        elif env.Blender():
            meta.context.user_preferences.edit.use_global_undo = self.undo
        elif env.Davinci():
            meta.fusion.EndUndo()
        elif env.Photoshop():
            from yurlungur.adapters import photoshop
            meta.activeDocument.ActiveHistoryState = self.label
            photoshop.do("undo")
            # app.DoJavaScript("app.activeDocument.suspendHistory(\"undo\", \"%s\")")


def cache(func, *args, **kwargs):
    saved = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args in saved:
            return saved[args]
        result = func(*args)
        saved[args] = result
        return result

    return wrapper if sys.version_info < (3, 2) else functools.lcu_cache(*args, **kwargs)


def trace(func):
    try:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                if hasattr(logger.logger, "warning"):
                    logger.logger.warning(traceback.format_exc())
                else:
                    logger.logger.log(traceback.format_exc(), logger.Warning)
    except (NameError, ImportError):
        wrapper = func

    return wrapper


def timer(func):
    import yurlungur

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        yurlungur.logger.pprint(
            '{0} start'.format(func.__name__)
        )
        start_time = time.clock()
        ret = func(*args, **kwargs)
        end_time = time.clock()
        yurlungur.logger.pprint(
            '\n{0}: {1:,f}s'.format("total: ", (end_time - start_time))
        )
        return ret

    return wrapper


@contextlib.contextmanager
def threads(func):
    """
    Maya, Houdini, 3dsMax, Substance and Nuke
    >>>
    :param func:
    :return:
    """
    t = threading.Thread(target=__worker, args=(func,))
    t.start()
    t.join()


def __worker(func):
    """
    thread runner
    :param func:
    :return:
    """
    if env.Maya():
        import maya.utils as utils
        utils.executeDeferred(func)

    elif env.Houdini():
        meta

    elif env.Nuke():
        meta.executeInMainThreadWithResult(func)

    elif env.Max():
        try:
            func.acquire()
            with meta.mxstoken():
                func
        except:
            raise
        finally:
            if func.locked():
                func.release()

    return func
