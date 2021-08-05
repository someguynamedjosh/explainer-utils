from bpy.app.handlers import persistent
import importlib
import sys


def import_or_reload(module_name):
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        globals()[module_name] = importlib.import_module(module_name)


def clear_all_registries():
    global register_listeners, unregister_listeners, update_listeners, object_panel_layouts
    register_listeners.clear()
    unregister_listeners.clear()
    update_listeners.clear()
    object_panel_layouts.clear()


@persistent
def on_update(scene, depsgraph):
    global update_listeners
    for listener in update_listeners:
        listener(scene, depsgraph)


register_listeners = []
unregister_listeners = []
update_listeners = []
object_panel_layouts = []
