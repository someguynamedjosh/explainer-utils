import importlib
import sys


def import_or_reload(module_name):
    if module_name in sys.modules:
        print('reloaded')
        importlib.reload(sys.modules[module_name])
    else:
        print('imported')
        globals()[module_name] = importlib.import_module(module_name)


def clear_all_registries():
    global register_listeners, unregister_listeners, object_panel_layouts
    register_listeners.clear()
    unregister_listeners.clear()
    object_panel_layouts.clear()


register_listeners = []
unregister_listeners = []
object_panel_layouts = []
