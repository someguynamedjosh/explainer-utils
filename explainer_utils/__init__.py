bl_info = {
    "name": "Explainer Utils",
    "category": "All",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
}

from explainer_utils import bootstrap_utils

modules = [
    *["explainer_utils." + module_name for module_name in [
        "test_module",
    ]]
]

def register():
    bootstrap_utils.clear_all_listeners()
    for module in modules:
        bootstrap_utils.import_or_reload(module)
    for listener in bootstrap_utils.register_listeners:
        listener()

def unregister():
    for listener in bootstrap_utils.unregister_listeners:
        listener()
